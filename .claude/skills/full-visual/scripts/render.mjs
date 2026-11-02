#!/usr/bin/env node
/**
 * full-visual renderer
 *
 *   node render.mjs <projectDir> [--stills <specs>] [--fps 30] [--workers N] [--no-tts]
 *
 * 1. copies fv-runtime.js into the project
 * 2. runs tts.py → timing.js, narration.wav/mp3, captions.srt
 * 3. --stills: screenshots only (spec = seconds | sceneId | sceneId@seconds, comma-separated)
 *    otherwise: steps the page frame by frame in headless Chromium (parallel workers),
 *    encodes H.264, muxes narration → out/<slug>.mp4, plus thumbnail.png and youtube.txt
 */
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { spawn, spawnSync } from 'node:child_process';
import { once } from 'node:events';
import { createRequire } from 'node:module';
import { fileURLToPath, pathToFileURL } from 'node:url';

const require = createRequire(import.meta.url);
let chromium;
try { ({ chromium } = require('playwright')); } catch { ({ chromium } = require('playwright-core')); }

const HERE = path.dirname(fileURLToPath(import.meta.url));
const argv = process.argv.slice(2);
const opt = (name, def) => { const i = argv.indexOf(`--${name}`); return i >= 0 ? argv[i + 1] : def; };
const flag = (name) => argv.includes(`--${name}`);
const VALUED = ['--stills', '--fps', '--workers'];
const projArg = argv.find((a, i) => !a.startsWith('--') && !VALUED.includes(argv[i - 1]));
if (!projArg) { console.error('usage: node render.mjs <projectDir> [--stills specs] [--fps 30] [--workers N] [--no-tts]'); process.exit(1); }

const proj = path.resolve(projArg);
const out = path.join(proj, 'out');
fs.mkdirSync(out, { recursive: true });
const cfg = JSON.parse(fs.readFileSync(path.join(proj, 'video.json'), 'utf8'));
const slug = cfg.slug || path.basename(proj);
const fps = +opt('fps', cfg.fps || 30);
const workers = Math.max(1, +opt('workers', Math.min(4, os.cpus().length)));

function run(cmd, args) {
  const r = spawnSync(cmd, args, { stdio: 'inherit' });
  if (r.status !== 0) throw new Error(`${cmd} failed (${r.status})`);
}
const ffmpegQuiet = ['-hide_banner', '-loglevel', 'error', '-y'];

// 1. runtime
fs.copyFileSync(path.join(HERE, '..', 'runtime', 'fv-runtime.js'), path.join(proj, 'fv-runtime.js'));

// 2. narration
if (!flag('no-tts')) {
  run('python3', [path.join(HERE, 'tts.py'), proj]);
  run('ffmpeg', [...ffmpegQuiet, '-i', path.join(out, 'narration.wav'), '-c:a', 'libmp3lame', '-b:a', '160k', path.join(proj, 'narration.mp3')]);
}
const timing = JSON.parse(fs.readFileSync(path.join(out, 'timing.json'), 'utf8'));
const pageUrl = pathToFileURL(path.join(proj, 'index.html')).href + '?render';

function resolveTime(spec) {
  if (/^[\d.]+$/.test(spec)) return +spec;
  const [id, off] = spec.split('@');
  const s = timing.scenes.find((x) => x.id === id);
  if (!s) throw new Error(`unknown scene "${id}"`);
  return s.start + (off !== undefined ? +off : s.dur * 0.6);
}

async function openPage(browser) {
  const page = await browser.newPage({ viewport: { width: timing.width || 1920, height: timing.height || 1080 }, deviceScaleFactor: 1 });
  page.on('pageerror', (e) => console.error('[page error]', e.message));
  page.on('console', (m) => { if (m.type() === 'error' || m.type() === 'warning') console.error('[page]', m.text()); });
  await page.goto(pageUrl);
  await page.evaluate(() => window.FV.ready);
  await page.evaluate(() => Promise.all(Array.from(document.images).map((i) => (i.complete ? 0 : new Promise((r) => (i.onload = i.onerror = r))))));
  return page;
}

async function shot(page, t, file) {
  await page.evaluate((x) => window.FV.seek(x), t);
  await page.screenshot({ path: file, type: 'png' });
}

