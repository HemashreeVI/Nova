"""Whiteboard-style Shorts: marker strokes draw themselves and handwriting appears in sync with the voice."""
def wb_page(title, badge, scene_ids, scenes_js, extra_js=""):
    sections = "\n".join(f'  <section class="fv-scene" data-scene="{s}"><svg class="wb" viewBox="0 0 1080 1920"></svg></section>' for s in scene_ids)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<link href="https://fonts.googleapis.com/css2?family=Caveat:wght@500;700&family=Kalam:wght@400;700&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet">
<style>
  #fv-stage{{background:#f7f7f2;color:#1f2937;font-family:Kalam,'Comic Sans MS',cursive}}
  #board{{position:absolute;inset:26px;border-radius:26px;border:10px solid #cbd5e1;box-shadow:inset 0 0 80px rgba(148,163,184,.25);background:
    radial-gradient(600px 400px at 20% 12%,rgba(148,163,184,.10),transparent 70%),radial-gradient(500px 500px at 85% 70%,rgba(148,163,184,.08),transparent 70%),#fcfcf9}}
  #tray{{position:absolute;left:120px;right:120px;bottom:26px;height:22px;border-radius:0 0 12px 12px;background:#94a3b8}}
  .badge{{position:absolute;left:50%;top:70px;transform:translateX(-50%) rotate(-1.5deg);padding:8px 26px;border:4px solid #1f2937;border-radius:16px;font:700 40px Caveat;color:#1f2937;white-space:nowrap;background:#fff}}
  .wb{{position:absolute;inset:0;width:1080px;height:1920px}}
  .wb text{{font-family:Caveat,cursive;font-weight:700}}
</style>
</head>
<body>
<div id="fv-stage">
  <div id="board"></div><div id="tray"></div>
  <div class="badge">{badge}</div>
{sections}
</div>
<script src="timing.js"></script>
<script src="fv-runtime.js"></script>
<script>
(() => {{
const {{ seg, css, enter, lerp, clamp, ease, pulse, $ }} = FV;
const NS = 'http://www.w3.org/2000/svg';
const el = (tag, a, p) => {{ const e = document.createElementNS(NS, tag); for (const k in a) e.setAttribute(k, a[k]); if (p) p.appendChild(e); return e; }};
const K = '#1f2937', B = '#2563eb', R = '#dc2626', G = '#16a34a', O = '#ea580c', P = '#7c3aed', Y = '#ca8a04';
let seed = 7; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
/* hand-drawn polyline: subdivide and wobble */
const wob = (pts, amt = 2.2) => {{ const out = []; for (let i = 0; i < pts.length - 1; i++) {{ const [x1, y1] = pts[i], [x2, y2] = pts[i + 1], n = Math.max(2, Math.round(Math.hypot(x2 - x1, y2 - y1) / 40)); for (let k = 0; k < n; k++) {{ const u = k / n; out.push([lerp(x1, x2, u) + (rnd() - .5) * amt, lerp(y1, y2, u) + (rnd() - .5) * amt]); }} }} out.push(pts[pts.length - 1]); return out; }};
const dPath = (pts) => pts.map((p, i) => (i ? 'L' : 'M') + p[0].toFixed(1) + ' ' + p[1].toFixed(1)).join(' ');
/* item constructors: every item has `at` = [line, from, to] (fractions of that narration line) or ['s', s0, s1] seconds */
const T = (x, y, s, o = {{}}, at) => ({{ k: 'text', x, y, s, o, at }});
const L = (pts, o = {{}}, at) => ({{ k: 'path', pts, o, at }});
const RECT = (x, y, w, h, o = {{}}, at) => ({{ k: 'path', pts: [[x, y], [x + w, y], [x + w, y + h], [x, y + h], [x, y + 2]], o, at }});
const CIRC = (cx, cy, r, o = {{}}, at) => ({{ k: 'path', pts: Array.from({{ length: 41 }}, (_, i) => [cx + Math.cos(i / 40 * 6.3 - 1.6) * r * (1 + (i > 36 ? .06 : 0)), cy + Math.sin(i / 40 * 6.3 - 1.6) * r * .92]), o, at }});
const ARROW = (x1, y1, x2, y2, o = {{}}, at) => {{ const a = Math.atan2(y2 - y1, x2 - x1), h = o.head || 30; return {{ k: 'path', pts: [[x1, y1], [x2, y2], [x2 - h * Math.cos(a - .5), y2 - h * Math.sin(a - .5)], [x2, y2], [x2 - h * Math.cos(a + .5), y2 - h * Math.sin(a + .5)]], o, at }}; }};
const UL = (x1, x2, y, o = {{}}, at) => L([[x1, y], [x2, y + 4]], Object.assign({{ w: 7 }}, o), at);
const EMO = (x, y, ch, size = 90, at) => ({{ k: 'emo', x, y, ch, size, at }});
const FN = (init) => ({{ k: 'fn', init }});   /* custom: init(svg) returns update(t, ctx) */
const span = (ctx, at) => at[0] === 's' ? [at[1], at[2]] : [ctx.line(at[0]) + (ctx.lineEnd(at[0]) - ctx.line(at[0])) * at[1], ctx.line(at[0]) + (ctx.lineEnd(at[0]) - ctx.line(at[0])) * at[2]];
function build(svg, items) {{
  const pen = el('g', {{ opacity: 0 }});
  el('rect', {{ x: -9, y: -70, width: 18, height: 70, rx: 4, fill: '#334155', transform: 'rotate(35)' }}, pen); el('rect', {{ x: -9, y: -90, width: 18, height: 22, rx: 4, fill: '#ef4444', transform: 'rotate(35)' }}, pen); el('path', {{ d: 'M-9 0 L0 14 L9 0 Z', fill: '#1f2937', transform: 'rotate(35)' }}, pen);
  const live = items.map((it) => {{
    if (it.k === 'path') {{ const p = el('path', {{ d: dPath(wob(it.pts, it.o.wob ?? 2.2)), fill: it.o.fill || 'none', stroke: it.o.c || K, 'stroke-width': it.o.w || 6, 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'fill-opacity': it.o.fo ?? .15 }}, svg); const len = p.getTotalLength(); p.setAttribute('stroke-dasharray', len + ' ' + len); return {{ it, p, len }}; }}
    if (it.k === 'text') {{ const id = 'c' + Math.random().toString(36).slice(2); const cp = el('clipPath', {{ id }}, svg); const cr = el('rect', {{ x: 0, y: 0, width: 0, height: 1920 }}, cp);
      const tx = el('text', {{ x: it.x, y: it.y, 'font-size': it.o.size || 64, fill: it.o.c || K, 'text-anchor': it.o.anchor || 'start', 'clip-path': `url(#${{id}})`, transform: it.o.rot ? `rotate(${{it.o.rot}} ${{it.x}} ${{it.y}})` : '', style: it.o.mono ? 'font-family:JetBrains Mono,monospace;font-weight:500;white-space:pre;font-variant-ligatures:none' : '' }}, svg); tx.textContent = it.s; return {{ it, tx, cr }}; }}
    if (it.k === 'emo') {{ const tx = el('text', {{ x: it.x, y: it.y, 'font-size': it.size, 'text-anchor': 'middle', style: 'font-family:sans-serif' }}, svg); tx.textContent = it.ch; return {{ it, tx }}; }}
    if (it.k === 'fn') return {{ it, up: it.init(svg) }};
  }});
  svg.appendChild(pen);
  return (t, ctx) => {{
    let tip = null;
    for (const L2 of live) {{
      const it = L2.it;
      if (it.k === 'fn') {{ L2.up(t, ctx); continue; }}
      const [a, b] = span(ctx, it.at), p = seg(t, a, b, ease.linear);
      if (it.o && it.o.until) {{ const gone = t >= span(ctx, it.o.until)[0]; const node = L2.p || L2.tx; node.style.opacity = gone ? 0 : 1; if (gone) continue; }}
      if (it.k === 'path') {{ L2.p.setAttribute('stroke-dashoffset', L2.len * (1 - p)); L2.p.setAttribute('fill-opacity', it.o.fill ? (it.o.fo ?? .15) * (p >= 1 ? 1 : 0) : 0); if (p > 0 && p < 1) {{ const q = L2.p.getPointAtLength(L2.len * p); tip = [q.x, q.y]; }} }}
      if (it.k === 'text') {{ let bb; try {{ bb = L2.tx.getBBox(); }} catch (e) {{ bb = {{ x: it.x, y: it.y - 60, width: 600, height: 80 }}; }} L2.cr.setAttribute('x', bb.x - 4); L2.cr.setAttribute('width', (bb.width + 10) * p); if (p > 0 && p < 1) tip = [bb.x + bb.width * p, bb.y + bb.height * .8]; }}
      if (it.k === 'emo') {{ const q = seg(t, a, b, ease.back); L2.tx.setAttribute('opacity', clamp(q * 1.5)); L2.tx.setAttribute('transform', `translate(${{it.x}} ${{it.y}}) scale(${{Math.max(0.01, q)}}) translate(${{-it.x}} ${{-it.y}})`); }}
    }}
    pen.setAttribute('opacity', tip ? 1 : 0); if (tip) pen.setAttribute('transform', `translate(${{tip[0]}} ${{tip[1]}})`);
  }};
}}
{extra_js}
const SCENES = {scenes_js};
document.querySelectorAll('.fv-scene').forEach((sec) => {{
  const id = sec.dataset.scene, svg = sec.querySelector('svg'); const up = build(svg, SCENES[id] || []);
  FV.scene(id, (t, ctx) => up(t, ctx));
}});
}})();
</script>
</body>
</html>
"""
