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
  return cached(`gh:${username.toLowerCase()}`, async () => {
    const u = encodeURIComponent(username);
    const gh = async (path) => {
      const r = await fetch(`https://api.github.com${path}`, { headers: { Accept: "application/vnd.github+json" } });
      if (r.status === 404) throw new Error(`No GitHub user "${username}"`);
      if (r.status === 403 || r.status === 429) throw new Error("GitHub rate limit, try again in a bit");
      if (!r.ok) throw new Error(`GitHub answered ${r.status}`);
      return r.json();
    };
    const [user, events, repos] = await Promise.all([
      gh(`/users/${u}`),
      gh(`/users/${u}/events/public?per_page=100`),
      gh(`/users/${u}/repos?sort=pushed&per_page=8`),
    ]);
    const activity = {};
    let lastPush = 0;
    for (const e of events) {
      const t = Date.parse(e.created_at);
      const n = e.type === "PushEvent" ? Math.max(1, e.payload?.distinct_size || e.payload?.size || 1) : 1;
      activity[localDay(t)] = (activity[localDay(t)] || 0) + n;
      if (e.type === "PushEvent" && t > lastPush) lastPush = t;
    }
    return {
      login: user.login,
      name: user.name || user.login,
      avatar: user.avatar_url,
      url: user.html_url,
      bio: user.bio,
      repos: user.public_repos,
      followers: user.followers,
      activity,
      lastPush,
      recent: repos.filter((r) => !r.fork).slice(0, 5).map((r) => ({
        name: r.name, url: r.html_url, lang: r.language, stars: r.stargazers_count, pushedAt: Date.parse(r.pushed_at),
      })),
    };
  }, { ttl: 10 * 60 * 1000, ...opts });
}

export const pushedToday = (gh) => (gh?.activity?.[localDay(Date.now())] || 0) > 0;

export function ghStreak(gh) {
  const d = new Date();
  if (!gh?.activity?.[localDay(d)]) d.setDate(d.getDate() - 1);
  let n = 0;
  while (gh?.activity?.[localDay(d)]) { n++; d.setDate(d.getDate() - 1); }
  return n;
}

/* ---------------- F1 (Jolpica, the community Ergast mirror) ---------------- */

const F1 = "https://api.jolpi.ca/ergast/f1";

export async function f1(opts) {
  return cached("f1", async () => {
    const [sched, drivers, teams] = await Promise.all([
      json(`${F1}/current.json?limit=40`),
      json(`${F1}/current/driverStandings.json?limit=40`),
      json(`${F1}/current/constructorStandings.json?limit=20`),
    ]);
    const at = (s) => (s?.date ? Date.parse(`${s.date}T${s.time || "12:00:00Z"}`) : null);
    const races = sched.MRData.RaceTable.Races.map((r) => {
      const sessions = [
        ["Practice 1", r.FirstPractice], ["Practice 2", r.SecondPractice], ["Practice 3", r.ThirdPractice],
        ["Sprint Qualifying", r.SprintQualifying || r.SprintShootout], ["Sprint", r.Sprint],
        ["Qualifying", r.Qualifying], ["Grand Prix", r],
      ].filter(([, s]) => s?.date).map(([name, s]) => ({ name, at: at(s) })).sort((a, b) => a.at - b.at);
      return {
        round: Number(r.round),
        name: r.raceName,
        circuit: r.Circuit.circuitName,
        locality: r.Circuit.Location.locality,
        country: r.Circuit.Location.country,
        lat: r.Circuit.Location.lat,
        lon: r.Circuit.Location.long,
        url: r.url,
        start: at(r),
        sessions,
      };
    });
    const ds = drivers.MRData.StandingsTable.StandingsLists[0]?.DriverStandings || [];
    const cs = teams.MRData.StandingsTable.StandingsLists[0]?.ConstructorStandings || [];
    return {
      season: sched.MRData.RaceTable.season,
      races,
      drivers: ds.map((d) => ({
        pos: Number(d.position), points: Number(d.points), wins: Number(d.wins),
        name: `${d.Driver.givenName} ${d.Driver.familyName}`, nationality: d.Driver.nationality,
        team: d.Constructors?.[0]?.name, teamId: d.Constructors?.[0]?.constructorId,
      })),
      teams: cs.map((c) => ({
        pos: Number(c.position), points: Number(c.points), wins: Number(c.wins),
        name: c.Constructor.name, nationality: c.Constructor.nationality, teamId: c.Constructor.constructorId,
      })),
    };
  }, { ttl: 60 * 60 * 1000, ...opts });
}

const WEATHER = {
  0: ["Clear sky", "☀"], 1: ["Mostly clear", "🌤"], 2: ["Partly cloudy", "⛅"], 3: ["Overcast", "☁"],
  45: ["Fog", "🌫"], 48: ["Fog", "🌫"], 51: ["Drizzle", "🌦"], 53: ["Drizzle", "🌦"], 55: ["Drizzle", "🌦"],
  61: ["Rain", "🌧"], 63: ["Rain", "🌧"], 65: ["Heavy rain", "🌧"], 71: ["Snow", "🌨"], 80: ["Showers", "🌦"],
  81: ["Showers", "🌦"], 82: ["Heavy showers", "⛈"], 95: ["Thunderstorm", "⛈"],
};

export async function weather(lat, lon) {
  if (!lat || !lon) return null;
  return cached(`wx:${lat},${lon}`, async () => {
    const j = await json(`https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}&current=temperature_2m,weather_code`);
    const [label, icon] = WEATHER[j.current.weather_code] || ["", "🌡"];
    return { temp: Math.round(j.current.temperature_2m), label, icon };
  }, { ttl: 30 * 60 * 1000 });
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
