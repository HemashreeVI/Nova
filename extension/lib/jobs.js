// Job storage: de-duplicate across sites, score against your profile, keep the list tidy.
import { get, set } from "./store.js";
import { DEFAULT_PROFILE } from "./profile.js";
import { scoreJob, findDeadline } from "./match.js";

const MAX_JOBS = 500;
const slug = (s = "") => s.toLowerCase().replace(/&/g, "and").replace(/[^a-z0-9]+/g, " ").trim();

export const jobId = (j) => `${slug(j.company) || "unknown"}|${slug(j.title)}`;

export async function getProfile() {
  return (await get("profile")) || DEFAULT_PROFILE;
}

function clean(r) {
  const text = (s, n) => (s ? String(s).replace(/\s+/g, " ").trim().slice(0, n) : "");
  let url = r.url || "";
  try {
    const u = new URL(url);
    if (!/^https?:$/.test(u.protocol)) url = "";
  } catch { url = ""; }
  return {
    title: text(r.title, 140),
    company: text(r.company, 90),
    location: text(r.location, 90),
    url,
    experience: text(r.experience, 60),
    salary: text(r.salary, 60),
    tags: (r.tags || []).map((t) => text(t, 40)).filter(Boolean).slice(0, 20),
    desc: text(r.desc, 4000),
    posted: r.posted || null,
    deadline: r.deadline || findDeadline(r.desc) || null,
  };
}

// Returns {fresh: jobs never seen before (for notifications), ids: id of every input job}.
export async function ingest(raw, source) {
  const profile = await getProfile();
  const jobs = await get("jobs");
  const fresh = [], ids = [];
  const now = Date.now();
  for (const r of raw || []) {
    const c = clean(r);
    if (!c.title || c.title.length < 3) continue;
    const id = jobId(c);
    ids.push(id);
    const prev = jobs[id];
    const merged = {
      ...(prev || {}),
      ...Object.fromEntries(Object.entries(c).filter(([, v]) => v && (!Array.isArray(v) || v.length))),
      id,
      source: prev?.source || source,
      sources: [...new Set([...(prev?.sources || []), source])],
      firstSeen: prev?.firstSeen || now,
      lastSeen: now,
    };
    if (prev?.desc && prev.desc.length > (c.desc || "").length) merged.desc = prev.desc;
    Object.assign(merged, scoreJob(merged, profile));
    jobs[id] = merged;
    if (!prev && !r.manual) fresh.push(merged);
  }
  await set("jobs", prune(jobs));
  return { fresh, ids };
}

export async function rescoreAll() {
  const profile = await getProfile();
  const jobs = await get("jobs");
  for (const j of Object.values(jobs)) Object.assign(j, scoreJob(j, profile));
  await set("jobs", jobs);
}

export async function patchJob(id, patch) {
  const jobs = await get("jobs");
  if (!jobs[id]) return null;
  jobs[id] = { ...jobs[id], ...patch, updated: Date.now() };
  await set("jobs", jobs);
  return jobs[id];
}

function prune(jobs) {
  const keep = (j) => j.saved || j.status;
  const monthAgo = Date.now() - 30 * 864e5;
  for (const [id, j] of Object.entries(jobs)) {
    if (!keep(j) && (j.hidden || j.lastSeen < monthAgo)) delete jobs[id];
  }
  const list = Object.values(jobs);
  if (list.length > MAX_JOBS) {
    list.filter((j) => !keep(j))
      .sort((a, b) => a.fit - b.fit || a.lastSeen - b.lastSeen)
      .slice(0, list.length - MAX_JOBS)
      .forEach((j) => delete jobs[j.id]);
  }
  return jobs;
}

// Skills that keep showing up in jobs that fit you reasonably well, but that you don't have yet.
export function skillGaps(jobs, minFit = 40) {
  const count = {};
  for (const j of Object.values(jobs)) {
    if (j.hidden || j.fit < minFit) continue;
    for (const s of j.missing || []) count[s] = (count[s] || 0) + 1;
  }
  return Object.entries(count).sort((a, b) => b[1] - a[1]).slice(0, 6);
}
