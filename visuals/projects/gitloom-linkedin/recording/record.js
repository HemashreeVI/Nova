// Records a real GitLoom session on a virtual display, timed to the narration.
// DISPLAY must point at an Xvfb screen of 1920x1080.
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const fs = require('fs');

const OUT = process.argv[2];             // folder for raw.mp4 + sync.json
const TIMING = JSON.parse(fs.readFileSync(process.argv[3], 'utf8'));
const MARKED = process.argv[4];
const BASE = 'http://127.0.0.1:8090/';
const S = Object.fromEntries(TIMING.scenes.map(s => [s.id, s]));

const CURSOR = `
(() => {
  if (window.top !== window) return;
  const add = () => {
    if (document.getElementById('__cur')) return;
    const c = document.createElement('div'); c.id = '__cur';
    c.innerHTML = '<svg width="26" height="26" viewBox="0 0 24 24"><path d="M4 2l15 9.5-6.6 1.3 3.9 7.4-2.9 1.5-3.9-7.4L4.6 19z" fill="#111" stroke="#fff" stroke-width="1.4" stroke-linejoin="round"/></svg>';
    Object.assign(c.style, { position: 'fixed', left: '-40px', top: '-40px', zIndex: 2147483647, pointerEvents: 'none', transition: 'none', filter: 'drop-shadow(0 2px 3px rgba(0,0,0,.35))' });
    const r = document.createElement('div'); r.id = '__ring';
    Object.assign(r.style, { position: 'fixed', width: '34px', height: '34px', marginLeft: '-17px', marginTop: '-17px', borderRadius: '50%', border: '3px solid #e3a72f', zIndex: 2147483646, pointerEvents: 'none', opacity: 0, transform: 'scale(.4)', transition: 'transform .35s ease, opacity .35s ease' });
    document.documentElement.append(r, c);
    const pos = JSON.parse(sessionStorage.getItem('__cur') || '[-40,-40]');
    c.style.left = pos[0] + 'px'; c.style.top = pos[1] + 'px';
    addEventListener('mousemove', e => { c.style.left = e.clientX + 'px'; c.style.top = e.clientY + 'px'; sessionStorage.setItem('__cur', JSON.stringify([e.clientX, e.clientY])); }, true);
    addEventListener('mousedown', e => { r.style.left = e.clientX + 'px'; r.style.top = e.clientY + 'px'; r.style.transition = 'none'; r.style.opacity = 1; r.style.transform = 'scale(.4)'; requestAnimationFrame(() => { r.style.transition = 'transform .45s ease, opacity .45s ease'; r.style.transform = 'scale(1.4)'; r.style.opacity = 0; }); }, true);
  };
  if (document.readyState === 'loading') addEventListener('DOMContentLoaded', add); else add();
})();`;

