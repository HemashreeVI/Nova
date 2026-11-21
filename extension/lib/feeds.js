// Every outside data source in one place. All are public, no API keys.
import { cached } from "./store.js";

async function json(url, init) {
  const r = await fetch(url, init);
  if (!r.ok) throw new Error(`${new URL(url).hostname} answered ${r.status}`);
  return r.json();
}

/* ---------------- LeetCode ---------------- */

async function lcQuery(query, variables = {}) {
  const j = await json("https://leetcode.com/graphql", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, variables }),
  });
  if (j.errors?.length) throw new Error(j.errors[0].message);
  return j.data;
}

const LC_PROFILE = `query novaProfile($username: String!) {
  allQuestionsCount { difficulty count }
  matchedUser(username: $username) {
    username
    profile { ranking }
    submitStatsGlobal { acSubmissionNum { difficulty count } }
    userCalendar { streak totalActiveDays }
    languageProblemCount { languageName problemsSolved }
  }
  recentAcSubmissionList(username: $username, limit: 10) { title titleSlug timestamp }
}`;

const LC_DAILY = `query novaDaily {
  activeDailyCodingChallengeQuestion { date link question { title difficulty topicTags { name } } }
}`;

export async function leetcodeDaily(opts) {
  return cached("lc:daily", async () => {
    const d = (await lcQuery(LC_DAILY)).activeDailyCodingChallengeQuestion;
    return {
      date: d.date,
      title: d.question.title,
      difficulty: d.question.difficulty,
      tags: d.question.topicTags.map((t) => t.name).slice(0, 3),
      url: "https://leetcode.com" + d.link,
    };
  }, { ttl: 30 * 60 * 1000, ...opts });
}

export async function leetcode(username, opts) {
  if (!username) return null;
  return cached(`lc:${username.toLowerCase()}`, async () => {
    const d = await lcQuery(LC_PROFILE, { username });
    const u = d.matchedUser;
    if (!u) throw new Error(`No LeetCode user "${username}"`);
    const solved = {}, totals = {};
    for (const x of u.submitStatsGlobal.acSubmissionNum) solved[x.difficulty] = x.count;
    for (const x of d.allQuestionsCount) totals[x.difficulty] = x.count;
    const langs = (u.languageProblemCount || []).sort((a, b) => b.problemsSolved - a.problemsSolved);
    const sql = langs.filter((l) => /sql|oracle|postgres/i.test(l.languageName)).reduce((n, l) => n + l.problemsSolved, 0);
    return {
      username: u.username,
      ranking: u.profile?.ranking,
      solved, totals, sql,
      languages: langs.slice(0, 4).map((l) => ({ name: l.languageName, solved: l.problemsSolved })),
      streak: u.userCalendar?.streak || 0,
      activeDays: u.userCalendar?.totalActiveDays || 0,
      recent: (d.recentAcSubmissionList || []).map((s) => ({
        title: s.title, url: `https://leetcode.com/problems/${s.titleSlug}/`, ts: Number(s.timestamp) * 1000,
      })),
    };
  }, { ttl: 5 * 60 * 1000, ...opts });
}

// LeetCode days run on UTC (they reset at 05:30 IST).
export const utcDay = (d = new Date()) => new Date(d).toISOString().slice(0, 10);
export const solvedToday = (lc, lcLog = {}) =>
  !!lcLog[utcDay()] || !!lc?.recent?.some((s) => utcDay(s.ts) === utcDay());
export function nextLeetCodeReset() {
  const d = new Date();
  return Date.UTC(d.getUTCFullYear(), d.getUTCMonth(), d.getUTCDate() + 1);
}

/* ---------------- GitHub (public API, 60 requests/hour without a token) ---------------- */

const localDay = (t) => {
  const d = new Date(t);
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
};

export async function github(username, opts) {
  if (!username) return null;
  return cached(`gh2:${username.toLowerCase()}`, async () => {
    const u = encodeURIComponent(username);
    const api = async (path) => {
      const r = await fetch(`https://api.github.com${path}`, { headers: { Accept: "application/vnd.github+json" } });
      if (r.status === 404) throw new Error(`No GitHub user "${username}"`);
      if (r.status === 403 || r.status === 429) throw new Error("GitHub rate limit, try again in a bit");
      if (!r.ok) throw new Error(`GitHub answered ${r.status}`);
      return r.json();
    };
    const [user, calendar, events] = await Promise.all([
      api(`/users/${u}`),
      contributionCalendar(username).catch(() => null),
      api(`/users/${u}/events/public?per_page=100`).catch(() => []),
    ]);

    // Fallback when the calendar page can't be read: build levels from public events.
    const days = calendar?.days || {};
    if (!calendar) {
      for (const e of events) {
        const k = localDay(Date.parse(e.created_at));
        const n = e.type === "PushEvent" ? Math.max(1, e.payload?.distinct_size || e.payload?.size || 1) : 1;
        days[k] = { count: (days[k]?.count || 0) + n };
      }
      for (const d of Object.values(days)) d.level = d.count < 2 ? 1 : d.count < 4 ? 2 : d.count < 8 ? 3 : 4;
    }
    const lastPush = events.filter((e) => e.type === "PushEvent").map((e) => Date.parse(e.created_at)).sort((a, b) => b - a)[0] || 0;
    return {
      login: user.login,
      name: user.name || user.login,
      avatar: user.avatar_url,
      url: user.html_url,
      days,
      total: calendar?.total ?? null,
      fromCalendar: !!calendar,
      lastPush,
    };
  }, { ttl: 10 * 60 * 1000, ...opts });
}

