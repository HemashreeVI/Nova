"""Shared builder for the project deep-dive videos (RootLens, TriageIQ, ...).

Each video has a build.py that lists its scenes with this module's helpers and
calls write(). That produces index.html and video.json in the same style as
the SeatLock deep dive (same CSS and the same declarative animation engine):

    data-at="2"      fade in at the start of narration line 2
    data-at="2.5"    ... halfway through line 2
    data-at="e2"     ... at the end of line 2
    data-at="s1.2"   ... 1.2 s into the scene
    data-draw="1-3"  draw an SVG path from line 1 to line 3
    data-move / data-path, data-hl, data-count/data-to, data-bar/data-w, data-type

Standard library only.
"""
import html
import json
import re
from pathlib import Path

SEATLOCK = Path(__file__).resolve().parent / "seatlock-deep-dive" / "index.html"


def _seatlock_css():
    src = SEATLOCK.read_text()
    return re.search(r"<style>(.*?)</style>", src, re.S).group(1)


EXTRA_CSS = """
  .chip{display:inline-flex;align-items:center;gap:8px;padding:8px 16px;border-radius:12px;font:700 22px 'JetBrains Mono';border:2px solid var(--c,#8b6cf6);background:color-mix(in srgb,var(--c,#8b6cf6) 14%,transparent);white-space:nowrap}
  .rows2{display:grid;grid-template-columns:1fr 1fr;gap:14px}
  .rows2 .row{margin:0}
  .note{font:600 24px/1.4 Inter;color:var(--mut)}
  .kv{font:700 26px 'JetBrains Mono';color:#e6e0f6}
  .kv b{color:var(--c,var(--amber))}
"""

