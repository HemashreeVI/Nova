// Nova's background worker: reminders, job scanning, news alerts, notifications.
import { get, set, update } from "./lib/store.js";
import { DEFAULT_PROFILE } from "./lib/profile.js";
import { ingest, patchJob, rescoreAll } from "./lib/jobs.js";
import { daysLeft } from "./lib/match.js";
import {
  leetcode, leetcodeDaily, solvedToday, nextLeetCodeReset, news, remotive, searchUrl, AUTO_SCAN_SITES,
  github, pushedToday, ghStreak, gmailLabel,
} from "./lib/feeds.js";

const ICON = "icons/icon128.png";

// Storage writes go through one queue so tabs reporting at the same time don't overwrite each other.
let chain = Promise.resolve();
const serial = (fn) => {
  const p = chain.then(() => fn());
  chain = p.catch(() => {});
  return p;
};

/* ---------------- setup ---------------- */

chrome.runtime.onInstalled.addListener(async ({ reason }) => {
  if (!(await get("profile"))) await set("profile", DEFAULT_PROFILE);
  chrome.contextMenus.removeAll(() => {
    chrome.contextMenus.create({ id: "nova-save-job", title: "Save this job to Nova", contexts: ["page", "link"] });
  });
  await schedule();
  if (reason === "install") {
    chrome.tabs.create({ url: chrome.runtime.getURL("newtab.html#welcome") });
    chrome.alarms.create("jobscan-first", { delayInMinutes: 2 });
  }
});

chrome.runtime.onStartup.addListener(async () => {
  await closeLeftoverScanWindows();
  await schedule();
});

chrome.storage.onChanged.addListener((changes, area) => {
  if (area !== "local") return;
  if (changes.settings) schedule();
  if (changes.profile) serial(rescoreAll);
});

function nextAt(hhmm) {
  const [h, m] = String(hhmm).split(":").map(Number);
  const d = new Date();
  d.setHours(h || 0, m || 0, 0, 0);
  if (d <= Date.now()) d.setDate(d.getDate() + 1);
  return d.getTime();
}

async function ensureAlarm(name, info) {
  const cur = await chrome.alarms.get(name);
  if (cur && cur.periodInMinutes === info.periodInMinutes) return;
  await chrome.alarms.create(name, info);
}

async function schedule() {
  const s = await get("settings");
  const all = await chrome.alarms.getAll();
  for (const a of all) if (a.name.startsWith("lc-")) await chrome.alarms.clear(a.name);
  (s.lcReminders || []).forEach((t, i) => {
    if (/^\d{1,2}:\d{2}$/.test(t)) chrome.alarms.create(`lc-${i}`, { when: nextAt(t), periodInMinutes: 1440 });
  });

  if (s.scanHours > 0) await ensureAlarm("jobscan", { delayInMinutes: 5, periodInMinutes: s.scanHours * 60 });
  else await chrome.alarms.clear("jobscan");

  if (s.newsAlertHours > 0) await ensureAlarm("news", { delayInMinutes: 30, periodInMinutes: s.newsAlertHours * 60 });
  else await chrome.alarms.clear("news");

  if (!(await chrome.alarms.get("deadlines"))) chrome.alarms.create("deadlines", { when: nextAt("09:00"), periodInMinutes: 1440 });

  if (s.mailAlerts) await ensureAlarm("mail", { delayInMinutes: 1, periodInMinutes: 15 });
  else await chrome.alarms.clear("mail");
}

chrome.alarms.onAlarm.addListener(async (a) => {
  try {
    if (a.name.startsWith("lc-")) await leetcodeReminder();
    else if (a.name === "jobscan" || a.name === "jobscan-first") await scanJobs();
    else if (a.name === "news") await newsAlert();
    else if (a.name === "deadlines") await deadlineCheck();
    else if (a.name === "mail") await mailCheck();
  } catch (e) {
    console.warn("Nova alarm failed", a.name, e);
  }
});

/* ---------------- notifications ---------------- */

async function notify(id, { title, message, url }) {
  if (url) {
    const { notifUrls = {} } = await chrome.storage.session.get("notifUrls");
    notifUrls[id] = url;
    await chrome.storage.session.set({ notifUrls });
  }
  chrome.notifications.create(id, { type: "basic", iconUrl: ICON, title, message, priority: 1 });
}

chrome.notifications.onClicked.addListener(async (id) => {
  const { notifUrls = {} } = await chrome.storage.session.get("notifUrls");
  if (notifUrls[id]) chrome.tabs.create({ url: notifUrls[id] });
  chrome.notifications.clear(id);
});

