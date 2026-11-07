// Records a narrated scroll through the GitHub profile README on a virtual display.
// usage: DISPLAY=:99 node record.js <long|short> <timing.json> <outdir>
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const fs = require('fs');
const [MODE, TIMING, OUT] = process.argv.slice(2);
const T = JSON.parse(fs.readFileSync(TIMING, 'utf8'));
const S = Object.fromEntries(T.scenes.map((s) => [s.id, s]));
const LONG = MODE === 'long';
const W = LONG ? 1920 : 1080, H = LONG ? 1080 : 1920;

// scene -> [from anchor, to anchor]; anchors are alt-text prefixes ('top' = page top)
const PLAN = LONG ? {
  intro: ['top', 'top'], hero: ['HEMASHREE, Software', 'HEMASHREE, Software'], about: ['01 About', 'Right now'],
  journey: ['02 Philosophy', '03 Journey'], work1: ['04 Selected', 'SeatLock:'], work2: ['RootLens:', 'GitLoom demo'],
  work3: ['Smart Walker', 'More projects'], toolkit: ['05 In progress', '06 Toolkit'], play: ['08 Play', 'Profile chess board'], outro: ['Profile chess board', 'top'],
} : {
  intro: ['top', 'top'], work1: ['Dental Malocclusion Detection:', 'RootLens:'], work2: ['TriageIQ:', 'RL Rover'],
  toolkit: ['06 Toolkit', 'Profile chess board'], outro: ['top', 'top'],
};
const PANEL = {
  intro: ['TOUR', "POV: you're on my GitHub 👀", 'every project · full code'],
  hero: ['ABOUT ME', 'Hemashree', 'B.Tech CSE · VIT Chennai'],
  about: ['01 · ABOUT', 'Live terminal', '+ what I\'m doing right now'],
  journey: ['02 – 03', 'Sense · Decide · Protect', 'VIT → research → Singapore → patent'],
  work1: ['04 · PROJECTS', 'Dental X-ray AI', 'SeatLock: zero double-bookings'],
  work2: ['04 · PROJECTS', 'RootLens · TriageIQ', 'GitLoom: GitHub → website'],
  work3: ['04 · PROJECTS', 'Smart Walker', 'RL Rover · Smart Grocer · more'],
  toolkit: ['05 – 06', 'Building next', 'and the full toolkit'],
  play: ['08 · PLAY', 'Chess in the README ♟️', 'you play White vs Stockfish'],
};