ENGINE = r"""
const { seg, pulse, css, ease, clamp, lerp } = FV;
const $ = (s, r = document) => r.querySelector(s), $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
function T(spec, ctx) {
  spec = String(spec).trim();
  if (spec[0] === 's') return +spec.slice(1);
  if (spec[0] === 'e') return ctx.lineEnd(+spec.slice(1));
  const v = +spec, i = Math.floor(v), f = v - i;
  const a = ctx.line(i), b = ctx.lineEnd(i);
  return a + (b - a) * f;
}
const range = (spec, ctx) => { const [a, b] = spec.split('-'); const ta = T(a, ctx); return [ta, b === undefined ? ta + 0.6 : Math.max(ta + 0.05, T(b, ctx))]; };
function build() {
  $$('[data-draw]').forEach((p) => { p.setAttribute('pathLength', 1); p.style.strokeDasharray = p.getAttribute('stroke-dasharray') ? p.getAttribute('stroke-dasharray') : '1 1'; if (!p.getAttribute('stroke-dasharray')) { p.style.strokeDashoffset = 1; } });
  $$('[data-type]').forEach((e) => (e.dataset.full = e.textContent));
}
const extra = {};
function generic(t, ctx) {
  const el = ctx.el;
  const k = $('.kicker', el), ti = $('.title', el);
  if (k) FV.enter(k, t, 0.05); if (ti) FV.enter(ti, t, 0.15);
  $$('[data-at]', el).forEach((e) => {
    const a = T(e.dataset.at, ctx);
    const p = seg(t, a, a + 0.6, ease.out);
    let o = p;
    if (e.dataset.out) o *= 1 - seg(t, T(e.dataset.out, ctx), T(e.dataset.out, ctx) + 0.4);
    if (e instanceof SVGElement) e.style.opacity = o;
    else css(e, { o, y: (1 - p) * 22 });
  });
  $$('[data-draw]', el).forEach((p) => {
    const [a, b] = range(p.dataset.draw, ctx); const q = seg(t, a, b);
    p.style.opacity = q > 0 ? 1 : 0;
    if (!p.getAttribute('stroke-dasharray')) p.style.strokeDashoffset = 1 - q;
  });
  $$('[data-move]', el).forEach((c) => {
    const [a, b] = range(c.dataset.move, ctx); const path = document.getElementById(c.dataset.path);
    const q = seg(t, a, b, ease.inOut); const L = path.getTotalLength(); const pt = path.getPointAtLength(L * q);
    c.setAttribute('cx', pt.x); c.setAttribute('cy', pt.y);
    c.style.opacity = t >= a && t <= b + 0.3 ? 1 : 0;
  });
  $$('[data-hl]', el).forEach((e) => {
    let g = 0; e.dataset.hl.split(',').forEach((r) => { const [a, b] = range(r, ctx); g = Math.max(g, seg(t, a, a + 0.3) * (1 - seg(t, b - 0.3, b))); });
    const tg = e.tagName === 'TR' ? Array.from(e.children) : [e];
    tg.forEach((x) => { x.style.boxShadow = g ? `inset 0 0 0 3px rgba(242,177,52,${g}), 0 0 ${30 * g}px rgba(242,177,52,${0.6 * g})` : 'none'; x.style.background = g ? `rgba(242,177,52,${0.18 * g})` : ''; });
  });
  $$('[data-count]', el).forEach((e) => {
    const [a, b] = range(e.dataset.count, ctx); const v = +e.dataset.to * seg(t, a, b, ease.out);
    const d = +(e.dataset.dec || 0);
    e.textContent = d ? v.toFixed(d) : Math.round(v).toLocaleString('en-US');
  });
  $$('[data-bar]', el).forEach((e) => { const [a, b] = range(e.dataset.bar, ctx); e.style.width = (+e.dataset.w * seg(t, a, b, ease.out)) + '%'; });
  $$('[data-type]', el).forEach((e) => { const [a, b] = range(e.dataset.type, ctx); e.textContent = FV.type(e.dataset.full, seg(t, a, b, ease.linear)); });
  $$('[data-blink]', el).forEach((e) => { const [a, b] = range(e.dataset.blink, ctx); const on = t >= a && t <= b; e.style.opacity = on ? 0.45 + 0.55 * Math.abs(Math.sin(t * 3)) : (t > b ? 1 : 0); });
  const chap = $('#chap'); if (el.dataset.chap && chap.textContent !== el.dataset.chap) chap.textContent = el.dataset.chap;
  if (extra[ctx.id]) extra[ctx.id](t, ctx);
}
"""

COLORS = {"violet": "var(--violet)", "amber": "var(--amber)", "grn": "var(--grn)", "red": "var(--red)",
          "blu": "var(--blu)", "pink": "var(--pink)", "cyan": "var(--cyan)", "org": "var(--org)", "mut": "var(--mut)"}


def c(name):
    return COLORS.get(name, name)


# ----------------------------------------------------------------- helpers

def at_attr(at):
    return f' data-at="{at}"' if at is not None else ""


def text(x, y, w, inner, at=None, style=""):
    return f'<div class="abs"{at_attr(at)} style="left:{x}px;top:{y}px;width:{w}px;{style}">{inner}</div>'


def center(y, inner, at=None, style=""):
    return f'<div class="abs"{at_attr(at)} style="left:0;right:0;top:{y}px;text-align:center;{style}">{inner}</div>'


def pill(label, color="violet", style=""):
    return f'<span class="pill" style="--c:{c(color)};{style}">{label}</span>'


def tag(label, color="violet"):
    return f'<span class="tag" style="--c:{c(color)}">{label}</span>'


def card(x, y, w, h, inner, at=None, style=""):
    hh = f"height:{h}px;" if h else ""
    return f'<div class="card"{at_attr(at)} style="left:{x}px;top:{y}px;width:{w}px;{hh}{style}">{inner}</div>'


def node(x, y, w, h, label, small="", color="violet", at=None, style="", nid=None):
    sm = f"<small>{small}</small>" if small else ""
    i = f' id="{nid}"' if nid else ""
    return (f'<div class="node"{i}{at_attr(at)} style="--c:{c(color)};left:{x}px;top:{y}px;width:{w}px;height:{h}px;{style}">'
            f'{label}{sm}</div>')