// The same contribution graph GitHub shows on your profile (public page, no token needed).
async function contributionCalendar(username) {
  const r = await fetch(`https://github.com/users/${encodeURIComponent(username)}/contributions`);
  if (!r.ok) throw new Error(`GitHub calendar answered ${r.status}`);
  const html = await r.text();
  const tips = {};
  for (const m of html.matchAll(/<tool-tip[^>]*\bfor="([^"]+)"[^>]*>([^<]*)<\/tool-tip>/g)) tips[m[1]] = m[2];
  const days = {};
  for (const m of html.matchAll(/<td\b[^>]*\bdata-date="(\d{4}-\d{2}-\d{2})"[^>]*>/g)) {
    const tag = m[0];
    const level = Number((tag.match(/data-level="(\d)"/) || [])[1] || 0);
    const id = (tag.match(/\bid="([^"]+)"/) || [])[1];
    const tip = tips[id] || "";
    const count = /^No /.test(tip) ? 0 : Number((tip.match(/^(\d[\d,]*)/) || [])[1]?.replace(/,/g, "") || (level ? 1 : 0));
    days[m[1]] = { level, count };
  }
  if (!Object.keys(days).length) throw new Error("Calendar layout not recognised");
  const total = html.match(/([\d,]+)\s+contributions?\s+in the last year/);
  return { days, total: total ? Number(total[1].replace(/,/g, "")) : null };
}

export const pushedToday = (gh) => (gh?.days?.[localDay(Date.now())]?.count || 0) > 0;

export function ghStreak(gh) {
  const d = new Date();
  const on = (x) => (gh?.days?.[localDay(x)]?.count || 0) > 0;
  if (!on(d)) d.setDate(d.getDate() - 1);
  let n = 0;
  while (on(d)) { n++; d.setDate(d.getDate() - 1); }
  return n;
}

/* ---------------- YouTube (channel page + public RSS feed, no API key) ---------------- */

export async function youtubeChannel(input, opts) {
  if (!input) return null;
  const meta = await cached(`ytmeta:${input.toLowerCase()}`, async () => {
    let id = (input.match(/UC[\w-]{22}/) || [])[0] || null;
    const handle = input.match(/@[\w.-]+/)?.[0];
    const page = id ? `https://www.youtube.com/channel/${id}` : `https://www.youtube.com/${handle || "@" + input.replace(/^.*youtube\.com\//, "")}`;
    const r = await fetch(page);
    if (!r.ok) throw new Error(`YouTube answered ${r.status}`);
    const html = await r.text();
    id ||= (html.match(/"(?:externalId|channelId|browseId)":"(UC[\w-]{22})"/) || html.match(/channel\/(UC[\w-]{22})/) || [])[1];
    if (!id) throw new Error("Couldn't find that channel");
    const og = (p) => decode((html.match(new RegExp(`<meta property="og:${p}" content="([^"]*)"`)) || [])[1] || "");
    const subs = (html.match(/"(?:simpleText|content|label)":"([\d.,]+\s?[KMBkmb]?)\s+subscribers?"/) || [])[1] || null;
    const videos = (html.match(/"(?:simpleText|content|label)":"([\d,.]+[KM]?)\s+videos?"/) || [])[1] || null;
    return { id, name: og("title"), avatar: og("image"), url: `https://www.youtube.com/channel/${id}`, handle: handle || null, subs, videos };
  }, { ttl: 6 * 60 * 60 * 1000, ...opts });

  const feed = await cached(`ytfeed:${meta.id}`, async () => {
    const r = await fetch(`https://www.youtube.com/feeds/videos.xml?channel_id=${meta.id}`);
    if (!r.ok) throw new Error(`YouTube feed answered ${r.status}`);
    const xml = await r.text();
    return [...xml.matchAll(/<entry>([\s\S]*?)<\/entry>/g)].map(([, e]) => {
      const vid = tag(e, "yt:videoId");
      return {
        id: vid,
        title: tag(e, "title"),
        url: `https://www.youtube.com/watch?v=${vid}`,
        thumb: `https://i.ytimg.com/vi/${vid}/mqdefault.jpg`,
        at: Date.parse(tag(e, "published")),
        views: Number((e.match(/<media:statistics views="(\d+)"/) || [])[1] || 0),
        short: /#shorts/i.test(e),
      };
    });
  }, { ttl: 30 * 60 * 1000, ...opts });

  return { ...meta, videos: meta.videos, feed: Array.isArray(feed) ? feed : [] };
}

