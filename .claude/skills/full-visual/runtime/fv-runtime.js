/*
 * full-visual runtime
 * A tiny timeline engine for narrated, frame-exact explainer videos.
 *
 * Every scene is drawn by a pure function of time, so the same page can be
 *   - played live in a browser (synced to narration.mp3), and
 *   - stepped frame-by-frame by render.mjs (?render) and encoded to MP4.
 *
 * Page contract:
 *   <div id="fv-stage"> <section class="fv-scene" data-scene="intro">…</section> … </div>
 *   <script src="timing.js"></script>      (written by tts.py, defines window.FV_TIMING)
 *   <script src="fv-runtime.js"></script>
 *   <script> FV.scene('intro', (t, ctx) => { … }); </script>
 *
 * ctx = { id, dur, el, lines, line(i), lineEnd(i) }   (all seconds, scene-local)
 * Never use CSS animations/transitions, timers or Math.random — derive everything from t.
 */
(function () {
  'use strict';
  const T0 = window.FV_TIMING || {};
  const W = T0.width || 1920, H = T0.height || 1080, FADE = 0.5;
  const VERT = H > W;
  const RENDER = new URLSearchParams(location.search).has('render');
  const FV = (window.FV = window.FV || {});
  FV.W = W; FV.H = H; FV.render = RENDER; FV.time = 0;

  const fns = {};
  FV.scene = (id, fn) => { fns[id] = fn; };

  /* ---------- helpers ---------- */
  const clamp = (FV.clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v)));
  FV.lerp = (a, b, p) => a + (b - a) * p;
  FV.ease = {
    linear: (t) => t,
    in: (t) => t * t * t,
    out: (t) => 1 - Math.pow(1 - t, 3),
    inOut: (t) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2),
    back: (t) => { const c1 = 1.70158, c3 = c1 + 1; return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2); },
  };
  /** eased 0→1 progress of t between a and b */
  FV.seg = (t, a, b, e = FV.ease.inOut) => (b <= a ? (t >= a ? 1 : 0) : e(clamp((t - a) / (b - a))));
  /** 0→1→0 bump between a and b */
  FV.pulse = (t, a, b) => (t <= a || t >= b ? 0 : Math.sin(((t - a) / (b - a)) * Math.PI));
  /** deterministic PRNG */
  FV.rand = (seed) => { let s = seed >>> 0; return () => { s = (s + 0x6d2b79f5) >>> 0; let r = Math.imul(s ^ (s >>> 15), 1 | s); r = (r + Math.imul(r ^ (r >>> 7), 61 | r)) ^ r; return ((r ^ (r >>> 14)) >>> 0) / 4294967296; }; };
  FV.type = (text, p) => text.slice(0, Math.round(text.length * clamp(p)));
  FV.$ = (sel, root = document) => root.querySelector(sel);
  FV.$$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));
  /** set opacity/transform shorthand + any style props: {o, x, y, s, r, ...style} */
  FV.css = (el, o) => {
    if (!el) return;
    const { o: op, x, y, s, r, ...rest } = o;
    if (op !== undefined) el.style.opacity = op;
    if (x !== undefined || y !== undefined || s !== undefined || r !== undefined)
      el.style.transform = `translate(${x || 0}px,${y || 0}px) scale(${s === undefined ? 1 : s}) rotate(${r || 0}deg)`;
    for (const k in rest) el.style[k] = rest[k];
  };
  /** standard entrance for an element: fade + rise starting at time a */
  FV.enter = (el, t, a, d = 0.6, rise = 24) => {
    const p = FV.seg(t, a, a + d, FV.ease.out);
    FV.css(el, { o: p, y: (1 - p) * rise });
    return p;
  };

  /* ---------- timing ---------- */
  let timing = window.FV_TIMING;
  let sceneEls = {};
  let captionEl;

  function fallbackTiming() {
    // Before tts.py has run: 6 s per scene, no narration.
    const scenes = FV.$$('.fv-scene').map((el, i) => ({ id: el.dataset.scene, start: i * 6, dur: 6, lines: [] }));
    return { total: scenes.length * 6, captions: false, scenes };
  }

  function ctxFor(s) {
    if (s._ctx) return s._ctx;
    s._ctx = {
      id: s.id, dur: s.dur, el: sceneEls[s.id], lines: s.lines,
      line: (i) => (s.lines[i] ? s.lines[i].start : s.dur),
      lineEnd: (i) => (s.lines[i] ? s.lines[i].end : s.dur),
    };
    return s._ctx;
  }

  function render(time) {
    FV.time = time;
    const list = timing.scenes, last = list.length - 1;
    list.forEach((s, i) => {
      const el = sceneEls[s.id];
      if (!el) return;
      const t = time - s.start;
      let op = 0;
      if (t >= 0) {
        op = i === 0 ? 1 : clamp(t / FADE);
        if (i !== last) op = Math.min(op, 1 - clamp((t - s.dur) / FADE));
      }
      el.style.opacity = op;
      el.style.visibility = op > 0 ? 'visible' : 'hidden';
      if (op > 0 && fns[s.id]) fns[s.id](Math.max(0, t), ctxFor(s));
    });
    if (captionEl) {
      let txt = '';
      if (timing.captions) {
        for (const s of list) {
          for (const ln of s.lines) for (const c of ln.chunks || [ln]) {
            if (time >= s.start + c.start && time < s.start + c.end + 0.25) txt = c.text;
          }
        }
      }
      if (captionEl.textContent !== txt) captionEl.textContent = txt;
      captionEl.style.opacity = txt ? 1 : 0;
    }
  }
  FV.seek = (t) => { render(t); return true; };

  /* ---------- page chrome ---------- */
  const style = document.createElement('style');
  style.textContent = `
    html,body{margin:0;height:100%;overflow:hidden;background:#000}
    #fv-stage{position:absolute;left:50%;top:50%;width:${W}px;height:${H}px;overflow:hidden;transform-origin:center center}
    .fv-scene{position:absolute;inset:0;opacity:0;visibility:hidden}
    #fv-caption{position:absolute;left:50%;bottom:${T0.captionBottom || (VERT ? 470 : 54)}px;transform:translateX(-50%);width:max-content;max-width:${W - (VERT ? 140 : 420)}px;padding:14px 30px;border-radius:14px;
      background:rgba(0,0,0,.62);color:#fff;font:${VERT ? '700 50px/1.25' : '500 40px/1.3'} Inter,system-ui,sans-serif;text-align:center;z-index:50;pointer-events:none}
    #fv-ui{position:fixed;left:0;right:0;bottom:0;display:flex;gap:12px;align-items:center;padding:10px 16px;z-index:100;
      background:linear-gradient(transparent,rgba(0,0,0,.75));font:500 14px Inter,system-ui,sans-serif;color:#fff}
    #fv-ui button{background:rgba(255,255,255,.14);color:#fff;border:0;border-radius:8px;padding:8px 14px;font:inherit;cursor:pointer}
    #fv-ui input{flex:1;accent-color:#38bdf8}
    #fv-big{position:fixed;inset:0;display:flex;align-items:center;justify-content:center;z-index:99;cursor:pointer;background:rgba(0,0,0,.35)}
    #fv-big div{width:120px;height:120px;border-radius:50%;background:rgba(255,255,255,.92);display:flex;align-items:center;justify-content:center}
    #fv-big div:after{content:"";margin-left:10px;border-left:38px solid #111;border-top:24px solid transparent;border-bottom:24px solid transparent}
  `;
  document.head.appendChild(style);

  function fit(stage) {
    const s = RENDER ? 1 : Math.min(innerWidth / W, innerHeight / H);
    stage.style.transform = `translate(-50%,-50%) scale(${s})`;
  }

  function fmt(t) { t = Math.max(0, t); return `${Math.floor(t / 60)}:${String(Math.floor(t % 60)).padStart(2, '0')}`; }

  function preview() {
    const audio = new Audio('narration.mp3');
    let audioOk = true, playing = false, clock = 0, t0 = 0;
    audio.addEventListener('error', () => { audioOk = false; });
    audio.addEventListener('ended', () => { playing = false; sync(); });
    const now = () => (audioOk ? audio.currentTime : playing ? clock + (performance.now() - t0) / 1000 : clock);

    const ui = document.createElement('div');
    ui.id = 'fv-ui';
    ui.innerHTML = `<button id="fv-play">Play</button><input id="fv-seek" type="range" min="0" step="0.01" value="0"><span id="fv-time">0:00</span><button id="fv-cc">CC</button>`;
    document.body.appendChild(ui);
    const big = document.createElement('div');
    big.id = 'fv-big'; big.innerHTML = '<div></div>';
    document.body.appendChild(big);
    const btn = FV.$('#fv-play'), seek = FV.$('#fv-seek'), time = FV.$('#fv-time');
    seek.max = timing.total;

    function sync() { btn.textContent = playing ? 'Pause' : 'Play'; big.style.display = playing ? 'none' : 'flex'; }
    function play() {
      if (now() >= timing.total - 0.05) setTime(0);
      playing = true;
      if (audioOk) audio.play().catch(() => { audioOk = false; clock = audio.currentTime; t0 = performance.now(); });
      else t0 = performance.now();
      sync();
    }
    function pause() { clock = now(); playing = false; if (audioOk) audio.pause(); sync(); }
    function setTime(t) { clock = t; t0 = performance.now(); if (audioOk) audio.currentTime = t; render(t); }
    btn.onclick = () => (playing ? pause() : play());
    big.onclick = play;
    seek.oninput = () => setTime(+seek.value);
    FV.$('#fv-cc').onclick = () => { timing.captions = !timing.captions; render(now()); };
    addEventListener('keydown', (e) => {
      if (e.code === 'Space') { e.preventDefault(); playing ? pause() : play(); }
      if (e.code === 'ArrowRight') setTime(Math.min(timing.total, now() + 5));
      if (e.code === 'ArrowLeft') setTime(Math.max(0, now() - 5));
    });
    (function loop() {
      let t = now();
      if (!audioOk && playing && t >= timing.total) { playing = false; clock = timing.total; sync(); }
      t = Math.min(t, timing.total);
      render(t);
      seek.value = t;
      time.textContent = `${fmt(t)} / ${fmt(timing.total)}`;
      requestAnimationFrame(loop);
    })();
    sync();
  }

  FV.ready = new Promise((resolve) => {
    addEventListener('load', async () => {
      const stage = FV.$('#fv-stage');
      fit(stage);
      addEventListener('resize', () => fit(stage));
      FV.$$('.fv-scene').forEach((el) => (sceneEls[el.dataset.scene] = el));
      if (!timing) { timing = fallbackTiming(); console.warn('[full-visual] timing.js missing — using 6 s/scene placeholder timing'); }
      captionEl = document.createElement('div');
      captionEl.id = 'fv-caption';
      stage.appendChild(captionEl);
      if (document.fonts) await document.fonts.ready;
      // end card: every .fv-endcard element gets the text of video.json "endCard" (e.g. the GitHub link)
      FV.$$('.fv-endcard').forEach((e) => { e.textContent = timing.endCard || ''; if (!timing.endCard) e.style.display = 'none'; });
      FV.total = timing.total;
      FV.timing = timing;
      render(0);
      if (!RENDER) preview();
      resolve(true);
    });
  });
})();
