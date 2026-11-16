"""Generate index.html for the CCPS Module 3 videos from a compact layout spec.

Block types (each block reveals at narration line L, optional fraction F):
  ("cards", cols, [(L, color, heading, html), ...], height?)
  ("bul", [(L, color, html), ...], size?)
  ("table", [header...], [(L, [cells...]), ...], fontsize?)
  ("chips", L, [(color, text), ...])
  ("eq", L, html, color?)
  ("note", L, html)
  ("svg", id, height)            -- drawn by a JS function DIAG[id](svg) -> update(t, ctx)
"""
import html, json, sys

HEAD = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>%s</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="fvlib.css">
<style>
 .flow{position:absolute;left:120px;top:228px;width:1680px;display:flex;flex-direction:column;gap:16px}
 .card{position:relative;border:2px solid var(--k);border-radius:18px;background:color-mix(in srgb,var(--k) 9%%,rgba(13,20,42,.86));padding:16px 20px;box-sizing:border-box}
 .card h3{margin:0 0 6px;font:800 27px Inter;color:var(--k)}
 .card p{margin:0;font:500 22px/1.38 Inter}
 .eqb{border:2px solid var(--k);border-radius:16px;background:rgba(13,20,42,.86);padding:14px 22px;font:600 28px/1.4 'JetBrains Mono',monospace;color:#fff}
 .tblw{border:2px solid rgba(148,163,200,.25);border-radius:18px;background:rgba(13,20,42,.86);padding:8px 16px}
 .tblw td,.tblw th{vertical-align:top}
 .bl .item{font-size:26px;margin:7px 0}
</style></head><body><div id="fv-stage"><div id="bg-grid"></div>
"""
COLORS = {"a": "var(--a)", "b": "var(--b)", "c": "var(--c)", "d": "var(--d)", "e": "var(--e)", "f": "var(--f)", "g": "var(--g)", "m": "var(--mut)"}


def attr(L):
    if isinstance(L, (int, float)):
        return f'data-l="{int(L)}"'
    l, f = L
    return f'data-l="{l}" data-f="{f}"'


def block(b):
    t = b[0]
    if t == "cards":
        cols, items = b[1], b[2]
        h = f"height:{b[3]}px;" if len(b) > 3 else ""
        out = f'<div style="display:grid;grid-template-columns:repeat({cols},1fr);gap:14px">'
        for L, c, hd, tx in items:
            out += f'<div class="card" {attr(L)} style="--k:{COLORS[c]};{h}"><h3>{hd}</h3><p>{tx}</p></div>'
        return out + "</div>"
    if t == "bul":
        size = b[2] if len(b) > 2 else 26
        out = '<div class="bl">'
        for L, c, tx in b[1]:
            out += f'<div class="item" {attr(L)} style="font-size:{size}px"><span class="dot" style="--k:{COLORS[c]}"></span>{tx}</div>'
        return out + "</div>"
    if t == "table":
        fs = b[3] if len(b) > 3 else 22
        out = f'<div class="tblw" data-l="0"><table class="tbl" style="width:100%;font-size:{fs}px;font-weight:500"><tr>'
        out += "".join(f"<th>{h}</th>" for h in b[1]) + "</tr>"
        for L, cells in b[2]:
            out += f"<tr {attr(L)}>" + "".join(f"<td>{c}</td>" for c in cells) + "</tr>"
        return out + "</table></div>"
    if t == "chips":
        out = f'<div class="flex" {attr(b[1])} style="gap:12px">'
        for c, tx in b[2]:
            out += f'<span class="chip sm" style="--k:{COLORS[c]}">{tx}</span>'
        return out + "</div>"
    if t == "eq":
        c = COLORS[b[3]] if len(b) > 3 else "var(--c)"
        return f'<div class="eqb" {attr(b[1])} style="--k:{c}">{b[2]}</div>'
    if t == "note":
        return f'<div class="note" {attr(b[1])} style="font-size:25px">{b[2]}</div>'
    if t == "svg":
        return f'<svg class="dg" id="{b[1]}" width="1680" height="{b[2]}"></svg>'
    raise ValueError(t)


def build(title, scenes, js, out):
    s = HEAD % html.escape(title)
    for sc in scenes:
        sid, kicker, ttl, blocks = sc["id"], sc["k"], sc["t"], sc["b"]
        if sc.get("hero"):
            s += f'<section class="fv-scene" data-scene="{sid}"><div class="abs" style="left:0;right:0;top:250px;text-align:center"><div data-l="0" class="mono" style="font-size:28px;letter-spacing:.3em;color:var(--a)">{kicker}</div><div data-l="0" data-f="0.3" class="big" style="margin-top:22px;font-size:92px">{ttl}</div></div><div class="flow" style="top:600px">'
        else:
            s += f'<section class="fv-scene" data-scene="{sid}"><div class="kicker">{kicker}</div><div class="title">{ttl}</div><div class="flow">'
        s += "".join(block(b) for b in blocks)
        if sid == "recap":
            s += '<div style="text-align:center;margin-top:10px"><span class="fv-endcard" data-l="%d"></span></div>' % sc.get("endl", 5)
        s += "</div></section>\n"
    s += """</div><script src="timing.js"></script><script src="fv-runtime.js"></script><script src="fvlib.js"></script><script>
const { seg, enter, css, ease, clamp, lerp } = FV;
const { COL, at, mk, reveal, arrow, traveller } = L;
const node = (svg, x, y, r, txt, c, fs = 24) => { const g = mk('g', {}, svg); mk('circle', { cx: x, cy: y, r, fill: 'rgba(13,20,42,.95)', stroke: c, 'stroke-width': 3.5 }, g); mk('text', { x, y: y + fs * 0.35, 'text-anchor': 'middle', fill: '#fff', 'font-size': fs, 'font-weight': 800 }, g, txt); return g; };
const boxS = (svg, x, y, w, h, a, b, c, fs = 24) => { const g = mk('g', {}, svg); mk('rect', { x, y, width: w, height: h, rx: 14, fill: 'rgba(13,20,42,.92)', stroke: c, 'stroke-width': 3 }, g); mk('text', { x: x + w / 2, y: y + h / 2 + (b ? -5 : fs * 0.35), 'text-anchor': 'middle', fill: '#fff', 'font-size': fs, 'font-weight': 800 }, g, a); if (b) mk('text', { x: x + w / 2, y: y + h / 2 + 24, 'text-anchor': 'middle', fill: COL.mut, 'font-size': 19 }, g, b); g.querySelectorAll('text').forEach((tx) => { try { const L = tx.getComputedTextLength(); if (L > w - 16) tx.setAttribute('textLength', w - 16), tx.setAttribute('lengthAdjust', 'spacingAndGlyphs'); } catch (e) {} }); return g; };
const fade = (el, t, ctx, l, f = 0) => { el.style.opacity = seg(t, at(ctx, l, f), at(ctx, l, f) + 0.4); };
const DIAG = {};
""" + js + """
document.querySelectorAll('.fv-scene').forEach((sec) => {
  const id = sec.dataset.scene; const svgs = [...sec.querySelectorAll('svg.dg')].map((s) => DIAG[s.id] ? DIAG[s.id](s) : null).filter(Boolean);
  FV.scene(id, (t, ctx) => { reveal(t, ctx); svgs.forEach((u) => u(t, ctx)); });
});
</script></body></html>"""
    open(out, "w").write(s)
