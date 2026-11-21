import { get, set } from "./lib/store.js";
import { DEFAULT_PROFILE } from "./lib/profile.js";
import { skillGaps } from "./lib/jobs.js";
import { daysLeft } from "./lib/match.js";
import { FACTS } from "./lib/facts.js";
import {
  leetcode, leetcodeDaily, solvedToday, nextLeetCodeReset, utcDay, news, searchUrl,
  github, ghStreak, youtubeChannel,
} from "./lib/feeds.js";

/* ---------------- tiny DOM helper (text only, never raw HTML) ---------------- */
function h(tag, attrs = {}, ...kids) {
  const el = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs || {})) {
    if (v == null || v === false) continue;
    if (k === "class") el.className = v;
    else if (k === "style") el.style.cssText = v;
    else if (k.startsWith("on")) el.addEventListener(k.slice(2), v);
    else if (k === "href" || k === "src") el[k] = safeUrl(v);
    else el.setAttribute(k, v === true ? "" : v);
  }
  for (const k of kids.flat()) if (k != null && k !== false) el.append(k instanceof Node ? k : String(k));
  return el;
}
const put = (el, ...kids) => el.replaceChildren(...kids.flat().filter((k) => k != null && k !== false));
const $ = (id) => document.getElementById(id);
function safeUrl(u) {
  try { const x = new URL(u, location.href); return ["http:", "https:", "chrome-extension:", "data:"].includes(x.protocol) ? x.href : "#"; }
  catch { return "#"; }
}
const pad = (n) => String(n).padStart(2, "0");
const ago = (t) => {
  const m = Math.round((Date.now() - t) / 60000);
  if (m < 1) return "just now";
  if (m < 60) return `${m}m ago`;
  const hr = Math.round(m / 60);
  if (hr < 24) return `${hr}h ago`;
  const d = Math.round(hr / 24);
  return d < 60 ? `${d}d ago` : `${Math.round(d / 30)}mo ago`;
};
const compact = (n) => new Intl.NumberFormat("en", { notation: "compact", maximumFractionDigits: 1 }).format(n);
const fmtDay = (t) => new Date(t).toLocaleDateString(undefined, { day: "numeric", month: "short" });
const fmtWhen = (t) => new Date(t).toLocaleString(undefined, { weekday: "short", hour: "2-digit", minute: "2-digit" });
const localDay = (d) => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;

const state = { settings: null, layout: null, lc: null, daily: null, jobs: {}, meta: {}, jobTab: "top", drawerFilter: "all", unseen: new Set(), editing: false };

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

function countdown(el, target) {
  const s = Math.max(0, Math.floor((target - Date.now()) / 1000));
  const parts = [["hours", Math.floor(s / 3600)], ["minutes", Math.floor((s % 3600) / 60)], ["seconds", s % 60]];
  el.replaceChildren(...parts.map(([u, v]) => h("div", {}, h("b", {}, pad(v)), h("span", {}, u))));
}