def row(inner, ic=None, num=None, color="violet", at=None, style=""):
    lead = f'<div class="num">{num}</div>' if num is not None else (f'<div class="ic">{ic}</div>' if ic else "")
    return f'<div class="row"{at_attr(at)} style="--c:{c(color)};{style}">{lead}<div>{inner}</div></div>'


def rows(x, y, w, items, grid=False):
    """items: (at, icon_or_number, html, color)"""
    out = []
    for it in items:
        at, ic, inner, color = it
        if isinstance(ic, int):
            out.append(row(inner, num=ic, color=color, at=at))
        else:
            out.append(row(inner, ic=ic, color=color, at=at))
    cls = ' class="rows2"' if grid else ""
    return f'<div class="abs" style="left:{x}px;top:{y}px;width:{w}px"><div{cls}>{"".join(out)}</div></div>'


def qa(x, y, w, items, color=None):
    """items: (at, question, answer)"""
    out = []
    for at, q, a in items:
        cc = f"--c:{c(color)};" if color else ""
        out.append(f'<div class="row"{at_attr(at)} style="display:block;{cc}"><div class="q">Q · {q}</div><div class="a">{a}</div></div>')
    return f'<div class="abs" style="left:{x}px;top:{y}px;width:{w}px">{"".join(out)}</div>'


def code(x, y, w, body, at=None, size=25, label=None, label_color="amber", h=None):
    lab = f'<span class="lbl" style="color:{c(label_color)}">{label}</span>\n' if label else ""
    hh = f"height:{h}px;" if h else ""
    return (f'<div class="card code"{at_attr(at)} style="left:{x}px;top:{y}px;width:{w}px;{hh}font-size:{size}px">'
            f'{lab}{body}</div>')


def shot(x, y, w, src, cap=None, at=None, h=None, pos="top"):
    hh = f"height:{h}px;" if h else ""
    img_style = f' style="height:100%;object-fit:cover;object-position:{pos}"' if h else ""
    cp = f'<div class="cap">{cap}</div>' if cap else ""
    return f'<div class="shot"{at_attr(at)} style="left:{x}px;top:{y}px;width:{w}px;{hh}"><img src="{src}"{img_style}>{cp}</div>'


def table(x, y, w, header, body, size=26):
    """body: list of (at, [cells], hl or None)"""
    th = "".join(f"<th>{h}</th>" for h in header)
    trs = []
    for at, cells, hl in body:
        hla = f' data-hl="{hl}"' if hl else ""
        trs.append(f"<tr{at_attr(at)}{hla}>" + "".join(f"<td>{cell}</td>" for cell in cells) + "</tr>")
    return (f'<div class="abs" style="left:{x}px;top:{y}px;width:{w}px"><table class="t" style="font-size:{size}px">'
            f'<tr>{th}</tr>{"".join(trs)}</table></div>')


def svg(inner):
    return f'<svg class="abs" width="1920" height="1080" style="left:0;top:0">{inner}</svg>'


MARK = {"amber": "mA", "grn": "mG", "red": "mR", "blu": "mB", "violet": "mV"}
HEX = {"amber": "#f2b134", "grn": "#34d399", "red": "#f87171", "blu": "#60a5fa", "violet": "#a78bfa",
       "pink": "#f472b6", "cyan": "#22d3ee", "org": "#fb923c", "mut": "#a59cbf"}


def arrow(d, color="amber", draw=None, pid=None, head=True, dash=None, width=5):
    m = f' marker-end="url(#{MARK.get(color, "mA")})"' if head else ""
    i = f' id="{pid}"' if pid else ""
    dr = f' data-draw="{draw}"' if draw else ""
    da = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<path{i} class="ar" d="{d}" stroke="{HEX.get(color, color)}" stroke-width="{width}"{m}{dr}{da}/>'


