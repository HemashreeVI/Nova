import { get } from "./lib/store.js";
import { leetcode, leetcodeDaily, solvedToday } from "./lib/feeds.js";

const $ = (id) => document.getElementById(id);
function h(tag, attrs = {}, ...kids) {
  const el = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (v == null || v === false) continue;
    if (k === "class") el.className = v;
    else if (k === "style") el.style.cssText = v;
    else if (k.startsWith("on")) el.addEventListener(k.slice(2), v);
    else el.setAttribute(k, v);
  }
  for (const k of kids.flat()) if (k != null && k !== false) el.append(k instanceof Node ? k : String(k));
  return el;
}
// replaceChildren() would print "null" for skipped items, so drop them first.
const put = (el, ...kids) => el.replaceChildren(...kids.flat().filter((k) => k != null && k !== false));
const color = (p) => (p >= 70 ? "var(--green)" : p >= 45 ? "var(--amber)" : "var(--red)");
const openUrl = (url) => { try { const u = new URL(url); if (/^https?:$/.test(u.protocol)) chrome.tabs.create({ url }); } catch { /* ignore */ } };

const JOB_HOSTS = /(^|\.)(naukri\.com|internshala\.com|linkedin\.com|indeed\.com|unstop\.com|wellfound\.com|instahyre\.com|foundit\.in|glassdoor\.(com|co\.in)|cutshort\.io|lever\.co|greenhouse\.io|myworkdayjobs\.com|remotive\.com)$/;

async function thisPage() {
  const body = $("page-body");
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  let host = "";
  try { host = new URL(tab.url).hostname.replace(/^www\./, ""); } catch { /* chrome:// page */ }
  let job = null;
  try { job = (await chrome.tabs.sendMessage(tab.id, { type: "nova:extract" }))?.job; } catch { /* no content script here */ }
  const looksJob = job || JOB_HOSTS.test(host) || /career|jobs?\b/i.test(tab.url || "");

  if (!looksJob) {
    put(body, 
      h("div", {}, "Not a job posting."),
      h("div", { class: "btns" }, h("button", { class: "ghost", onclick: () => score(tab, null, host) }, "Score it as a job anyway")),
    );
    return;
  }
  await score(tab, job, host);
}

async function score(tab, job, host) {
  const body = $("page-body");
  const raw = job || { title: (tab.title || "").replace(/\s*[|–-]\s*(LinkedIn|Naukri\.com|Indeed.*|Internshala).*$/i, ""), company: host.split(".")[0], url: tab.url };
  const res = await chrome.runtime.sendMessage({ type: "jobs:add", job: raw, site: host.split(".")[0] || "web" });
  const j = res?.job;
  if (!j) { body.textContent = "Couldn't read a job here."; return; }
  const save = h("button", { class: "ghost" }, j.saved ? "♥ Saved" : "♡ Save");
  save.onclick = async () => { await chrome.runtime.sendMessage({ type: "jobs:patch", id: j.id, patch: { saved: true } }); save.textContent = "♥ Saved"; };
  const applied = h("button", { class: "ghost" }, j.status === "Applied" ? "✓ Applied" : "Mark applied");
  applied.onclick = async () => { await chrome.runtime.sendMessage({ type: "jobs:patch", id: j.id, patch: { status: "Applied", saved: true } }); applied.textContent = "✓ Applied"; };
  put(body, 
    h("div", { class: "row" },
      h("span", { class: "fit", style: `--p:${j.fit};--c:${color(j.fit)}` }, h("b", {}, `${j.fit}%`)),
      h("div", {}, h("div", { class: "title" }, j.title), h("div", { class: "muted" }, [j.company, j.location].filter(Boolean).join(" · ")),
        h("div", { class: "muted", style: "font-size:11.5px" }, j.reasons.join(" · ")))),
    h("div", { class: "chips" },
      ...j.have.slice(0, 6).map((s) => h("span", { class: "chip" }, s)),
      ...j.missing.slice(0, 5).map((s) => h("span", { class: "chip miss" }, `missing: ${s}`))),
    j.deadline ? h("div", { class: "warn", style: "margin-top:6px" }, `Apply by ${new Date(j.deadline).toLocaleDateString(undefined, { day: "numeric", month: "short" })}`) : null,
    h("div", { class: "btns" }, save, applied),
    job ? null : h("div", { class: "muted", style: "margin-top:6px;font-size:11px" }, "Scored from the page title only. Open the full job page for a better score."),
  );
}

async function leetcodeToday() {
  const s = await get("settings");
  const [lc, daily] = await Promise.allSettled([leetcode(s.leetcode), leetcodeDaily()]);
  const done = solvedToday(lc.value, await get("lcLog"));
  const d = daily.value;
  put($("lc"), 
    h("div", { class: done ? "ok" : "warn" }, done ? "✓ Solved today" : "Not solved yet today", lc.value ? ` · ${lc.value.streak}🔥 streak` : ""),
    d ? h("div", {}, "Daily: ", h("a", { href: "#", onclick: (e) => { e.preventDefault(); openUrl(d.url); } }, d.title), ` (${d.difficulty})`) : null,
    s.leetcode ? null : h("div", { class: "muted" }, "Add your LeetCode username in dashboard settings."),
  );
}

async function matches() {
  const jobs = Object.values(await get("jobs")).filter((j) => !j.hidden && !j.status).sort((a, b) => b.fit - a.fit).slice(0, 4);
  put($("matches"), ...(jobs.length ? jobs.map((j) => h("li", { onclick: () => openUrl(j.url), title: j.reasons.join(" · ") },
    h("span", { class: "p", style: `color:${color(j.fit)}` }, `${j.fit}%`),
    h("span", { class: "t" }, `${j.title} · ${j.company}`))) : [h("li", { class: "muted" }, "No jobs yet. Scan or browse a job site.")]));
}

$("open").onclick = () => chrome.tabs.create({ url: chrome.runtime.getURL("newtab.html") });
$("scan").onclick = async () => {
  $("scan").disabled = true;
  $("scan").textContent = "Scanning…";
  const r = await chrome.runtime.sendMessage({ type: "jobs:scan" });
  $("scan").textContent = r?.error ? "Scan failed" : `${r.fresh} new · ${r.good} strong`;
  $("scan").disabled = false;
  matches();
};

thisPage().catch(() => { $("page-body").textContent = "Can't read this page."; });
leetcodeToday().catch(() => { $("lc").textContent = "Couldn't reach LeetCode."; });
matches();