/* ---------------- YouTube ---------------- */
async function loadYouTube(force) {
  const ch = state.settings.youtube;
  if (!ch) {
    $("yt-name").textContent = "Your YouTube channel";
    put($("yt-sub"), h("button", { class: "link", onclick: (e) => { e.preventDefault(); openSettings(); } }, "Add your channel in settings"));
    $("yt-latest").hidden = true;
    put($("yt-list"));
    put($("yt-state"));
    return relayout();
  }
  let yt = null, err = null;
  try { yt = await youtubeChannel(ch, { force }); } catch (e) { err = String(e.message || e); }
  if (!yt) {
    $("yt-name").textContent = ch;
    $("yt-sub").textContent = "";
    put($("yt-state"), h("span", { class: "warn" }, "⚠ Couldn't load the channel"), h("span", { class: "sep" }), h("span", {}, err));
    return relayout();
  }
  $("yt-link").href = safeUrl(yt.url);
  if (yt.avatar) $("yt-avatar").src = safeUrl(yt.avatar);
  $("yt-name").textContent = yt.name || ch;
  $("yt-sub").textContent = [yt.subs && `${yt.subs} subscribers`, yt.videos && `${yt.videos} videos`, !yt.subs && yt.handle].filter(Boolean).join(" · ") || "YouTube channel";

  const [latest, ...rest] = yt.feed;
  $("yt-latest").hidden = !latest;
  if (latest) {
    $("yt-latest").href = safeUrl(latest.url);
    $("yt-thumb").src = safeUrl(latest.thumb);
    $("yt-title").textContent = latest.title;
    $("yt-meta").textContent = `${compact(latest.views)} views · ${ago(latest.at)}`;
  }
  put($("yt-list"), rest.slice(0, 3).map((v) => h("li", {},
    h("a", { href: v.url, target: "_blank", rel: "noopener", title: v.title }, v.title),
    h("span", { class: "muted" }, `${compact(v.views)} · ${ago(v.at)}`))));

  const days = latest ? Math.floor((Date.now() - latest.at) / 864e5) : null;
  const total = yt.feed.reduce((n, v) => n + v.views, 0);
  put($("yt-state"),
    days === null ? h("span", {}, "No uploads yet") :
      days >= 7 ? h("span", { class: "warn" }, `Last upload ${days} days ago. Time for a new one?`) :
        h("span", { class: "ok" }, `Uploaded ${days === 0 ? "today" : `${days}d ago`}`),
    total ? h("span", { class: "sep" }) : null,
    total ? h("span", {}, `${compact(total)} views on last ${yt.feed.length}`) : null);
  relayout();
}

/* ---------------- GitHub ---------------- */
const WEEKS = 21; // fits the card: 28px day labels + 21 weeks × 13px
const MONTHS = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split(" ");