/* ---------------- News ---------------- */

const decode = (s = "") => s
  .replace(/<!\[CDATA\[([\s\S]*?)\]\]>/g, "$1")
  .replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&quot;/g, '"').replace(/&#39;|&apos;/g, "'")
  .replace(/&#(\d+);/g, (_, n) => String.fromCharCode(n)).replace(/&amp;/g, "&").trim();
const tag = (xml, t) => decode((xml.match(new RegExp(`<${t}[^>]*>([\\s\\S]*?)</${t}>`)) || [])[1]);

async function googleNews(topic) {
  const q = encodeURIComponent(`${topic} when:2d`);
  const r = await fetch(`https://news.google.com/rss/search?q=${q}&hl=en-IN&gl=IN&ceid=IN:en`);
  if (!r.ok) throw new Error(`Google News answered ${r.status}`);
  const xml = await r.text();
  return [...xml.matchAll(/<item>([\s\S]*?)<\/item>/g)].slice(0, 4).map(([, it]) => {
    const source = tag(it, "source");
    let title = tag(it, "title");
    if (source && title.endsWith(` - ${source}`)) title = title.slice(0, -(source.length + 3));
    return { topic, title, url: tag(it, "link"), source, at: Date.parse(tag(it, "pubDate")) || Date.now() };
  });
}

async function hackerNews() {
  const j = await json("https://hn.algolia.com/api/v1/search?tags=front_page&hitsPerPage=8");
  return j.hits.map((h) => ({
    topic: "Hacker News",
    title: h.title,
    url: h.url || `https://news.ycombinator.com/item?id=${h.objectID}`,
    source: `${h.points} points`,
    at: h.created_at_i * 1000,
  }));
}

export async function news(topics, opts) {
  return cached(`news:${topics.join("|")}`, async () => {
    const all = await Promise.allSettled([...topics.map(googleNews), hackerNews()]);
    const items = all.flatMap((r) => (r.status === "fulfilled" ? r.value : []));
    if (!items.length) throw new Error("No news sources answered");
    const seen = new Set();
    return items
      .filter((n) => n.title && !seen.has(n.title.toLowerCase()) && seen.add(n.title.toLowerCase()))
      .sort((a, b) => b.at - a.at);
  }, { ttl: 30 * 60 * 1000, ...opts });
}

/* ---------------- Job boards with public APIs ---------------- */

export async function remotive(keywords) {
  const out = [];
  for (const kw of keywords.slice(0, 4)) {
    const j = await json(`https://remotive.com/api/remote-jobs?search=${encodeURIComponent(kw)}&limit=25`);
    for (const x of j.jobs || []) {
      out.push({
        title: x.title, company: x.company_name, url: x.url,
        location: `Remote · ${x.candidate_required_location || "Worldwide"}`,
        desc: (x.description || "").replace(/<[^>]+>/g, " "), tags: x.tags || [],
        posted: x.publication_date, salary: x.salary,
      });
    }
  }
  return out;
}

/* ---------------- Search pages the scanner opens ---------------- */

const kebab = (s) => s.toLowerCase().trim().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");

export function searchUrl({ site, keyword, location }) {
  const k = encodeURIComponent(keyword.trim());
  const l = location?.trim();
  switch (site) {
    case "naukri":
      return `https://www.naukri.com/${kebab(keyword)}-jobs${l ? `-in-${kebab(l)}` : ""}?k=${k}${l ? `&l=${encodeURIComponent(l)}` : ""}&experience=0&jobAge=7`;
    case "internshala":
      return `https://internshala.com/internships/keywords-${kebab(keyword)}/`;
    case "internshala-jobs":
      return `https://internshala.com/jobs/keywords-${kebab(keyword)}/`;
    case "linkedin":
      return `https://www.linkedin.com/jobs/search/?keywords=${k}${l ? `&location=${encodeURIComponent(l)}` : "&location=India"}&f_E=1%2C2&f_TPR=r604800`;
    case "indeed":
      return `https://in.indeed.com/jobs?q=${k}${l ? `&l=${encodeURIComponent(l)}` : ""}&fromage=7`;
    case "unstop":
      return `https://unstop.com/jobs?search=${k}`;
    default:
      return null;
  }
}

// Only these are opened automatically; the rest are read when you browse them yourself.
export const AUTO_SCAN_SITES = ["naukri", "internshala", "internshala-jobs"];
