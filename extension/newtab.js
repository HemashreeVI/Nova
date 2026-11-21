import { get, set } from "./lib/store.js";
import { DEFAULT_PROFILE } from "./lib/profile.js";
import { skillGaps } from "./lib/jobs.js";
import { daysLeft } from "./lib/match.js";
import { FACTS } from "./lib/facts.js";
import {
  f1, weather, leetcode, leetcodeDaily, solvedToday, nextLeetCodeReset, utcDay, news, searchUrl,
} from "./lib/feeds.js";

/* ---------------- tiny DOM helper (text only, never raw HTML) ---------------- */
function h(tag, attrs = {}, ...kids) {
  const el = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs || {})) {
    if (v == null || v === false) continue;
    if (k === "class") el.className = v;
    else if (k === "style") el.style.cssText = v;
    else if (k.startsWith("on")) el.addEventListener(k.slice(2), v);
    else if (k === "href") el.href = safeUrl(v);
    else el.setAttribute(k, v === true ? "" : v);
  }
  for (const k of kids.flat()) if (k != null && k !== false) el.append(k instanceof Node ? k : String(k));
  return el;
}
const $ = (id) => document.getElementById(id);
function safeUrl(u) {
  try { const x = new URL(u, location.href); return ["http:", "https:", "chrome-extension:"].includes(x.protocol) ? x.href : "#"; }
  catch { return "#"; }
}
const pad = (n) => String(n).padStart(2, "0");
const ago = (t) => {
  const m = Math.round((Date.now() - t) / 60000);
  if (m < 1) return "just now";
  if (m < 60) return `${m}m ago`;
  const hr = Math.round(m / 60);
  return hr < 24 ? `${hr}h ago` : `${Math.round(hr / 24)}d ago`;
};
const fmtDay = (t) => new Date(t).toLocaleDateString(undefined, { day: "numeric", month: "short" });
const fmtWhen = (t) => new Date(t).toLocaleString(undefined, { weekday: "short", month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" });

const state = { settings: null, f1: null, raceIdx: 0, lc: null, daily: null, jobs: {}, meta: {}, standingsTab: "drivers", jobTab: "top", drawerFilter: "all", unseen: new Set() };

/* ---------------- clock, greeting, facts ---------------- */
function tickClock() {
  const d = new Date();
  $("clock").textContent = `${pad(d.getHours())}:${pad(d.getMinutes())}`;
  const part = d.getHours() < 12 ? "morning" : d.getHours() < 17 ? "afternoon" : "evening";
  const name = state.settings?.name?.trim();
  $("greet").textContent = `Good ${part}${name ? `, ${name}` : ""} · ${d.toLocaleDateString(undefined, { weekday: "long", day: "numeric", month: "long" })}`;
}
let factIdx = Math.floor(Math.random() * FACTS.length);
function rotateFact() {
  const el = $("fact");
  el.style.opacity = 0;
  setTimeout(() => { el.textContent = `💡 ${FACTS[factIdx++ % FACTS.length]}`; el.style.opacity = 1; }, 400);
}

/* ---------------- countdown boxes ---------------- */
function countdown(el, target, units) {
  let s = Math.max(0, Math.floor((target - Date.now()) / 1000));
  const parts = { days: Math.floor(s / 86400), hours: Math.floor((s % 86400) / 3600), minutes: Math.floor((s % 3600) / 60), seconds: s % 60 };
  if (!units.includes("days")) parts.hours += parts.days * 24;
  el.replaceChildren(...units.map((u) => h("div", {}, h("b", {}, pad(parts[u])), h("span", {}, u))));
}

/* ---------------- F1 ---------------- */
const FLAGS = {
  British: "🇬🇧", Dutch: "🇳🇱", Monegasque: "🇲🇨", Spanish: "🇪🇸", Mexican: "🇲🇽", Australian: "🇦🇺", Italian: "🇮🇹",
  German: "🇩🇪", French: "🇫🇷", Canadian: "🇨🇦", Japanese: "🇯🇵", Thai: "🇹🇭", Chinese: "🇨🇳", Danish: "🇩🇰",
  Finnish: "🇫🇮", American: "🇺🇸", "New Zealander": "🇳🇿", Brazilian: "🇧🇷", Argentine: "🇦🇷", Argentinian: "🇦🇷",
  Austrian: "🇦🇹", Swiss: "🇨🇭", Belgian: "🇧🇪", Indian: "🇮🇳", Polish: "🇵🇱", Russian: "🇷🇺", Swedish: "🇸🇪",
};
const TEAM = {
  red_bull: "#3671C6", ferrari: "#E8002D", mercedes: "#27F4D2", mclaren: "#FF8000", aston_martin: "#229971",
  alpine: "#0093CC", williams: "#64C4FF", rb: "#6692FF", sauber: "#52E252", kick_sauber: "#52E252", audi: "#F50537",
  haas: "#B6BABD", cadillac: "#D4AF37",
};
const shortTeam = (n = "") => n.replace(/ F1 Team| Racing| Formula One Team| Team/g, "").replace("Red Bull", "Red Bull").slice(0, 14);

function renderStandings() {
  const ol = $("standings-rows");
  ol.className = "rows standings-full";
  const list = state.standingsTab === "drivers" ? state.f1?.drivers : state.f1?.teams;
  if (!list?.length) { ol.replaceChildren(h("li", { class: "muted pad" }, state.f1 ? "No standings yet this season." : "Couldn't load standings.")); return; }
  ol.replaceChildren(...list.map((r) => h("li", {},
    h("span", { class: "pos" }, r.pos),
    h("span", { class: "flag" }, FLAGS[r.nationality] || "🏁"),
    h("span", { class: "name" }, r.name),
    state.standingsTab === "drivers" ? h("span", { class: "team" }, h("i", { style: `background:${TEAM[r.teamId] || "#888"}` }), shortTeam(r.team)) : h("span", { class: "team" }, h("i", { style: `background:${TEAM[r.teamId] || "#888"}` }), `${r.wins} wins`),
    h("span", { class: "pts" }, r.points, h("small", {}, "Pts")),
  )));
}

async function renderRace() {
  const race = state.f1?.races?.[state.raceIdx];
  if (!race) { $("race-name").textContent = "Season schedule unavailable"; return; }
  const first = race.sessions[0]?.at || race.start;
  $("race-dates").textContent = `${fmtDay(first)} – ${fmtDay(race.start)}`.toUpperCase();
  $("race-name").textContent = race.name;
  $("race-circuit").textContent = race.circuit;
  const meta = $("race-meta");
  meta.replaceChildren(h("span", {}, "📍 ", `${race.locality}, ${race.country}`));
  weather(race.lat, race.lon).then((w) => {
    if (!w || state.f1.races[state.raceIdx] !== race) return;
    meta.append(h("span", { class: "sep" }), h("span", {}, "🌡 ", h("b", {}, `${w.temp}°C`)), h("span", { class: "sep" }), h("span", {}, `${w.icon} ${w.label}`));
  }).catch(() => {});

  const now = Date.now();
  const nextSession = race.sessions.find((s) => s.at > now);
  $("race-session").textContent = nextSession ? nextSession.name : "Race weekend finished";
  $("race-when").textContent = nextSession ? fmtWhen(nextSession.at) : "";
  $("race-stats").replaceChildren(
    h("div", {}, h("span", {}, "Round"), h("b", {}, `${race.round} / ${state.f1.races.length}`)),
    h("div", {}, h("span", {}, "Season"), h("b", {}, state.f1.season)),
  );
  $("race-schedule").replaceChildren(...race.sessions.map((s) => h("li", { class: s.at < now ? "past" : s === nextSession ? "next" : "" }, h("span", {}, s.name), h("span", {}, fmtWhen(s.at)))));
  state.raceTarget = nextSession?.at || null;
  tickRace();
}
function tickRace() {
  if (state.raceTarget) countdown($("race-count"), state.raceTarget, ["days", "hours", "minutes", "seconds"]);
  else $("race-count").replaceChildren(h("div", { class: "muted pad" }, "🏁 Finished: pick the next race above"));
}

async function loadF1(force) {
  try {
    state.f1 = await f1({ force });
  } catch {
    state.f1 = null;
  }
  renderStandings();
  if (!state.f1) { $("race-name").textContent = "F1 data unavailable"; return; }
  const now = Date.now();
  let idx = state.f1.races.findIndex((r) => r.start + 3 * 36e5 > now);
  if (idx < 0) idx = state.f1.races.length - 1;
  state.raceIdx = idx;
  $("race-pick").replaceChildren(...state.f1.races.map((r, i) => h("option", { value: i, selected: i === idx }, r.name.replace(" Grand Prix", " GP"))));
  renderRace();
}

/* ---------------- LeetCode ---------------- */
async function loadLeetCode(force) {
  const s = state.settings;
  const [daily, lc] = await Promise.allSettled([leetcodeDaily({ force }), leetcode(s.leetcode, { force })]);
  state.daily = daily.status === "fulfilled" ? daily.value : null;
  state.lc = lc.status === "fulfilled" ? lc.value : null;
  state.lcError = lc.status === "rejected" ? String(lc.reason?.message || lc.reason) : null;
  await renderLeetCode();
}

async function renderLeetCode() {
  const { daily, lc, settings } = state;
  const t = $("lc-title");
  t.textContent = daily?.title || "Today's problem";
  t.href = daily?.url || "https://leetcode.com/problemset/";
  const diff = $("lc-diff");
  diff.textContent = daily?.difficulty || "—";
  diff.className = `pill ${daily?.difficulty || ""}`;
  $("lc-tags").textContent = daily?.tags?.join(" · ") || "";
  $("lc-reset").textContent = fmtWhen(nextLeetCodeReset());

  const lcLog = await get("lcLog");
  const done = solvedToday(lc, lcLog);
  const st = $("lc-state");
  st.replaceChildren();
  if (done) st.append(h("span", { class: "ok" }, "✓ Solved today. Streak safe"));
  else st.append(h("span", { class: "warn" }, "Not solved yet today"));
  if (!settings.leetcode) {
    st.append(h("span", { class: "sep" }), h("button", { class: "link", onclick: () => openSettings() }, "Add LeetCode username"));
  } else if (state.lcError) {
    st.append(h("span", { class: "sep" }), h("span", { title: state.lcError }, "⚠ couldn't reach LeetCode"));
  }
  if (!done) {
    st.append(h("span", { class: "sep" }), h("button", {
      class: "link",
      onclick: async () => { const log = await get("lcLog"); log[utcDay()] = true; await set("lcLog", log); renderLeetCode(); },
    }, "Mark solved"));
  }

  const total = lc?.solved?.All;
  $("lc-stats").replaceChildren(
    h("div", {}, h("span", {}, "Solved"), h("b", {}, total ?? "—"), lc ? h("span", { style: "letter-spacing:0;text-transform:none;margin-top:2px" }, `E ${lc.solved.Easy} · M ${lc.solved.Medium} · H ${lc.solved.Hard}`) : ""),
    h("div", {}, h("span", {}, "Streak"), h("b", {}, lc ? `${lc.streak}🔥` : "—")),
    h("div", {}, h("span", {}, "SQL solved"), h("b", {}, lc ? lc.sql : "—")),
  );
  $("lc-recent").replaceChildren(...(lc?.recent?.length
    ? lc.recent.map((r) => h("li", {}, h("a", { href: r.url, target: "_blank", rel: "noopener" }, r.title), h("span", { class: "muted" }, ago(r.ts))))
    : [h("li", { class: "muted" }, settings.leetcode ? "No recent accepted submissions." : "Add your username in settings to see your solves.")]));
}

/* ---------------- jobs ---------------- */
const STATUSES = ["", "Applied", "OA / Test", "Interview", "Offer", "Rejected"];

function jobRow(j, full = false) {
  const p = j.fit;
  const c = p >= 70 ? "var(--green)" : p >= 45 ? "var(--amber)" : "var(--red)";
  const d = daysLeft(j.deadline);
  const side = [];
  if (d !== null && d >= 0) side.push(h("span", { class: `due ${d <= 2 ? "urgent" : ""}` }, d === 0 ? "Due today" : `${d}d left · ${fmtDay(j.deadline)}`));
  else if (d !== null && d < 0) side.push(h("span", { class: "muted" }, "Closed"));
  side.push(h("span", { class: "src" }, j.source));
  if (state.unseen.has(j.id)) side.push(h("span", { class: "due", style: "color:var(--red)" }, "NEW"));

  const stop = (fn) => (e) => { e.stopPropagation(); fn(e); };
  const patch = (pt) => chrome.runtime.sendMessage({ type: "jobs:patch", id: j.id, patch: pt });
  const acts = h("span", { class: "acts" },
    h("button", { class: `act ${j.saved ? "on" : ""}`, title: j.saved ? "Unsave" : "Save", onclick: stop(() => patch({ saved: !j.saved })) }, j.saved ? "♥" : "♡"),
    full ? h("select", { class: "status", title: "Application status", onclick: (e) => e.stopPropagation(), onchange: (e) => patch({ status: e.target.value || null, saved: true }) },
      ...STATUSES.map((s) => h("option", { value: s, selected: (j.status || "") === s }, s || "Status…"))) : null,
    !full ? h("button", { class: "act", title: "Mark applied", onclick: stop(() => patch({ status: "Applied", saved: true })) }, "✓") : null,
    h("button", { class: "act", title: j.hidden ? "Unhide" : "Not interested", onclick: stop(() => patch({ hidden: !j.hidden })) }, j.hidden ? "↺" : "✕"),
  );
  if (full) side.push(acts);

  return h("li", { onclick: () => j.url && window.open(j.url, "_blank", "noopener") , title: [j.reasons?.join(" · "), j.missing?.length ? `Missing: ${j.missing.join(", ")}` : ""].filter(Boolean).join("\n") },
    h("span", { class: "fit", style: `--p:${p};--c:${c}` }, h("b", {}, `${p}%`)),
    h("div", { class: "job-main" },
      h("div", { class: "job-title" }, j.title),
      h("div", { class: "job-sub" }, [j.company, j.location, j.status ? `● ${j.status}` : ""].filter(Boolean).join(" · ")),
      full ? h("div", { class: "reasons" }, [j.reasons?.join(" · "), j.missing?.length ? `missing: ${j.missing.slice(0, 4).join(", ")}` : ""].filter(Boolean).join("  |  ")) : null,
    ),
    h("div", { class: "job-side" }, ...(full ? side : [...side, acts])),
  );
}

function renderRadar() {
  const all = Object.values(state.jobs).filter((j) => !j.hidden);
  let list;
  if (state.jobTab === "saved") list = all.filter((j) => j.saved && !j.status).sort((a, b) => (daysLeft(a.deadline) ?? 999) - (daysLeft(b.deadline) ?? 999) || b.fit - a.fit);
  else if (state.jobTab === "applied") list = all.filter((j) => j.status).sort((a, b) => (b.updated || 0) - (a.updated || 0));
  else list = all.filter((j) => !j.status && (daysLeft(j.deadline) ?? 0) >= 0).sort((a, b) => b.fit - a.fit || b.firstSeen - a.firstSeen);
  const ol = $("radar-rows");
  if (!list.length) {
    const msg = state.jobTab === "top"
      ? (Object.keys(state.jobs).length ? "No open matches right now." : "No jobs yet. Click “Scan now”, or just browse Naukri / Internshala / LinkedIn and Nova will read the listings.")
      : state.jobTab === "saved" ? "Nothing saved yet. Tap ♡ on a job." : "Nothing in your pipeline yet. Tap ✓ when you apply.";
    ol.replaceChildren(h("li", { class: "muted pad" }, msg));
  } else ol.replaceChildren(...list.slice(0, 5).map((j) => jobRow(j)));

  const gaps = skillGaps(state.jobs);
  $("radar-gaps").replaceChildren(...(gaps.length ? [h("span", {}, "Top skill gaps:"), ...gaps.slice(0, 4).map(([s, n]) => h("span", { class: "chip", title: `Asked in ${n} jobs that fit you` }, s))] : []));
  $("saved-dot").hidden = !Object.values(state.jobs).some((j) => j.saved && !j.status && (daysLeft(j.deadline) ?? 99) <= 2 && (daysLeft(j.deadline) ?? -1) >= 0);
  renderScanStatus();
  if (!$("drawer-jobs").hidden) renderJobsDrawer();
}

function renderScanStatus() {
  const m = state.meta;
  const n = Object.keys(state.jobs).length;
  $("scan-status").textContent = m.lastScan ? `${n} jobs · scanned ${ago(m.lastScan)} ·` : `${n} jobs ·`;
}

function renderJobsDrawer() {
  const q = $("jobs-q").value.trim().toLowerCase();
  const min = Number($("jobs-min").value);
  $("jobs-min-v").textContent = `${min}%`;
  const f = state.drawerFilter;
  let list = Object.values(state.jobs).filter((j) =>
    f === "hidden" ? j.hidden :
    !j.hidden && (f === "saved" ? j.saved : f === "applied" ? !!j.status : true));
  if (f === "all") list = list.filter((j) => j.fit >= min);
  if (q) list = list.filter((j) => [j.title, j.company, j.location, ...(j.have || []), ...(j.missing || []), ...(j.tags || [])].join(" ").toLowerCase().includes(q));
  list.sort((a, b) => b.fit - a.fit);
  $("jobs-list").replaceChildren(...(list.length ? list.slice(0, 200).map((j) => jobRow(j, true)) : [h("li", { class: "muted pad" }, "No jobs match these filters.")]));

  const gaps = skillGaps(state.jobs);
  $("jobs-gaps").replaceChildren(...(gaps.length ? [h("span", {}, "Learn next (asked most in jobs that fit you):"), ...gaps.map(([s, n]) => h("span", { class: "chip" }, `${s} · ${n}`))] : []));

  const kw = state.settings.searches?.[0]?.keyword || "data analyst";
  const loc = state.settings.searches?.[0]?.location || "";
  $("searchers").replaceChildren(h("span", { class: "muted", style: "align-self:center;font-size:12.5px" }, "Browse & Nova reads it:"),
    ...[["naukri", "Naukri"], ["internshala", "Internshala"], ["linkedin", "LinkedIn"], ["indeed", "Indeed"], ["unstop", "Unstop"]]
      .map(([site, label]) => h("a", { href: searchUrl({ site, keyword: kw, location: loc }), target: "_blank", rel: "noopener" }, `${label} ↗`)));
}

async function loadJobs() {
  state.jobs = await get("jobs");
  state.meta = await get("jobMeta");
  renderRadar();
}

/* ---------------- news ticker ---------------- */
async function loadNews(force) {
  let items = [];
  try { items = await news(state.settings.newsTopics, { force }); } catch { /* offline */ }
  const nodes = [];
  const facts = [...FACTS].sort(() => Math.random() - 0.5);
  items.slice(0, 24).forEach((n, i) => {
    nodes.push(h("a", { href: n.url, target: "_blank", rel: "noopener" }, h("span", { class: "topic" }, n.topic), n.title, h("span", { class: "ago" }, `${n.source ? `${n.source} · ` : ""}${ago(n.at)}`)));
    if (i % 5 === 4) nodes.push(h("span", { class: "fact-item" }, `💡 ${facts[i % facts.length]}`));
  });
  if (!nodes.length) facts.slice(0, 8).forEach((f) => nodes.push(h("span", { class: "fact-item" }, `💡 ${f}`)));
  const track = $("ticker-track");
  track.replaceChildren(...nodes, ...nodes.map((n) => n.cloneNode(true)));
  track.style.setProperty("--dur", `${Math.max(60, nodes.length * 9)}s`);
}

/* ---------------- wallpaper ---------------- */
async function applyWallpaper() {
  const w = await get("wallpaper");
  const bg = $("bg");
  if (w) { bg.style.backgroundImage = `url("${w}")`; bg.classList.add("photo"); }
  else { bg.style.backgroundImage = ""; bg.classList.remove("photo"); }
}
async function pickWallpaper(file) {
  const img = await createImageBitmap(file);
  const scale = Math.min(1, 2560 / img.width);
  const c = new OffscreenCanvas(Math.round(img.width * scale), Math.round(img.height * scale));
  c.getContext("2d").drawImage(img, 0, 0, c.width, c.height);
  const blob = await c.convertToBlob({ type: "image/jpeg", quality: 0.86 });
  const url = await new Promise((r) => { const fr = new FileReader(); fr.onload = () => r(fr.result); fr.readAsDataURL(blob); });
  await set("wallpaper", url);
  applyWallpaper();
}

/* ---------------- drawers & settings ---------------- */
function openDrawer(id) { $(id).hidden = false; }
function closeDrawers() { document.querySelectorAll(".drawer").forEach((d) => (d.hidden = true)); history.replaceState(null, "", location.pathname); }

const SITES = [["naukri", "Naukri (auto)"], ["internshala", "Internshala internships (auto)"], ["internshala-jobs", "Internshala jobs (auto)"], ["linkedin", "LinkedIn"], ["indeed", "Indeed"], ["unstop", "Unstop"]];
function searchRow(s = { site: "naukri", keyword: "", location: "" }) {
  const row = h("div", { class: "search-row" },
    h("select", { name: "site" }, ...SITES.map(([v, l]) => h("option", { value: v, selected: s.site === v }, l))),
    h("input", { name: "keyword", placeholder: "keyword e.g. data analyst", value: s.keyword }),
    h("input", { name: "location", placeholder: "location", value: s.location || "" }),
    h("button", { type: "button", title: "Remove", onclick: () => row.remove() }, "×"),
  );
  return row;
}

async function openSettings(welcome = false) {
  const s = state.settings;
  const p = (await get("profile")) || DEFAULT_PROFILE;
  const f = $("settings-form");
  f.name.value = s.name;
  f.leetcode.value = s.leetcode;
  f.showF1.checked = s.showF1;
  f.lcReminders.value = s.lcReminders.join(", ");
  f.fitAlert.value = s.fitAlert;
  f.scanHours.value = s.scanHours;
  f.newsAlertHours.value = s.newsAlertHours;
  f.newsTopics.value = s.newsTopics.join(", ");
  f.remoteBoards.checked = s.remoteBoards;
  f.skills.value = p.skills.join(", ");
  f.roles.value = p.roles.join(", ");
  f.locations.value = p.locations.join(", ");
  $("search-rows").replaceChildren(...s.searches.map(searchRow));
  const src = Object.entries(state.meta.sources || {});
  $("sources").replaceChildren(...(src.length ? [h("b", { style: "color:var(--text)" }, "Last scan results")] : []),
    ...src.map(([k, v]) => h("div", { class: v.ok ? "" : "bad", title: v.error || "" }, h("span", {}, `${v.ok ? "✓" : "⚠"} ${k}`), h("span", {}, `${v.count} read · ${ago(v.at)}`))));
  $("welcome").hidden = !welcome;
  $("save-msg").textContent = "";
  openDrawer("drawer-settings");
}

const list = (v) => v.split(/[,\n]/).map((x) => x.trim()).filter(Boolean);

async function saveSettings(e) {
  e.preventDefault();
  const f = e.target;
  const searches = [...$("search-rows").children].map((r) => ({
    site: r.querySelector("[name=site]").value,
    keyword: r.querySelector("[name=keyword]").value.trim(),
    location: r.querySelector("[name=location]").value.trim(),
  })).filter((s) => s.keyword);
  const settings = {
    ...state.settings,
    name: f.name.value.trim(),
    leetcode: f.leetcode.value.trim().replace(/^.*leetcode\.com\/(u\/)?/i, "").replace(/\/$/, ""),
    showF1: f.showF1.checked,
    lcReminders: list(f.lcReminders.value).filter((t) => /^\d{1,2}:\d{2}$/.test(t)),
    fitAlert: Number(f.fitAlert.value) || 70,
    scanHours: Math.max(0, Number(f.scanHours.value) || 0),
    newsAlertHours: Math.max(0, Number(f.newsAlertHours.value) || 0),
    newsTopics: list(f.newsTopics.value).slice(0, 8),
    remoteBoards: f.remoteBoards.checked,
    searches,
  };
  const profile = { ...((await get("profile")) || DEFAULT_PROFILE), skills: list(f.skills.value.toLowerCase()), roles: list(f.roles.value.toLowerCase()), locations: list(f.locations.value.toLowerCase()) };
  const lcChanged = settings.leetcode !== state.settings.leetcode;
  const topicsChanged = settings.newsTopics.join() !== state.settings.newsTopics.join();
  await set("settings", settings);
  await set("profile", profile);
  state.settings = settings;
  $("save-msg").textContent = "Saved ✓ (jobs are being re-scored)";
  applyLayout();
  tickClock();
  if (lcChanged) loadLeetCode(true);
  if (topicsChanged) loadNews(true);
}

function applyLayout() {
  $("col-left").hidden = !state.settings.showF1;
  if (state.settings.showF1 && !state.f1) loadF1();
}

/* ---------------- wire up ---------------- */
function wire() {
  document.querySelectorAll("[data-expand]").forEach((b) => b.addEventListener("click", () => b.closest(".card").classList.toggle("open")));
  document.querySelectorAll("#standings .tab").forEach((b) => b.addEventListener("click", () => {
    state.standingsTab = b.dataset.tab;
    document.querySelectorAll("#standings .tab").forEach((x) => x.classList.toggle("on", x === b));
    renderStandings();
  }));
  document.querySelectorAll("#radar .tab").forEach((b) => b.addEventListener("click", () => {
    state.jobTab = b.dataset.jtab;
    document.querySelectorAll("#radar .tab").forEach((x) => x.classList.toggle("on", x === b));
    renderRadar();
  }));
  document.querySelectorAll("#jobs-tabs .tab").forEach((b) => b.addEventListener("click", () => {
    state.drawerFilter = b.dataset.f;
    document.querySelectorAll("#jobs-tabs .tab").forEach((x) => x.classList.toggle("on", x === b));
    renderJobsDrawer();
  }));
  $("race-pick").addEventListener("change", (e) => { state.raceIdx = Number(e.target.value); renderRace(); });
  $("jobs-q").addEventListener("input", renderJobsDrawer);
  $("jobs-min").addEventListener("input", renderJobsDrawer);
  $("open-jobs").addEventListener("click", () => { renderJobsDrawer(); openDrawer("drawer-jobs"); });
  $("btn-saved").addEventListener("click", () => {
    state.drawerFilter = "saved";
    document.querySelectorAll("#jobs-tabs .tab").forEach((x) => x.classList.toggle("on", x.dataset.f === "saved"));
    renderJobsDrawer(); openDrawer("drawer-jobs");
  });
  $("btn-menu").addEventListener("click", () => openSettings());
  $("btn-wall").addEventListener("click", () => $("wall-file").click());
  $("wall-file").addEventListener("change", (e) => e.target.files[0] && pickWallpaper(e.target.files[0]));
  $("wall-reset").addEventListener("click", async () => { await set("wallpaper", null); applyWallpaper(); });
  document.querySelectorAll("[data-close]").forEach((b) => b.addEventListener("click", closeDrawers));
  document.querySelectorAll(".drawer").forEach((d) => d.addEventListener("click", (e) => { if (e.target === d) closeDrawers(); }));
  document.addEventListener("keydown", (e) => { if (e.key === "Escape") closeDrawers(); });
  $("settings-form").addEventListener("submit", saveSettings);
  $("add-search").addEventListener("click", () => $("search-rows").append(searchRow()));
  $("test-notify").addEventListener("click", () => chrome.runtime.sendMessage({ type: "test:notify" }));

  $("scan-now").addEventListener("click", async () => {
    const b = $("scan-now");
    b.disabled = true;
    b.textContent = "Scanning… (minimized windows)";
    const r = await chrome.runtime.sendMessage({ type: "jobs:scan" }).catch((e) => ({ error: String(e) }));
    b.disabled = false;
    b.textContent = r?.error ? "Scan failed, retry" : `Found ${r.fresh} new (${r.good} strong) · Scan again`;
  });

  $("export").addEventListener("click", async () => {
    const all = await chrome.storage.local.get(null);
    delete all.cache;
    const blob = new Blob([JSON.stringify(all, null, 2)], { type: "application/json" });
    const a = h("a", { href: URL.createObjectURL(blob), download: `nova-backup-${new Date().toISOString().slice(0, 10)}.json` });
    a.click();
  });
  $("import").addEventListener("click", () => $("import-file").click());
  $("import-file").addEventListener("change", async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    try {
      const data = JSON.parse(await file.text());
      const allowed = ["settings", "profile", "jobs", "jobMeta", "lcLog", "notified", "newsSeen", "wallpaper"];
      await chrome.storage.local.set(Object.fromEntries(Object.entries(data).filter(([k]) => allowed.includes(k))));
      location.reload();
    } catch { $("save-msg").textContent = "That file isn't a Nova backup."; }
  });

  chrome.storage.onChanged.addListener((ch, area) => {
    if (area !== "local") return;
    if (ch.jobs) { state.jobs = ch.jobs.newValue || {}; renderRadar(); }
    if (ch.jobMeta) { state.meta = ch.jobMeta.newValue || {}; renderScanStatus(); }
    if (ch.settings) state.settings = { ...state.settings, ...ch.settings.newValue };
  });
}

async function main() {
  state.settings = await get("settings");
  wire();
  applyWallpaper();
  tickClock();
  rotateFact();
  applyLayout();
  setInterval(() => {
    tickClock();
    tickRace();
    countdown($("lc-count"), nextLeetCodeReset(), ["hours", "minutes", "seconds"]);
  }, 1000);
  countdown($("lc-count"), nextLeetCodeReset(), ["hours", "minutes", "seconds"]);
  setInterval(rotateFact, 20000);

  // Remember which jobs are new to you before marking them seen (clears the toolbar badge).
  const jobs = await get("jobs");
  state.unseen = new Set(Object.values(jobs).filter((j) => !j.seen).map((j) => j.id));
  await loadJobs();
  chrome.runtime.sendMessage({ type: "jobs:seen" }).catch(() => {});

  loadLeetCode();
  loadNews();
  if (location.hash === "#welcome" || (!state.settings.name && !state.settings.leetcode && !(await get("profile")))) openSettings(true);
  else if (location.hash === "#jobs") { renderJobsDrawer(); openDrawer("drawer-jobs"); }
}

main();
