exec(open('../m3-gen.py').read())
K = "Module 3 · "
scenes = [
 {"id": "intro", "hero": 1, "k": "CCPS MODULE 3 · PART 4", "t": "Data-Centric &amp; <span style='color:var(--a)'>Hierarchical Routing</span>", "b": [
   ("chips", 1, [("a", "Flooding"), ("a", "Gossiping"), ("b", "SPIN"), ("b", "Directed Diffusion"), ("c", "LEACH"), ("e", "PEGASIS"), ("g", "TEEN")])]},
 {"id": "why", "k": K + "12.1–12.2", "t": "Why data-centric routing?", "b": [
   ("cards", 3, [(1, "d", "No unique IDs", "Too many sensors for global IDs"), (2, "d", "Random deployment", "Topology unknown — can't address \"node 57\""), (3, "d", "Redundant transmission", "Every sensor in an area sends the same data → energy wasted")], 150),
   ("eq", 4, "Ask by <b>WHAT</b> the data is: \"temperature &gt; 40°C in region R\" — not by <b>WHICH</b> node", "b"),
   ("chips", 5, [("a", "selective node usage"), ("a", "aggregation while relaying"), ("a", "query to regions")]),
   ("cards", 2, [(6, "b", "SPIN", "First data-centric protocol — <b>negotiation</b> removes redundant data"), ((6, .5), "e", "Directed Diffusion", "Improves on SPIN — foundation for later research")], 120)]},
 {"id": "flood", "k": K + "12.3", "t": "Flooding (baseline)", "b": [
   ("note", 0, "Broadcast to <b>all neighbours</b> until destination or max hop count · ✓ very simple, no routing or topology maintenance"),
   ("svg", "flood", 260),
   ("cards", 3, [(2, "d", "Implosion", "Same message reaches a node many times (D gets A's packet twice)"), (3, "d", "Overlap", "Nodes sensing the same region send similar data"), (4, "d", "Energy exhaustion", "Huge redundant traffic drains batteries")], 160)]},
 {"id": "gossip", "k": K + "12.4", "t": "Gossiping", "b": [
   ("note", 0, "Modified flooding: send to <b>one random neighbour</b>, which repeats"),
   ("cards", 2, [(1, "b", "✓ Advantage", "Fewer copies → <b>avoids implosion</b>"), (2, "d", "✗ Disadvantages", "<b>Propagation delay</b> (random route); packet may move <b>away</b> or <b>loop</b> and fail")], 130),
   ("table", ["", "Flooding", "Gossiping"], [(3, ["<b>Sends to</b>", "All neighbours", "One random neighbour"]), (3, ["<b>Implosion</b>", "Yes", "Avoided"]), (4, ["<b>Delay</b>", "Low", "High"]), (4, ["<b>Delivery</b>", "Almost guaranteed", "Not guaranteed (loops)"]), (4, ["<b>Energy</b>", "Very high", "Lower"])], 25)]},
 {"id": "spin", "k": K + "12.5", "t": "SPIN — negotiation", "b": [
   ("chips", 2, [("c", "ADV · \"I have new data (metadata)\""), ("a", "REQ · \"I'm interested, send it\""), ("b", "DATA · actual sensor data")]),
   ("svg", "spin", 330),
   ("cards", 2, [(5, "b", "✓ Advantages", "Solves implosion, overlap, energy exhaustion; only <b>single-hop</b> knowledge"), (6, "d", "✗ Limitations", "<b>No delivery guarantee</b> — stops at an uninterested middle node; not for mission-critical CPS")], 140)]},
 {"id": "dd", "k": K + "12.6", "t": "Directed Diffusion", "b": [
   ("eq", 1, "interest: type = vehicle · interval = 20 ms · duration = 10 s · rect = [-100, 100, 200, 400]", "e"),
   ("svg", "dd", 300),
   ("cards", 2, [(6, "b", "✓ Advantages", "No unique addressing · caching cuts delay · energy-efficient, on-demand"), (7, "d", "✗ Limitation", "Poor for <b>continuous monitoring / real-time</b> (battlefield, traffic, environment)")], 130)]},
 {"id": "spindd", "k": K + "12", "t": "SPIN vs Directed Diffusion", "b": [
   ("table", ["", "SPIN", "Directed Diffusion"], [(1, ["<b>Who starts</b>", "Source advertises (<b>push</b>)", "Sink queries with interest (<b>pull</b>)"]), (2, ["<b>Data naming</b>", "Metadata", "Attribute-value pairs"]), (3, ["<b>Delivery</b>", "No guarantee", "Better (multi-path, reinforcement)"]), (4, ["<b>Good for</b>", "Small networks, interested nodes", "Query-driven applications"])], 28)]},
 {"id": "hier", "k": K + "13", "t": "Hierarchical routing", "b": [("svg", "hier", 480), ("note", 1, "Higher levels <b>aggregate &amp; forward</b> → most nodes transmit only short distances")]},
 {"id": "leach", "k": K + "13.1", "t": "LEACH — Low-Energy Adaptive Clustering Hierarchy", "b": [
   ("cards", 3, [(1, "c", "Clustering", "1 CH + members; CH aggregates → BS"), (2, "e", "Random CH rotation", "Probability-based; recent CHs less likely again"), (3, "b", "Aggregation", "CH compresses member data")], 140),
   ("svg", "leach", 420)]},
 {"id": "thresh", "k": K + "13.1 · extra for full marks (not on slides)", "t": "LEACH CH election threshold", "b": [
   ("eq", 2, "T(n) = P / [ 1 − P × (r mod 1/P) ]   if n not CH in last 1/P rounds, else 0"),
   ("note", 3, "Node becomes CH if random(0,1) &lt; T(n) · P = desired CH fraction · r = current round"),
   ("table", ["P = 0.05 → 1/P = 20", "Calculation", "T(n)"], [(5, ["Round 0", "0.05 / (1 − 0)", "<b>0.05</b>"]), (5, ["Round 10", "0.05 / (1 − 0.5)", "<b>0.10</b>"]), (6, ["Round 19", "0.05 / (1 − 0.95)", "<b>1</b> → all remaining become CH"])], 24),
   ("cards", 2, [(7, "b", "✓ Advantages", "Energy efficiency · scalability · self-organising"), (8, "d", "✗ Disadvantages", "Uneven random CHs · single-hop CH→BS · setup overhead (dynamic nets)")], 120)]},
 {"id": "pegasis", "k": K + "13.2", "t": "PEGASIS — chain-based", "b": [
   ("chips", 1, [("e", "greedy chain from farthest node"), ("e", "rotating leader"), ("e", "fuse along chain"), ("e", "only leader → BS")]),
   ("svg", "chain", 200),
   ("cards", 2, [(6, "b", "✓ vs LEACH", "Close-neighbour talk only · 1 BS transmission/round · no cluster formation"), (7, "d", "✗ Disadvantages", "Latency · scalability · chain rebuild overhead · single point of failure")], 120),
   ("table", ["", "LEACH", "PEGASIS"], [(8, ["Structure · talks to BS", "Clusters · every CH", "Chain · only leader"]), ((8, .5), ["Energy · latency · failure", "Good · lower · one cluster", "Better · higher · whole chain"])], 21)]},
 {"id": "teen", "k": K + "13.3", "t": "TEEN — threshold-sensitive", "b": [
   ("cards", 2, [(2, "d", "Hard threshold (HT)", "Absolute value: transmit only when value &gt; HT"), (3, "c", "Soft threshold (ST)", "After first send: again only if change ≥ ST")], 110),
   ("table", ["Reading (HT 50, ST 2)", "&gt; HT?", "Change from last sent", "Transmit?"], [(5, ["45", "No", "–", "No"]), (5, ["51", "Yes", "first crossing", "<b style='color:var(--b)'>Yes</b> (last = 51)"]), (6, ["52", "Yes", "1 &lt; 2", "No"]), (6, ["53.5", "Yes", "2.5 ≥ 2", "<b style='color:var(--b)'>Yes</b> (last = 53.5)"]), (7, ["49", "No", "–", "No"])], 22),
   ("note", 7, "<b>2 transmissions instead of 5</b> → energy saved · phases: cluster formation → threshold broadcast → transmission → aggregation"),
   ("note", 9, "<span style='color:var(--d)'>Drawback (general knowledge):</span> threshold never reached → BS can't tell quiet from dead")]},
 {"id": "glance", "k": K + "13.4", "t": "Hierarchical protocols at a glance", "b": [
   ("table", ["", "LEACH", "PEGASIS", "TEEN"], [(1, ["<b>Structure</b>", "Clusters, rotating CH", "Chain, rotating leader", "Clusters + thresholds"]), (1, ["<b>Sending</b>", "Periodic (TDMA)", "Periodic along chain", "Reactive (threshold)"]), (2, ["<b>Best for</b>", "Periodic monitoring", "Max energy saving", "Time-critical events"]), (3, ["<b>Weakness</b>", "Uneven CHs, single-hop to BS", "Latency, chain breaks", "Silent when no event"])], 26)]},
 {"id": "recap", "endl": 6, "k": "Last-minute one-liners", "t": "Whole module in 6 lines", "b": [
   ("bul", [(1, "c", "Energy ∝ d² → <b>multi-hop</b> saves energy"),
            (2, "d", "Local minimum → <b>GPSR</b> / <b>WEAR</b> · path overuse → <b>GEAR, WEAR, GREES</b>"),
            (3, "a", "Beaconless → <b>BOSS, EBGRES</b> (DATA, ACK, SELECT) · virtual grid sleep → <b>GAF</b>"),
            (4, "b", "<b>SPIN</b> = ADV → REQ → DATA (push) · <b>DD</b> = interest → gradient → reinforcement (pull)"),
            (5, "e", "<b>LEACH</b> = setup + steady, TDMA, random CH · <b>PEGASIS</b> = chain + leader · <b>TEEN</b> = HT + ST")], 26)]},
]
JS = r"""
DIAG.flood = (svg) => {
  const P = { A: [300, 130], B: [700, 40], C: [700, 220], D: [1100, 130] }; Object.entries(P).forEach(([n, [x, y]]) => node(svg, x, y, 32, n, n === 'D' ? COL.d : COL.a, 24));
  const a = [arrow(svg, 330, 115, 668, 50, COL.a), arrow(svg, 330, 145, 668, 210, COL.a), arrow(svg, 730, 50, 1068, 118, COL.d), arrow(svg, 730, 210, 1068, 142, COL.d)];
  const lab = mk('text', { x: 1160, y: 140, fill: COL.d, 'font-size': 24, 'font-weight': 800 }, svg, 'D gets A\'s packet TWICE');
  return (t, ctx) => { a[0](t, at(ctx, 0, .3)); a[1](t, at(ctx, 0, .3)); a[2](t, at(ctx, 2, .1)); a[3](t, at(ctx, 2, .2)); lab.style.opacity = seg(t, at(ctx, 2, .5), at(ctx, 2, .8)); };
};
DIAG.spin = (svg) => {
  node(svg, 150, 160, 40, 'A', COL.a, 26); node(svg, 750, 160, 40, 'B', COL.e, 26); [[1400, 50, 1], [1400, 160, 1], [1400, 270, 0]].forEach(([x, y, i]) => node(svg, x, y, 30, i ? 'C' : 'x', i ? COL.b : COL.mut, 20));
  mk('text', { x: 1450, y: 290, fill: COL.mut, 'font-size': 18 }, svg, 'not interested');
  const m = [arrow(svg, 195, 130, 705, 130, COL.c, { label: '1 · ADV', fs: 22 }), arrow(svg, 705, 160, 195, 160, COL.a, { label: '2 · REQ', fs: 22, ly: 152 }), arrow(svg, 195, 190, 705, 190, COL.b, { label: '3 · DATA', fs: 22, ly: 225 }),
    arrow(svg, 795, 145, 1365, 55, COL.c, { label: '4 · ADV', fs: 22, lx: 1000, ly: 70 }), arrow(svg, 795, 160, 1365, 160, COL.c), arrow(svg, 795, 175, 1365, 265, COL.c),
    arrow(svg, 1365, 70, 800, 155, COL.a, { label: '5 · REQ', fs: 22, lx: 1180, ly: 120 }), arrow(svg, 795, 200, 1365, 180, COL.b, { label: '6 · DATA', fs: 22, lx: 1100, ly: 225 })];
  return (t, ctx) => { m[0](t, at(ctx, 3, 0)); m[1](t, at(ctx, 3, .3)); m[2](t, at(ctx, 3, .6)); m[3](t, at(ctx, 4, 0)); m[4](t, at(ctx, 4, 0)); m[5](t, at(ctx, 4, 0)); m[6](t, at(ctx, 4, .4)); m[7](t, at(ctx, 4, .75)); };
};
DIAG.dd = (svg) => {
  const pan = ['a · Interest propagation', 'b · Gradients set up', 'c · Data on reinforced path'];
  const gs = pan.map((p, k) => { const g = mk('g', {}, svg); const x = k * 560; mk('rect', { x: x + 10, y: 10, width: 520, height: 280, rx: 16, fill: 'rgba(13,20,42,.7)', stroke: 'rgba(148,163,200,.3)', 'stroke-width': 2 }, g);
    mk('text', { x: x + 30, y: 50, fill: COL.ink, 'font-size': 22, 'font-weight': 800 }, g, p);
    const sink = [x + 90, 170], mid = [[x + 270, 110], [x + 270, 230]], src = [x + 450, 170];
    mid.forEach(([mx, my], i) => {
      if (k === 0) { arrow(g, sink[0] + 30, sink[1], mx - 22, my, COL.e)(1e9, 0); arrow(g, mx + 22, my, src[0] - 26, src[1], COL.e)(1e9, 0); }
      if (k === 1) { arrow(g, src[0] - 26, src[1], mx + 22, my, COL.c, { dash: '8 6' })(1e9, 0); arrow(g, mx - 22, my, sink[0] + 30, sink[1], COL.c, { dash: '8 6' })(1e9, 0); }
      if (k === 2 && i === 0) { arrow(g, src[0] - 26, src[1], mx + 22, my, COL.b, { w: 7 })(1e9, 0); arrow(g, mx - 22, my, sink[0] + 30, sink[1], COL.b, { w: 7 })(1e9, 0); }
      node(g, mx, my, 20, 'n', COL.mut, 16); });
    node(g, sink[0], sink[1], 30, 'Sink', COL.a, 16); node(g, src[0], src[1], 26, 'Src', COL.g, 16);
    return g; });
  return (t, ctx) => { fade(gs[0], t, ctx, 1, .5); fade(gs[1], t, ctx, 2); fade(gs[2], t, ctx, 3); };
};
DIAG.hier = (svg) => {
  const BS = boxS(svg, 690, 10, 300, 70, 'Base station', '', COL.a, 26);
  const c2 = node(svg, 840, 160, 36, 'CH²', COL.e, 20); mk('text', { x: 900, y: 168, fill: COL.e, 'font-size': 20 }, svg, '2nd-level CH');
  const c1 = [[540, 290], [1140, 290]].map(([x, y]) => node(svg, x, y, 32, 'CH¹', COL.c, 18));
  mk('text', { x: 1200, y: 298, fill: COL.c, 'font-size': 20 }, svg, '1st-level CH');
  const ns = []; [[440, 420], [640, 420], [1040, 420], [1240, 420]].forEach(([x, y]) => ns.push(node(svg, x, y, 22, '', COL.mut)));
  const ar = [arrow(svg, 450, 400, 525, 315, COL.mut), arrow(svg, 630, 400, 555, 315, COL.mut), arrow(svg, 1050, 400, 1125, 315, COL.mut), arrow(svg, 1230, 400, 1155, 315, COL.mut), arrow(svg, 565, 270, 810, 180, COL.c), arrow(svg, 1115, 270, 870, 180, COL.c), arrow(svg, 840, 122, 840, 85, COL.e)];
  return (t, ctx) => ar.forEach((f, k) => f(t, at(ctx, 0, .3) + k * 0.3));
};
DIAG.leach = (svg) => {
  const setup = mk('g', {}, svg); mk('rect', { x: 0, y: 0, width: 820, height: 410, rx: 18, fill: 'rgba(167,139,250,.07)', stroke: COL.e, 'stroke-width': 3 }, setup);
  mk('text', { x: 24, y: 40, fill: COL.e, 'font-size': 26, 'font-weight': 800 }, setup, '1 · Setup phase');
  ['① nodes self-elect CH (probability); CHs advertise', '② non-CH joins CH with strongest signal', '③ each CH makes a TDMA schedule'].forEach((s, k) => mk('text', { x: 24, y: 90 + k * 40, fill: COL.ink, 'font-size': 22 }, setup, s));
  const ss = mk('g', {}, svg); mk('rect', { x: 860, y: 0, width: 820, height: 410, rx: 18, fill: 'rgba(52,211,153,.07)', stroke: COL.b, 'stroke-width': 3 }, ss);
  mk('text', { x: 884, y: 40, fill: COL.b, 'font-size': 26, 'font-weight': 800 }, ss, '2 · Steady-state phase');
  ['④ members send in TDMA slots (radio off otherwise)', '⑤ CH aggregates → sends to BS', '⑥ round time over → back to setup, new CHs'].forEach((s, k) => mk('text', { x: 884, y: 90 + k * 40, fill: COL.ink, 'font-size': 22 }, ss, s));
  const cl = [[200, 320], [600, 320]].map(([x, y]) => { const g = mk('g', {}, setup); [-90, 0, 90].forEach((dx) => { mk('line', { x1: x + dx, y1: y + 60, x2: x, y2: y, stroke: COL.mut, 'stroke-width': 2 }, g); node(g, x + dx, y + 60, 14, '', COL.mut); }); node(g, x, y, 26, 'CH', COL.c, 16); return g; });
  const slots = [...Array(6)].map((_, k) => mk('rect', { x: 900 + k * 120, y: 290, width: 110, height: 50, rx: 8, fill: COL.mut }, ss));
  mk('text', { x: 900, y: 375, fill: COL.mut, 'font-size': 19 }, ss, 'TDMA frame: one slot per member');
  return (t, ctx) => { fade(setup, t, ctx, 4); fade(ss, t, ctx, 6); const k = Math.floor((t * 2) % 6); slots.forEach((s, i) => s.setAttribute('fill', i === k ? COL.b : '#334155')); };
};
DIAG.chain = (svg) => {
  const xs = [150, 400, 700, 1000, 1250]; const ns = xs.map((x, k) => node(svg, x, 130, 32, String(k), k === 2 ? COL.c : COL.e, 24));
  mk('text', { x: 700, y: 85, 'text-anchor': 'middle', fill: COL.c, 'font-size': 20, 'font-weight': 800 }, svg, 'leader');
  const bs = boxS(svg, 1420, 10, 240, 70, 'Base station', '', COL.a, 22);
  const a = [arrow(svg, 185, 130, 365, 130, COL.e, { label: 'raw', fs: 18 }), arrow(svg, 435, 130, 665, 130, COL.e, { label: 'fused', fs: 18 }), arrow(svg, 1215, 130, 1035, 130, COL.e, { label: 'raw', fs: 18 }), arrow(svg, 965, 130, 735, 130, COL.e, { label: 'fused', fs: 18 }), arrow(svg, 730, 105, 1415, 50, COL.c, { label: 'one fused packet', fs: 20, lx: 1100, ly: 58 })];
  return (t, ctx) => { a[0](t, at(ctx, 5, .2)); a[1](t, at(ctx, 5, .35)); a[2](t, at(ctx, 5, .5)); a[3](t, at(ctx, 5, .65)); a[4](t, at(ctx, 5, .85)); };
};
"""
build("CCPS Module 3 Part 4", scenes, JS, "index.html")