const quietHours = () => { const h = new Date().getHours(); return h < 8 || h >= 23; };
const fmtDate = (iso) => new Date(iso).toLocaleDateString(undefined, { day: "numeric", month: "short" });

/* ---------------- LeetCode ---------------- */

async function leetcodeReminder() {
  const s = await get("settings");
  const lcLog = await get("lcLog");
  const [lcR, ghR, dailyR] = await Promise.allSettled([
    leetcode(s.leetcode, { force: true }),
    s.ghReminder ? github(s.github, { force: true }) : Promise.resolve(null),
    leetcodeDaily(),
  ]);
  const lc = lcR.value || null, gh = ghR.value || null, daily = dailyR.value || null;
  const lcDone = solvedToday(lc, lcLog);
  // Only nag about GitHub when we could actually check it.
  const ghDone = !s.ghReminder || !s.github || ghR.status === "rejected" || pushedToday(gh);
  if (lcDone && ghDone) return;

  const hrs = Math.max(0, Math.floor((nextLeetCodeReset() - Date.now()) / 36e5));
  const lines = [];
  if (!lcDone) lines.push(daily ? `LeetCode: ${daily.title} (${daily.difficulty}), ${hrs}h before reset` : `LeetCode: nothing solved yet, ${hrs}h before reset`);
  if (!ghDone) lines.push(`GitHub: no push today${ghStreak(gh) ? ` (keep your ${ghStreak(gh)}-day streak)` : ""}. Commit something small.`);
  const title = !lcDone && !ghDone ? "⏰ LeetCode + GitHub: not done yet today"
    : !lcDone ? (lc?.streak ? `🔥 Your ${lc.streak}-day LeetCode streak is at risk` : "⏰ LeetCode time")
    : "⏰ No GitHub push yet today";
  await notify(`lc-${Date.now()}`, {
    title,
    message: lines.join("\n"),
    url: !lcDone ? (daily?.url || "https://leetcode.com/problemset/") : (gh?.url || `https://github.com/${s.github}`),
  });
}

/* ---------------- job scanning ---------------- */

const scanWaiters = new Map(); // tabId -> (jobs) => void
let scanning = null;

async function rememberScanWindow(id, add) {
  const { scanWindows = [] } = await chrome.storage.session.get("scanWindows");
  const next = add ? [...scanWindows, id] : scanWindows.filter((w) => w !== id);
  await chrome.storage.session.set({ scanWindows: next });
}

async function closeLeftoverScanWindows() {
  const { scanWindows = [] } = await chrome.storage.session.get("scanWindows");
  for (const id of scanWindows) await chrome.windows.remove(id).catch(() => {});
  await chrome.storage.session.set({ scanWindows: [] });
}

// Opens a search page in a minimized window, lets the content script read it, then closes it.
async function scanPage(url) {
  let win;
  try {
    win = await chrome.windows.create({ url, focused: false, state: "minimized" });
  } catch (e) {
    return { jobs: [], error: String(e.message || e) };
  }
  const tabId = win.tabs[0].id;
  await rememberScanWindow(win.id, true);
  const jobs = await new Promise((resolve) => {
    const got = [];
    let settle = null;
    const finish = () => { scanWaiters.delete(tabId); clearTimeout(hard); clearTimeout(settle); resolve(got); };
    const hard = setTimeout(finish, 40000);
    scanWaiters.set(tabId, (list) => {
      got.push(...list);
      clearTimeout(settle);
      settle = setTimeout(finish, got.length ? 4000 : 12000);
    });
  });
  await chrome.windows.remove(win.id).catch(() => {});
  await rememberScanWindow(win.id, false);
  return { jobs, error: jobs.length ? null : "Page loaded but no job cards were read (layout change, login wall or captcha?)" };
}