def mover(pid, when, color="amber", r=14):
    return f'<circle data-move="{when}" data-path="{pid}" r="{r}" fill="{HEX.get(color, color)}"/>'


def bar(x, y, w, label, pct, when, color="violet", value=""):
    return (f'<div class="abs" style="left:{x}px;top:{y}px;width:{w}px">'
            f'<div style="display:flex;justify-content:space-between;font:700 24px Inter;margin-bottom:8px"><span>{label}</span>'
            f'<span style="color:{c(color)}">{value}</span></div>'
            f'<div style="height:26px;border-radius:13px;background:rgba(255,255,255,.08)">'
            f'<div data-bar="{when}" data-w="{pct}" style="height:100%;width:0;border-radius:13px;background:{c(color)}"></div></div></div>')


# ----------------------------------------------------------------- scenes

class Scene:
    def __init__(self, sid, title, chap, kicker, heading, lines, body, pad=(0.4, 0.55), hold=None):
        self.id, self.title, self.chap, self.kicker, self.heading = sid, title, chap, kicker, heading
        self.lines, self.body, self.pad, self.hold = lines, body, list(pad), hold

    def html(self):
        head = ""
        if self.kicker:
            head += f'<div class="kicker">{self.kicker}</div>'
        if self.heading:
            head += f'<div class="title">{self.heading}</div>'
        body = "\n  ".join(self.body) if isinstance(self.body, (list, tuple)) else self.body
        return (f'<section class="fv-scene" data-scene="{self.id}" data-chap="{html.escape(self.chap)}">\n  {head}\n  {body}\n</section>\n')

    def json(self):
        d = {"id": self.id, "title": self.title, "pad": self.pad, "lines": self.lines}
        if self.hold:
            d["hold"] = self.hold
        return d


def write(folder, meta, brand_icon, brand_name, scenes, extra_js=""):
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    ids = [s.id for s in scenes]
    assert len(ids) == len(set(ids)), "duplicate scene ids"
    # every data-at line index must exist
    for s in scenes:
        n = len(s.lines)
        blob = s.html()
        for m in re.finditer(r'data-(?:at|draw|move|hl|count|bar|type|blink|out)="([^"]+)"', blob):
            for part in re.split(r"[-,]", m.group(1)):
                part = part.strip()
                if not part or part[0] == "s":
                    continue
                k = int(float(part.lstrip("e")))
                assert 0 <= k < n, f"{s.id}: line {k} out of range ({n} lines) in {m.group(0)}"
    doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(brand_name)} Deep Dive</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@500;700;800&display=swap" rel="stylesheet">
<style>{_seatlock_css()}{EXTRA_CSS}</style>
</head>
<body>
<div id="fv-stage">
  <div id="bg-grid"></div>
  <div class="brand"><i>{brand_icon}</i>{html.escape(brand_name)} <span>· deep dive</span></div>
  <div id="chap"></div>
  <svg width="0" height="0" style="position:absolute">
    <defs>
      <marker id="mA" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#f2b134"/></marker>
      <marker id="mG" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#34d399"/></marker>
      <marker id="mR" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#f87171"/></marker>
      <marker id="mB" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#60a5fa"/></marker>
      <marker id="mV" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#a78bfa"/></marker>
    </defs>
  </svg>

{"".join(s.html() for s in scenes)}
</div>
<script src="timing.js"></script>
<script src="fv-runtime.js"></script>
<script>
{ENGINE}
{extra_js}
build();
FV.$$('.fv-scene').forEach((s) => FV.scene(s.dataset.scene, generic));
</script>
</body>
</html>
"""
    (folder / "index.html").write_text(doc)
    data = dict(meta)
    data["scenes"] = [s.json() for s in scenes]
    (folder / "video.json").write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n")
    words = sum(len(l.split()) for s in scenes for l in s.lines)
    print(f"wrote {folder}: {len(scenes)} scenes, {words} words (~{words / 150:.0f} min at 150 wpm)")
