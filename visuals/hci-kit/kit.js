/*
 * hci-kit: declarative animation attributes on top of the full-visual runtime.
 * Time spec: "2.5" = line 2, 50% through it; "@1.2" = 1.2 s into scene; "end" = scene end;
 *            any spec can add "+0.4" / "-0.4" seconds.
 *   data-in="spec"           fade + rise in       (data-pop: spring scale-in instead)
 *   data-out="spec"          fade out
 *   data-hl="spec~spec"      highlight (scale + --hl glow) during range
 *   data-on="spec"           add class "on" from spec onward
 *   data-strike="spec"       add class "struck" from spec onward
 *   data-move="a~b:x,y;c~d:x,y"  piecewise translate
 *   data-grow="a~b"          scaleX 0→1
 *   data-type="a~b"          typewriter
 *   data-count="a~b:from,to[,dec]"
 *   data-click="spec,spec"   press (scale dip) at these times
 *   data-shake="spec"        shake for 0.5 s
 *   data-base="css transform" prepended to computed transform
 */
(function () {
  const { seg, pulse, ease, clamp, lerp } = FV;
  const SEL = '[data-rot],[data-in],[data-out],[data-hl],[data-on],[data-move],[data-grow],[data-type],[data-count],[data-click],[data-shake],[data-strike]';
  const custom = {};
  function T(spec, ctx) {
    spec = String(spec).trim();
    let off = 0;
    const m = spec.match(/^(.*?)([+-]\d*\.?\d+)$/);
    if (m && m[1] !== '') { spec = m[1]; off = +m[2]; }
    let base;
    if (spec === 'end') base = ctx.dur;
    else if (spec[0] === '@') base = +spec.slice(1);
    else { const v = +spec, i = Math.floor(v), f = v - i; base = ctx.line(i) + (ctx.lineEnd(i) - ctx.line(i)) * f; }
    return base + off;
  }
  const range = (s, ctx) => { const [a, b] = s.split('~'); return [T(a, ctx), T(b, ctx)]; };
  function apply(root, t, ctx) {
    root.querySelectorAll(SEL).forEach((el) => {
      const d = el.dataset;
      let o = 1, x = 0, y = 0, s = 1, sx = 1, rot = 0;
      if (d.in) {
        const a = T(d.in, ctx);
        if (d.pop !== undefined) { const p = seg(t, a, a + 0.55, ease.back); o *= clamp(seg(t, a, a + 0.25, ease.out)); s *= lerp(0.4, 1, p); }
        else { const p = seg(t, a, a + 0.6, ease.out); o *= p; y += (1 - p) * 26; }
      }
      if (d.out) { const b = T(d.out, ctx); o *= 1 - seg(t, b, b + 0.4); }
      if (d.hl) {
        let h = 0;
        d.hl.split(',').forEach((r) => { const [a, b] = range(r, ctx); h = Math.max(h, seg(t, a, a + 0.3) * (1 - seg(t, b, b + 0.3))); });
        s *= 1 + 0.05 * h; el.style.setProperty('--hl', h.toFixed(3));
      }
      if (d.on) el.classList.toggle('on', t >= T(d.on, ctx));
      if (d.strike) el.classList.toggle('struck', t >= T(d.strike, ctx));
      if (d.move) {
        d.move.split(';').forEach((st) => {
          const [r, xy] = st.split(':'); const [a, b] = range(r, ctx); const [tx, ty] = xy.split(',').map(Number);
          const p = seg(t, a, b, ease.inOut); x = lerp(x, tx, p); y = lerp(y, ty, p);
        });
      }
      if (d.rot) d.rot.split(';').forEach((st) => { const [r, deg] = st.split(':'); const [a, b] = range(r, ctx); rot = lerp(rot, +deg, seg(t, a, b, ease.inOut)); });
      if (d.grow) { const [a, b] = range(d.grow, ctx); sx = seg(t, a, b, ease.inOut); }
      if (d.type) { if (el._txt === undefined) el._txt = el.textContent; const [a, b] = range(d.type, ctx); el.textContent = FV.type(el._txt, seg(t, a, b, ease.linear)); }
      if (d.count) {
        const [r, v] = d.count.split(':'); const [a, b] = range(r, ctx); const [f, to, dec] = v.split(',').map(Number);
        el.textContent = lerp(f, to, seg(t, a, b, ease.out)).toFixed(dec || 0);
      }
      if (d.click) d.click.split(',').forEach((c) => { const a = T(c, ctx); s *= 1 - 0.18 * pulse(t, a, a + 0.3); });
      if (d.shake) { const a = T(d.shake, ctx); x += Math.sin((t - a) * 50) * 14 * pulse(t, a, a + 0.5); }
      el.style.opacity = o;
      el.style.transform = `${d.base || ''} translate(${x}px,${y}px) scale(${s}) scaleX(${sx}) rotate(${rot}deg)`;
    });
  }
  window.K = {
    T, apply,
    scene(id, fn) { custom[id] = fn; },
    init() {
      FV.$$('.fv-scene').forEach((el) => {
        const id = el.dataset.scene, fn = custom[id];
        FV.scene(id, (t, ctx) => { apply(ctx.el, t, ctx); if (fn) fn(t, ctx); });
      });
    },
    cursorSVG: '<svg viewBox="0 0 44 52" width="44" height="52"><path d="M3 3 L3 42 L13 32 L20 49 L28 45 L21 29 L36 29 Z" fill="#fff" stroke="#000" stroke-width="3" stroke-linejoin="round"/></svg>',
  };
  // fill <div class="cursor"></div> elements with the arrow
  addEventListener('DOMContentLoaded', () => FV.$$('.cursor').forEach((c) => { if (!c.innerHTML.trim()) c.innerHTML = K.cursorSVG; }));
})();