(async () => {
  const browser = await chromium.launch({
    headless: false,
    ignoreDefaultArgs: ['--enable-automation'],
    args: ['--kiosk', '--window-position=0,0', '--window-size=1920,1200', '--force-device-scale-factor=1.3333333', '--hide-scrollbars', '--disable-features=DownloadBubble,DownloadBubbleV2'],
  });
  const ctx = await browser.newContext({ viewport: null, acceptDownloads: true });
  await ctx.route('https://cdn.jsdelivr.net/npm/marked@12.0.2/marked.min.js', r => r.fulfill({ path: MARKED, contentType: 'text/javascript' }));
  await ctx.addInitScript(CURSOR);
  const page = await ctx.newPage();
  page.on('download', d => d.cancel().catch(() => {}));

  // Warm up: clean state, fonts and the demo profile.
  await page.goto(BASE + 'studio.html');
  await page.evaluate(() => { localStorage.clear(); sessionStorage.clear(); });
  await page.goto(BASE + 'studio.html?user=__demo'); await page.waitForTimeout(2500);
  await page.evaluate(() => localStorage.clear());
  const site = await ctx.newPage(); await site.goto('about:blank');
  await page.bringToFront();
  await page.goto(BASE + 'index.html'); await page.waitForTimeout(3000);
  await page.mouse.move(700, 560);

  const OFF = Math.round(await page.evaluate(() => (window.outerHeight - window.innerHeight) * devicePixelRatio));
  console.log('toolbar px', OFF);
  // Start capture, then show a magenta sync flash that ends exactly at T0.
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'x11grab', '-framerate', '30', '-video_size', '1920x1080', '-draw_mouse', '0', '-i', process.env.DISPLAY + '+0,' + OFF,
    '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '14', '-pix_fmt', 'yuv444p', OUT + '/raw.mp4'], { stdio: ['pipe', 'inherit', 'inherit'] });
  await page.waitForTimeout(2000);
  await page.evaluate(() => { const f = document.createElement('div'); f.id = '__sync'; Object.assign(f.style, { position: 'fixed', inset: 0, background: '#ff00ff', zIndex: 2147483647 }); document.documentElement.append(f); });
  await page.waitForTimeout(800);
  await page.evaluate(() => document.getElementById('__sync').remove());
  const T0 = Date.now();
  const at = async sec => { const w = T0 + sec * 1000 - Date.now(); if (w > 0) await page.waitForTimeout(w); };
  const box = async sel => { const b = await page.locator(sel).first().boundingBox(); return [b.x + b.width / 2, b.y + b.height / 2]; };
  const glide = async (sel, steps = 18) => { const [x, y] = await box(sel); await page.mouse.move(x, y, { steps }); return [x, y]; };
  const click = async (sel, steps = 18) => { await glide(sel, steps); await page.waitForTimeout(120); await page.mouse.down(); await page.waitForTimeout(60); await page.mouse.up(); };
  const preview = () => page.frames().find(f => f.url().includes('portfolio.html'));
  const scrollPreview = async (target) => { const f = preview(); if (f) await f.evaluate(t => { const el = t === 'top' ? null : document.getElementById(t); window.scrollTo({ top: el ? el.getBoundingClientRect().top + scrollY - 20 : 0, behavior: 'smooth' }); }, target); };

  // ---- hook: the loom weaves a row per character
  const h = S.hook;
  await at(h.start + 0.4); await glide('#heroUser', 25);
  await at(h.start + 1.6); await page.mouse.down(); await page.mouse.up(); await page.locator('#heroUser').focus();
  await at(h.start + h.lines[1].start - 0.2);
  for (const ch of 'mira-demo') { await page.keyboard.type(ch); await page.waitForTimeout(230); }
  await at(h.start + h.dur - 1.2); await glide('a[href="studio.html?user=__demo"]', 20);

  // ---- load: demo profile in the studio
  const l = S.load;
  await at(l.start - 0.25); await page.mouse.down(); await page.mouse.up();
  await page.goto(BASE + 'studio.html?user=__demo');
  await page.waitForTimeout(800);
  await at(l.start + 2.0); await scrollPreview('projects');
  await at(l.start + 4.6); await scrollPreview('languages');
  await at(l.start + 7.0); await scrollPreview('activity');
  await at(l.start + 9.4); await scrollPreview('top');

  // ---- templates: ten looks, same data
  const t = S.templates;
  await at(t.start); await click('[data-tab="design"]', 14);
  const order = ['midnight', 'terminal', 'bento', 'brutalist', 'swiss', 'blueprint', 'zen', 'sunrise', 'aurora'];
  const step = (t.dur - 0.9) / order.length;
  for (let i = 0; i < order.length; i++) { await at(t.start + 0.6 + i * step); await click(`#tpls .tpl[data-t="${order[i]}"]`, 8); }

  // ---- style: accent colours and fonts
  const s = S.style;
  await at(s.start); await page.locator('#swatches').scrollIntoViewIfNeeded();
  await click('#swatches > :nth-child(3)', 10);
  await at(s.start + 0.9); await click('#swatches > :nth-child(6)', 10);
  await at(s.start + 1.7); await page.locator('#fonts').scrollIntoViewIfNeeded(); await click('#fonts > :nth-child(4)', 10);
  await at(s.start + 2.5); await click('#fonts > :nth-child(2)', 10);

  // ---- sections: drag Projects to the top
  const se = S.sections;
  await at(se.start); await click('[data-tab="content"]', 12);
  await page.locator('#sections').scrollIntoViewIfNeeded();
  await at(se.start + 0.9);
  const from = await glide('#sections li[data-id="projects"]', 14);
  const to = await box('#sections li:first-child');
  await page.mouse.down(); await page.mouse.move(from[0], from[1] - 8, { steps: 4 });
  await page.mouse.move(to[0], to[1] - 10, { steps: 26 }); await page.waitForTimeout(150); await page.mouse.up();
  await at(se.start + 2.6); await scrollPreview('projects');

  // ---- phone
  const ph = S.phone;
  await at(ph.start); await click('.dev[data-w="390px"]', 16);
  await at(ph.start + 1.4); await scrollPreview('top');
  const href = await page.locator('#open').getAttribute('href');
  await site.goto(BASE + href); await site.waitForTimeout(1200);

  // ---- finish: the generated site, Ctrl+K, print view
  const fi = S.finish;
  await at(fi.start - 0.6); await click('.dev[data-w="100%"]', 10);
  await at(fi.start); await site.bringToFront(); await site.mouse.move(700, 420, { steps: 12 });
  await at(fi.start + 0.9); await site.keyboard.press('Control+k');
  await at(fi.start + 1.9); await site.locator('.kbar-in').pressSequentially('tiny', { delay: 170 });
  await at(fi.start + 4.9); await site.keyboard.press('Escape');
  await at(fi.start + 5.3); await site.emulateMedia({ media: 'print' }); await site.evaluate(() => window.scrollTo({ top: 0, behavior: 'instant' }));
  await at(fi.start + 6.9); await site.evaluate(() => window.scrollTo({ top: 380, behavior: 'smooth' }));

  // ---- publish: download one HTML file
  const pu = S.publish;
  await at(pu.start); await page.bringToFront();
  await at(pu.start + 0.4); await click('[data-tab="publish"]', 14);
  await page.locator('#dl2').scrollIntoViewIfNeeded();
  await at(pu.start + 1.6); await glide('#dl2', 20);
  await at(pu.start + 2.4); await page.mouse.down(); await page.mouse.up();
  await at(pu.start + 3.6); await glide('#pagesUrl', 24);
  await at(S.outro.start + 0.6);

  ff.stdin.write('q'); await new Promise(r => ff.on('close', r));
  fs.writeFileSync(OUT + '/sync.json', JSON.stringify({ note: 'T0 = first frame after the magenta flash' }));
  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