const browser = await chromium.launch();
try {
  // 3a. stills
  let stills = opt('stills');
  if (flag('stills') && (!stills || stills.startsWith('--') || stills === projArg)) stills = 'all';
  if (flag('stills')) {
    const dir = path.join(out, 'stills');
    fs.mkdirSync(dir, { recursive: true });
    const page = await openPage(browser);
    const specs = stills === 'all' ? timing.scenes.map((s) => s.id) : stills.split(',');
    for (const spec of specs) {
      const t = resolveTime(spec.trim());
      const f = path.join(dir, `${spec.trim().replace(/[^\w@.-]/g, '_')}.png`);
      await shot(page, t, f);
      console.log(`still ${spec} @ ${t.toFixed(2)}s → ${f}`);
    }
    process.exit(0);
  }

  // 3b. frames → segments
  const frames = Math.ceil(timing.total * fps);
  const per = Math.ceil(frames / workers);
  let done = 0, lastPct = -1;
  const started = Date.now();
  console.log(`[render] ${frames} frames @ ${fps}fps, ${workers} workers`);
  const segs = await Promise.all(Array.from({ length: workers }, async (_, w) => {
    const a = w * per, b = Math.min(frames, a + per);
    const seg = path.join(out, `seg_${w}.mp4`);
    if (a >= b) return null;
    const page = await openPage(browser);
    const ff = spawn('ffmpeg', [...ffmpegQuiet, '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'mjpeg', '-i', '-',
      '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', '-r', String(fps), seg], { stdio: ['pipe', 'inherit', 'inherit'] });
    for (let f = a; f < b; f++) {
      await page.evaluate((x) => window.FV.seek(x), f / fps);
      const buf = await page.screenshot({ type: 'jpeg', quality: 95 });
      if (!ff.stdin.write(buf)) await once(ff.stdin, 'drain');
      done++;
      const pct = Math.floor((done / frames) * 100);
      if (pct % 5 === 0 && pct !== lastPct) { lastPct = pct; console.log(`[render] ${pct}%  (${((Date.now() - started) / 1000).toFixed(0)}s)`); }
    }
    ff.stdin.end();
    const [code] = await once(ff, 'close');
    if (code !== 0) throw new Error(`ffmpeg segment ${w} failed`);
    await page.close();
    return seg;
  }));

  // 4. concat + mux
  const list = path.join(out, 'segments.txt');
  fs.writeFileSync(list, segs.filter(Boolean).map((s) => `file '${s}'`).join('\n'));
  const mp4 = path.join(out, `${slug}.mp4`);
  run('ffmpeg', [...ffmpegQuiet, '-f', 'concat', '-safe', '0', '-i', list, '-i', path.join(out, 'narration.wav'),
    '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-shortest', '-movflags', '+faststart', mp4]);
  segs.filter(Boolean).forEach((s) => fs.unlinkSync(s));
  fs.unlinkSync(list);

  // 5. thumbnail
  const page = await openPage(browser);
  const thumbT = resolveTime(cfg.thumbnail || `${timing.scenes[0].id}@${Math.min(4, timing.scenes[0].dur - 0.5)}`);
  await page.evaluate(() => { const c = document.getElementById('fv-caption'); if (c) c.style.display = 'none'; });
  const big = path.join(out, 'thumbnail_1080.png');
  await shot(page, thumbT, big);
  run('ffmpeg', [...ffmpegQuiet, '-i', big, '-vf', timing.height > timing.width ? 'scale=720:1280' : 'scale=1280:720', path.join(out, 'thumbnail.png')]);
  fs.unlinkSync(big);

  // 6. youtube.txt with chapters
  const ts = (t) => `${Math.floor(t / 60)}:${String(Math.floor(t % 60)).padStart(2, '0')}`;
  const chapters = [];
  for (const s of timing.height > timing.width ? [] : timing.scenes) {   // Shorts have no chapters
    const prev = chapters[chapters.length - 1];
    // YouTube needs every chapter ≥ 10 s: fold a too-short chapter into the one that follows it
    if (prev && s.start - prev.start < 10) { if (prev.start > 0) prev.title = s.title; continue; }
    chapters.push({ start: chapters.length ? s.start : 0, title: s.title });
  }
  const yt = [
    `TITLE:\n${cfg.title || slug}\n`,
    `DESCRIPTION:\n${cfg.description || ''}\n`,
    chapters.map((c) => `${ts(c.start)} ${c.title}`).join('\n'),
    cfg.tags ? `\nTAGS:\n${cfg.tags.join(', ')}` : '',
  ].join('\n');
  fs.writeFileSync(path.join(out, 'youtube.txt'), yt + '\n');

  const mb = (fs.statSync(mp4).size / 1e6).toFixed(1);
  console.log(`[render] done in ${((Date.now() - started) / 1000).toFixed(0)}s → ${mp4} (${mb} MB, ${timing.total.toFixed(1)}s)`);
} finally {
  await browser.close();
}
