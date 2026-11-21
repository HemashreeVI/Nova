// Tiny wrapper around chrome.storage.local. Everything stays in your own browser profile.

export const DEFAULTS = {
  settings: {
    name: "",
    leetcode: "",
    github: "HemashreeVI",
    showF1: true,
    ghReminder: true,                   // also nudge if you haven't pushed to GitHub today
    lcReminders: ["19:00", "22:30"],   // local times; nudged only if you haven't solved today
    fitAlert: 70,                       // notify for new jobs at or above this fit %
    scanHours: 4,                       // auto-scan interval; 0 = only when you click "Scan now"
    searches: [                         // what the auto-scan looks for
      { site: "naukri", keyword: "data analyst", location: "chennai" },
      { site: "naukri", keyword: "python developer fresher", location: "" },
      { site: "naukri", keyword: "backend developer", location: "bangalore" },
      { site: "internshala", keyword: "data analytics", location: "" },
      { site: "internshala", keyword: "python", location: "" },
      { site: "internshala", keyword: "machine learning", location: "" },
    ],
    remoteBoards: true,                 // also poll Remotive's public API
    newsTopics: ["NVIDIA", "GTA 6", "OpenAI", "Data analytics", "Tech hiring India"],
    newsAlertHours: 4,                  // 0 = no news notifications
  },
  profile: null,      // filled from lib/profile.js on first run
  jobs: {},           // id -> job
  jobMeta: { lastScan: 0, scanCursor: 0, sources: {} },
  lcLog: {},          // "yyyy-mm-dd" -> true when you tick "solved" manually
  notified: {},       // notification bookkeeping
  newsSeen: [],       // links already pushed as notifications
  cache: {},          // API cache {key: {ts, data}}
  wallpaper: null,    // data URL of your own background picture
};

const clone = (v) => (v === undefined ? v : JSON.parse(JSON.stringify(v)));

export async function get(key) {
  const r = await chrome.storage.local.get(key);
  if (r[key] === undefined || r[key] === null) return clone(DEFAULTS[key]);
  if (key === "settings") return { ...DEFAULTS.settings, ...r[key] };
  return r[key];
}

export async function set(key, value) {
  await chrome.storage.local.set({ [key]: value });
}

export async function update(key, fn) {
  const current = await get(key);
  const next = fn(current);
  const value = next === undefined ? current : next;
  await set(key, value);
  return value;
}

// Local calendar date as yyyy-mm-dd.
export const dayKey = (d = new Date()) => {
  const x = new Date(d);
  return `${x.getFullYear()}-${String(x.getMonth() + 1).padStart(2, "0")}-${String(x.getDate()).padStart(2, "0")}`;
};

export async function cached(key, fn, { force = false, ttl = 10 * 60 * 1000 } = {}) {
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
    if (hit) return Array.isArray(hit.data) ? hit.data : { ...hit.data, stale: true };
    throw err;
  }
}