async function loadGitHub(force) {
  const user = state.settings.github;
  let gh = null, err = null;
  if (user) {
    try { gh = await github(user, { force }); } catch (e) { err = String(e.message || e); }
  }
  $("gh-link").href = safeUrl(gh?.url || (user ? `https://github.com/${encodeURIComponent(user)}` : "https://github.com/"));
  if (gh?.avatar) $("gh-avatar").src = safeUrl(gh.avatar);
  $("gh-name").textContent = gh?.name || user || "GitHub";
  $("gh-login").textContent = gh ? `@${gh.login}` : user ? "" : "Add your username in settings";

  // Calendar: Sunday-first week columns, like github.com
  const start = new Date();
  start.setHours(12, 0, 0, 0);
  start.setDate(start.getDate() - start.getDay() - (WEEKS - 1) * 7);
  const today = localDay(new Date());
  const cells = [], months = [];
  let lastMonth = -1, lastLabelCol = -9;
  let shownTotal = 0;
  const step = 13; // cell 10px + gap 3px
  for (let w = 0; w < WEEKS; w++) {
    const first = new Date(start);
    first.setDate(start.getDate() + w * 7);
    if (first.getMonth() !== lastMonth) {
      if (w - lastLabelCol >= 3 && w <= WEEKS - 2) {
        months.push(h("span", { style: `left:${w * step}px` }, MONTHS[first.getMonth()]));
        lastLabelCol = w;
      }
      lastMonth = first.getMonth();
    }
    for (let d = 0; d < 7; d++) {
      const day = new Date(first);
      day.setDate(first.getDate() + d);
      const k = localDay(day);
      if (k > today) { cells.push(h("i", { class: "future" })); continue; }
      const info = gh?.days?.[k];
      const n = info?.count || 0;
      shownTotal += n;
      cells.push(h("i", {
        class: `${info?.level ? `l${info.level}` : ""}${k === today ? " today" : ""}`,
        title: `${n === 0 ? "No" : n} contribution${n === 1 ? "" : "s"} on ${day.toLocaleDateString(undefined, { month: "long", day: "numeric" })}`,
      }));
    }
  }
  put($("gh-months"), months);
  put($("gh-grid"), cells);
  $("gh-total").textContent = !gh ? "" : gh.total != null ? `${gh.total.toLocaleString()} contributions this year` : `${shownTotal} public contributions shown`;

  const todayCount = gh?.days?.[today]?.count || 0;
  const streak = gh ? ghStreak(gh) : 0;
  const st = $("gh-state");
  if (!user) put(st, h("button", { class: "link", onclick: () => openSettings() }, "Add your GitHub username"));
  else if (!gh) put(st, h("span", { class: "warn" }, "⚠ Couldn't reach GitHub"), h("span", { class: "sep" }), h("span", {}, err || ""));
  else put(st,
    todayCount ? h("span", { class: "ok" }, `✓ ${todayCount} contribution${todayCount > 1 ? "s" : ""} today`) : h("span", { class: "warn" }, "No contributions yet today"),
    streak ? h("span", { class: "sep" }) : null,
    streak ? h("span", {}, `${streak}-day streak 🔥`) : null);
  relayout();
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
  t.href = safeUrl(daily?.url || "https://leetcode.com/problemset/");
  const diff = $("lc-diff");
  diff.textContent = daily?.difficulty || "—";
  diff.className = `pill ${daily?.difficulty || ""}`;
  $("lc-tags").textContent = daily?.tags?.join(" · ") || "";
  $("lc-reset").textContent = fmtWhen(nextLeetCodeReset());

  const done = solvedToday(lc, await get("lcLog"));
  put($("lc-state"),
    done ? h("span", { class: "ok" }, "✓ Solved today, streak safe") : h("span", { class: "warn" }, "Not solved yet today"),
    !settings.leetcode ? [h("span", { class: "sep" }), h("button", { class: "link", onclick: () => openSettings() }, "Add username")] : null,
    settings.leetcode && state.lcError ? [h("span", { class: "sep" }), h("span", { title: state.lcError }, "⚠ offline")] : null,
    !done ? [h("span", { class: "sep" }), h("button", {
      class: "link",
      onclick: async () => { const log = await get("lcLog"); log[utcDay()] = true; await set("lcLog", log); renderLeetCode(); },
    }, "Mark solved")] : null);

  put($("lc-stats"),
    h("div", {}, h("span", {}, "Solved"), h("b", {}, lc?.solved?.All ?? "—"), lc ? h("span", { style: "letter-spacing:0;text-transform:none" }, `E ${lc.solved.Easy} · M ${lc.solved.Medium} · H ${lc.solved.Hard}`) : null),
    h("div", {}, h("span", {}, "Streak"), h("b", {}, lc ? `${lc.streak}🔥` : "—")),
    h("div", {}, h("span", {}, "SQL"), h("b", {}, lc ? lc.sql : "—")));
  put($("lc-recent"), lc?.recent?.length
    ? lc.recent.slice(0, 6).map((r) => h("li", {}, h("a", { href: r.url, target: "_blank", rel: "noopener" }, r.title), h("span", { class: "muted" }, ago(r.ts))))
    : [h("li", { class: "muted" }, settings.leetcode ? "No recent accepted submissions." : "Add your username in settings.")]);
  relayout();
}

/* ---------------- jobs ---------------- */
const STATUSES = ["", "Applied", "OA / Test", "Interview", "Offer", "Rejected"];

function jobRow(j, full = false) {
  const p = j.fit;
  const c = p >= 70 ? "var(--green)" : p >= 45 ? "var(--amber)" : "var(--red)";
  const d = daysLeft(j.deadline);
  const side = [];
  if (d !== null && d >= 0) side.push(h("span", { class: `due ${d <= 2 ? "urgent" : ""}` }, d === 0 ? "Due today" : `${d}d left`));
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

  return h("li", {
    onclick: () => j.url && window.open(j.url, "_blank", "noopener"),
    title: [j.reasons?.join(" · "), j.missing?.length ? `Missing: ${j.missing.join(", ")}` : ""].filter(Boolean).join("\n"),
  },
    h("span", { class: "fit", style: `--p:${p};--c:${c}` }, h("b", {}, `${p}%`)),
    h("div", { class: "job-main" },
      h("div", { class: "job-title" }, j.title),
      h("div", { class: "job-sub" }, [j.company, j.location, j.status ? `● ${j.status}` : ""].filter(Boolean).join(" · ")),
      full ? h("div", { class: "reasons" }, [j.reasons?.join(" · "), j.missing?.length ? `missing: ${j.missing.slice(0, 4).join(", ")}` : ""].filter(Boolean).join("  |  ")) : null),
    h("div", { class: "job-side" }, ...side, acts),
  );
}