async function scanJobs({ manual = false } = {}) {
  if (scanning) return scanning;
  scanning = (async () => {
    const s = await get("settings");
    const meta = await get("jobMeta");
    const status = { ...(meta.sources || {}) };
    const fresh = [];

    if (s.remoteBoards) {
      try {
        const kws = [...new Set(s.searches.map((x) => x.keyword))];
        const list = await remotive(kws);
        fresh.push(...(await serial(() => ingest(list, "remotive"))).fresh);
        status.remotive = { ok: true, count: list.length, at: Date.now() };
      } catch (e) {
        status.remotive = { ok: false, count: 0, at: Date.now(), error: String(e.message || e) };
      }
    }

    const autos = s.searches.filter((x) => AUTO_SCAN_SITES.includes(x.site) && x.keyword);
    const n = manual ? autos.length : Math.min(3, autos.length); // be gentle: 3 pages per automatic run
    for (let i = 0; i < n; i++) {
      const srch = autos[((meta.scanCursor || 0) + i) % autos.length];
      const url = searchUrl(srch);
      const res = await scanPage(url);
      if (res.jobs.length) fresh.push(...(await serial(() => ingest(res.jobs, srch.site))).fresh);
      status[`${srch.site} · ${srch.keyword}${srch.location ? ` · ${srch.location}` : ""}`] = {
        ok: res.jobs.length > 0, count: res.jobs.length, at: Date.now(), error: res.error, url,
      };
    }

    await update("jobMeta", (m) => ({
      ...m,
      lastScan: Date.now(),
      scanCursor: autos.length ? ((m.scanCursor || 0) + n) % autos.length : 0,
      sources: status,
    }));
    await announce(fresh);
    return { fresh: fresh.length, good: fresh.filter((j) => j.fit >= s.fitAlert).length };
  })();
  try { return await scanning; } finally { scanning = null; }
}

async function announce(fresh) {
  const s = await get("settings");
  const good = fresh.filter((j) => j.fit >= s.fitAlert).sort((a, b) => b.fit - a.fit);
  await refreshBadge();
  if (!good.length) return;
  const top = good[0];
  const dl = top.deadline ? ` · apply by ${fmtDate(top.deadline)}` : "";
  await notify(`jobs-${Date.now()}`, good.length === 1
    ? {
      title: `🎯 ${top.fit}% fit · ${top.title}`,
      message: `${top.company || "Unknown company"}${top.location ? ` · ${top.location}` : ""}${dl}\n${top.reasons.join(" · ")}`,
      url: top.url || chrome.runtime.getURL("newtab.html#jobs"),
    }
    : {
      title: `🎯 ${good.length} new jobs match your resume`,
      message: good.slice(0, 3).map((j) => `${j.fit}% ${j.title} · ${j.company}`).join("\n"),
      url: chrome.runtime.getURL("newtab.html#jobs"),
    });
}

async function refreshBadge() {
  const s = await get("settings");
  const jobs = Object.values(await get("jobs"));
  const n = jobs.filter((j) => !j.seen && !j.hidden && j.fit >= s.fitAlert).length;
  await chrome.action.setBadgeBackgroundColor({ color: "#e10600" });
  await chrome.action.setBadgeText({ text: n ? String(Math.min(n, 99)) : "" });
}

async function deadlineCheck() {
  const s = await get("settings");
  const jobs = Object.values(await get("jobs"));
  const notified = await get("notified");
  for (const j of jobs) {
    if (!j.deadline || j.hidden || j.status) continue;
    if (!j.saved && j.fit < s.fitAlert) continue;
    const d = daysLeft(j.deadline);
    if (d === null || d < 0 || d > 2) continue;
    const key = `dl:${j.id}:${d}`;
    if (notified[key]) continue;
    notified[key] = Date.now();
    await notify(`dl-${Date.now()}-${d}`, {
      title: d === 0 ? `⏳ Last day to apply: ${j.title}` : `⏳ ${d} day${d > 1 ? "s" : ""} left: ${j.title}`,
      message: `${j.company} · ${j.fit}% fit · apply by ${fmtDate(j.deadline)}`,
      url: j.url,
    });
  }
  // forget reminders older than 60 days
  for (const [k, t] of Object.entries(notified)) if (Date.now() - t > 60 * 864e5) delete notified[k];
  await set("notified", notified);
}

/* ---------------- CDC / NeoPAT mail ---------------- */

