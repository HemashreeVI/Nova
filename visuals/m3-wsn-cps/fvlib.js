/* Shared helpers for the exam-revision explainers (pure functions of t). */
(function () {
  const { seg, enter, ease, lerp } = FV;
  const NS = 'http://www.w3.org/2000/svg';
  const COL = { a: '#38bdf8', b: '#34d399', c: '#fbbf24', d: '#f87171', e: '#a78bfa', f: '#f472b6', g: '#fb923c', mut: '#8b97b0', ink: '#e8edf7' };
  const at = (ctx, l, f = 0) => ctx.line(l) + f * (ctx.lineEnd(l) - ctx.line(l));
  function mk(tag, attrs, parent, text) {
    const e = document.createElementNS(NS, tag);
    for (const k in attrs) e.setAttribute(k, attrs[k]);
    if (text !== undefined) e.textContent = text;
    if (parent) parent.appendChild(e);
    return e;
  }
  /* data-l="line" [data-f="fraction"] → fade/rise in; data-hl="l1,l2" → glow while spoken */
  function reveal(t, ctx) {
    ctx.el.querySelectorAll('[data-l]').forEach((e) => enter(e, t, at(ctx, +e.dataset.l, +(e.dataset.f || 0)), 0.5, 20));
    ctx.el.querySelectorAll('[data-hl]').forEach((e) => {
      const on = e.dataset.hl.split(',').some((l) => t >= ctx.line(+l) && t < ctx.lineEnd(+l) + 0.2);
      e.classList.toggle('hl', on);
    });
    enter(ctx.el.querySelector('.kicker'), t, 0.05);
    enter(ctx.el.querySelector('.title'), t, 0.15);
  }
  /* arrow that draws itself: returns update(t, start, dur) */
  function arrow(svg, x1, y1, x2, y2, color, opts = {}) {
    const g = mk('g', {}, svg);
    const ln = mk('line', { x1, y1, x2: x1, y2: y1, stroke: color, 'stroke-width': opts.w || 4, 'stroke-dasharray': opts.dash || 'none' }, g);
    const head = mk('polygon', { points: '0,0 -20,-9 -20,9', fill: color }, g);
    const lab = opts.label ? mk('text', { x: opts.lx !== undefined ? opts.lx : (x1 + x2) / 2, y: opts.ly !== undefined ? opts.ly : Math.min(y1, y2) - 12, 'text-anchor': 'middle', fill: opts.lc || color, 'font-size': opts.fs || 24, 'font-weight': 700 }, g, opts.label) : null;
    const ang = Math.atan2(y2 - y1, x2 - x1) * 180 / Math.PI;
    return (t, s, d = 0.7) => {
      const p = seg(t, s, s + d, ease.inOut);
      const ex = lerp(x1, x2, p), ey = lerp(y1, y2, p);
      ln.setAttribute('x2', ex); ln.setAttribute('y2', ey);
      head.setAttribute('transform', `translate(${ex},${ey}) rotate(${ang})`);
      g.style.opacity = p > 0 ? 1 : 0;
      if (lab) lab.style.opacity = seg(t, s + 0.2, s + 0.6);
      return p;
    };
  }
  /* a dot travelling along a path, looping, from time s */
  function traveller(svg, d, color, r = 11) {
    const p = mk('path', { d, fill: 'none', stroke: 'none' }, svg);
    const c = mk('circle', { r, fill: color }, svg);
    const len = () => p.getTotalLength();
    return (t, s, period = 1.6, offset = 0) => {
      if (t < s) { c.style.opacity = 0; return; }
      const q = (((t - s) / period) + offset) % 1;
      const pt = p.getPointAtLength(q * len());
      c.setAttribute('cx', pt.x); c.setAttribute('cy', pt.y);
      c.style.opacity = Math.min(1, Math.min(q, 1 - q) * 8);
    };
  }
  /* sequence diagram: rows [{dir:'>'|'<', y, label, c, l, f}] */
  function seq(svg, o) {
    const cx = o.cx, sx = o.sx, top = o.top || 280, bot = o.bot || 880, bw = o.bw || 180;
    const life = mk('g', {}, svg);
    [[cx, o.cl || 'Client', o.cc || COL.a], [sx, o.sl || 'Server', o.sc || COL.c]].forEach(([x, name, c]) => {
      mk('rect', { x: x - bw / 2, y: top - 58, width: bw, height: 50, rx: 12, fill: 'rgba(13,20,42,.9)', stroke: c, 'stroke-width': 2 }, life);
      mk('text', { x, y: top - 24, 'text-anchor': 'middle', fill: '#e8edf7', 'font-size': 26, 'font-weight': 700 }, life, name);
      mk('line', { x1: x, y1: top, x2: x, y2: bot, stroke: c, 'stroke-opacity': 0.6, 'stroke-width': 4 }, life);
    });
    const rows = o.rows.map((r) => {
      const fromX = r.dir === '>' ? cx : sx, toX = r.dir === '>' ? sx : cx;
      return { r, up: arrow(svg, fromX + (r.dir === '>' ? 4 : -4), r.y, toX + (r.dir === '>' ? -4 : 4), r.y + (r.dy || 14), COL[r.c || 'a'], { label: r.label, fs: r.fs || 25, lc: r.lc }) };
    });
    return (t, ctx) => {
      life.style.opacity = seg(t, 0.2, 0.8);
      rows.forEach((q) => q.up(t, at(ctx, q.r.l, q.r.f || 0), q.r.d || 0.8));
    };
  }
  window.L = { COL, at, mk, reveal, arrow, traveller, seq };
})();