function renderRadar() {
  const all = Object.values(state.jobs).filter((j) => !j.hidden);
  let list;
  if (state.jobTab === "saved") list = all.filter((j) => j.saved && !j.status).sort((a, b) => (daysLeft(a.deadline) ?? 999) - (daysLeft(b.deadline) ?? 999) || b.fit - a.fit);
  else if (state.jobTab === "applied") list = all.filter((j) => j.status).sort((a, b) => (b.updated || 0) - (a.updated || 0));
  else list = all.filter((j) => !j.status && j.fit >= 40 && (daysLeft(j.deadline) ?? 0) >= 0).sort((a, b) => b.fit - a.fit || b.firstSeen - a.firstSeen);
  if (!list.length) {
    const msg = state.jobTab === "top"
      ? (Object.keys(state.jobs).length ? "No open matches right now." : "No jobs yet. Click “Scan now”, or browse Naukri / Internshala / LinkedIn and Nova reads the listings.")
      : state.jobTab === "saved" ? "Nothing saved yet. Tap ♡ on a job." : "Nothing in your pipeline yet. Tap ✓ when you apply.";
    put($("radar-rows"), h("li", { class: "muted pad" }, msg));
  } else put($("radar-rows"), list.slice(0, 4).map((j) => jobRow(j)));

  const gaps = skillGaps(state.jobs);
  put($("radar-gaps"), gaps.length ? [h("span", {}, "Skill gaps:"), ...gaps.slice(0, 4).map(([s, n]) => h("span", { class: "chip", title: `Asked in ${n} jobs that fit you` }, s))] : []);
  $("saved-dot").hidden = !Object.values(state.jobs).some((j) => j.saved && !j.status && (daysLeft(j.deadline) ?? 99) <= 2 && (daysLeft(j.deadline) ?? -1) >= 0);
  renderScanStatus();
  if (!$("drawer-jobs").hidden) renderJobsDrawer();
  relayout();
}

function renderScanStatus() {
  const n = Object.keys(state.jobs).length;
  $("scan-status").textContent = state.meta.lastScan ? `${n} jobs · ${ago(state.meta.lastScan)} ·` : `${n} jobs ·`;
}

