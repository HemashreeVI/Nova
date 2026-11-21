// Public LeetCode + GitHub data, cached so new tabs open instantly.
import { get, set, dayKey } from "./store.js";

const TTL = 10 * 60 * 1000; // 10 minutes

async function cached(key, fn, { force = false, ttl = TTL } = {}) {
  const cache = await get("cache");
  const hit = cache[key];
  if (!force && hit && Date.now() - hit.ts < ttl) return hit.data;
  try {
    const data = await fn();
    const fresh = await get("cache"); // re-read: another fetch may have written meanwhile
    fresh[key] = { ts: Date.now(), data };
    await set("cache", fresh);
    return data;
  } catch (err) {
    if (hit) return { ...hit.data, stale: true, error: String(err.message || err) };
    throw err;
  }
}

/* ---------------- LeetCode ---------------- */

async function lcQuery(query, variables = {}) {
  const r = await fetch("https://leetcode.com/graphql", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, variables }),
  });
  if (!r.ok) throw new Error(`LeetCode answered ${r.status}`);
  const j = await r.json();
  if (j.errors?.length) throw new Error(j.errors[0].message);
  return j.data;
}

const LC_PROFILE = `query novaProfile($username: String!) {
  allQuestionsCount { difficulty count }
  matchedUser(username: $username) {
    username
    profile { ranking }
    submitStatsGlobal { acSubmissionNum { difficulty count } }
    userCalendar { streak totalActiveDays submissionCalendar }
  }
  recentAcSubmissionList(username: $username, limit: 10) { title titleSlug timestamp }
}`;

const LC_LANGS = `query novaLangs($username: String!) {
  matchedUser(username: $username) { languageProblemCount { languageName problemsSolved } }
}`;

const LC_DAILY = `query novaDaily {
  activeDailyCodingChallengeQuestion { date link question { title difficulty } }
}`;

export async function leetcode(username, opts) {
  if (!username) return null;
  return cached(`lc:${username.toLowerCase()}`, async () => {
    const [profile, langs, daily] = await Promise.allSettled([
      lcQuery(LC_PROFILE, { username }),
      lcQuery(LC_LANGS, { username }),
      lcQuery(LC_DAILY),
    ]);
    if (profile.status === "rejected") throw profile.reason;
    const d = profile.value;
    if (!d.matchedUser) throw new Error(`No LeetCode user "${username}"`);

    const solved = {}, totals = {};
    for (const x of d.matchedUser.submitStatsGlobal.acSubmissionNum) solved[x.difficulty] = x.count;
    for (const x of d.allQuestionsCount) totals[x.difficulty] = x.count;

    // submissionCalendar keys are UTC-midnight timestamps (seconds)
    const calendar = {};
    const raw = JSON.parse(d.matchedUser.userCalendar?.submissionCalendar || "{}");
    for (const [ts, n] of Object.entries(raw)) {
      calendar[new Date(Number(ts) * 1000).toISOString().slice(0, 10)] = n;
    }

    const languages = langs.status === "fulfilled"
      ? (langs.value.matchedUser?.languageProblemCount || [])
          .sort((a, b) => b.problemsSolved - a.problemsSolved)
          .map((l) => ({ name: l.languageName, solved: l.problemsSolved }))
      : [];

    const dq = daily.status === "fulfilled" ? daily.value.activeDailyCodingChallengeQuestion : null;

    return {
      username: d.matchedUser.username,
      ranking: d.matchedUser.profile?.ranking,
      solved, totals, calendar, languages,
      streak: d.matchedUser.userCalendar?.streak || 0,
      activeDays: d.matchedUser.userCalendar?.totalActiveDays || 0,
      recent: (d.recentAcSubmissionList || []).map((s) => ({
        title: s.title, slug: s.titleSlug, ts: Number(s.timestamp) * 1000,
      })),
      daily: dq ? {
        title: dq.question.title,
        difficulty: dq.question.difficulty,
        url: "https://leetcode.com" + dq.link,
      } : null,
    };
  }, opts);
}

/* ---------------- GitHub ---------------- */

async function gh(path) {
  const r = await fetch("https://api.github.com" + path, {
    headers: { Accept: "application/vnd.github+json" },
  });
  if (r.status === 404) throw new Error("GitHub user not found");
  if (r.status === 403 || r.status === 429) throw new Error("GitHub rate limit hit, try again later");
  if (!r.ok) throw new Error(`GitHub answered ${r.status}`);
  return r.json();
}

export async function github(username, opts) {
  if (!username) return null;
  return cached(`gh:${username.toLowerCase()}`, async () => {
    const u = encodeURIComponent(username);
    const [user, events, repos] = await Promise.all([
      gh(`/users/${u}`),
      gh(`/users/${u}/events/public?per_page=100`),
      gh(`/users/${u}/repos?sort=pushed&per_page=6`),
    ]);
    const activity = {};
    let lastPush = null;
    for (const e of events) {
      const k = dayKey(new Date(e.created_at));
      const weight = e.type === "PushEvent" ? Math.max(1, e.payload?.size || e.payload?.distinct_size || 1) : 1;
      activity[k] = (activity[k] || 0) + weight;
      if (e.type === "PushEvent" && (!lastPush || e.created_at > lastPush)) lastPush = e.created_at;
    }
    return {
      login: user.login,
      name: user.name,
      avatar: user.avatar_url,
      url: user.html_url,
      publicRepos: user.public_repos,
      followers: user.followers,
      activity, lastPush,
      repos: repos.filter((r) => !r.fork).slice(0, 5).map((r) => ({
        name: r.name, url: r.html_url, desc: r.description, lang: r.language,
        stars: r.stargazers_count, pushedAt: r.pushed_at,
      })),
    };
  }, opts);
}
