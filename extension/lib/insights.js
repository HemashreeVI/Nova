// Turns raw data into "how am I doing today" answers. Shared by the new tab and background.
import { dayKey } from "./store.js";

export const GOALS = [
  { id: "leetcode", label: () => "Solve 1 LeetCode problem", icon: "◆" },
  { id: "github", label: () => "Push code to GitHub", icon: "⎇" },
  { id: "focus", label: (s) => `Focus ${s.dailyFocusGoal} min on learning`, icon: "◷" },
  { id: "apply", label: () => "Apply / reach out for 1 job", icon: "➤" },
];

export function todayStatus({ lc, gh, focusLog, jobs, goalsLog, settings }) {
  const k = dayKey();
  const auto = {
    leetcode: !!lc?.recent?.some((s) => dayKey(new Date(s.ts)) === k),
    github: (gh?.activity?.[k] || 0) > 0,
    focus: (focusLog[k] || 0) >= settings.dailyFocusGoal,
    apply: jobs.some((j) => j.status !== "Wishlist" && dayKey(new Date(j.updated || j.added)) === k),
  };
  const manual = goalsLog[k] || {};
  return GOALS.map((g) => ({
    id: g.id,
    icon: g.icon,
    label: g.label(settings),
    auto: auto[g.id],
    done: auto[g.id] || !!manual[g.id],
  }));
}

// date -> {lc, gh, focus, jobs, score}
export function activityMap({ lc, gh, focusLog, jobs }) {
  const map = {};
  const bump = (k, field, n) => {
    if (!n) return;
    map[k] ??= { lc: 0, gh: 0, focus: 0, jobs: 0 };
    map[k][field] += n;
  };
  for (const [k, n] of Object.entries(lc?.calendar || {})) bump(k, "lc", n);
  for (const [k, n] of Object.entries(gh?.activity || {})) bump(k, "gh", n);
  for (const [k, n] of Object.entries(focusLog || {})) bump(k, "focus", n);
  for (const j of jobs || []) bump(dayKey(new Date(j.added)), "jobs", 1);
  for (const v of Object.values(map)) {
    v.score = v.lc * 2 + v.gh + Math.floor(v.focus / 15) + v.jobs * 2;
  }
  return map;
}

// Consecutive active days ending today (or yesterday, so the streak survives until you act today).
export function streak(map) {
  const d = new Date();
  if (!map[dayKey(d)]) d.setDate(d.getDate() - 1);
  let n = 0;
  while (map[dayKey(d)]) {
    n++;
    d.setDate(d.getDate() - 1);
  }
  return n;
}

export function bestStreak(map) {
  const days = Object.keys(map).sort();
  let best = 0, run = 0, prev = null;
  for (const k of days) {
    const cur = new Date(k + "T12:00:00");
    run = prev && (cur - prev) / 864e5 === 1 ? run + 1 : 1;
    best = Math.max(best, run);
    prev = cur;
  }
  return best;
}

// Figure out what kind of page a URL is, so the popup can offer the right action.
export function classify(url = "", title = "") {
  let u;
  try { u = new URL(url); } catch { return { kind: "other", title }; }
  const host = u.hostname.replace(/^www\./, "");
  const clean = (t) => t.replace(/\s*[-|–]\s*(YouTube|LeetCode|LinkedIn|GitHub)\s*$/i, "").trim();

  if ((host === "youtube.com" || host === "m.youtube.com") && u.pathname === "/watch") {
    return { kind: "video", title: clean(title.replace(/^\(\d+\)\s*/, "")), id: u.searchParams.get("v") };
  }
  if (host === "youtu.be") return { kind: "video", title: clean(title), id: u.pathname.slice(1) };

  const lc = u.pathname.match(/^\/problems\/([^/]+)/);
  if (host === "leetcode.com" && lc) {
    const pretty = lc[1].split("-").map((w) => w[0].toUpperCase() + w.slice(1)).join(" ");
    return { kind: "leetcode", title: clean(title).replace(/\s*-\s*LeetCode.*$/i, "") || pretty, url: `https://leetcode.com/problems/${lc[1]}/` };
  }

  const repo = u.pathname.match(/^\/([^/]+)\/([^/]+)/);
  if (host === "github.com" && repo && !["settings", "orgs", "topics", "search"].includes(repo[1])) {
    return { kind: "repo", title: `${repo[1]}/${repo[2]}`, url: `https://github.com/${repo[1]}/${repo[2]}` };
  }

  const jobHosts = ["linkedin.com", "naukri.com", "internshala.com", "indeed.com", "in.indeed.com",
    "wellfound.com", "glassdoor.com", "glassdoor.co.in", "instahyre.com", "foundit.in", "cutshort.io",
    "unstop.com", "lever.co", "jobs.lever.co", "greenhouse.io", "boards.greenhouse.io", "myworkdayjobs.com"];
  const looksJob = jobHosts.some((h) => host === h || host.endsWith("." + h)) &&
    !(host.endsWith("linkedin.com") && !/\/jobs\//.test(u.pathname));
  if (looksJob || /(^|\.)careers?\.|\/careers?\/|\/jobs?\//i.test(host + u.pathname)) {
    return { kind: "job", ...parseJob(title, host) };
  }
  return { kind: "other", title: clean(title) };
}

export function parseJob(title = "", host = "") {
  let t = title.replace(/^\(\d+\)\s*/, "").replace(/\s*[|–-]\s*(LinkedIn|Naukri\.com|Indeed.*|Glassdoor.*|Internshala|Wellfound)\s*$/i, "");
  let role = t, company = "";
  let m = t.match(/^(.*?)\s+(?:at|@)\s+(.+?)(?:\s*[|–-].*)?$/i);
  if (m) { role = m[1]; company = m[2]; }
  else if ((m = t.match(/^(.+?)\s*[|–-]\s*(.+?)(?:\s*[|–-].*)?$/))) { role = m[1]; company = m[2]; }
  if (!company) {
    const parts = host.split(".");
    const base = parts.find((p) => !["www", "jobs", "careers", "career", "boards"].includes(p)) || "";
    company = base ? base[0].toUpperCase() + base.slice(1) : "";
  }
  return { role: role.trim().slice(0, 120), company: company.trim().slice(0, 80) };
}
