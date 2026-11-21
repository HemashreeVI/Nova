// Runs on job sites you visit. Reads the job cards / job page you're looking at,
// sends them to Nova for fit scoring, and shows a small fit badge on job detail pages.
(() => {
  if (window.__novaJobs) return;
  window.__novaJobs = true;

  const host = location.hostname.replace(/^www\./, "");
  const site =
    host.endsWith("naukri.com") ? "naukri" :
    host.endsWith("internshala.com") ? "internshala" :
    host.endsWith("linkedin.com") ? "linkedin" :
    host.includes("indeed.") ? "indeed" :
    host.endsWith("unstop.com") ? "unstop" :
    host.endsWith("wellfound.com") ? "wellfound" :
    host.endsWith("instahyre.com") ? "instahyre" :
    host.endsWith("foundit.in") ? "foundit" :
    host.endsWith("glassdoor.co.in") || host.endsWith("glassdoor.com") ? "glassdoor" : host;

  const txt = (el) => (el ? el.textContent.replace(/\s+/g, " ").trim() : "");
  const q = (root, sel) => {
    for (const s of sel.split("||")) {
      const el = root.querySelector(s.trim());
      if (el && txt(el)) return el;
    }
    return null;
  };
  const abs = (href) => { try { return new URL(href, location.href).href; } catch { return ""; } };
  // DOMParser builds an inert document, so nothing in the HTML can run or load.
  const strip = (html = "") =>
    (new DOMParser().parseFromString(String(html), "text/html").body.textContent || "").replace(/\s+/g, " ").trim();

  /* ---------- schema.org JobPosting (works on most job sites and career pages) ---------- */
  function fromJsonLd() {
    const out = [];
    const visit = (node) => {
      if (!node || typeof node !== "object") return;
      if (Array.isArray(node)) return node.forEach(visit);
      const type = [].concat(node["@type"] || []);
      if (type.includes("JobPosting")) {
        const org = node.hiringOrganization;
        const locs = [].concat(node.jobLocation || []).map((l) => {
          const a = l.address || {};
          return [a.addressLocality, a.addressRegion].filter(Boolean).join(", ");
        }).filter(Boolean);
        if (/telecommute/i.test(node.jobLocationType || "")) locs.unshift("Remote");
        out.push({
          title: node.title,
          company: typeof org === "string" ? org : org?.name,
          location: [...new Set(locs)].join(" / "),
          url: node.url || location.href,
          desc: strip(node.description),
          tags: [].concat(node.skills || []).flatMap((s) => String(s).split(/,\s*/)),
          experience: typeof node.experienceRequirements === "string" ? node.experienceRequirements
            : node.experienceRequirements?.monthsOfExperience ? `${Math.round(node.experienceRequirements.monthsOfExperience / 12)} years` : "",
          posted: node.datePosted || null,
          deadline: node.validThrough || null,
          detail: true,
        });
      }
      if (node["@graph"]) visit(node["@graph"]);
    };
    for (const s of document.querySelectorAll('script[type="application/ld+json"]')) {
      try { visit(JSON.parse(s.textContent)); } catch { /* malformed JSON-LD is common, skip it */ }
    }
    return out;
  }

  /* ---------- search result cards, per site ---------- */
  const CARDS = {
    naukri: {
      card: ".srp-jobtuple-wrapper, article.jobTuple, .cust-job-tuple",
      title: "a.title || .title a || .title",
      company: "a.comp-name || .comp-name || .subTitle",
      location: ".locWdth || .loc-wrap || .location || .loc",
      experience: ".expwdth || .exp-wrap || .exp",
      salary: ".sal-wrap || .salary",
      desc: ".job-desc || .job-description",
      tags: ".tags-gt li, ul.tags li",
      link: "a.title, .title a",
    },
    internshala: {
      card: ".individual_internship, .internship_meta.experience_meta",
      title: ".job-internship-name || .profile a || h3 a || h3",
      company: ".company-name || .company_name a || .company_name || .link_display_like_text",
      location: ".locations || .row-1-item.locations || #location_names",
      salary: ".stipend || .desktop-text",
      desc: ".about_job || .internship_other_details_container",
      tags: ".job_skill, .round_tabs",
      link: ".job-internship-name a, .profile a, h3 a, a.view_detail_button",
    },
    linkedin: {
      card: ".job-card-container, .base-card, li.jobs-search-results__list-item, .job-card-job-posting-card-wrapper",
      title: ".job-card-list__title--link strong || .job-card-list__title || .base-search-card__title || .artdeco-entity-lockup__title",
      company: ".artdeco-entity-lockup__subtitle || .base-search-card__subtitle || .job-card-container__primary-description",
      location: ".job-card-container__metadata-wrapper || .job-search-card__location || .artdeco-entity-lockup__caption",
      link: 'a[href*="/jobs/view/"], a.base-card__full-link',
    },
    indeed: {
      card: ".job_seen_beacon, .cardOutline, .resultContent",
      title: "h2.jobTitle span[title] || h2.jobTitle",
      company: '[data-testid="company-name"] || .companyName',
      location: '[data-testid="text-location"] || .companyLocation',
      salary: ".salary-snippet-container || .metadata.salary-snippet-container",
      desc: ".job-snippet || [data-testid=\"jobsnippet_footer\"]",
      link: "h2.jobTitle a, a.jcs-JobTitle",
    },
  };

  function fromCards() {
    const cfg = CARDS[site];
    if (!cfg) return [];
    const out = [];
    for (const card of document.querySelectorAll(cfg.card)) {
      const title = txt(q(card, cfg.title));
      if (!title) continue;
      const linkEl = card.querySelector(cfg.link) || card.closest("a");
      let url = linkEl ? abs(linkEl.getAttribute("href")) : "";
      if (!url && card.dataset.href) url = abs(card.dataset.href);
      const jk = card.querySelector("[data-jk]")?.dataset.jk || card.dataset.jk;
      if (site === "indeed" && jk) url = `https://${location.hostname}/viewjob?jk=${jk}`;
      out.push({
        title,
        company: txt(q(card, cfg.company)),
        location: txt(cfg.location && q(card, cfg.location)),
        experience: txt(cfg.experience && q(card, cfg.experience)),
        salary: txt(cfg.salary && q(card, cfg.salary)),
        desc: txt(cfg.desc && q(card, cfg.desc)),
        tags: cfg.tags ? [...card.querySelectorAll(cfg.tags)].map(txt).filter(Boolean) : [],
        url,
      });
    }
    return out;
  }

  /* ---------- a single job page without JSON-LD ---------- */
  const DETAIL = {
    naukri: /\/job-listings-/,
    internshala: /\/(internship|job)\/detail\//,
    linkedin: /\/jobs\/view\//,
    indeed: /\/viewjob/,
  };

  function fromDetailPage() {
    const rx = DETAIL[site];
    if (!rx || !rx.test(location.pathname)) return [];
    const main = document.querySelector("main, #root, .detail_view, .jd-container") || document.body;
    const title = txt(document.querySelector("h1"));
    if (!title) return [];
    const company =
      txt(document.querySelector(".jd-header-comp-name a, .styles_jd-header-comp-name__MvqAI a, .company_name a, .company-name, .job-details-jobs-unified-top-card__company-name, [data-testid=\"inlineHeader-companyName\"]")) || "";
    const body = main.innerText.slice(0, 6000);
    return [{
      title, company,
      location: txt(document.querySelector(".location_link, #location_names, .styles_jhc__location__W_pVs, .job-details-jobs-unified-top-card__primary-description-container, [data-testid=\"inlineHeader-companyLocation\"]")),
      desc: body,
      tags: [...document.querySelectorAll(".key-skill a, .styles_key-skill__GIPn_ a, .round_tabs, .job-details-skill-match-status-list li")].map(txt).filter(Boolean),
      url: location.href.split("#")[0],
      detail: true,
    }];
  }

  /* ---------- report to the extension ---------- */
  const sent = new Set();
  let badgeFor = "", emptyFor = "";

  function scan() {
    const ld = fromJsonLd();
    const jobs = [...ld, ...(ld.length ? [] : fromDetailPage()), ...fromCards()];
    const fresh = jobs.filter((j) => {
      const k = `${j.title}|${j.company}`.toLowerCase();
      if (sent.has(k)) return false;
      sent.add(k);
      return true;
    });
    const detail = jobs.find((j) => j.detail);
    if (!fresh.length && (!detail || badgeFor === location.href)) {
      // Tell Nova once per page that nothing was found (the auto-scanner waits for this).
      if (!jobs.length && emptyFor !== location.href) {
        emptyFor = location.href;
        chrome.runtime.sendMessage({ type: "jobs:found", site, jobs: [], page: location.href }).catch(() => {});
      }
      return;
    }
    chrome.runtime.sendMessage({ type: "jobs:found", site, jobs: fresh.length ? fresh : [detail], page: location.href, detail: !!detail })
      .then((res) => {
        if (detail && res?.detail) { badgeFor = location.href; showBadge(res.detail); }
      })
      .catch(() => { /* extension reloaded; ignore */ });
  }

  let timer = null;
  const schedule = () => { clearTimeout(timer); timer = setTimeout(scan, 900); };
  new MutationObserver(schedule).observe(document.documentElement, { childList: true, subtree: true });
  let lastUrl = location.href;
  setInterval(() => { if (location.href !== lastUrl) { lastUrl = location.href; badgeFor = ""; schedule(); } }, 1000);
  schedule();

  // The popup asks "what job is on this page?"
  chrome.runtime.onMessage.addListener((msg, _sender, reply) => {
    if (msg?.type === "nova:extract") {
      const ld = fromJsonLd();
      reply({ job: ld[0] || fromDetailPage()[0] || null });
    }
  });

  /* ---------- the fit badge ---------- */
  function showBadge(job) {
    document.getElementById("nova-fit-badge")?.remove();
    const box = document.createElement("div");
    box.id = "nova-fit-badge";
    const shadow = box.attachShadow({ mode: "closed" });
    const color = job.fit >= 70 ? "#3ddc84" : job.fit >= 45 ? "#ffb547" : "#ff5d5d";
    const el = (tagName, cls, text) => { const e = document.createElement(tagName); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; };

    const style = el("style");
    style.textContent = `
      .card{position:fixed;right:18px;bottom:18px;z-index:2147483647;width:280px;font:13px/1.45 system-ui,-apple-system,"Segoe UI",sans-serif;
        color:#f2f2f4;background:rgba(22,22,28,.88);backdrop-filter:blur(14px);border:1px solid rgba(255,255,255,.14);
        border-radius:18px;padding:14px 16px;box-shadow:0 12px 40px rgba(0,0,0,.35)}
      .top{display:flex;align-items:center;gap:12px}
      .ring{width:52px;height:52px;border-radius:50%;display:grid;place-items:center;font-weight:800;font-size:15px;flex:none;
        background:conic-gradient(${color} ${job.fit * 3.6}deg, rgba(255,255,255,.12) 0)}
      .ring span{width:42px;height:42px;border-radius:50%;background:#16161c;display:grid;place-items:center}
      .k{font-size:10px;letter-spacing:.14em;text-transform:uppercase;color:#a9a9b3}
      .t{font-weight:600;margin-top:2px}
      .row{margin-top:10px}
      .chip{display:inline-block;margin:3px 4px 0 0;padding:2px 8px;border-radius:99px;font-size:11.5px;background:rgba(255,255,255,.08)}
      .miss .chip{background:rgba(255,93,93,.16);color:#ffb3b3}
      .have .chip{background:rgba(61,220,132,.14);color:#a6f0c6}
      .x{position:absolute;top:8px;right:10px;background:none;border:0;color:#a9a9b3;font-size:16px;cursor:pointer}
      .dl{margin-top:8px;color:#ffb547;font-weight:600}
      button.save{margin-top:12px;width:100%;padding:8px;border-radius:10px;border:0;font-weight:700;cursor:pointer;background:#f2f2f4;color:#111}
    `;
    const card = el("div", "card");
    const x = el("button", "x", "×"); x.title = "Hide"; x.onclick = () => box.remove();
    const top = el("div", "top");
    const ring = el("div", "ring"); ring.append(el("span", null, `${job.fit}%`));
    const head = el("div");
    head.append(el("div", "k", "Nova resume fit"), el("div", "t", job.reasons?.slice(0, 2).join(" · ") || "Scored against your profile"));
    top.append(ring, head);
    card.append(x, top);
    if (job.have?.length) {
      const r = el("div", "row have"); r.append(el("div", "k", "You have"));
      job.have.slice(0, 8).forEach((s) => r.append(el("span", "chip", s))); card.append(r);
    }
    if (job.missing?.length) {
      const r = el("div", "row miss"); r.append(el("div", "k", "Missing"));
      job.missing.slice(0, 6).forEach((s) => r.append(el("span", "chip", s))); card.append(r);
    }
    if (job.deadline) card.append(el("div", "dl", `Apply by ${new Date(job.deadline).toLocaleDateString(undefined, { day: "numeric", month: "short" })}`));
    const save = el("button", "save", job.saved ? "♥ Saved in Nova" : "♡ Save to Nova");
    save.onclick = () => chrome.runtime.sendMessage({ type: "jobs:patch", id: job.id, patch: { saved: true } })
      .then(() => { save.textContent = "♥ Saved in Nova"; }).catch(() => {});
    card.append(save);
    shadow.append(style, card);
    document.documentElement.append(box);
  }
})();
