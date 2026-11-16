/*
 * lesson.js — data-driven animated lesson scenes for full-visual.
 * window.LESSON = { scenes: [{ id, kicker, title, tip:{t,at}, viz:{type,...} }] }
 * Every visual is a pure function of t; item timing uses `at` = narration line index
 * (fractions allowed: 2.5 = halfway through line 2).
 */
(function () {
  'use strict';
  const { seg, css, ease, clamp, lerp } = FV;
  const PAL = { c1: '#38bdf8', c2: '#a78bfa', c3: '#fbbf24', c4: '#f472b6', c5: '#34d399', c6: '#fb923c', c7: '#f87171', c8: '#94a3b8', c9: '#60a5fa' };
  const C = (c) => PAL[c] || c || PAL.c1;
  const AX = 100, AY = 236, AW = 1720, AH = 640; // content area
  const md = (s) => String(s == null ? '' : s)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;')
    .replace(/\*\*(.+?)\*\*/g, '<b>$1</b>')
    .replace(/__(.+?)__/g, '<mark>$1</mark>')
    .replace(/\^(\w+)/g, '<sup>$1</sup>')
    .replace(/\n/g, '<br>');
  function el(tag, cls, html, parent, style) {
    const e = document.createElement(tag);
    if (cls) e.className = cls;
    if (html != null) e.innerHTML = html;
    if (style) Object.assign(e.style, style);
    if (parent) parent.appendChild(e);
    return e;
  }
  const SVGNS = 'http://www.w3.org/2000/svg';
  function sv(tag, attrs, parent) {
    const e = document.createElementNS(SVGNS, tag);
    for (const k in attrs) e.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(e);
    return e;
  }
  function fit(box, min = 15) {
    let fs = parseFloat(getComputedStyle(box).fontSize);
    let guard = 60;
    while ((box.scrollHeight > box.clientHeight + 1 || box.scrollWidth > box.clientWidth + 1) && fs > min && guard--) {
      fs -= 1; box.style.fontSize = fs + 'px';
    }
  }
  function fitEach(nodes, min) { nodes.forEach((n) => fit(n, min)); }
  // equalize font size across siblings (smallest wins) for a tidy look
  function fitUniform(nodes, min) {
    fitEach(nodes, min);
    const m = Math.min(...nodes.map((n) => parseFloat(n.style.fontSize || getComputedStyle(n).fontSize)));
    nodes.forEach((n) => (n.style.fontSize = m + 'px'));
  }

  const css0 = document.createElement('style');
  css0.textContent = `
  #fv-stage{background:radial-gradient(1300px 900px at 75% 12%,#14204a 0%,#0a1024 45%,#060a14 78%);color:#e8edf7;font-family:Inter,system-ui,sans-serif}
  #fv-stage b{color:#fff;font-weight:700}
  #fv-stage mark{background:none;color:#fbbf24;font-weight:700}
  .L-kick{position:absolute;left:100px;top:62px;font:700 23px/1 'JetBrains Mono',monospace;letter-spacing:.14em;text-transform:uppercase;color:#38bdf8}
  .L-title{position:absolute;left:100px;top:100px;width:1180px;font:800 58px/1.08 Inter;letter-spacing:-.02em}
  .L-title.wide{width:1720px}
  .L-tip{position:absolute;right:100px;top:70px;max-width:520px;padding:14px 22px;border-radius:16px;background:rgba(251,191,36,.12);border:2px solid rgba(251,191,36,.7);font:600 24px/1.3 Inter;color:#fde68a}
  .L-tip:before{content:"EXAM TIP";display:block;font:800 16px/1 'JetBrains Mono';letter-spacing:.18em;color:#fbbf24;margin-bottom:8px}
  .L-area{position:absolute;left:${AX}px;top:${AY}px;width:${AW}px;height:${AH}px}
  .L-dots{position:absolute;inset:0;pointer-events:none}
  .L-card{position:relative;box-sizing:border-box;border-radius:22px;padding:20px 26px;background:rgba(255,255,255,.045);border:2px solid rgba(255,255,255,.10);overflow:hidden;font-size:31px;line-height:1.3}
  .L-card .ic{font-size:46px;line-height:1;margin-bottom:8px}
  .L-card.row{display:flex;gap:22px;align-items:flex-start}
  .L-card.row .ic{margin:2px 0 0}
  .L-card .hd{font-weight:800;font-size:1.18em;margin-bottom:6px;line-height:1.15}
  .L-card .bd{color:#c9d3e6}
  .L-grid{position:absolute;inset:0;display:grid;gap:22px}
  .L-hero{position:absolute;left:0;right:0;text-align:center}
  .L-chip{display:inline-block;padding:12px 24px;margin:8px;border-radius:999px;border:2px solid;font:700 28px/1 Inter}
  .L-tbl{border-collapse:separate;border-spacing:0 8px;width:100%;font-size:27px}
  .L-tbl th{text-align:left;font:800 0.9em Inter;color:#8b97b0;text-transform:uppercase;letter-spacing:.06em;padding:4px 18px}
  .L-tbl td{padding:12px 18px;background:rgba(255,255,255,.045);vertical-align:top;line-height:1.28}
  .L-tbl td:first-child{border-radius:14px 0 0 14px;font-weight:800}
  .L-tbl td:last-child{border-radius:0 14px 14px 0}
  .L-node{position:absolute;text-align:center}
  .L-node .circ{width:118px;height:118px;margin:0 auto;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:60px;background:#111a33;border:3px solid}
  .L-node .lb{font:800 26px/1.15 Inter;margin-top:12px}
  .L-node .sb{font:500 21px/1.2 Inter;color:#9fb0cc;margin-top:4px}
  .L-steps{position:absolute;display:flex;flex-direction:column;gap:10px}
  .L-step{display:flex;gap:.6em;align-items:center;padding:.4em .75em;border-radius:16px;background:rgba(255,255,255,.04);border:2px solid rgba(255,255,255,.08);font-size:27px;line-height:1.28}
  .L-step .n{flex:none;width:1.55em;height:1.55em;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:.85em;color:#0a1024}
  .L-layer{position:absolute;box-sizing:border-box;border-radius:14px;display:flex;align-items:center;justify-content:center;text-align:center;font:700 29px/1.15 Inter;border:2px solid}
  .L-fld{position:absolute;box-sizing:border-box;border:2px solid;border-radius:10px;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;font:700 22px/1.15 Inter;padding:4px}
  .L-fld .sz{position:absolute;top:-30px;left:0;right:0;font:600 19px 'JetBrains Mono';color:#9fb0cc}
  .L-lbl{position:absolute;font:600 22px/1.2 Inter;color:#c9d3e6}
  .L-mono{font-family:'JetBrains Mono',monospace}
  .L-calc{position:absolute;font:600 34px/1.35 'JetBrains Mono';white-space:pre}
  .L-ans{padding:10px 22px;border-radius:14px;border:3px solid #34d399;background:rgba(52,211,153,.12);color:#a7f3d0;display:inline-block}
  .L-var{position:absolute;width:250px;height:150px;border-radius:20px;background:rgba(255,255,255,.05);border:2px solid rgba(255,255,255,.15);text-align:center}
  .L-var .k{font:800 26px 'JetBrains Mono';color:#9fb0cc;margin-top:16px}
  .L-var .v{font:800 70px/1.1 'JetBrains Mono'}
  .L-tier{position:absolute;left:0;width:100%;border-radius:20px;box-sizing:border-box;border:2px solid}
  .L-tier .nm{position:absolute;left:28px;top:50%;transform:translateY(-50%);font:800 32px/1.1 Inter}
  .L-tier .ds{display:block;font:600 22px Inter;color:#c9d3e6;margin-top:6px}
  `;
  document.head.appendChild(css0);

  /* ---------- timing helpers bound per scene ---------- */
  function mkA(ctx) {
    const at = (i) => {
      if (i == null) return 0;
      if (i < 0) return 0;
      const k = Math.floor(i), f = i - k;
      if (k >= ctx.lines.length) return ctx.dur;
      return ctx.line(k) + f * (ctx.lineEnd(k) - ctx.line(k));
    };
    const end = (i) => { const k = Math.floor(i); return k >= ctx.lines.length ? ctx.dur : ctx.lineEnd(k); };
    const show = (t, i, d = 0.55) => seg(t, at(i) - 0.15, at(i) - 0.15 + d, ease.out);
    // highlight weight while between at(i) and at(j)
    const win = (t, i, j) => {
      const a = at(i), b = j == null ? ctx.dur + 1 : at(j);
      return seg(t, a - 0.15, a + 0.25) * (1 - seg(t, b - 0.15, b + 0.25));
    };
    return { at, end, show, win };
  }
  // next distinct `at` after item k in a list (for highlight windows)
  function nextAt(list, k) {
    const a = list[k].at ?? 0;
    for (let j = k + 1; j < list.length; j++) if ((list[j].at ?? 0) > a) return list[j].at;
    return null;
  }
  function hlStyle(e, w, color, base = 0.045) {
    e.style.borderColor = w > 0.01 ? color : 'rgba(255,255,255,.10)';
    e.style.boxShadow = w > 0.01 ? `0 0 ${40 * w}px ${color}55, inset 0 0 0 ${w * 1}px ${color}` : 'none';
    e.style.background = `rgba(255,255,255,${base + 0.05 * w})`;
  }

  /* ---------- viz builders: (area, viz, scene) -> update(t, A, ctx) ---------- */
  const V = {};

  V.hero = (area, v) => {
    const big = el('div', 'L-hero', md(v.big), area, { top: (v.y ?? 150) + 'px', font: `800 ${v.size || 104}px/1.06 Inter`, letterSpacing: '-.03em' });
    const sub = v.sub ? el('div', 'L-hero', md(v.sub), area, { top: (v.subY ?? 360) + 'px', font: '500 40px/1.3 Inter', color: '#9fb0cc', padding: '0 120px' }) : null;
    const icon = v.icon ? el('div', 'L-hero', v.icon, area, { top: '-40px', fontSize: '130px' }) : null;
    const chipBox = el('div', 'L-hero', '', area, { top: (v.chipY ?? 470) + 'px', padding: '0 80px' });
    const chips = (v.chips || []).map((c) => el('span', 'L-chip', md(c.t), chipBox, { borderColor: C(c.c), color: C(c.c) }));
    return (t, A) => {
      FV.enter(big, t, A.at(v.bigAt ?? 0) - 0.3, 0.8, 40);
      if (icon) { const p = seg(t, 0, 0.8, ease.back); css(icon, { o: p, s: 0.6 + 0.4 * p, y: Math.sin(t * 1.6) * 8 }); }
      if (sub) FV.enter(sub, t, A.at(v.subAt ?? 0) + 0.2);
      chips.forEach((c, i) => { const p = A.show(t, v.chips[i].at ?? 0); css(c, { o: p, s: 0.8 + 0.2 * ease.back(p) }); });
    };
  };

  V.cards = (area, v) => {
    const n = v.items.length;
    const cols = v.cols || (n <= 3 ? n : n === 4 ? 2 : 3);
    const g = el('div', 'L-grid', null, area, { gridTemplateColumns: `repeat(${cols},1fr)`, gridAutoRows: '1fr' });
    if (v.top) g.style.top = v.top + 'px';
    const cards = v.items.map((it) => {
      const c = el('div', 'L-card' + (v.row ? ' row' : ''), null, g);
      if (it.span) c.style.gridColumn = `span ${it.span}`;
      if (v.compact) {
        c.style.padding = '12px 22px';
        el('div', null, `<span style="font-weight:800;color:${C(it.c)}">${it.icon ? it.icon + ' ' : ''}${md(it.h)}</span><br><span class="bd">${md(it.b)}</span>`, c);
      } else {
      if (it.icon) el('div', 'ic', it.icon, c);
      const tx = el('div', null, null, c);
      if (it.h) el('div', 'hd', md(it.h), tx, { color: C(it.c) });
      if (it.b) el('div', 'bd', md(it.b), tx);
      }
      if (v.fs) c.style.fontSize = v.fs + 'px';
      return c;
    });
    fitUniform(cards, 16);
    return (t, A) => {
      cards.forEach((c, i) => {
        const it = v.items[i];
        const p = A.show(t, it.at ?? 0);
        const w = v.nohl ? 0 : A.win(t, it.at ?? 0, nextAt(v.items, i));
        css(c, { o: p, y: (1 - p) * 30, s: 1 + 0.015 * w });
        hlStyle(c, w, C(it.c));
      });
    };
  };

  V.table = (area, v) => {
    const wrap = el('div', null, null, area, { position: 'absolute', inset: '0', overflow: 'hidden', fontSize: (v.fs || 28) + 'px' });
    const tb = el('table', 'L-tbl', null, wrap);
    tb.style.fontSize = '1em';
    if (v.cols) { const tr = el('tr', null, null, tb); v.cols.forEach((c) => el('th', null, md(c), tr)); }
    const rows = v.rows.map((r) => {
      const tr = el('tr', null, null, tb);
      r.c.forEach((x, j) => { const td = el('td', null, md(x), tr); if (j === 0 && r.color) td.style.color = C(r.color); if (v.widths) td.style.width = v.widths[j]; });
      return tr;
    });
    fit(wrap, 15);
    return (t, A) => {
      rows.forEach((tr, i) => {
        const r = v.rows[i];
        const p = A.show(t, r.at ?? 0);
        const w = A.win(t, r.at ?? 0, nextAt(v.rows, i));
        css(tr, { o: p, x: (1 - p) * -30 });
        Array.from(tr.children).forEach((td) => { td.style.background = `rgba(${w > 0.01 ? '56,189,248' : '255,255,255'},${0.045 + 0.1 * w})`; });
      });
    };
  };

  V.flow = (area, v) => {
    const ny = v.nodeY ?? 10, n = v.nodes.length;
    const svg = sv('svg', { width: AW, height: AH, style: 'position:absolute;left:0;top:0;overflow:visible' }, area);
    const xs = v.nodes.map((nd, i) => nd.x != null ? nd.x / 100 * AW : (AW / n) * (i + 0.5));
    const ys = v.nodes.map((nd) => (nd.y != null ? nd.y / 100 * AH : ny + 59));
    const links = v.links || v.nodes.slice(1).map((_, i) => [i, i + 1]);
    const lines = links.map(([a, b, at]) => sv('line', { x1: xs[a], y1: ys[a], x2: xs[b], y2: ys[b], stroke: '#3b4a6b', 'stroke-width': 5, 'stroke-dasharray': '12 10' }, svg));
    const nodes = v.nodes.map((nd, i) => {
      const NW = v.nodeW || 260;
      const e = el('div', 'L-node', null, area, { left: xs[i] - NW / 2 + 'px', top: ys[i] - 59 + 'px', width: NW + 'px' });
      const c = el('div', 'circ', nd.icon || '●', e, { borderColor: C(nd.c) });
      el('div', 'lb', md(nd.l), e, { color: C(nd.c) });
      if (nd.s) el('div', 'sb', md(nd.s), e);
      e._c = c;
      return e;
    });
    const dots = (v.steps || []).map((s) => (s.from != null ? sv('circle', { r: 14, fill: C(s.c || 'c3'), stroke: '#fff', 'stroke-width': 3, opacity: 0 }, svg) : null));
    let st = null;
    if (v.steps && !v.noList) {
      st = el('div', 'L-steps', null, area, { left: (v.listX ?? 0) + 'px', top: (v.listY ?? 300) + 'px', width: (v.listW ?? AW) + 'px', bottom: '0px' });
      v.steps.forEach((s, i) => {
        const r = el('div', 'L-step', null, st);
        el('div', 'n', s.n ?? i + 1, r, { background: C(s.c || 'c3') });
        el('div', null, md(s.t), r);
      });
      fitUniform(Array.from(st.children), 16);
      // shrink list if overflowing
      let fs = parseFloat(st.children[0].style.fontSize || 27), guard = 40;
      while (st.scrollHeight > st.clientHeight + 2 && fs > 16 && guard--) { fs -= 1; Array.from(st.children).forEach((c) => (c.style.fontSize = fs + 'px')); }
    }
    return (t, A) => {
      nodes.forEach((e, i) => {
        const p = A.show(t, v.nodes[i].at ?? 0);
        css(e, { o: p, s: 0.7 + 0.3 * ease.back(p) });
      });
      lines.forEach((ln, k) => {
        const [a, b, at] = links[k];
        const p = A.show(t, at ?? Math.max(v.nodes[a].at ?? 0, v.nodes[b].at ?? 0), 0.8);
        ln.setAttribute('opacity', p);
        ln.setAttribute('stroke-dashoffset', -t * 30);
      });
      // active node glow from steps
      const glow = new Array(n).fill(0);
      (v.steps || []).forEach((s, i) => {
        if (st) {
          const r = st.children[i];
          const p = A.show(t, s.at ?? 0), w = A.win(t, s.at ?? 0, nextAt(v.steps, i));
          css(r, { o: p, x: (1 - p) * 30 });
          hlStyle(r, w, C(s.c || 'c3'), 0.04);
        }
        if (s.from != null) {
          const a = A.at(s.at ?? 0), b = a + (s.d || 1.6);
          const p = seg(t, a, b, ease.inOut);
          const on = t > a - 0.05 && t < b + 0.35;
          const fx = xs[s.from], fy = ys[s.from], tx = xs[s.to], ty = ys[s.to];
          dots[i].setAttribute('cx', lerp(fx, tx, p));
          dots[i].setAttribute('cy', lerp(fy, ty, p) - Math.sin(p * Math.PI) * 40);
          dots[i].setAttribute('opacity', on ? 1 : 0);
          if (on) { glow[s.from] = Math.max(glow[s.from], 1 - p); glow[s.to] = Math.max(glow[s.to], p); }
        }
        if (s.hl != null) [].concat(s.hl).forEach((k) => (glow[k] = Math.max(glow[k], A.win(t, s.at ?? 0, nextAt(v.steps, i)))));
      });
      nodes.forEach((e, i) => { const col = C(v.nodes[i].c); e._c.style.boxShadow = glow[i] > 0.01 ? `0 0 ${50 * glow[i]}px ${col}` : 'none'; e._c.style.background = glow[i] > 0.01 ? '#1c2a50' : '#111a33'; });
    };
  };

  V.stack = (area, v) => {
    const W = v.w || 900, X = v.x ?? 60, n = v.layers.length;
    const H = v.h || AH - 20, gap = 10;
    const lh = (H - gap * (n - 1)) / n;
    const L = v.layers.map((ly, i) => {
      const e = el('div', 'L-layer', md(ly.l), area, { left: X + 'px', top: i * (lh + gap) + 'px', width: W + 'px', height: (ly.hmul ? lh * ly.hmul : lh) + 'px', borderColor: C(ly.c), background: C(ly.c) + '22', color: '#fff' });
      if (ly.split) { e.innerHTML = ''; e.style.justifyContent = 'stretch'; e.style.gap = '0'; ly.split.forEach((s, k) => el('div', null, md(s), e, { flex: 1, borderLeft: k ? `2px solid ${C(ly.c)}` : 'none', alignSelf: 'stretch', display: 'flex', alignItems: 'center', justifyContent: 'center' })); }
      return e;
    });
    const B = (v.brackets || []).map((b) => {
      const top = b.from * (lh + gap), bot = b.to * (lh + gap) + lh;
      const g = el('div', null, null, area, { position: 'absolute', left: X + W + 30 + 'px', top: top + 'px', height: bot - top + 'px', width: '600px', borderLeft: `5px solid ${C(b.c)}`, paddingLeft: '26px', display: 'flex', alignItems: 'center', font: '700 30px/1.25 Inter', color: C(b.c), boxSizing: 'border-box' });
      g.innerHTML = md(b.l);
      return g;
    });
    const notes = v.layers.map((ly, i) => ly.note ? el('div', 'L-lbl', md(ly.note), area, { left: X + W + 30 + 'px', top: i * (lh + gap) + lh / 2 - 16 + 'px', width: AW - X - W - 40 + 'px' }) : null);
    return (t, A) => {
      L.forEach((e, i) => {
        const ly = v.layers[i];
        const p = A.show(t, ly.at ?? 0), w = A.win(t, ly.at ?? 0, nextAt(v.layers, i));
        css(e, { o: p, x: (1 - p) * -40 });
        e.style.boxShadow = w > 0.01 ? `0 0 ${40 * w}px ${C(ly.c)}` : 'none';
        e.style.background = C(ly.c) + (w > 0.5 ? '55' : '22');
        if (notes[i]) css(notes[i], { o: p });
      });
      B.forEach((g, i) => { const p = A.show(t, v.brackets[i].at ?? 0); css(g, { o: p, x: (1 - p) * 20 }); });
    };
  };

  let SEQN = 0;
  V.seq = (area, v) => {
    const n = v.actors.length;
    const xs = v.actors.map((_, i) => (AW / n) * (i + 0.5));
    const top = 0, hdrH = 76, y0 = hdrH + 34, y1 = AH - 10;
    const svg = sv('svg', { width: AW, height: AH, style: 'position:absolute;left:0;top:0;overflow:visible' }, area);
    const defs = sv('defs', {}, svg);
    const mk = sv('marker', { id: 'ah' + (++SEQN), viewBox: '0 0 10 10', refX: 9, refY: 5, markerWidth: 7, markerHeight: 7, orient: 'auto-start-reverse' }, defs);
    sv('path', { d: 'M0,0 L10,5 L0,10 z', fill: '#e8edf7' }, mk);
    const heads = v.actors.map((a, i) => {
      sv('line', { x1: xs[i], y1: hdrH, x2: xs[i], y2: y1, stroke: '#3b4a6b', 'stroke-width': 3 }, svg);
      return el('div', null, md(a.l || a), area, { position: 'absolute', left: xs[i] - 150 + 'px', top: top + 'px', width: '300px', height: hdrH + 'px', display: 'flex', alignItems: 'center', justifyContent: 'center', textAlign: 'center', borderRadius: '14px', border: `2px solid ${C(a.c || 'c3')}`, background: C(a.c || 'c3') + '22', font: '700 24px/1.15 Inter', boxSizing: 'border-box' });
    });
    const m = v.msgs.length, step = (y1 - y0) / Math.max(m, 1);
    const fs = Math.min(26, step * 0.48);
    const items = v.msgs.map((g, k) => {
      const y = y0 + step * (k + 0.62);
      const x1 = xs[g.f], x2 = xs[g.t];
      const ln = sv('line', { x1, y1: y, x2: x1, y2: y, stroke: g.c ? C(g.c) : '#e8edf7', 'stroke-width': 3.5, 'marker-end': `url(#${mk.id})`, 'stroke-dasharray': g.dash ? '10 8' : 'none' }, svg);
      const lx = Math.min(x1, x2), lw = Math.abs(x2 - x1);
      const lb = el('div', null, md(g.l), area, { position: 'absolute', left: lx + 'px', width: lw + 'px', top: y - fs * 1.35 - 4 + 'px', textAlign: 'center', font: `${g.i ? 'italic ' : ''}600 ${fs}px/1.2 Inter`, color: g.c ? C(g.c) : '#e8edf7', whiteSpace: 'nowrap' });
      return { ln, lb, x1, x2 };
    });
    return (t, A) => {
      heads.forEach((h) => FV.enter(h, t, 0.1));
      items.forEach((it, k) => {
        const g = v.msgs[k];
        const a = A.at(g.at ?? k);
        const p = seg(t, a, a + (g.d || 0.9), ease.inOut);
        it.ln.setAttribute('x2', lerp(it.x1, it.x2, p));
        it.ln.setAttribute('opacity', p > 0 ? 1 : 0);
        const w = A.win(t, g.at ?? k, nextAt(v.msgs, k));
        it.ln.setAttribute('stroke-width', 3.5 + 2.5 * w);
        css(it.lb, { o: seg(t, a + 0.2, a + 0.7), s: 1 + 0.05 * w });
        it.lb.style.textShadow = w > 0.3 ? '0 0 18px rgba(251,191,36,.9)' : 'none';
      });
    };
  };

  V.frame = (area, v) => {
    const rows = v.rows.map((r, ri) => {
      const y = r.y ?? ri * 190 + 40, H = r.h || 110;
      const X0 = r.x ?? 0, W = r.w || AW;
      const tot = r.f.reduce((s, f) => s + (f.w || 1), 0);
      let x = X0;
      const lab = r.l ? el('div', 'L-lbl', md(r.l), area, { left: X0 + 'px', top: y - (r.f.some((f) => f.sz) ? 76 : 40) + 'px', font: '800 26px Inter', color: C(r.c || 'c1') }) : null;
      const fs = r.f.map((f) => {
        const w = (f.w || 1) / tot * W;
        const e = el('div', 'L-fld', md(f.l), area, { left: x + 'px', top: y + 'px', width: w - 6 + 'px', height: H + 'px', borderColor: C(f.c || r.c), background: C(f.c || r.c) + '26', fontSize: (r.fs || 22) + 'px' });
        if (f.sz) el('div', 'sz', md(f.sz), e);
        x += w;
        return e;
      });
      const span = (r.spans || []).map((s) => {
        const sx = X0 + s.a / tot * W, ex = X0 + s.b / tot * W;
        const e = el('div', 'L-lbl', md(s.l), area, { left: sx + 'px', width: ex - sx - 6 + 'px', top: y + H + 10 + 'px', textAlign: 'center', borderTop: `4px solid ${C(s.c || 'c8')}`, paddingTop: '6px', font: '700 23px Inter', color: C(s.c || 'c8') });
        return e;
      });
      return { lab, fs, span };
    });
    const notes = (v.notes || []).map((nt) => el('div', 'L-lbl', md(nt.t), area, { left: (nt.x ?? 0) + 'px', top: nt.y + 'px', width: (nt.w || AW) + 'px', font: `500 ${nt.fs || 26}px/1.35 Inter` }));
    return (t, A) => {
      rows.forEach((R, ri) => {
        const r = v.rows[ri];
        const p = A.show(t, r.at ?? 0);
        if (R.lab) css(R.lab, { o: p });
        R.fs.forEach((e, k) => {
          const f = r.f[k];
          const pk = A.show(t, f.at ?? r.at ?? 0);
          const w = f.at != null ? A.win(t, f.at, f.until ?? nextAt(r.f, k)) : 0;
          css(e, { o: Math.min(p, pk), y: (1 - pk) * 20, s: 1 + 0.04 * w });
          e.style.boxShadow = w > 0.01 ? `0 0 ${36 * w}px ${C(f.c || r.c)}` : 'none';
          e.style.zIndex = w > 0.5 ? 2 : 1;
        });
        R.span.forEach((e, k) => css(e, { o: A.show(t, r.spans[k].at ?? r.at ?? 0) }));
      });
      notes.forEach((e, k) => FV.enter(e, t, A.at(v.notes[k].at ?? 0) - 0.1));
    };
  };

  V.timeline = (area, v) => {
    const X0 = v.x ?? 220, W = v.w || AW - X0 - 20, laneH = v.laneH || 110, Y0 = v.y ?? 30;
    const xo = (x) => X0 + (x / 100) * W;
    const lanes = (v.lanes || []).map((l, i) => el('div', 'L-lbl', md(l), area, { left: '0px', width: X0 - 20 + 'px', top: Y0 + i * (laneH + 20) + laneH / 2 - 18 + 'px', font: '800 26px/1.2 Inter', textAlign: 'right' }));
    const base = (v.lanes || []).map((_, i) => el('div', null, null, area, { position: 'absolute', left: X0 + 'px', width: W + 'px', top: Y0 + i * (laneH + 20) + laneH + 'px', height: '3px', background: '#3b4a6b' }));
    const blocks = v.blocks.map((b) => {
      const e = el('div', 'L-fld', md(b.l || ''), area, { left: xo(b.x0) + 'px', width: xo(b.x1) - xo(b.x0) - 3 + 'px', top: Y0 + (b.lane || 0) * (laneH + 20) + (b.dy || 0) + 'px', height: (b.h || laneH) + 'px', borderColor: C(b.c), background: C(b.c) + (b.solid ? 'cc' : '30'), fontSize: (b.fs || 22) + 'px', color: b.solid ? '#0a1024' : '#fff', transformOrigin: 'left center' });
      return e;
    });
    const spans = (v.spans || []).map((s) => el('div', 'L-lbl', md(s.l), area, { left: xo(s.x0) + 'px', width: xo(s.x1) - xo(s.x0) + 'px', top: s.y + 'px', textAlign: 'center', borderTop: `4px solid ${C(s.c || 'c8')}`, paddingTop: '8px', font: '700 24px/1.25 Inter', color: C(s.c || 'c8') }));
    const marks = (v.marks || []).map((m) => el('div', 'L-lbl', md(m.l), area, { left: xo(m.x) - 160 + 'px', width: '320px', top: m.y + 'px', textAlign: 'center', font: '700 23px/1.2 Inter', color: C(m.c || 'c3') }));
    const notes = (v.notes || []).map((nt) => el('div', 'L-lbl', md(nt.t), area, { left: (nt.x ?? 0) + 'px', top: nt.y + 'px', width: (nt.w || AW) + 'px', font: `500 ${nt.fs || 26}px/1.35 Inter` }));
    const ph = v.play ? el('div', null, null, area, { position: 'absolute', top: Y0 - 14 + 'px', height: (v.lanes ? v.lanes.length : 1) * (laneH + 20) + 10 + 'px', width: '4px', background: '#fbbf24', boxShadow: '0 0 18px #fbbf24' }) : null;
    return (t, A) => {
      lanes.forEach((e) => FV.enter(e, t, 0.1));
      base.forEach((e) => css(e, { o: seg(t, 0, 0.6) }));
      blocks.forEach((e, k) => {
        const b = v.blocks[k];
        const p = A.show(t, b.at ?? 0, 0.6);
        const w = b.hl != null ? A.win(t, b.hl, b.hlEnd ?? null) : 0;
        e.style.opacity = p > 0 ? 1 : 0;
        e.style.transform = `scaleX(${p}) translateY(${-6 * w}px)`;
        e.style.boxShadow = w > 0.01 ? `0 0 ${40 * w}px ${C(b.c)}` : 'none';
      });
      spans.forEach((e, k) => css(e, { o: A.show(t, v.spans[k].at ?? 0) }));
      marks.forEach((e, k) => css(e, { o: A.show(t, v.marks[k].at ?? 0) }));
      notes.forEach((e, k) => FV.enter(e, t, A.at(v.notes[k].at ?? 0) - 0.1));
      if (ph) {
        const a = A.at(v.play[0]), b = A.at(v.play[1]);
        const p = seg(t, a, b, ease.linear);
        css(ph, { o: t > a - 0.1 ? 1 : 0, x: xo(p * 100) });
      }
    };
  };

  V.topo = (area, v) => {
    const svg = sv('svg', { width: AW, height: AH, style: 'position:absolute;left:0;top:0;overflow:visible' }, area);
    const P = {};
    const X = (x) => (v.ox ?? 0) + x / 100 * (v.w || AW), Y = (y) => y / 100 * AH;
    v.nodes.forEach((nd) => (P[nd.id] = [X(nd.x), Y(nd.y)]));
    const E = v.edges.map(([a, b, at]) => sv('line', { x1: P[a][0], y1: P[a][1], x2: P[b][0], y2: P[b][1], stroke: '#34d399', 'stroke-width': 4 }, svg));
    const colr = { coord: '#38bdf8', ffd: '#3b82f6', rfd: '#f87171' };
    const N = v.nodes.map((nd) => {
      const r = nd.k === 'coord' ? 30 : 21;
      const g = sv('g', {}, svg);
      if (nd.k === 'coord') sv('circle', { cx: P[nd.id][0], cy: P[nd.id][1], r: r + 12, fill: 'none', stroke: '#38bdf8', 'stroke-width': 3, opacity: 0.6 }, g);
      sv('circle', { cx: P[nd.id][0], cy: P[nd.id][1], r, fill: colr[nd.k] || '#3b82f6', stroke: '#fff', 'stroke-width': 3 }, g);
      return g;
    });
    const labels = (v.labels || []).map((l) => el('div', 'L-lbl', md(l.t), area, { left: X(l.x) + 'px', top: Y(l.y) + 'px', font: `700 ${l.fs || 26}px/1.25 Inter`, color: C(l.c || '#e8edf7'), width: (l.w || 420) + 'px' }));
    const pk = v.packets ? v.packets.map(() => sv('circle', { r: 11, fill: '#fbbf24', stroke: '#fff', 'stroke-width': 2, opacity: 0 }, svg)) : [];
    return (t, A) => {
      N.forEach((g, i) => { const p = A.show(t, v.nodes[i].at ?? 0); g.setAttribute('opacity', p); });
      E.forEach((e, i) => { const at = v.edges[i][2]; e.setAttribute('opacity', A.show(t, at ?? 0, 0.8)); });
      labels.forEach((e, i) => css(e, { o: A.show(t, v.labels[i].at ?? 0) }));
      pk.forEach((c, i) => {
        const pkt = v.packets[i], path = pkt.path;
        const a = A.at(pkt.at), d = pkt.d || 2.4;
        const p = seg(t, a, a + d, ease.linear) * (path.length - 1);
        const on = t > a && t < a + d + 0.3;
        const k = Math.min(path.length - 2, Math.floor(p)), f = p - k;
        const s = P[path[k]], e = P[path[k + 1]];
        c.setAttribute('cx', lerp(s[0], e[0], f)); c.setAttribute('cy', lerp(s[1], e[1], f));
        c.setAttribute('opacity', on ? 1 : 0);
      });
    };
  };

  V.calc = (area, v) => {
    const L = v.lines.map((l) => {
      const e = el('div', 'L-calc', '', area, { left: (l.x ?? 40) + 'px', top: l.y + 'px', fontSize: (l.fs || 34) + 'px', color: C(l.c || '#e8edf7'), fontFamily: l.sans ? 'Inter' : null, fontWeight: l.sans ? 600 : null });
      if (l.ans) e.classList.add('L-ans');
      return e;
    });
    return (t, A) => {
      L.forEach((e, i) => {
        const l = v.lines[i];
        const a = A.at(l.at ?? 0);
        const p = seg(t, a, a + (l.d || Math.max(0.8, Math.min(2.2, l.t.length * 0.035))), ease.linear);
        e.innerHTML = md(FV.type(l.t, p)) + (p > 0 && p < 1 ? '<span style="color:#38bdf8">▌</span>' : '');
        css(e, { o: t >= a - 0.05 ? 1 : 0 });
      });
    };
  };

  V.steps = (area, v) => {
    const LW = v.listW || 1000;
    const st = el('div', 'L-steps', null, area, { left: '0px', top: '0px', width: LW + 'px', height: AH + 'px' });
    const rows = v.steps.map((s, i) => {
      const r = el('div', 'L-step', null, st);
      el('div', 'n', s.n ?? i + 1, r, { background: C(s.c || 'c1'), borderRadius: s.dec ? '8px' : '50%', transform: s.dec ? 'rotate(45deg)' : 'none' });
      el('div', null, md(s.t), r);
      if (v.fs) r.style.fontSize = v.fs + 'px';
      return r;
    });
    fitUniform(rows, 16);
    let fs = parseFloat(rows[0].style.fontSize || 27), guard = 40;
    while (st.scrollHeight > AH + 2 && fs > 16 && guard--) { fs -= 1; rows.forEach((c) => (c.style.fontSize = fs + 'px')); }
    const names = v.vars ? v.vars.names : [];
    const VX = LW + 70;
    const boxes = names.map((nm, i) => {
      const b = el('div', 'L-var', null, area, { left: VX + (i % 2) * 290 + 'px', top: Math.floor(i / 2) * 180 + 'px' });
      el('div', 'k', nm, b);
      return el('div', 'v', '', b);
    });
    const note = v.vars ? el('div', 'L-lbl', '', area, { left: VX + 'px', top: Math.ceil(names.length / 2) * 180 + 10 + 'px', width: AW - VX + 'px', font: '600 27px/1.35 Inter', color: '#fde68a' }) : null;
    return (t, A) => {
      rows.forEach((r, i) => {
        const s = v.steps[i];
        const p = A.show(t, s.at ?? 0), w = s.hl != null ? A.win(t, s.hl, s.hlEnd ?? null) : A.win(t, s.at ?? 0, nextAt(v.steps, i));
        css(r, { o: p, x: (1 - p) * -30 });
        hlStyle(r, w, C(s.c || 'c1'), 0.04);
      });
      if (v.vars) {
        let cur = null, curAt = -1, k = -1;
        v.vars.states.forEach((s, i) => { const a = A.at(s.at); if (t >= a - 0.1) { cur = s; curAt = a; k = i; } });
        boxes.forEach((b, i) => {
          const val = cur ? cur.v[names[i]] : undefined;
          b.textContent = val == null ? '–' : val;
          const prev = k > 0 ? v.vars.states[k - 1].v[names[i]] : undefined;
          const flash = cur && prev !== val ? 1 - seg(t, curAt, curAt + 1.2) : 0;
          b.style.color = flash > 0.05 ? '#fbbf24' : '#e8edf7';
          b.parentNode.style.boxShadow = flash > 0.05 ? `0 0 ${40 * flash}px #fbbf24` : 'none';
          css(b.parentNode, { o: seg(t, 0, 0.6) });
        });
        if (note) note.innerHTML = cur && cur.note ? md(cur.note) : '';
      }
    };
  };

  V.tiers = (area, v) => {
    const n = v.tiers.length, gap = 16, th = (AH - gap * (n - 1)) / n;
    const T = v.tiers.map((tr, i) => {
      const e = el('div', 'L-tier', null, area, { top: i * (th + gap) + 'px', height: th + 'px', borderColor: C(tr.c), background: C(tr.c) + '18' });
      el('div', 'nm', md(tr.l) + `<span class="ds">${md(tr.d || '')}</span>`, e, { color: C(tr.c) });
      const box = el('div', null, null, e, { position: 'absolute', left: '400px', right: '20px', top: '0', bottom: '0', display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: '6px 4px' });
      e._chips = tr.chips.map((c) => el('span', 'L-chip', md(c), box, { borderColor: C(tr.c), color: '#fff', background: C(tr.c) + '33', fontSize: (v.chipFs || 25) + 'px', margin: '4px', padding: '10px 20px' }));
      return e;
    });
    return (t, A) => {
      T.forEach((e, i) => {
        const tr = v.tiers[i];
        const p = A.show(t, tr.at ?? 0), w = A.win(t, tr.at ?? 0, nextAt(v.tiers, i));
        css(e, { o: p, x: (1 - p) * -40 });
        e.style.boxShadow = w > 0.01 ? `0 0 ${40 * w}px ${C(tr.c)}66` : 'none';
        e._chips.forEach((c, k) => { const q = seg(t, A.at(tr.at ?? 0) + 0.3 + k * 0.18, A.at(tr.at ?? 0) + 0.8 + k * 0.18, ease.back); css(c, { o: clamp(q), s: 0.6 + 0.4 * q }); });
      });
    };
  };

  V.bars = (area, v) => {
    const n = v.items.length, LW = v.labelW || 320, gap = 14;
    const bh = Math.min(80, (AH - (v.top || 0) - gap * (n - 1)) / n);
    const max = v.max || Math.max(...v.items.map((i) => i.v));
    const B = v.items.map((it, i) => {
      const y = (v.top || 0) + i * (bh + gap);
      const lb = el('div', 'L-lbl', md(it.l), area, { left: '0px', width: LW - 20 + 'px', top: y + bh / 2 - 17 + 'px', textAlign: 'right', font: '800 28px Inter', color: C(it.c) });
      const bar = el('div', null, null, area, { position: 'absolute', left: LW + 'px', top: y + 'px', height: bh + 'px', borderRadius: '12px', background: C(it.c), transformOrigin: 'left center', width: (it.v / max) * (AW - LW - 420) + 'px' });
      const tx = el('div', 'L-lbl', md(it.txt || ''), area, { left: LW + (it.v / max) * (AW - LW - 420) + 18 + 'px', top: y + bh / 2 - 17 + 'px', width: '420px', font: '700 26px Inter' });
      return { lb, bar, tx };
    });
    const notes = (v.notes || []).map((nt) => el('div', 'L-lbl', md(nt.t), area, { left: (nt.x ?? 0) + 'px', top: nt.y + 'px', width: (nt.w || AW) + 'px', font: `600 ${nt.fs || 26}px/1.35 Inter`, color: C(nt.c || '#e8edf7') }));
    return (t, A) => {
      B.forEach((b, i) => {
        const it = v.items[i];
        const p = A.show(t, it.at ?? 0, 0.9);
        css(b.lb, { o: p }); css(b.tx, { o: seg(p, 0.6, 1) });
        b.bar.style.transform = `scaleX(${p})`;
        const w = A.win(t, it.at ?? 0, nextAt(v.items, i));
        b.bar.style.boxShadow = w > 0.01 ? `0 0 ${30 * w}px ${C(it.c)}` : 'none';
      });
      notes.forEach((e, k) => FV.enter(e, t, A.at(v.notes[k].at ?? 0) - 0.1));
    };
  };

  // two or more vizzes side by side / stacked: {type:'multi', parts:[{x,y,w,h,viz}]} — implemented by sub-areas
  V.multi = (area, v, sc) => {
    const ups = v.parts.map((pt) => {
      const sub = el('div', null, null, area, { position: 'absolute', left: (pt.x || 0) + 'px', top: (pt.y || 0) + 'px', width: (pt.w || AW) + 'px', height: (pt.h || AH) + 'px' });
      return V[pt.viz.type](sub, pt.viz, sc);
    });
    return (t, A, ctx) => ups.forEach((u) => u(t, A, ctx));
  };

  /* ---------- build every scene ---------- */
  const stage = document.getElementById('fv-stage');
  const updaters = {};
  LESSON.scenes.forEach((sc, si) => {
    const s = el('section', 'fv-scene', null, stage);
    s.dataset.scene = sc.id;
    // drifting background dots
    const dots = sv('svg', { class: 'L-dots', width: 1920, height: 1080 }, s);
    const R = FV.rand(si * 97 + 13), D = [];
    for (let i = 0; i < 26; i++) D.push({ c: sv('circle', { r: 1.5 + R() * 2.5, fill: '#38bdf8', opacity: 0.08 + R() * 0.18 }, dots), x: R() * 1920, y: R() * 1080, vx: (R() - 0.5) * 14, vy: (R() - 0.5) * 10 });
    const kick = sc.kicker ? el('div', 'L-kick', md(sc.kicker), s) : null;
    const title = sc.title ? el('div', 'L-title' + (sc.tip ? '' : ' wide'), md(sc.title), s) : null;
    if (sc.titleColor && kick) kick.style.color = C(sc.titleColor);
    const tip = sc.tip ? el('div', 'L-tip', md(sc.tip.t), s) : null;
    const area = el('div', 'L-area', null, s);
    if (sc.area) Object.assign(area.style, sc.area);
    const up = sc.viz ? V[sc.viz.type](area, sc.viz, sc) : () => {};
    const extra = (sc.extra || []).map((x) => {
      const sub = el('div', null, null, area, { position: 'absolute', left: (x.x || 0) + 'px', top: (x.y || 0) + 'px', width: (x.w || AW) + 'px', height: (x.h || AH) + 'px' });
      return V[x.viz.type](sub, x.viz, sc);
    });
    const endc = sc.endcard ? el('div', 'fv-endcard', '', s, { position: 'absolute', left: '50%', top: '930px', transform: 'translateX(-50%)', padding: '14px 34px', borderRadius: '999px', border: '2px solid #38bdf8', font: '700 30px Inter', color: '#38bdf8', background: 'rgba(56,189,248,.1)' }) : null;
    updaters[sc.id] = { up, extra, kick, title, tip, D, endc };
    FV.scene(sc.id, (t, ctx) => {
      const A = mkA(ctx);
      const U = updaters[sc.id];
      U.D.forEach((d) => { d.c.setAttribute('cx', ((d.x + d.vx * t) % 1920 + 1920) % 1920); d.c.setAttribute('cy', ((d.y + d.vy * t) % 1080 + 1080) % 1080); });
      if (U.kick) FV.enter(U.kick, t, 0.05);
      if (U.title) FV.enter(U.title, t, 0.15, 0.7, 30);
      if (U.tip) { const p = A.show(t, sc.tip.at ?? 0); css(U.tip, { o: p, s: 0.9 + 0.1 * ease.back(p) }); }
      U.up(t, A, ctx);
      U.extra.forEach((u) => u(t, A, ctx));
      if (U.endc) { const p = seg(t, ctx.dur - 4, ctx.dur - 3.2, ease.out); U.endc.style.opacity = p; }
    });
  });
})();