function renderJobsDrawer() {
  const q = $("jobs-q").value.trim().toLowerCase();
  const min = Number($("jobs-min").value);
  $("jobs-min-v").textContent = `${min}%`;
  const f = state.drawerFilter;
  let list = Object.values(state.jobs).filter((j) =>
    f === "hidden" ? j.hidden : !j.hidden && (f === "saved" ? j.saved : f === "applied" ? !!j.status : true));
  if (f === "all") list = list.filter((j) => j.fit >= min);
  if (q) list = list.filter((j) => [j.title, j.company, j.location, ...(j.have || []), ...(j.missing || []), ...(j.tags || [])].join(" ").toLowerCase().includes(q));
  list.sort((a, b) => b.fit - a.fit);
  put($("jobs-list"), list.length ? list.slice(0, 200).map((j) => jobRow(j, true)) : [h("li", { class: "muted pad" }, "No jobs match these filters.")]);

  const gaps = skillGaps(state.jobs);
  put($("jobs-gaps"), gaps.length ? [h("span", {}, "Learn next (asked most in jobs that fit you):"), ...gaps.map(([s, n]) => h("span", { class: "chip" }, `${s} · ${n}`))] : []);

  const kw = state.settings.searches?.[0]?.keyword || "data analyst";
  const loc = state.settings.searches?.[0]?.location || "";
  put($("searchers"), h("span", { class: "muted", style: "align-self:center;font-size:12px" }, "Browse & Nova reads it:"),
    [["naukri", "Naukri"], ["internshala", "Internshala"], ["linkedin", "LinkedIn"], ["indeed", "Indeed"], ["unstop", "Unstop"]]
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

/* ================= layout: drag, hide, resize ================= */
const BOXES = () => [...document.querySelectorAll(".box")];
const boxId = (el) => el.dataset.box;
const scale = () => state.layout.scale || 1;
const bottomReserve = () => (state.layout.hidden.news ? 12 : 58);
let relayoutQueued = false;

function relayout() {
  if (relayoutQueued) return;
  relayoutQueued = true;
  requestAnimationFrame(() => { relayoutQueued = false; applyLayout(); });
}

// Size of a box in board coordinates (the board is zoomed by the size slider).
function size(el) {
  const r = el.getBoundingClientRect();
  return { w: r.width / scale(), h: r.height / scale() };
}

function applyLayout() {
  const L = state.layout;
  document.body.classList.toggle("stacked", window.innerWidth < 900);
  $("board").style.setProperty("--scale", L.scale || 1);
  $("ticker").hidden = !!L.hidden.news;
  for (const el of BOXES()) el.hidden = !!L.hidden[boxId(el)];
  if (document.body.classList.contains("stacked")) {
    for (const el of BOXES()) { el.style.left = ""; el.style.top = ""; }
    return;
  }
  const W = window.innerWidth / scale(), H = window.innerHeight / scale();
  const maxY = H - bottomReserve() / scale();
  const corner = 70 / scale(); // keep clear of the round buttons on the right
  const gap = 12, edge = 16;

  // Default spots for boxes you haven't moved: left column, right column, centred clock.
  const def = {};
  const col = (ids, x, y0) => {
    let y = y0;
    for (const id of ids) {
      const el = document.querySelector(`[data-box="${id}"]`);
      if (!el || el.hidden) continue;
      const { w, h } = size(el);
      if (y + h > maxY && y > y0) {
        // No room in the column: park it bottom-centre instead.
        def[id] = { x: (W - w) / 2, y: maxY - h - 4 };
      } else {
        def[id] = { x: typeof x === "function" ? x(w) : x, y };
        y += h + gap;
      }
    }
  };
  col(["youtube", "github"], edge, edge);
  col(["jobs", "leetcode"], (w) => W - w - edge, corner);
  { const el = document.querySelector('[data-box="clock"]'); const { w } = size(el); def.clock = { x: (W - w) / 2, y: 10 }; }

  for (const el of BOXES()) {
    if (el.hidden || el.classList.contains("dragging")) continue;
    const id = boxId(el);
    const { w, h } = size(el);
    const saved = L.pos[id];
    let x = saved ? saved.x * W : def[id]?.x ?? edge;
    let y = saved ? saved.y * H : def[id]?.y ?? edge;
    x = Math.max(0, Math.min(x, W - w));
    y = Math.max(0, Math.min(y, Math.max(0, maxY - h)));
    el.style.left = `${x}px`;
    el.style.top = `${y}px`;
    el.classList.remove("placing");
  }
}

async function saveLayout() {
  await set("layout", state.layout);
}

function setupBoxes() {
  for (const el of BOXES()) {
    el.classList.add("placing");
    const tools = h("div", { class: "box-tools" },
      h("span", {}, el.dataset.label),
      h("button", { type: "button", onclick: (e) => { e.stopPropagation(); toggleBox(boxId(el)); } }, "Hide"));
    el.prepend(tools);
    el.addEventListener("pointerdown", (e) => startDrag(e, el));
  }
}

function startDrag(e, el) {
  if (!state.editing || e.button !== 0 || e.target.closest(".box-tools button")) return;
  e.preventDefault();
  el.setPointerCapture(e.pointerId);
  el.classList.add("dragging");
  const sx = e.clientX, sy = e.clientY;
  const ox = parseFloat(el.style.left) || 0, oy = parseFloat(el.style.top) || 0;
  const { w, h } = size(el);
  const W = window.innerWidth / scale(), H = window.innerHeight / scale();
  const move = (ev) => {
    const x = Math.max(0, Math.min(ox + (ev.clientX - sx) / scale(), W - w));
    const y = Math.max(0, Math.min(oy + (ev.clientY - sy) / scale(), H - h));
    el.style.left = `${x}px`;
    el.style.top = `${y}px`;
  };
  const up = () => {
    el.classList.remove("dragging");
    el.removeEventListener("pointermove", move);
    el.removeEventListener("pointerup", up);
    el.removeEventListener("pointercancel", up);
    state.layout.pos[boxId(el)] = { x: parseFloat(el.style.left) / W, y: parseFloat(el.style.top) / H };
    saveLayout();
  };
  el.addEventListener("pointermove", move);
  el.addEventListener("pointerup", up);
  el.addEventListener("pointercancel", up);
}

const CHIP_ITEMS = [["clock", "Clock"], ["youtube", "YouTube"], ["github", "GitHub"], ["jobs", "Job Radar"], ["leetcode", "LeetCode"], ["news", "News ticker"]];
function renderChips() {
  put($("eb-chips"), CHIP_ITEMS.map(([id, label]) => h("button", {
    type: "button", class: state.layout.hidden[id] ? "off" : "", title: state.layout.hidden[id] ? "Show" : "Hide",
    onclick: () => toggleBox(id),
  }, label)));
}
function toggleBox(id) {
  state.layout.hidden[id] = !state.layout.hidden[id];
  saveLayout();
  renderChips();
  applyLayout();
}

function setEditing(on) {
  state.editing = on;
  document.body.classList.toggle("editing", on);
  $("btn-edit").classList.toggle("on", on);
  $("editbar").hidden = !on;
  if (on) {
    $("eb-scale").value = Math.round(scale() * 100);
    $("eb-scale-v").textContent = `${$("eb-scale").value}%`;
    renderChips();
  }
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
  const k = Math.min(1, 2560 / img.width);
  const c = new OffscreenCanvas(Math.round(img.width * k), Math.round(img.height * k));
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
    h("button", { type: "button", title: "Remove", onclick: () => row.remove() }, "×"));
  return row;
}

async function openSettings(welcome = false) {
  const s = state.settings;
  const p = (await get("profile")) || DEFAULT_PROFILE;
  const f = $("settings-form");
  f.name.value = s.name;
  f.leetcode.value = s.leetcode;
  f.github.value = s.github || "";
  f.youtube.value = s.youtube || "";
  f.ghReminder.checked = s.ghReminder;
  f.lcReminders.value = s.lcReminders.join(", ");
  f.fitAlert.value = s.fitAlert;
  f.scanHours.value = s.scanHours;
  f.newsAlertHours.value = s.newsAlertHours;
  f.newsTopics.value = s.newsTopics.join(", ");
  f.remoteBoards.checked = s.remoteBoards;
  f.skills.value = p.skills.join(", ");
  f.roles.value = p.roles.join(", ");
  f.locations.value = p.locations.join(", ");
  put($("search-rows"), s.searches.map(searchRow));
  const src = Object.entries(state.meta.sources || {});
  put($("sources"), src.length ? h("b", { style: "color:var(--text)" }, "Last scan results") : null,
    src.map(([k, v]) => h("div", { class: v.ok ? "" : "bad", title: v.error || "" }, h("span", {}, `${v.ok ? "✓" : "⚠"} ${k}`), h("span", {}, `${v.count} read · ${ago(v.at)}`))));
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
    github: f.github.value.trim().replace(/^.*github\.com\//i, "").replace(/\/.*$/, ""),
    youtube: f.youtube.value.trim(),
    ghReminder: f.ghReminder.checked,
    lcReminders: list(f.lcReminders.value).filter((t) => /^\d{1,2}:\d{2}$/.test(t)),
    fitAlert: Number(f.fitAlert.value) || 70,
    scanHours: Math.max(0, Number(f.scanHours.value) || 0),
    newsAlertHours: Math.max(0, Number(f.newsAlertHours.value) || 0),
    newsTopics: list(f.newsTopics.value).slice(0, 8),
    remoteBoards: f.remoteBoards.checked,
    searches,
  };
  const profile = { ...((await get("profile")) || DEFAULT_PROFILE), skills: list(f.skills.value.toLowerCase()), roles: list(f.roles.value.toLowerCase()), locations: list(f.locations.value.toLowerCase()) };
  const prev = state.settings;
  await set("settings", settings);
  await set("profile", profile);
  state.settings = settings;
  $("save-msg").textContent = "Saved ✓ (jobs are being re-scored)";
  tickClock();
  if (settings.leetcode !== prev.leetcode) loadLeetCode(true);
  if (settings.github !== prev.github) loadGitHub(true);
  if (settings.youtube !== prev.youtube) loadYouTube(true);
  if (settings.newsTopics.join() !== prev.newsTopics.join()) loadNews(true);
}

/* ---------------- wire up ---------------- */
function wire() {
  document.querySelectorAll("[data-expand]").forEach((b) => b.addEventListener("click", () => { b.closest(".card").classList.toggle("open"); relayout(); }));
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
  document.addEventListener("keydown", (e) => { if (e.key === "Escape") { closeDrawers(); setEditing(false); } });
  $("settings-form").addEventListener("submit", saveSettings);
  $("add-search").addEventListener("click", () => $("search-rows").append(searchRow()));
  $("test-notify").addEventListener("click", () => chrome.runtime.sendMessage({ type: "test:notify" }));

  // edit mode
  $("btn-edit").addEventListener("click", () => setEditing(!state.editing));
  $("eb-done").addEventListener("click", () => setEditing(false));
  $("eb-scale").addEventListener("input", (e) => {
    state.layout.scale = Number(e.target.value) / 100;
    $("eb-scale-v").textContent = `${e.target.value}%`;
    applyLayout();
  });
  $("eb-scale").addEventListener("change", saveLayout);
  $("eb-reset").addEventListener("click", async () => {
    state.layout = { pos: {}, hidden: {}, scale: 1 };
    await saveLayout();
    setEditing(true);
    applyLayout();
  });
  window.addEventListener("resize", relayout);

  $("scan-now").addEventListener("click", async () => {
    const b = $("scan-now");
    b.disabled = true;
    b.textContent = "Scanning…";
    const r = await chrome.runtime.sendMessage({ type: "jobs:scan" }).catch((e) => ({ error: String(e) }));
    b.disabled = false;
    b.textContent = r?.error ? "Scan failed, retry" : `+${r.fresh} new · Scan again`;
  });

  $("export").addEventListener("click", async () => {
    const all = await chrome.storage.local.get(null);
    delete all.cache;
    const blob = new Blob([JSON.stringify(all, null, 2)], { type: "application/json" });
    h("a", { href: URL.createObjectURL(blob), download: `nova-backup-${new Date().toISOString().slice(0, 10)}.json` }).click();
  });
  $("import").addEventListener("click", () => $("import-file").click());
  $("import-file").addEventListener("change", async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    try {
      const data = JSON.parse(await file.text());
      const allowed = ["settings", "profile", "jobs", "jobMeta", "lcLog", "notified", "newsSeen", "wallpaper", "layout"];
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
  const saved = await get("layout");
  state.layout = { pos: {}, hidden: {}, scale: 1, ...(saved || {}) };
  setupBoxes();
  wire();
  applyWallpaper();
  tickClock();
  rotateFact();
  relayout();
  setInterval(() => { tickClock(); countdown($("lc-count"), nextLeetCodeReset()); }, 1000);
  countdown($("lc-count"), nextLeetCodeReset());
  setInterval(rotateFact, 20000);

  // Remember which jobs are new to you before marking them seen (clears the toolbar badge).
  const jobs = await get("jobs");
  state.unseen = new Set(Object.values(jobs).filter((j) => !j.seen).map((j) => j.id));
  await loadJobs();
  chrome.runtime.sendMessage({ type: "jobs:seen" }).catch(() => {});

  loadLeetCode();
  loadGitHub();
  loadYouTube();
  loadNews();
  if (location.hash === "#welcome") openSettings(true);
  else if (location.hash === "#jobs") { renderJobsDrawer(); openDrawer("drawer-jobs"); }
}

main();