// Only the placement labels notify; job-alert mail is shown in the Mail box but stays quiet.
async function mailCheck() {
  const s = await get("settings");
  if (!s.mailAlerts) return;
  const labels = (s.mailLabels || []).filter((l) => /cdc|neopat/i.test(l));
  const results = await Promise.allSettled(labels.map((l) => gmailLabel(l, s.gmailAccount, { force: true })));
  const fresh = results.flatMap((r) => (r.status === "fulfilled" ? r.value.items.map((m) => ({ ...m, label: r.value.label })) : []));
  const prev = await get("mailSeen");
  const seen = new Set(prev || []);
  const unseen = fresh.filter((m) => !seen.has(m.id));
  await set("mailSeen", [...new Set([...fresh.map((m) => m.id), ...(prev || [])])].slice(0, 500));
  if (prev === null || !unseen.length) return; // first run: just remember what's already there
  const top = unseen.find((m) => /eligible|register|deadline|before/i.test(m.title)) || unseen[0];
  await notify(`mail-${Date.now()}`, {
    title: unseen.length === 1 ? `📩 ${top.label}: ${top.title}` : `📩 ${unseen.length} new ${[...new Set(unseen.map((m) => m.label))].join(" / ")} mails`,
    message: unseen.length === 1 ? (top.summary || "").slice(0, 180) : unseen.slice(0, 3).map((m) => `• ${m.title}`).join("\n"),
    url: unseen.length === 1 && top.url ? top.url : `https://mail.google.com/mail/u/${encodeURIComponent(s.gmailAccount || "0")}/#label/${encodeURIComponent(top.label)}`,
  });
}

/* ---------------- news ---------------- */

async function newsAlert() {
  const s = await get("settings");
  if (!s.newsAlertHours || quietHours()) return;
  const items = await news(s.newsTopics, { force: true });
  const seen = new Set(await get("newsSeen"));
  const recent = (n) => Date.now() - n.at < 12 * 36e5;
  const pick = items.find((n) => !seen.has(n.url) && n.topic !== "Hacker News" && recent(n))
    || items.find((n) => !seen.has(n.url) && recent(n));
  if (!pick) return;
  await set("newsSeen", [pick.url, ...seen].slice(0, 300));
  await notify(`news-${Date.now()}`, {
    title: `🔥 ${pick.topic}`,
    message: `${pick.title}${pick.source ? `\n${pick.source}` : ""}`,
    url: pick.url,
  });
}

/* ---------------- messages from pages, popup and content scripts ---------------- */

chrome.runtime.onMessage.addListener((msg, sender, reply) => {
  handle(msg, sender).then(reply, (e) => reply({ error: String(e.message || e) }));
  return true; // async reply
});

async function handle(msg, sender) {
  switch (msg?.type) {
    case "jobs:found": {
      const tabId = sender.tab?.id;
      if (scanWaiters.has(tabId)) { scanWaiters.get(tabId)(msg.jobs || []); return {}; }
      if (!msg.jobs?.length) return {};
      const { ids } = await serial(() => ingest(msg.jobs, msg.site || "web"));
      if (!msg.detail) return {};
      const jobs = await get("jobs");
      const detailIdx = msg.jobs.findIndex((j) => j.detail);
      return { detail: jobs[ids[detailIdx >= 0 ? detailIdx : 0]] || null };
    }
    case "jobs:add": {  // from the popup or context menu
      const { ids } = await serial(() => ingest([{ ...msg.job, manual: true }], msg.site || "saved"));
      if (!ids[0]) return { job: null };
      const job = msg.save ? await serial(() => patchJob(ids[0], { saved: true, seen: true })) : (await get("jobs"))[ids[0]];
      return { job };
    }
    case "jobs:patch":
      return { job: await serial(() => patchJob(msg.id, msg.patch)) };
    case "jobs:scan":
      return await scanJobs({ manual: true });
    case "jobs:seen": {
      await serial(async () => {
        const jobs = await get("jobs");
        for (const j of Object.values(jobs)) j.seen = true;
        await set("jobs", jobs);
      });
      await refreshBadge();
      return {};
    }
    case "test:notify":
      await notify(`test-${Date.now()}`, { title: "✅ Nova notifications work", message: "You'll get LeetCode, job and news alerts like this." });
      return {};
    default:
      return { error: "unknown message" };
  }
}

/* ---------------- right-click "Save this job to Nova" ---------------- */

chrome.contextMenus.onClicked.addListener(async (info, tab) => {
  if (info.menuItemId !== "nova-save-job" || !tab?.id) return;
  let job = null;
  try { job = (await chrome.tabs.sendMessage(tab.id, { type: "nova:extract" }))?.job; } catch { /* not a job site */ }
  if (!job) {
    const host = new URL(info.linkUrl || tab.url).hostname.replace(/^www\./, "");
    job = { title: tab.title, company: host.split(".")[0], url: info.linkUrl || tab.url };
  }
  const res = await handle({ type: "jobs:add", job, save: true, site: "saved" }, {});
  if (res.job) {
    await notify(`saved-${Date.now()}`, {
      title: `♥ Saved · ${res.job.fit}% fit`,
      message: `${res.job.title}${res.job.company ? ` · ${res.job.company}` : ""}`,
    });
  }
});
