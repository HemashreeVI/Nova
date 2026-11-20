/* HCI exam kit — builds scenes from window.SPEC (generated from video.json "viz" fields).
 * Every animation is a pure function of t; items appear at narration line `at`. */
(function () {
  const { seg, css, ease, clamp, lerp, pulse } = FV;
  const COL = { b: '#38bdf8', p: '#a78bfa', y: '#fbbf24', k: '#f472b6', g: '#34d399', o: '#fb923c', r: '#f87171', w: '#e8edf7' };
  const col = (c, i) => COL[c] || c || Object.values(COL)[i % 7];
  const h = (tag, cls, html, style) => { const e = document.createElement(tag); if (cls) e.className = cls; if (html != null) e.innerHTML = html; if (style) Object.assign(e.style, style); return e; };
  const stage = document.getElementById('fv-stage');
  const X0 = 110, X1 = 1810, Y0 = 250, Y1 = 900;
  const builders = {}, anim = {};
  const SVGNS = 'http://www.w3.org/2000/svg';
  const svg = (tag, attrs, parent) => { const e = document.createElementNS(SVGNS, tag); for (const k in attrs) e.setAttribute(k, attrs[k]); if (parent) parent.appendChild(e); return e; };

  // ---- helpers ----------------------------------------------------------
  function at(ctx, a) { if (a == null) return 0.2; const i = Math.floor(a), f = a - i; return ctx.line(i) + (ctx.lineEnd(i) - ctx.line(i)) * f; }
  function activeWin(ctx, items, k) {
    const s = at(ctx, items[k].at);
    let e = ctx.dur;
    for (let j = k + 1; j < items.length; j++) { const sj = at(ctx, items[j].at); if (sj > s) { e = sj; break; } }
    return [s, e];
  }
  function reveal(el, t, s, rise = 26) { const p = seg(t, s, s + 0.55, ease.out); css(el, { o: p, y: (1 - p) * rise }); return p; }
  function spot(el, t, ctx, items, k, c) {
    const [s, e] = activeWin(ctx, items, k);
    const on = t >= s && t < e ? 1 : 0;
    const g = Math.min(seg(t, s, s + 0.3), 1 - seg(t, e, e + 0.3));
    el.style.boxShadow = g > 0.01 ? `0 0 0 ${3 * g}px ${c}, 0 0 ${50 * g}px ${c}55` : 'none';
    return g;
  }

  // ---- CARDS ------------------------------------------------------------
  builders.cards = (root, v) => {
    const n = v.items.length;
    const cols = v.cols || (n <= 3 ? n : n === 4 ? 2 : n <= 6 ? 3 : 4);
    const rows = Math.ceil(n / cols);
    const top = v.top || Y0, bot = v.bottom || Y1, gap = 26;
    const W = (X1 - X0 - gap * (cols - 1)) / cols, H = Math.min(v.maxH || (rows === 1 ? 600 : 420), (bot - top - gap * (rows - 1)) / rows);
    const totalH = rows * H + (rows - 1) * gap, y0 = top + Math.max(0, (bot - top - totalH) / 2);
    v._els = v.items.map((it, i) => {
      const r = Math.floor(i / cols), c = i % cols, inRow = Math.min(cols, n - r * cols);
      const xoff = (cols - inRow) * (W + gap) / 2;
      const cc = col(it.c, i);
      const big = H > 230 && !v.small;
      const e = h('div', 'card', `${it.icon ? `<div class="ic" style="font-size:${big ? 64 : 46}px">${it.icon}</div>` : ''}<div class="ch" style="color:${cc};font-size:${it.hs || (big ? 42 : 34)}px">${it.h}</div>${it.b ? `<div class="cb" style="font-size:${it.bs || v.bs || (big ? 31 : 26)}px">${it.b}</div>` : ''}`,
        { left: X0 + xoff + c * (W + gap) + 'px', top: y0 + r * (H + gap) + 'px', width: W + 'px', height: H + 'px', borderTop: `6px solid ${cc}` });
      root.appendChild(e); return e;
    });
  };
  anim.cards = (v, t, ctx) => v.items.forEach((it, k) => { reveal(v._els[k], t, at(ctx, it.at)); spot(v._els[k], t, ctx, v.items, k, col(it.c, k)); });

  // ---- FLOW (chain of boxes with arrows) ---------------------------------
  builders.flow = (root, v) => {
    const n = v.nodes.length, vert = v.dir === 'v';
    const sv = svg('svg', { width: 1920, height: 1080, class: 'abs', style: 'left:0;top:0' }, root);
    v._els = []; v._ar = []; v._dots = [];
    const top = v.top || Y0, bot = v.bottom || Y1;
    let boxes;
    if (vert) {
      const gap = 34, H = Math.min(130, (bot - top - gap * (n - 1)) / n), W = v.w || 1100;
      const x = (1920 - W) / 2, y0 = top + (bot - top - (n * H + (n - 1) * gap)) / 2;
      boxes = v.nodes.map((_, i) => ({ x, y: y0 + i * (H + gap), w: W, h: H }));
    } else {
      const gap = 70, W = (X1 - X0 - gap * (n - 1)) / n, H = v.h || 300;
      const y = top + (bot - top - H) / 2;
      boxes = v.nodes.map((_, i) => ({ x: X0 + i * (W + gap), y, w: W, h: H }));
    }
    v.nodes.forEach((nd, i) => {
      const b = boxes[i], cc = col(nd.c, i);
      const e = h('div', 'card flowbox' + (vert ? ' vrow' : ''), `${nd.icon ? `<div class="ic" style="font-size:${vert ? 44 : 58}px">${nd.icon}</div>` : ''}<div><div class="ch" style="color:${cc};font-size:${vert ? 34 : 36}px">${nd.h}</div>${nd.b ? `<div class="cb" style="font-size:${vert ? 25 : 27}px">${nd.b}</div>` : ''}</div>`,
        { left: b.x + 'px', top: b.y + 'px', width: b.w + 'px', height: b.h + 'px', borderTop: `6px solid ${cc}` });
      root.appendChild(e); v._els.push(e);
      if (i < n - 1) {
        const nb = boxes[i + 1];
        const [x1, y1, x2, y2] = vert ? [b.x + b.w / 2, b.y + b.h + 4, nb.x + nb.w / 2, nb.y - 6] : [b.x + b.w + 6, b.y + b.h / 2, nb.x - 8, nb.y + nb.h / 2];
        const ln = svg('line', { x1, y1, x2, y2, stroke: '#64748b', 'stroke-width': 5, 'marker-end': 'url(#ah)' }, sv);
        const L = Math.hypot(x2 - x1, y2 - y1); ln.style.strokeDasharray = L; v._ar.push([ln, L]);
        const d = svg('circle', { r: 9, fill: cc }, sv); v._dots.push([d, x1, y1, x2, y2]);
      }
    });
    defs(sv);
  };
  anim.flow = (v, t, ctx) => v.nodes.forEach((nd, k) => {
    const s = at(ctx, nd.at);
    reveal(v._els[k], t, s); spot(v._els[k], t, ctx, v.nodes, k, col(nd.c, k));
    if (k > 0) {
      const [ln, L] = v._ar[k - 1]; const p = seg(t, s - 0.35, s + 0.1);
      ln.style.strokeDashoffset = L * (1 - p); ln.style.opacity = p > 0 ? 1 : 0;
      const [d, x1, y1, x2, y2] = v._dots[k - 1]; const q = seg(t, s - 0.35, s + 0.25, ease.linear);
      d.setAttribute('cx', lerp(x1, x2, q)); d.setAttribute('cy', lerp(y1, y2, q)); d.style.opacity = q > 0 && q < 1 ? 1 : 0;
    }
  });
  defs.n = 0;
  function defs(sv) {
    const d = svg('defs', {}, sv);
    const m = svg('marker', { id: 'ah' + (++defs.n), class: 'mk', markerWidth: 10, markerHeight: 10, refX: 6, refY: 5, orient: 'auto', markerUnits: 'strokeWidth' }, d);
    svg('path', { d: 'M0,1 L8,5 L0,9 z', fill: '#94a3b8' }, m);
  }

  // ---- FORMULA ------------------------------------------------------------
  builders.formula = (root, v) => {
    v._f = h('div', 'formula', v.f, { top: (v.ftop || 270) + 'px', fontSize: (v.fs || 76) + 'px' }); root.appendChild(v._f);
    v._els = (v.rows || []).map((r, i) => { const e = h('div', 'frow', r.t, { top: (v.rtop || 440) + i * (v.rgap || 92) + 'px', fontSize: (r.fs || v.rfs || 38) + 'px', color: r.c ? col(r.c) : '' }); root.appendChild(e); return e; });
  };
  anim.formula = (v, t, ctx) => {
    const s = at(ctx, v.at); const p = seg(t, s, s + 0.7, ease.back); css(v._f, { o: clamp(p * 1.4), s: 0.8 + 0.2 * p });
    v._f.style.textShadow = `0 0 ${40 * pulse(t, s, s + 1.6)}px #fbbf24`;
    (v.rows || []).forEach((r, k) => { reveal(v._els[k], t, at(ctx, r.at)); });
  };

  // ---- TABLE ---------------------------------------------------------------
  builders.table = (root, v) => {
    const tb = h('table', 'tbl', null, { top: (v.top || 270) + 'px', fontSize: (v.fs || 32) + 'px' });
    tb.innerHTML = `<tr>${v.head.map((x) => `<th>${x}</th>`).join('')}</tr>`;
    v._els = v.rows.map((r, i) => { const tr = document.createElement('tr'); tr.innerHTML = r.cells.map((x, j) => `<td style="${j === 0 ? `color:${col(r.c, i)};font-weight:800` : ''}">${x}</td>`).join(''); tb.appendChild(tr); return tr; });
    root.appendChild(tb);
  };
  anim.table = (v, t, ctx) => v.rows.forEach((r, k) => {
    const s = at(ctx, r.at); const p = seg(t, s, s + 0.5, ease.out); v._els[k].style.opacity = p;
    const [a, e] = activeWin(ctx, v.rows, k); v._els[k].style.background = t >= a && t < e ? 'rgba(56,189,248,.14)' : 'transparent';
  });

  // ---- CHAT (conversation bubbles) ----------------------------------------
  builders.chat = (root, v) => {
    const people = v.people || {}; const n = v.msgs.length;
    const top = v.top || 260, gap = Math.min(78, (Y1 - top) / n);
    v._els = v.msgs.map((m, i) => {
      const pc = people[m.who] || {}; const right = pc.side === 'r';
      const e = h('div', 'bub' + (right ? ' r' : ''), `<span class="who" style="background:${col(pc.c, i)}">${m.who}</span><span class="txt">${m.t}</span>`,
        { top: top + i * gap + 'px', [right ? 'right' : 'left']: (v.x || 260) + 'px', fontSize: (v.fs || 34) + 'px' });
      if (m.note) e.innerHTML += `<span class="note" style="color:${col(m.nc || 'y')}">${m.note}</span>`;
      root.appendChild(e); return e;
    });
  };
  anim.chat = (v, t, ctx) => v.msgs.forEach((m, k) => {
    const s = at(ctx, m.at); const p = seg(t, s, s + 0.4, ease.back); css(v._els[k], { o: clamp(p * 2), s: 0.85 + 0.15 * p });
  });

  // ---- ACRONYM (big letters that expand) ----------------------------------
  builders.acronym = (root, v) => {
    const n = v.letters.length, gap = 24, W = Math.min(330, (X1 - X0 - gap * (n - 1)) / n);
    const x0 = (1920 - (n * W + (n - 1) * gap)) / 2, y = v.top || 280;
    v._els = v.letters.map((L, i) => {
      const cc = col(L.c, i);
      const e = h('div', 'acr', `<div class="L" style="color:${cc};font-size:${v.ls || 150}px">${L.L}</div><div class="w" style="font-size:${v.ws || 38}px">${L.w}</div>${L.d ? `<div class="d" style="font-size:${v.ds || 26}px">${L.d}</div>` : ''}`,
        { left: x0 + i * (W + gap) + 'px', top: y + 'px', width: W + 'px', height: (v.h || 560) + 'px', borderTop: `6px solid ${cc}` });
      root.appendChild(e); return e;
    });
  };
  anim.acronym = (v, t, ctx) => v.letters.forEach((L, k) => {
    const s = at(ctx, L.at); const p = seg(t, s, s + 0.6, ease.back); css(v._els[k], { o: clamp(p * 1.5), y: (1 - p) * 60 });
    spot(v._els[k], t, ctx, v.letters, k, col(L.c, k));
  });

  // ---- TIMELINE -------------------------------------------------------------
  builders.timeline = (root, v) => {
    const n = v.events.length, y = v.y || 560;
    const sv = svg('svg', { width: 1920, height: 1080, class: 'abs', style: 'left:0;top:0' }, root);
    v._line = svg('line', { x1: X0, y1: y, x2: X1, y2: y, stroke: '#475569', 'stroke-width': 6 }, sv);
    const step = (X1 - X0) / n;
    v._els = v.events.map((ev, i) => {
      const cx = X0 + step * (i + 0.5), cc = col(ev.c, i), up = i % 2 === 0;
      svg('circle', { cx, cy: y, r: 16, fill: cc }, sv);
      const e = h('div', 'card tl', `<div class="yr" style="color:${cc}">${ev.y}</div>${ev.icon ? `<div class="ic" style="font-size:52px">${ev.icon}</div>` : ''}<div class="ch" style="font-size:31px">${ev.h}</div>${ev.b ? `<div class="cb" style="font-size:24px">${ev.b}</div>` : ''}`,
        { left: cx - step / 2 + 10 + 'px', width: step - 20 + 'px', top: (up ? y - (v.hUp || 300) - 30 : y + 30) + 'px', height: (up ? v.hUp || 300 : v.hDn || 300) + 'px', borderTop: `6px solid ${cc}` });
      root.appendChild(e); return e;
    });
  };
  anim.timeline = (v, t, ctx) => {
    v._line.style.opacity = seg(t, 0, 0.6);
    v.events.forEach((ev, k) => { reveal(v._els[k], t, at(ctx, ev.at)); spot(v._els[k], t, ctx, v.events, k, col(ev.c, k)); });
  };

  // ---- HOOK / RECAP ------------------------------------------------------------
  builders.hook = (root, v) => {
    v._e = [h('div', 'hookicon', v.icon || ''), h('div', 'hookt', v.t), h('div', 'hooks', v.s || '')];
    v._chips = (v.chips || []).map((c, i) => h('span', 'chip', c, { borderColor: col(null, i), color: col(null, i) }));
    const row = h('div', 'chiprow'); v._chips.forEach((c) => row.appendChild(c)); v._e.push(row);
    v._e.forEach((e) => root.appendChild(e));
  };
  anim.hook = (v, t, ctx) => {
    css(v._e[0], { o: seg(t, 0.1, 0.6), s: 0.6 + 0.4 * seg(t, 0.1, 0.9, ease.back), y: Math.sin(t * 1.6) * 8 });
    reveal(v._e[1], t, 0.35); reveal(v._e[2], t, at(ctx, v.sAt != null ? v.sAt : 0.5));
    v._e[3].style.opacity = 1;
    v._chips.forEach((c, i) => { const s = at(ctx, v.cAt != null ? v.cAt : 1) + i * 0.18; const p = seg(t, s, s + 0.4, ease.back); css(c, { o: clamp(p * 2), s: 0.7 + 0.3 * p }); });
  };

  // ---- NOTE (exam tip banner, any scene) ------------------------------------------
  function addNote(root, v) {
    if (!v.note) return;
    v._note = h('div', 'tipbar', `<b>${v.noteLabel || 'MEMORY HOOK'}</b> ${v.note}`); root.appendChild(v._note);
  }
  function animNote(v, t, ctx) { if (v._note) { const s = at(ctx, v.noteAt != null ? v.noteAt : ctx.lines.length - 1); reveal(v._note, t, s, 16); } }

  // ======================= CUSTOM DIAGRAMS =======================
  const custom = {};
  const box = (root, x, y, w, hh, html, c, cls = 'card') => { const e = h('div', cls + ' cbox', html, { left: x + 'px', top: y + 'px', width: w + 'px', height: hh + 'px', borderTop: `6px solid ${c}` }); root.appendChild(e); return e; };

  // MHP architecture: memories + processors, a signal travels eyes → perceptual → stores → WM → cognitive → LTM → motor
  custom.mhp = {
    build(root, v) {
      const sv = svg('svg', { width: 1920, height: 1080, class: 'abs', style: 'left:0;top:0' }, root); defs(sv);
      v.E = {
        sense: box(root, 110, 560, 230, 170, '<div class="ic" style="font-size:52px">👁️👂</div><div class="ch" style="font-size:28px">Eyes &amp; Ears</div>', COL.w),
        perc: box(root, 420, 580, 320, 130, '<div class="ch" style="color:#38bdf8;font-size:34px">Perceptual Processor</div><div class="cb" style="font-size:24px">τp ≈ 100 ms</div>', COL.b),
        vis: box(root, 420, 300, 150, 170, '<div class="ch" style="font-size:26px;color:#38bdf8">Visual Store</div><div class="cb" style="font-size:22px">VIS</div>', COL.b),
        aud: box(root, 590, 300, 150, 170, '<div class="ch" style="font-size:26px;color:#38bdf8">Auditory Store</div><div class="cb" style="font-size:22px">AIS</div>', COL.b),
        wm: box(root, 820, 300, 420, 170, '<div class="ch" style="font-size:34px;color:#fbbf24">Working Memory</div><div class="cb" style="font-size:24px">activated chunks of LTM</div>', COL.y),
        ltm: box(root, 820, 250 - 0, 420, 0, '', COL.y),
        cog: box(root, 840, 580, 380, 130, '<div class="ch" style="color:#a78bfa;font-size:34px">Cognitive Processor</div><div class="cb" style="font-size:24px">τc ≈ 70 ms</div>', COL.p),
        ltm2: box(root, 1320, 300, 430, 170, '<div class="ch" style="font-size:34px;color:#34d399">Long-Term Memory</div><div class="cb" style="font-size:24px">semantic, infinite decay</div>', COL.g),
        mot: box(root, 1320, 580, 430, 130, '<div class="ch" style="color:#f472b6;font-size:34px">Motor Processor</div><div class="cb" style="font-size:24px">τm ≈ 70 ms → arm, hand, finger</div>', COL.k),
      };
      v.E.ltm.style.display = 'none';
      const A = (x1, y1, x2, y2) => { const l = svg('line', { x1, y1, x2, y2, stroke: '#94a3b8', 'stroke-width': 5, 'marker-end': 'url(#ah)' }, sv); return l; };
      v.arrows = [A(342, 645, 412, 645), A(500, 575, 500, 478), A(660, 575, 660, 478), A(745, 385, 812, 385), A(1030, 475, 1030, 572), A(1245, 385, 1312, 385), A(1225, 645, 1312, 645)];
      v.dot = svg('circle', { r: 12, fill: '#fbbf24' }, sv);
      v.path = [[230, 645], [420, 645], [500, 575], [500, 470], [745, 385], [820, 385], [1030, 470], [1030, 580], [1225, 645], [1320, 645], [1535, 645]];
    },
    anim(v, t, ctx) {
      const b = v.beats; // [sense, perc, stores, wm, cog, ltm, motor, signal]
      const order = [['sense'], ['perc'], ['vis', 'aud'], ['wm'], ['cog'], ['ltm2'], ['mot']];
      order.forEach((ks, i) => ks.forEach((k) => reveal(v.E[k], t, at(ctx, b[i]))));
      v.arrows.forEach((a, i) => { a.style.opacity = seg(t, at(ctx, b[Math.min(6, i + 1)]) - 0.2, at(ctx, b[Math.min(6, i + 1)]) + 0.3); });
      const s = at(ctx, b[7]); const per = 4.5; const q = t < s ? -1 : ((t - s) % per) / per;
      if (q < 0) { v.dot.style.opacity = 0; return; }
      v.dot.style.opacity = 1;
      const P = v.path, segs = P.length - 1, f = q * segs, i = Math.min(segs - 1, Math.floor(f)), r = f - i;
      v.dot.setAttribute('cx', lerp(P[i][0], P[i + 1][0], r)); v.dot.setAttribute('cy', lerp(P[i][1], P[i + 1][1], r));
    },
  };

  // Stroop-like demo: coloured words, then colour names, then THE CAT
  custom.stroop = {
    build(root, v) {
      const mk = (words, x) => words.map(([w, c], i) => { const e = h('div', 'sw', w, { left: x + 'px', top: 290 + i * 88 + 'px', color: c }); root.appendChild(e); return e; });
      v.a = mk([['Human', '#22c55e'], ['Computer', '#a855f7'], ['Interface', '#f97316'], ['Impression', '#ef4444'], ['Memory', '#3b82f6'], ['Scheme', '#facc15']], 170);
      v.b = mk([['Green', '#22c55e'], ['Purple', '#a855f7'], ['Orange', '#f97316'], ['Red', '#ef4444'], ['Blue', '#3b82f6'], ['Yellow', '#facc15']], 760);
      v.la = h('div', 'tag', 'T1 — read the INK colour', { left: '170px', top: '235px' }); v.lb = h('div', 'tag', 'T2 — faster!  T1 &gt; T2', { left: '760px', top: '235px' });
      const G = '<svg class="amb" viewBox="0 0 80 100" width="0.78em" height="0.8em"><path d="M8 100 L40 4 L72 100 M22 58 L58 58" fill="none" stroke="#fbbf24" stroke-width="12"/></svg>'; v.cat = h('div', 'cat', 'T' + G + 'E&nbsp;&nbsp;C' + G + 'T', { left: '1180px', top: '360px' });
      v.lc = h('div', 'tag', 'SAME shape → read as H, then A', { left: '1180px', top: '540px', width: '640px' });
      [v.la, v.lb, v.cat, v.lc].forEach((e) => root.appendChild(e));
    },
    anim(v, t, ctx) {
      const b = v.beats;
      reveal(v.la, t, at(ctx, b[0])); v.a.forEach((e, i) => reveal(e, t, at(ctx, b[0]) + 0.25 * i));
      reveal(v.lb, t, at(ctx, b[1])); v.b.forEach((e, i) => reveal(e, t, at(ctx, b[1]) + 0.15 * i));
      reveal(v.cat, t, at(ctx, b[2])); reveal(v.lc, t, at(ctx, b[2]) + 0.6);
      v.cat.querySelectorAll('.amb').forEach((e) => (e.style.filter = `drop-shadow(0 0 ${12 * pulse(t, at(ctx, b[2]) + 0.6, at(ctx, b[2]) + 2.6)}px #fbbf24)`, e.style.x0 = `0 0 ${30 * pulse(t, at(ctx, b[2]) + 0.6, at(ctx, b[2]) + 2.6)}px #fbbf24`));
    },
  };

  // practice curve Tn = T1 n^-a
  custom.practice = {
    build(root, v) {
      const sv = svg('svg', { width: 1920, height: 1080, class: 'abs', style: 'left:0;top:0' }, root);
      const ox = 1060, oy = 820, W = 720, H = 480;
      svg('line', { x1: ox, y1: oy, x2: ox + W, y2: oy, stroke: '#64748b', 'stroke-width': 4 }, sv);
      svg('line', { x1: ox, y1: oy, x2: ox, y2: oy - H, stroke: '#64748b', 'stroke-width': 4 }, sv);
      let d = ''; for (let n = 1; n <= 30; n += 0.25) { const x = ox + (n - 1) / 29 * W, y = oy - H * Math.pow(n, -0.4); d += (d ? 'L' : 'M') + x.toFixed(1) + ',' + y.toFixed(1); }
      v.curve = svg('path', { d, fill: 'none', stroke: '#34d399', 'stroke-width': 7 }, sv);
      v.L = v.curve.getTotalLength ? 2000 : 2000; v.curve.style.strokeDasharray = 2000;
      const lab = (x, y, t) => { const e = h('div', 'axl', t, { left: x + 'px', top: y + 'px' }); root.appendChild(e); return e; };
      v.labs = [lab(ox + W - 260, oy + 14, 'attempt number n →'), lab(ox - 20, oy - H - 52, 'time Tn'), lab(ox + W - 330, oy - 120, 'α = 0.2 to 0.6 (illustrative 0.4)')];
      if (v.left) v.lc = box(root, 110, 290, 860, 520, v.left, COL.g);
      v.f = h('div', 'formula', 'T<sub>n</sub> = T<sub>1</sub> · n<sup>−α</sup>', { left: '1060px', top: '260px', width: '720px', fontSize: '64px' }); root.appendChild(v.f);
    },
    anim(v, t, ctx) {
      if (v.lc) reveal(v.lc, t, 0.4);
      const s = at(ctx, v.beats[0]); reveal(v.f, t, s);
      v.curve.style.strokeDashoffset = 2000 * (1 - seg(t, s + 0.4, s + 3));
      v.labs.forEach((e, i) => reveal(e, t, s + 0.6 + i * 0.4));
    },
  };

  // Fitts: Mac edge menu vs Windows offset menu
  custom.fittsMenu = {
    build(root, v) {
      const mk = (x, name, c, off) => {
        const scr = h('div', 'screen', '', { left: x + 'px', top: '300px', width: '760px', height: '420px' });
        const bar = h('div', 'mbar', 'File &nbsp; Edit &nbsp; View', { top: off + 'px', background: c });
        scr.appendChild(bar);
        if (off) scr.appendChild(h('div', 'tbar', 'Title bar', { top: '0px' }));
        const cur = h('div', 'cursor', '↖'); scr.appendChild(cur);
        const lab = h('div', 'ch', name, { position: 'absolute', left: x + 'px', top: '240px', color: c, fontSize: '40px' });
        root.appendChild(scr); root.appendChild(lab);
        return { scr, bar, cur, lab };
      };
      v.m = mk(130, 'Mac — menu on screen edge, W ≈ 50 mm', '#34d399', 0);
      v.w = mk(1030, 'Windows — menu below title bar, W ≈ 5 mm', '#f87171', 46);
      v.rm = h('div', 'res', '50 + 150·log₂(80/50 + 1) ≈ <b style="color:#34d399">256 ms</b>', { left: '130px', top: '750px', width: '760px' });
      v.rw = h('div', 'res', '50 + 150·log₂(80/5 + 1) ≈ <b style="color:#f87171">663 ms</b>', { left: '1030px', top: '750px', width: '760px' });
      root.appendChild(v.rm); root.appendChild(v.rw);
    },
    anim(v, t, ctx) {
      const b = v.beats;
      [v.m, v.w].forEach((o, i) => {
        const s = at(ctx, b[i]); reveal(o.scr, t, s); reveal(o.lab, t, s);
        const p = seg(t, s + 0.7, s + 2.2, ease.inOut);
        // Mac: cursor flies past target and stops at edge; Windows: must slow down to land in the thin bar
        const ty = i === 0 ? lerp(330, -6, p) : lerp(330, 44, p) + Math.sin(p * 18) * 14 * (1 - p);
        css(o.cur, { x: lerp(460, 150, p), y: ty });
        o.bar.style.boxShadow = p >= 1 ? '0 0 30px ' + (i ? '#f87171' : '#34d399') : 'none';
      });
      reveal(v.rm, t, at(ctx, b[2])); reveal(v.rw, t, at(ctx, b[2]) + 0.4);
    },
  };

  // Hick's menu demo
  custom.hick = {
    build(root, v) {
      v.items = [];
      const names = ['Open', 'Save', 'Print', 'Share', 'Export', 'Rename', 'Delete', 'Close'];
      names.forEach((n, i) => { const e = h('div', 'mitem', n, { left: '180px', top: 280 + i * 66 + 'px' }); root.appendChild(e); v.items.push(e); });
      v.f = h('div', 'formula', 'T = a + b · log<sub>2</sub>(n + 1)', { left: '760px', width: '1050px', top: '290px', fontSize: '66px' });
      v.r1 = h('div', 'frow', 'Raskin: a = 50 ms, b = 150 ms', { left: '760px', width: '1050px', top: '430px', fontSize: '40px' });
      v.r2 = h('div', 'frow', 'n = 7 → 50 + 150 · log<sub>2</sub>(8) = 50 + 450 = <b style="color:#fbbf24">500 ms</b>', { left: '760px', width: '1050px', top: '520px', fontSize: '38px' });
      v.r3 = h('div', 'frow', 'double the choices → only ONE more 150 ms step', { left: '760px', width: '1050px', top: '610px', fontSize: '36px', color: '#34d399' });
      [v.f, v.r1, v.r2, v.r3].forEach((e) => root.appendChild(e));
    },
    anim(v, t, ctx) {
      const b = v.beats;
      v.items.forEach((e, i) => reveal(e, t, at(ctx, b[0]) + i * 0.12));
      const sc = (t - at(ctx, b[0]) - 1.2) / 0.35; const k = Math.floor(sc) % 8;
      v.items.forEach((e, i) => (e.style.background = sc > 0 && i === k ? 'rgba(251,191,36,.25)' : ''));
      reveal(v.f, t, at(ctx, b[1])); reveal(v.r1, t, at(ctx, b[2])); reveal(v.r2, t, at(ctx, b[3])); reveal(v.r3, t, at(ctx, b[4]));
    },
  };

  // CPM-GOMS PERT chart
  custom.pert = {
    build(root, v) {
      const sv = svg('svg', { width: 1920, height: 1080, class: 'abs', style: 'left:0;top:0' }, root); defs(sv);
      const rows = [['Perceptual (visual)', 330, '#38bdf8'], ['Cognitive', 480, '#a78bfa'], ['Motor (eyes)', 630, '#f472b6'], ['Motor (hands)', 760, '#f472b6']];
      v.lanes = rows.map(([n, y, c]) => { svg('line', { x1: 480, y1: y, x2: 1800, y2: y, stroke: '#334155', 'stroke-width': 3, 'stroke-dasharray': '10 10' }, sv); const e = h('div', 'lane', n, { top: y - 22 + 'px', color: c }); root.appendChild(e); return e; });
      const B = (x, y, txt, c) => { const e = h('div', 'pbox', txt, { left: x + 'px', top: y - 36 + 'px', borderColor: c }); root.appendChild(e); return e; };
      v.bx = [B(560, 480, 'start eye move', '#a78bfa'), B(860, 630, 'move eyes to target', '#f472b6'), B(1180, 330, 'perceive target', '#38bdf8'), B(1480, 480, 'verify paragraph', '#a78bfa')];
      const P = (x1, y1, x2, y2) => svg('line', { x1, y1, x2, y2, stroke: '#fbbf24', 'stroke-width': 5, 'marker-end': 'url(#ah)' }, sv);
      v.ln = [P(800, 495, 870, 600), P(1100, 600, 1190, 362), P(1420, 362, 1490, 455)];
    },
    anim(v, t, ctx) {
      const b = v.beats; v.lanes.forEach((e, i) => reveal(e, t, at(ctx, b[0]) + i * 0.2));
      v.bx.forEach((e, i) => reveal(e, t, at(ctx, b[1]) + i * 0.7));
      v.ln.forEach((e, i) => (e.style.opacity = seg(t, at(ctx, b[1]) + i * 0.7 + 0.5, at(ctx, b[1]) + i * 0.7 + 0.9)));
      const g = pulse(t, at(ctx, b[2]), at(ctx, b[2]) + 3); v.ln.forEach((e) => e.setAttribute('stroke-width', 5 + 6 * g));
    },
  };

  // State transition network
  custom.stn = {
    build(root, v) {
      const sv = svg('svg', { width: 1920, height: 1080, class: 'abs', style: 'left:0;top:0' }, root); defs(sv);
      const N = { start: [200, 560, 'Start'], s1: [460, 560, 'Menu'], s2: [820, 400, 'File list'], s3: [1180, 400, 'Preview'], f1: [1520, 400, 'Finish'], s2b: [820, 720, 'Settings'], s3b: [1180, 720, 'Confirm'], f2: [1520, 720, 'Finish'] };
      v.nodes = {}; for (const k in N) { const [x, y, l] = N[k]; const g = svg('g', {}, sv); svg('circle', { cx: x, cy: y, r: k.startsWith('f') || k === 'start' ? 62 : 82, fill: '#111a33', stroke: k.startsWith('f') ? '#34d399' : '#38bdf8', 'stroke-width': 5 }, g); const tx = svg('text', { x, y: y + 10, 'text-anchor': 'middle', fill: '#e8edf7', 'font-size': 28, 'font-weight': 700, 'font-family': 'Inter' }, g); tx.textContent = l; v.nodes[k] = g; }
      const E = (a, b, lab, curve) => { const [x1, y1] = N[a], [x2, y2] = N[b]; const g = svg('g', {}, sv); const ang = Math.atan2(y2 - y1, x2 - x1); const r1 = a === 'start' ? 64 : 84, r2 = b.startsWith('f') ? 70 : 90;
        const p = curve ? `M${x1},${y1 + r1} C${x1},${y1 + 200} ${x2},${y2 + 200} ${x2},${y2 + r2}` : `M${x1 + Math.cos(ang) * r1},${y1 + Math.sin(ang) * r1} L${x2 - Math.cos(ang) * r2},${y2 - Math.sin(ang) * r2}`;
        svg('path', { d: p, fill: 'none', stroke: '#94a3b8', 'stroke-width': 4, 'marker-end': 'url(#ah)' }, g);
        const tx = svg('text', { x: curve ? (x1 + x2) / 2 : (x1 + x2) / 2, y: curve ? y1 + 170 : (y1 + y2) / 2 - 18, 'text-anchor': 'middle', fill: '#fbbf24', 'font-size': 24, 'font-family': 'JetBrains Mono' }, g); tx.textContent = lab; return g; };
      v.edges = [E('start', 's1', 'open'), E('s1', 's2', 'click File'), E('s2', 's3', 'select'), E('s3', 'f1', 'OK'), E('s1', 's2b', 'click Tools'), E('s2b', 's3b', 'change'), E('s3b', 'f2', 'Apply'), E('s3b', 's2b', 'edit again ↺', true)];
    },
    anim(v, t, ctx) {
      const b = v.beats; const ord = ['start', 's1', 's2', 's3', 'f1', 's2b', 's3b', 'f2'];
      ord.forEach((k, i) => (v.nodes[k].style.opacity = seg(t, at(ctx, b[i < 5 ? 0 : 1]) + (i % 5) * 0.4, at(ctx, b[i < 5 ? 0 : 1]) + (i % 5) * 0.4 + 0.4)));
      v.edges.forEach((e, i) => (e.style.opacity = seg(t, at(ctx, b[i < 4 ? 0 : i < 7 ? 1 : 2]) + (i % 4) * 0.4 + 0.3, at(ctx, b[i < 4 ? 0 : i < 7 ? 1 : 2]) + (i % 4) * 0.4 + 0.7)));
    },
  };

  // Buxton Three-State Model
  custom.tsm = {
    build(root, v) {
      const sv = svg('svg', { width: 1920, height: 1080, class: 'abs', style: 'left:0;top:0' }, root); defs(sv);
      const S = [[360, 560, 'State 0', 'Out of range', 'disengaged', '#94a3b8'], [960, 560, 'State 1', 'Tracking', 'cursor follows', '#38bdf8'], [1560, 560, 'State 2', 'Dragging', 'button held', '#f472b6']];
      v.st = S.map(([x, y, a, bb, c, cc]) => { const g = svg('g', {}, sv); svg('circle', { cx: x, cy: y, r: 150, fill: '#111a33', stroke: cc, 'stroke-width': 7 }, g);
        [[a, -40, 30, '#8b97b0'], [bb, 10, 44, cc], [c, 56, 26, '#e8edf7']].forEach(([s, dy, fs, f]) => { const tx = svg('text', { x, y: y + dy, 'text-anchor': 'middle', fill: f, 'font-size': fs, 'font-weight': 700, 'font-family': 'Inter' }, g); tx.textContent = s; }); return g; });
      const A = (x1, x2, y, lab) => { const g = svg('g', {}, sv); svg('line', { x1, y1: y, x2, y2: y, stroke: '#e8edf7', 'stroke-width': 5, 'marker-end': 'url(#ah)' }, g); const tx = svg('text', { x: (x1 + x2) / 2, y: y - 16, 'text-anchor': 'middle', fill: '#fbbf24', 'font-size': 26, 'font-family': 'JetBrains Mono' }, g); tx.textContent = lab; return g; };
      v.ar = [A(1120, 1400, 520, 'button down'), A(1400, 1120, 620, 'button up'), A(520, 800, 520, 'touch / pen down'), A(800, 520, 620, 'lift')];
      v.ar[3].querySelector('text').setAttribute('y', 660); v.ar[1].querySelector('text').setAttribute('y', 660);
      v.lab = [h('div', 'tag', '🖱️ Mouse: lives in 1 ⇄ 2 (lift it → disengaged move)', { left: '520px', top: '800px', width: '900px', textAlign: 'center' }), h('div', 'tag', '✍️ Light pen / finger on touch-screen: 0 ⇄ 1, re-engages anywhere', { left: '420px', top: '268px', width: '1100px', textAlign: 'center' })];
      v.lab.forEach((e) => root.appendChild(e));
    },
    anim(v, t, ctx) {
      const b = v.beats;
      [1, 2, 0].forEach((k, i) => (v.st[k].style.opacity = seg(t, at(ctx, b[i]), at(ctx, b[i]) + 0.5)));
      v.ar[0].style.opacity = v.ar[1].style.opacity = seg(t, at(ctx, b[1]) + 0.4, at(ctx, b[1]) + 0.9);
      v.ar[2].style.opacity = v.ar[3].style.opacity = seg(t, at(ctx, b[2]) + 0.4, at(ctx, b[2]) + 0.9);
      reveal(v.lab[0], t, at(ctx, b[3])); reveal(v.lab[1], t, at(ctx, b[3]) + 0.8);
    },
  };

  // V-model
  custom.vmodel = {
    build(root, v) {
      const sv = svg('svg', { width: 1920, height: 1080, class: 'abs', style: 'left:0;top:0' }, root); defs(sv);
      const L = ['Client Needs', 'Requirements', 'Functional Specs', 'Technical Specs'], R = ['UAT', 'System Testing', 'Integration Testing', 'Unit Testing'];
      v.l = L.map((n, i) => box(root, 150 + i * 100, 270 + i * 150, 380, 100, `<div class="ch" style="font-size:32px">${n}</div>`, '#94a3b8'));
      v.r = R.map((n, i) => box(root, 1390 - i * 100, 270 + i * 150, 380, 100, `<div class="ch" style="font-size:32px;color:${i ? '#38bdf8' : '#fb923c'}">${n}</div>`, i ? '#38bdf8' : '#fb923c'));
      v.ln = L.map((_, i) => svg('line', { x1: 540 + i * 100, y1: 320 + i * 150, x2: 1380 - i * 100, y2: 320 + i * 150, stroke: '#64748b', 'stroke-width': 4, 'stroke-dasharray': '12 10', 'marker-end': 'url(#ah)' }, sv));
    },
    anim(v, t, ctx) {
      const b = v.beats;
      v.l.forEach((e, i) => reveal(e, t, at(ctx, b[0]) + i * 0.4));
      v.r.slice().reverse().forEach((e, i) => reveal(e, t, at(ctx, b[1]) + i * 0.4));
      v.ln.forEach((e, i) => (e.style.opacity = seg(t, at(ctx, b[2]) + i * 0.3, at(ctx, b[2]) + i * 0.3 + 0.4)));
      v.r[0].style.boxShadow = `0 0 ${60 * pulse(t, at(ctx, b[3]), at(ctx, b[3]) + 3)}px #fb923c`;
      v.l[0].style.boxShadow = `0 0 ${60 * pulse(t, at(ctx, b[3]), at(ctx, b[3]) + 3)}px #fb923c`;
    },
  };

  // Window layout strategies: mini screens
  custom.winlayouts = {
    build(root, v) {
      const kinds = v.kinds, n = kinds.length, cols = v.cols || 3, rows = Math.ceil(n / cols), gx = 40, lab = 70;
      const W = (X1 - X0 - gx * (cols - 1)) / cols, H = Math.min(W * 0.56, (Y1 - Y0 - rows * lab) / rows);
      v.cells = kinds.map((k, i) => {
        const r = Math.floor(i / cols), inRow = Math.min(cols, n - r * cols), xo = (cols - inRow) * (W + gx) / 2;
        const x = X0 + xo + (i % cols) * (W + gx), y = Y0 + r * (H + lab);
        const scr = h('div', 'mini', '', { left: x + 'px', top: y + 'px', width: W + 'px', height: H + 'px' });
        const lb = h('div', 'minil', k.n, { left: x + 'px', top: y + H + 8 + 'px', width: W + 'px' });
        root.appendChild(scr); root.appendChild(lb);
        const wins = k.w.map((r2, j) => { const e = h('div', 'mw', k.l ? `<span>${k.l[j] || ''}</span>` : '', { background: Object.values(COL)[j % 6] + '33', borderColor: Object.values(COL)[j % 6] }); scr.appendChild(e); return e; });
        return { scr, lb, wins, k, W: W - 8, H: H - 8 };
      });
    },
    anim(v, t, ctx) {
      v.cells.forEach((c, i) => {
        const s = at(ctx, c.k.at); reveal(c.scr, t, s); reveal(c.lb, t, s);
        const live = Math.max(0, t - s);
        c.wins.forEach((e, j) => {
          const p = seg(t, s + 0.2 + j * 0.15, s + 0.8 + j * 0.15, ease.out);
          let [x, y, w, hh] = c.k.w[j];
          if (c.k.anim === 'flip') { const k = Math.floor(live / 0.9) % c.wins.length; e.style.zIndex = j === k ? 9 : 1; e.style.opacity = j === k ? 1 : 0.25 * p; }
          else e.style.opacity = p;
          if (c.k.anim === 'zoom' && j === 0) { const z = 0.5 - 0.5 * Math.cos(live * 1.4); x = x * (1 - z); y = y * (1 - z); w = w + (100 - w) * z; hh = hh + (100 - hh) * z; e.style.zIndex = 9; }
          Object.assign(e.style, { left: x * c.W / 100 + 'px', top: y * c.H / 100 + 'px', width: w * c.W / 100 + 'px', height: hh * c.H / 100 + 'px', transform: `translateY(${(1 - p) * -20}px)` });
        });
        spot(c.scr, t, ctx, v.kinds, i, '#38bdf8');
      });
    },
  };

  // overview + detail with field-of-view box
  custom.overview = {
    build(root, v) {
      v.ov = h('div', 'mapv', '', { left: '150px', top: '300px', width: '520px', height: '390px' });
      v.dt = h('div', 'mapv', '', { left: '760px', top: '260px', width: '1000px', height: '560px', overflow: 'hidden' });
      v.inner = h('div', 'mapbg', '', { width: '520px', height: '390px', transformOrigin: '0 0' }); v.dt.appendChild(v.inner);
      v.ov.appendChild(h('div', 'mapbg', '', { width: '520px', height: '390px' }));
      v.fov = h('div', 'fov'); v.ov.appendChild(v.fov);
      v.l1 = h('div', 'minil', 'Overview + field-of-view box', { left: '150px', top: '700px', width: '520px' });
      v.l2 = h('div', 'minil', 'Detail view (same aspect ratio)', { left: '760px', top: '830px', width: '1000px' });
      v.zf = h('div', 'tag', 'zoom factor 5 to 30 ✔  · above 30 → add an intermediate view', { left: '150px', top: '760px', width: '560px' });
      [v.ov, v.dt, v.l1, v.l2, v.zf].forEach((e) => root.appendChild(e));
    },
    anim(v, t, ctx) {
      const b = v.beats; reveal(v.ov, t, at(ctx, b[0])); reveal(v.l1, t, at(ctx, b[0])); reveal(v.dt, t, at(ctx, b[0]) + 0.4); reveal(v.l2, t, at(ctx, b[0]) + 0.4);
      const z = 520 / 104; // fov 104x58.5 → zoom ~5
      const m = Math.max(0, t - at(ctx, b[1]));
      const fx = 20 + 300 * (0.5 - 0.5 * Math.cos(m * 0.5)), fy = 20 + 250 * (0.5 - 0.5 * Math.cos(m * 0.33));
      css(v.fov, { left: fx + 'px', top: fy + 'px', width: '180px', height: '101px' });
      css(v.inner, { s: z * 1.92, x: -fx * z * 1.92, y: -fy * z * 1.92 });
      v.inner.style.transform = `scale(${1000 / 180}) translate(${-fx}px,${-fy}px)`;
      reveal(v.zf, t, at(ctx, b[2]));
    },
  };

  // Elastic windows
  custom.elastic = {
    build(root, v) {
      v.box = h('div', 'mini', '', { left: '360px', top: '260px', width: '1200px', height: '600px' }); root.appendChild(v.box);
      v.names = ['Teacher role', 'Researcher role', 'Parent role'];
      v.w = v.names.map((n, i) => { const e = h('div', 'mw ew', `<b>${n}</b><span>vision · people · tasks · schedule</span>`, { borderColor: Object.values(COL)[i], background: Object.values(COL)[i] + '22' }); v.box.appendChild(e); return e; });
    },
    anim(v, t, ctx) {
      const b = v.beats; reveal(v.box, t, at(ctx, b[0]));
      const s = at(ctx, b[1]); const ph = Math.max(0, t - s) / 2.5; const k = Math.floor(ph) % 3, f = seg(ph % 1, 0, 0.4);
      const prev = (k + 2) % 3;
      const big = t < s ? -1 : k;
      const wts = v.w.map((_, i) => (big < 0 ? 1 : i === k ? lerp(1, 4, f) + (i === prev ? 0 : 0) : i === prev ? lerp(4, 1, f) : 1));
      const sum = wts.reduce((a, c) => a + c, 0); let x = 0;
      v.w.forEach((e, i) => { const w = (1200 - 16) * wts[i] / sum; css(e, { left: 8 + x + 'px', top: '8px', width: w - 8 + 'px', height: '584px' }); x += w; });
    },
  };

  // Moore's law vs UI
  custom.moore = {
    build(root, v) {
      const sv = svg('svg', { width: 1920, height: 1080, class: 'abs', style: 'left:0;top:0' }, root);
      const data = [['now', 1], ['5 yrs', 10], ['10 yrs', 100], ['20 yrs', 10000]];
      v.bars = data.map(([l, val], i) => { const x = 220 + i * 260, hh = 120 * Math.log10(val) + 20; const r = svg('rect', { x, y: 820 - hh, width: 170, height: hh, rx: 10, fill: '#38bdf8' }, sv); const e = h('div', 'axl', `${l}<br><b style="color:#38bdf8;font-size:40px">${val.toLocaleString()}×</b>`, { left: x - 20 + 'px', top: 820 - hh - 110 + 'px', width: '210px', textAlign: 'center' }); root.appendChild(e); return [r, e, hh]; });
      v.ui = svg('rect', { x: 1320, y: 780, width: 400, height: 40, rx: 10, fill: '#f472b6' }, sv);
      v.uil = h('div', 'axl', 'User interfaces<br><b style="color:#f472b6;font-size:40px">no Moore\'s Law!</b>', { left: '1320px', top: '640px', width: '400px', textAlign: 'center' }); root.appendChild(v.uil);
      v.cap = h('div', 'tag', 'Hardware (log scale)', { left: '220px', top: '850px' }); root.appendChild(v.cap);
    },
    anim(v, t, ctx) {
      const b = v.beats;
      v.bars.forEach(([r, e, hh], i) => { const p = seg(t, at(ctx, b[0]) + i * 0.6, at(ctx, b[0]) + i * 0.6 + 0.7); r.setAttribute('height', hh * p); r.setAttribute('y', 820 - hh * p); e.style.opacity = p; });
      v.cap.style.opacity = seg(t, at(ctx, b[0]), at(ctx, b[0]) + 0.5);
      const q = seg(t, at(ctx, b[1]), at(ctx, b[1]) + 0.6); v.ui.style.opacity = q; v.uil.style.opacity = q;
    },
  };

  // PUI: human ↔ computer
  custom.pui = {
    build(root, v) {
      v.hm = h('div', 'bigic', '🧍', { left: '170px', top: '400px' }); v.pc = h('div', 'bigic', '💻', { left: '1560px', top: '400px' });
      v.mid = box(root, 640, 380, 640, 330, '<div class="ch" style="font-size:30px;color:#fbbf24;line-height:1.5">Sensing / perception · Cognitive skills<br>Social skills · Social conventions<br>Shared knowledge · Adaptation</div>', COL.y);
      v.tags = ['vision', 'speech', 'haptics', 'graphics', 'user modelling', 'learning', 'taste ?', 'smell ?'].map((s, i) => { const e = h('span', 'chip', s, { position: 'absolute', left: 300 + (i % 4) * 340 + 'px', top: (i < 4 ? 270 : 780) + 'px', borderColor: col(null, i), color: col(null, i) }); root.appendChild(e); return e; });
      root.appendChild(v.hm); root.appendChild(v.pc);
      v.arr = h('div', 'dblar', '⟵ natural two-way communication ⟶', { left: '560px', top: '730px', width: '800px' }); root.appendChild(v.arr);
    },
    anim(v, t, ctx) {
      const b = v.beats; reveal(v.hm, t, at(ctx, b[0])); reveal(v.pc, t, at(ctx, b[0]) + 0.3); reveal(v.mid, t, at(ctx, b[1])); reveal(v.arr, t, at(ctx, b[1]) + 0.5);
      v.tags.forEach((e, i) => reveal(e, t, at(ctx, b[2]) + i * 0.2));
    },
  };

  // ---------------- build everything ----------------
  const spec = window.SPEC;
  stage.innerHTML = '';
  spec.scenes.forEach((sc, si) => {
    const root = h('section', 'fv-scene'); root.dataset.scene = sc.id; stage.appendChild(root);
    const v = sc.viz || { type: 'hook', t: sc.title };
    if (v.type !== 'hook') {
      root.appendChild(h('div', 'kicker', spec.kicker));
      root.appendChild(h('div', 'title', sc.title.replace(/^\d+\.\s*/, '')));
      root.appendChild(h('div', 'prog', `${si + 1} / ${spec.scenes.length}`));
    }
    if (v.type === 'custom') custom[v.name].build(root, v); else builders[v.type](root, v);
    addNote(root, v);
    root.querySelectorAll('svg').forEach((sv) => { const mk = sv.querySelector('marker'); if (mk) sv.querySelectorAll('[marker-end]').forEach((e) => e.setAttribute('marker-end', `url(#${mk.id})`)); });
    if (v.endcard) { v._end = h('div', 'fv-endcard'); root.appendChild(v._end); }
    FV.scene(sc.id, (t, ctx) => {
      FV.$$('.kicker,.title,.prog', ctx.el).forEach((e, i) => reveal(e, t, 0.05 + i * 0.1, 16));
      if (v.type === 'custom') custom[v.name].anim(v, t, ctx); else anim[v.type](v, t, ctx);
      animNote(v, t, ctx);
      if (v._end) reveal(v._end, t, at(ctx, v.endAt != null ? v.endAt : ctx.lines.length - 1));
    });
  });
})();