(async () => {
  const browser = await chromium.launch({ headless: false, ignoreDefaultArgs: ['--enable-automation'],
    args: ['--window-position=0,0', `--window-size=${W},${H + 200}`, '--force-device-scale-factor=1', '--hide-scrollbars', '--autoplay-policy=no-user-gesture-required'] });
  const ctx = await browser.newContext({ viewport: null, colorScheme: 'dark' });
  const page = await ctx.newPage();
  await page.goto('https://github.com/HemashreeVI/HemashreeVI', { waitUntil: 'networkidle', timeout: 120000 }).catch(() => {});
  // load every lazy image once
  for (let y = 0; y < 22000; y += 700) { await page.evaluate((v) => window.scrollTo(0, v), y); await page.waitForTimeout(120); }
  await page.waitForTimeout(2500);
  const OFF = Math.round(await page.evaluate(() => window.outerHeight - window.innerHeight));
  await page.evaluate(([LONG]) => {
    const art = document.querySelector('article.markdown-body');
    document.body.innerHTML = ''; document.body.appendChild(art);
    const st = document.createElement('style');
    st.textContent = `html,body{background:#0d1117!important;margin:0;overflow:hidden}
      article.markdown-body{box-sizing:border-box;width:1012px;max-width:none!important;margin:0 ${LONG ? '0 0 80px' : 'auto'}!important;padding:40px 0 1400px!important;background:#0d1117}
      #pnl{position:fixed;left:1160px;right:70px;top:0;bottom:0;display:flex;flex-direction:column;justify-content:center;font-family:Inter,system-ui,sans-serif;color:#e6edf3}
      #pnl .k{font:700 30px 'JetBrains Mono',monospace;letter-spacing:.18em;color:#839dfb}
      #pnl .t{font:800 64px/1.08 Inter;margin-top:18px;letter-spacing:-.02em}
      #pnl .s{font:500 34px/1.35 Inter;color:#9aa4b2;margin-top:18px}
      #url{position:fixed;left:50%;top:${LONG ? '50%' : '42%'};transform:translate(-50%,-50%) scale(.6);opacity:0;transition:none;padding:${LONG ? '46px 64px' : '40px 46px'};border-radius:34px;
        background:#0b1020;border:4px solid #839dfb;box-shadow:0 0 120px rgba(131,157,251,.5);text-align:center;font-family:Inter,system-ui,sans-serif;color:#fff;white-space:nowrap}
      #url .a{font:600 ${LONG ? 40 : 38}px Inter;color:#9aa4b2} #url .b{font:800 ${LONG ? 84 : 66}px 'JetBrains Mono',monospace;margin:18px 0;color:#fff} #url .c{font:600 ${LONG ? 38 : 36}px Inter;color:#8fe3c8}`;
    document.head.appendChild(st);
    const f = document.createElement('link'); f.rel = 'stylesheet'; f.href = 'https://fonts.googleapis.com/css2?family=Inter:wght@500;600;700;800&family=JetBrains+Mono:wght@600;800&display=swap'; document.head.appendChild(f);
    if (LONG) { const p = document.createElement('div'); p.id = 'pnl'; p.innerHTML = '<div class="k"></div><div class="t"></div><div class="s"></div>'; document.body.appendChild(p); }
    const u = document.createElement('div'); u.id = 'url'; u.innerHTML = '<div class="a">💻 get the full code</div><div class="b">github.com/HemashreeVI</div><div class="c">free · every project</div>'; document.body.appendChild(u);
    window.scrollTo(0, 0);
  }, [LONG]);
  // preload the intro GIF so it can restart from frame 0 exactly at T0
  const gifOk = await page.evaluate(async () => {
    const img = document.querySelector('article img'); if (!img) return false;
    try { const r = await fetch(img.currentSrc || img.src); const b = await r.blob(); window.__gif = URL.createObjectURL(b); window.__gifImg = img; return b.size; } catch (e) { return 'fail ' + e.message; }
  });
  console.log('gif', gifOk, 'toolbar', OFF);
  const Y = await page.evaluate((plan) => {
    const imgs = [...document.querySelectorAll('article img')];
    const out = {};
    for (const [id, pair] of Object.entries(plan)) out[id] = pair.map((a) => { if (a === 'top') return 0; const el = imgs.find((i) => (i.alt || '').startsWith(a)); return el ? Math.round(el.getBoundingClientRect().top + window.scrollY) : null; });
    return out;
  }, PLAN);
  console.log(JSON.stringify(Y));
  await page.waitForTimeout(1500);

  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'x11grab', '-framerate', '30', '-video_size', `${W}x${H}`, '-draw_mouse', '0', '-i', `${process.env.DISPLAY}+0,${OFF}`,
    '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '14', '-pix_fmt', 'yuv444p', OUT + '/raw.mp4'], { stdio: ['pipe', 'inherit', 'inherit'] });
  await page.waitForTimeout(2000);
  await page.evaluate(() => { const f = document.createElement('div'); f.id = '__sync'; Object.assign(f.style, { position: 'fixed', inset: 0, background: '#ff00ff', zIndex: 99999 }); document.body.appendChild(f); });
  await page.waitForTimeout(800);
  await page.evaluate(() => { document.getElementById('__sync').remove(); if (window.__gif) window.__gifImg.src = window.__gif; });
  const T0 = Date.now();
  // the timeline runs inside the page for smooth 60fps scrolling
  await page.evaluate(([scenes, Y, PANEL, LONG]) => {
    const t0 = performance.now(), ease = (u) => u < .5 ? 4 * u * u * u : 1 - Math.pow(-2 * u + 2, 3) / 2;
    const top = LONG ? 60 : 160, pnl = document.getElementById('pnl'), url = document.getElementById('url');
    let last = '';
    (function frame() {
      const t = (performance.now() - t0) / 1000;
      const sc = scenes.find((s) => t >= s.start && t < s.start + s.dur) || scenes[scenes.length - 1];
      const [a, b] = Y[sc.id] || [0, 0], u = Math.min(1, Math.max(0, (t - sc.start - 0.25) / Math.max(0.5, sc.dur - 0.9)));
      let y = (a == null ? 0 : a) + ((b == null ? a : b) - (a == null ? 0 : a)) * ease(u) - top; if (a === 0 && b === 0) y = 0;
      if (sc.id === 'outro') y = (a || 0) - top + ((b || 0) - (a || 0)) * ease(Math.min(1, u * 1.8));
      window.scrollTo(0, Math.max(0, y));
      if (pnl && sc.id !== last) { const p = PANEL[sc.id]; pnl.style.opacity = p ? 1 : 0; if (p) { pnl.children[0].textContent = p[0]; pnl.children[1].textContent = p[1]; pnl.children[2].textContent = p[2]; } last = sc.id; }
      if (sc.id === 'outro') { const lineB = sc.lines[sc.lines.length - 1].start; const v = Math.min(1, Math.max(0, (t - sc.start - (LONG ? lineB : 0.4)) / 0.5)); url.style.opacity = v; url.style.transform = `translate(-50%,-50%) scale(${0.6 + 0.4 * (1 - Math.pow(1 - v, 3))})`; if (pnl) pnl.style.opacity = 0; }
      if (t < scenes[scenes.length - 1].start + scenes[scenes.length - 1].dur + 1) requestAnimationFrame(frame);
    })();
  }, [T.scenes.map((s) => ({ id: s.id, start: s.start, dur: s.dur, lines: s.lines })), Y, PANEL, LONG]);
  await page.waitForTimeout(T.total * 1000 + 1500 - (Date.now() - T0));
  ff.stdin.write('q'); await new Promise((r) => ff.on('close', r));
  await browser.close();
})().catch((e) => { console.error(e); process.exit(1); });
