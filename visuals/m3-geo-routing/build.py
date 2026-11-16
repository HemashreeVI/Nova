exec(open('../m3-gen.py').read())
K = "Module 3 · 11 · "
scenes = [
 {"id": "intro", "hero": 1, "k": "CCPS MODULE 3 · PART 3", "t": "Location-Based <span style='color:var(--a)'>Geographic Routing</span>", "b": [
   ("chips", 1, [("a", "Greedy"), ("b", "GPSR"), ("c", "GEAR"), ("e", "WEAR"), ("g", "GAF"), ("f", "GREES"), ("a", "BOSS"), ("b", "EBGRES"), ("d", "Secure routing")])]},
 {"id": "concepts", "k": K + "11.1", "t": "Key concepts", "b": [
   ("cards", 3, [(0, "a", "Step 1 · Locate", "Own + neighbours' location via <b>GPS</b> or <b>localization</b> (triangulation)"), (2, "b", "Step 2 · Share", "Nodes share locations with neighbours"), (3, "c", "Step 3 · Forward", "Based on source, neighbour &amp; destination locations")], 150),
   ("svg", "tri", 250),
   ("note", 4, "<b>Greedy forwarding:</b> send to the neighbour <b>closest to the destination</b>"),
   ("chips", 5, [("m", "greedy"), ("m", "stateless"), ("m", "on-demand — paths made only when needed")])]},
 {"id": "greedy", "k": K + "worked example", "t": "Greedy forwarding", "b": [("svg", "greedy", 620)]},
 {"id": "pros", "k": K + "11.2–11.4", "t": "Advantages, disadvantages, solutions", "b": [
   ("cards", 5, [((1, 0), "b", "Efficient", "greedy ≈ shortest path"), ((1, .5), "b", "Localized", "one-hop exchange, no flooding"), ((2, 0), "b", "Low memory", "stateless → scalable"), ((2, .35), "b", "Adaptive", "cheap periodic neighbour updates"), ((2, .7), "b", "Flexible", "add energy-aware, hole-avoiding")], 150),
   ("cards", 2, [(3, "d", "✗ Local minimum", "Stuck at a <b>hole</b>: no neighbour closer to destination than itself"), (4, "d", "✗ Path overuse", "Same best path reused → those nodes <b>die early</b>, imbalanced load")], 130),
   ("table", ["Problem", "Solution protocols"], [
     ((5, 0), ["Local minimum", "<b>GPSR</b> (perimeter), <b>WEAR</b> (hole info)"]), ((5, .2), ["Path overuse (energy-aware)", "<b>GEAR, WEAR, GREES</b>"]), ((5, .4), ["Control-message overhead (beaconless)", "<b>BOSS, EBGRES</b>"]),
     ((5, .6), ["Energy via sleep scheduling", "<b>GAF</b>"]), ((5, .8), ["Security (blackhole, selective forwarding)", "<b>Secure geographic routing</b>"])], 21)]},
 {"id": "gpsr", "k": K + "11.5", "t": "GPSR — Greedy Perimeter Stateless Routing", "b": [
   ("cards", 2, [(1, "b", "Mode 1 · Greedy (primary)", "While a neighbour closer to D exists"), (2, "d", "Mode 2 · Perimeter (fallback)", "At a local minimum: <b>planar graph</b> + <b>right-hand rule</b>")], 120),
   ("svg", "gpsr", 400),
   ("note", 5, "Reached a node <b>closer than where greedy failed</b>? → switch back to greedy. Solves local minimum, keeps greedy's efficiency.")]},
 {"id": "gear", "k": K + "11.6", "t": "GEAR — Geography &amp; Energy-Aware Routing", "b": [
   ("bul", [(1, "c", "<b>Dual criteria:</b> distance to destination + <b>residual energy</b>"), (2, "c", "Avoid overusing low-energy nodes; <b>composite metric</b>, prefer higher energy")], 24),
   ("eq", 3, "cost = α · (norm. distance) + (1 − α) · (norm. energy used) → choose min <span style='font:500 18px Inter;color:var(--mut)'>(illustration, not on slides)</span>"),
   ("cards", 2, [(4, "b", "Benefits", "Load distribution, no bottlenecks, longer lifetime"), (5, "d", "When greedy fails", "<b>Recursive geographic forwarding</b> · <b>restricted flooding</b>")], 110),
   ("svg", "gear", 220)]},
 {"id": "wear", "k": K + "11.7", "t": "WEAR — Wear-Evidence-Aware Routing", "b": [
   ("svg", "hole", 250),
   ("cards", 3, [(1, "e", "Hole detection", "Exchange location + activity; sparse area = hole; edge nodes = <b>boundary nodes</b>"), (3, "c", "Broadcast", "Hole info via <b>controlled flooding</b> → low overhead"), (4, "a", "4 decision factors", "distance · energy · location · <b>local hole info</b>")], 190),
   ("note", 5, "<b>Benefits:</b> hole avoidance · load balancing · fault tolerance (new holes)")]},
 {"id": "gaf", "k": K + "11.8", "t": "GAF — Geographical Adaptive Fidelity", "b": [
   ("note", 1, "<b>Virtual grid:</b> nodes in one cell are <b>equivalent</b> — any can reach any node in adjacent cells"),
   ("svg", "gaf", 250),
   ("cards", 3, [(2, "m", "Sleep", "Radio off; others keep the cell connected"), (3, "c", "Discovery", "Wake periodically, find cell neighbours, decide active/sleep"), (4, "b", "Active", "Routes; <b>one active node per cell</b>")], 120),
   ("note", 5, "Discovery → Active (chosen) / Sleep (another active) · Active → Discovery (time over) · Sleep → Discovery (timer)"),
   ("eq", 7, "4 nodes per cell, 1 awake → each awake ~25% → lifetime ≈ 4×", "b")]},
 {"id": "grees", "k": K + "11.9", "t": "GREES — Environmental Energy Supply", "b": [
   ("cards", 5, [(1, "a", "1 · Geo + energy", "Proximity &amp; route energy efficiency"), (2, "d", "2 · Real channels", "Attenuation, interference, varying links"), (3, "c", "3 · Packet advance", "Big progress per hop → fewer hops"), (4, "b", "4 · Residual energy", "High-energy nodes preferred"), (5, "g", "5 · Harvesting", "Solar-powered nodes preferred ☀")], 300),
   ("note", 6, "Realistic model · load balancing · longer lifetime. <b>Sunny day:</b> solar node chosen over battery-only node at similar distance.")]},
 {"id": "boss", "k": K + "11.10–11.11", "t": "BOSS &amp; EBGRES — beaconless", "b": [
   ("note", 1, "Problem: periodic <b>beacons</b> for neighbour tables = big overhead → BOSS: <b>the DATA message is the probe</b>"),
   ("svg", "boss", 300),
   ("note", 6, "<b>Adapts</b> to mobility &amp; link changes (probes every transmission) · efficient · real-time · less congestion"),
   ("cards", 1, [(7, "b", "EBGRES", "Like BOSS: beaconless, fewer control messages, uses <b>DATA · ACK · SELECT</b> — plus considers <b>environmental energy (solar)</b> → energy-harvesting networks")])]},
 {"id": "secure", "k": K + "11.12", "t": "Secure geographic routing", "b": [
   ("note", 0, "Threats: <b style='color:var(--d)'>blackhole</b> (drop all) · <b style='color:var(--d)'>selective forwarding</b> (drop some)"),
   ("table", ["Mechanism", "Counters", "How"], [
     (1, ["<b>Rate control</b>", "Packet-overflow (DoS)", "Node estimates max rate it can handle, drops excess"]),
     (2, ["<b>Forwarding verification</b>", "Blackhole &amp; selective fwd", "Ask a trusted peer (anchor) to confirm forwarding"]),
     (3, ["<b>Probabilistic next hop</b>", "Predictable routing", "Random among suitable neighbours → route unpredictable"]),
     (4, ["<b>Multi-path routing</b>", "Blackhole &amp; selective fwd", "Several paths; one compromised, others deliver"])], 24)]},
 {"id": "recap", "endl": 5, "k": "Exam recap", "t": "Remember these", "b": [
   ("bul", [(1, "a", "Locate (GPS/triangulation) → share → <b>greedy</b> to neighbour closest to destination"),
            (2, "d", "Local minimum → <b>GPSR</b> (perimeter, right-hand rule) / <b>WEAR</b> (hole info)"),
            (3, "c", "Path overuse → <b>GEAR, WEAR, GREES</b> · Beaconless → <b>BOSS, EBGRES</b> (DATA, ACK, SELECT)"),
            (4, "b", "Virtual grid sleep → <b>GAF</b> · Security → rate control, verification, probabilistic, multi-path")], 26)]},
]
JS = r"""
DIAG.tri = (svg) => {
  const U = [840, 140]; const A = [[600, 60, 'Anchor 1'], [1080, 70, 'Anchor 2'], [840, 300, 'Anchor 3']];
  const g = mk('g', {}, svg);
  A.forEach(([x, y, n]) => { const r = Math.hypot(U[0] - x, U[1] - y); mk('circle', { cx: x, cy: y, r, fill: 'none', stroke: COL.a, 'stroke-width': 2, 'stroke-dasharray': '6 6', 'stroke-opacity': .7 }, g); node(g, x, y, 14, '', COL.a); mk('text', { x: x + (x < 840 ? -20 : 20), y: y - 18, 'text-anchor': x < 840 ? 'end' : 'start', fill: COL.a, 'font-size': 20, 'font-weight': 700 }, g, n); });
  node(g, U[0], U[1], 16, '?', COL.c, 18); mk('text', { x: 1260, y: 150, fill: COL.c, 'font-size': 22, 'font-weight': 700 }, g, 'unknown node = intersection');
  return (t, ctx) => fade(g, t, ctx, 1);
};
DIAG.greedy = (svg) => {
  const X = (x) => 260 + (x + 3) * 85, Y = (y) => 330 - y * 85;
  const ax = mk('g', {}, svg);
  mk('line', { x1: X(-3), y1: Y(0), x2: X(11), y2: Y(0), stroke: 'rgba(148,163,200,.3)', 'stroke-width': 2 }, ax);
  for (let i = -2; i <= 10; i += 2) mk('text', { x: X(i), y: Y(0) + 34, 'text-anchor': 'middle', fill: COL.mut, 'font-size': 18 }, ax, i);
  const S = node(svg, X(0), Y(0), 26, 'S', COL.a), D = node(svg, X(10), Y(0), 26, 'D', COL.b);
  mk('text', { x: X(10), y: Y(0) - 40, 'text-anchor': 'middle', fill: COL.b, 'font-size': 20 }, svg, '(10, 0)');
  const nb = [['A', 3, 2, '√(7²+2²) = √53 ≈ 7.3', 2], ['B', 4, 0, '10 − 4 = 6', 3], ['C', -2, 1, '√(12²+1²) ≈ 12', 4]];
  const gs = nb.map(([n, x, y, d, l]) => { const g = mk('g', {}, svg); mk('line', { x1: X(x), y1: Y(y), x2: X(10), y2: Y(0), stroke: COL.mut, 'stroke-width': 2, 'stroke-dasharray': '6 6' }, g); node(g, X(x), Y(y), 22, n, COL.e, 20); mk('text', { x: X(x), y: Y(y) - 34, 'text-anchor': 'middle', fill: COL.ink, 'font-size': 20 }, g, `(${x}, ${y})`); mk('text', { x: X(x) + (n === 'B' ? 0 : 30), y: Y(y) + (n === 'B' ? 60 : -60), 'text-anchor': n === 'C' ? 'end' : 'start', fill: COL.c, 'font-size': 22, 'font-weight': 700 }, g, 'to D: ' + d); return [g, l]; });
  const win = arrow(svg, X(0) + 28, Y(0), X(4) - 24, Y(0), COL.b, { label: 'S → B (closest)', fs: 24, ly: Y(0) + 100 });
  return (t, ctx) => { gs.forEach(([g, l]) => fade(g, t, ctx, l)); win(t, at(ctx, 5, .1)); };
};
DIAG.gpsr = (svg) => {
  const P = { S: [100, 300], X: [450, 300], P1: [600, 120], P2: [900, 80], D: [1500, 280], Q: [1200, 300] };
  const hole = mk('ellipse', { cx: 800, cy: 300, rx: 260, ry: 80, fill: 'rgba(248,113,113,.1)', stroke: COL.d, 'stroke-width': 2, 'stroke-dasharray': '8 6' }, svg);
  mk('text', { x: 800, y: 308, 'text-anchor': 'middle', fill: COL.d, 'font-size': 24, 'font-weight': 800 }, svg, 'HOLE');
  Object.entries(P).forEach(([n, [x, y]]) => node(svg, x, y, 26, n, n === 'X' ? COL.d : n === 'D' ? COL.b : COL.a, n.length > 1 ? 18 : 22));
  const a1 = arrow(svg, 128, 300, 422, 300, COL.b, { label: 'greedy', fs: 22 });
  const xt = mk('text', { x: 450, y: 370, 'text-anchor': 'middle', fill: COL.d, 'font-size': 21, 'font-weight': 700 }, svg, 'stuck: local minimum');
  const a2 = arrow(svg, 470, 280, 585, 140, COL.c, { label: 'perimeter', fs: 21, lx: 480, ly: 190 }), a3 = arrow(svg, 625, 115, 872, 85, COL.c, { label: 'right-hand rule', fs: 21, ly: 70 });
  const a4 = arrow(svg, 925, 90, 1180, 285, COL.b, { label: 'P2 closer than X → greedy', fs: 21, lx: 1150, ly: 170 }), a5 = arrow(svg, 1226, 297, 1472, 283, COL.b);
  return (t, ctx) => { a1(t, at(ctx, 1, .2)); xt.style.opacity = seg(t, at(ctx, 2, 0), at(ctx, 2, .3)); a2(t, at(ctx, 3, .2)); a3(t, at(ctx, 4, .2)); a4(t, at(ctx, 5, .2)); a5(t, at(ctx, 5, .6)); };
};
DIAG.gear = (svg) => {
  const g = mk('g', {}, svg); node(g, 120, 110, 30, 'S', COL.a); node(g, 1540, 110, 30, 'D', COL.b);
  node(g, 700, 50, 28, 'A', COL.d); node(g, 800, 175, 28, 'B', COL.b);
  mk('text', { x: 740, y: 30, fill: COL.d, 'font-size': 21, 'font-weight': 700 }, g, 'A: 5 m to D, battery 10% ← pure greedy');
  mk('text', { x: 840, y: 215, fill: COL.b, 'font-size': 21, 'font-weight': 700 }, g, 'B: 6 m to D, battery 90% ← GEAR picks');
  const a = arrow(svg, 150, 120, 770, 170, COL.b, { label: '', fs: 1 });
  return (t, ctx) => { fade(g, t, ctx, 6); a(t, at(ctx, 6, .6)); };
};
DIAG.hole = (svg) => {
  const r = FV.rand(5); const g = mk('g', {}, svg);
  mk('ellipse', { cx: 840, cy: 125, rx: 250, ry: 95, fill: 'rgba(248,113,113,.08)', stroke: COL.d, 'stroke-width': 2, 'stroke-dasharray': '8 6' }, g);
  mk('text', { x: 840, y: 133, 'text-anchor': 'middle', fill: COL.d, 'font-size': 24, 'font-weight': 800 }, g, 'hole: no active sensors');
  for (let i = 0; i < 70; i++) { const x = 80 + r() * 1520, y = 15 + r() * 220; const dx = (x - 840) / 250, dy = (y - 125) / 95; const d = dx * dx + dy * dy; if (d < 1) continue; mk('circle', { cx: x, cy: y, r: 8, fill: d < 1.7 ? COL.c : COL.mut }, g); }
  mk('text', { x: 1500, y: 245, 'text-anchor': 'end', fill: COL.c, 'font-size': 20, 'font-weight': 700 }, g, '● boundary nodes');
  return (t, ctx) => fade(g, t, ctx, 0, .3);
};
DIAG.gaf = (svg) => {
  const cells = [[2, 0], [3, 1], [2, 2]]; const gs = [];
  cells.forEach(([n], k) => {
    const x = 120 + k * 520; mk('rect', { x, y: 20, width: 420, height: 210, rx: 16, fill: 'rgba(13,20,42,.6)', stroke: 'rgba(148,163,200,.4)', 'stroke-width': 2, 'stroke-dasharray': '8 6' }, svg);
    mk('text', { x: x + 14, y: 48, fill: COL.mut, 'font-size': 19 }, svg, 'grid cell ' + (k + 1));
    const ns = []; for (let i = 0; i <= n; i++) { const c = mk('circle', { cx: x + 90 + i * 110, cy: 140, r: 26 }, svg); ns.push(c); }
    gs.push(ns);
  });
  return (t, ctx) => { gs.forEach((ns, k) => { const act = Math.floor((t / 3 + k) % ns.length); ns.forEach((c, i) => { c.setAttribute('fill', i === act ? COL.b : '#334155'); c.setAttribute('stroke', i === act ? '#fff' : 'none'); c.setAttribute('stroke-width', 3); }); }); };
};
DIAG.boss = (svg) => {
  const S = [200, 150]; const A = [900, 60]; const B = [900, 240];
  node(svg, S[0], S[1], 34, 'S', COL.a); node(svg, A[0], A[1], 30, 'A', COL.b); node(svg, B[0], B[1], 30, 'B', COL.mut);
  const m = [arrow(svg, 238, 140, 865, 65, COL.a, { label: '1 · DATA (broadcast probe)', fs: 21, lx: 520, ly: 70 }), arrow(svg, 238, 160, 865, 235, COL.a),
    arrow(svg, 870, 85, 245, 160, COL.b, { label: '2–3 · response / ACK (good link, closer)', fs: 21, lx: 1150, ly: 130 }),
    arrow(svg, 870, 215, 245, 175, COL.mut)];
  const sel = arrow(svg, 240, 120, 868, 45, COL.c, { label: '4 · SELECT A as forwarder', fs: 22, lx: 1220, ly: 50 });
  return (t, ctx) => { m[0](t, at(ctx, 2, .2)); m[1](t, at(ctx, 2, .3)); m[2](t, at(ctx, 3, .2)); m[3](t, at(ctx, 3, .4)); sel(t, at(ctx, 5, .2)); };
};
"""
build("CCPS Module 3 Part 3", scenes, JS, "index.html")
