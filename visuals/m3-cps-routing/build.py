exec(open('../m3-gen.py').read())
K = "Module 3 · "
scenes = [
 {"id": "intro", "hero": 1, "k": "CCPS MODULE 3 · PART 2", "t": "CPS Architectures &amp; <span style='color:var(--a)'>Routing Challenges</span>", "b": [
   ("chips", 1, [("m", "CPS architectures"), ("m", "Healthcare · smart space · emergency · transport"), ("m", "Role of WSN"), ("m", "8 routing challenges"), ("m", "Classification")])]},
 {"id": "overview", "k": K + "7.1–7.3", "t": "CPS overview &amp; high-level architectures", "b": [
   ("cards", 2, [(0, "m", "Diverse definitions", "Vary by application domain — <b>no consensus</b> on one definition"), (1, "a", "Overlaps", "With WSN, MANET, M2M, IoT — but <b>tightly integrates</b> information &amp; physical processes")]),
   ("svg", "ovr", 330),
   ("note", 5, "<b style='color:var(--d)'>Limitation:</b> restrictive — reduces CPS to a <b>simple bridge</b>; lacks awareness of complex cyber-physical interactions")]},
 {"id": "five", "k": K + "7.4", "t": "Five-layer CPS architecture", "b": [("svg", "five", 610)]},
 {"id": "health", "k": K + "7.5 · frequently asked", "t": "Healthcare CPS — 9 steps", "b": [("svg", "health", 620)]},
 {"id": "smart", "k": K + "7.6", "t": "Smart-space CPS: smart air-conditioning", "b": [
   ("svg", "smart", 420),
   ("note", 1, "Control box supports <b>Wi-Fi, Bluetooth, ZigBee, infrared</b>")]},
 {"id": "emerg", "k": K + "7.7", "t": "CPS in emergency response", "b": [
   ("cards", 3, [(1, "a", "Pervasive sensing &amp; comm.", "Global view of affected areas; communication <b>timely, efficient, secure</b>"), (2, "c", "Control &amp; computing", "Event <b>priorities</b>; response plans: <b>trajectory navigation, task allocation</b>"), (3, "g", "Action", "Decisions → static &amp; mobile devices (<b>robots, drones</b>)")], 200),
   ("cards", 3, [(4, "b", "1 · Wireless comm. networks layer", "Sensors acquire data from heterogeneous entities &amp; events"), (5, "b", "2 · Environment perception layer", "Perceptions + <b>global map</b> of the situation"), (6, "b", "3 · Heterogeneous networks convergence", "Service composition, coverage, <b>QoS</b>")], 180),
   ("note", 7, "<b>Autonomous mobile robots:</b> interaction &amp; perception; challenges = <b>coordination &amp; relocation</b> in dynamic conditions")]},
 {"id": "its", "k": K + "7.8", "t": "Intelligent transport CPS", "b": [("svg", "its", 520)]},
 {"id": "role", "k": K + "8 · 10-mark answer", "t": "Role of WSN in CPS", "b": [
   ("table", ["Role", "Point 1", "Point 2"], [
     (1, ["<b>1 · Data collection &amp; reporting</b>", "Timely data from the right areas/events", "Contextual reporting to neighbours &amp; apps"]),
     (2, ["<b>2 · Data routing &amp; support</b>", "Route data between physical facilities", "Processing support when needed"]),
     (3, ["<b>3 · Monitoring &amp; control</b>", "Condition monitoring of devices", "Operational control in applications"]),
     (4, ["<b>4 · Aggregation &amp; analysis</b>", "Aggregate, filter, analyse, process", "Decision forwarding cyber → physical"]),
     (5, ["<b>5 · Intelligence &amp; autonomy</b>", "Embedded intelligence in the environment", "Multi-level control"]),
     (6, ["<b>6 · Security &amp; energy</b>", "Secure processing &amp; routing", "Save energy in appliances"])], 23),
   ("note", 7, "<b>Smart building:</b> collect occupancy (1) → route (2) → monitor HVAC (3) → aggregate per floor (4) → auto lights off (5) → save energy (6)")]},
 {"id": "energy", "k": K + "9.1", "t": "Routing challenge 1: energy", "b": [
   ("chips", 0, [("c", "E"), ("c", "D"), ("c", "M"), ("c", "R"), ("c", "S"), ("c", "D"), ("c", "S"), ("c", "Q"), ("m", "Energy · Deployment · Mobility · Reliability · Security · Data model · Scalability · QoS")]),
   ("bul", [(2, "c", "Transmission energy <b>∝ d²</b> (or <b>d⁴</b> with obstacles)"), (3, "d", "Battery death → node failure → topology change → re-route"), (4, "b", "<b>Multi-hop</b> for large areas · direct only when close to sink")], 25),
   ("svg", "energy", 300)]},
 {"id": "deploy", "k": K + "9.2–9.4", "t": "Deployment, mobility, reliability", "b": [
   ("table", ["", "Deterministic", "Random"], [
     (0, ["<b>How</b>", "Predefined, fixed locations", "Scattered (dropped from aircraft) → ad hoc"]),
     (0, ["<b>Routing</b>", "Predetermined, simple paths", "Unpredictable topology; needs <b>clustering</b>"]),
     ((1, 0), ["<b>Use</b>", "Specific coverage &amp; control (factory)", "Inaccessible/hazardous: forests, battlefields, volcanoes"])], 23),
   ("cards", 2, [(2, "a", "Mobility", "Static = common. Mobile: <b>disaster response</b>, sensors on <b>UAVs</b>.<br>Routes change → protocol must <b>adapt</b>"), (4, "b", "Reliability", "<b>Robustness:</b> tolerate node/link failures.<br><b>Redundancy:</b> multiple routing paths")], 200)]},
 {"id": "security", "k": K + "9.5", "t": "Security: three routing attacks", "b": [
   ("svg", "worm", 200),
   ("cards", 3, [(1, "d", "Wormhole", "Record packets at one place, <b>tunnel</b> via fast private link, replay elsewhere → <b>false short path</b>, misrouting"),
                 (3, "f", "Sybil", "One attacker, <b>many fake identities</b> → undue influence on voting, resource allocation, routing"),
                 (4, "g", "Rushing", "Forwards <b>RREQ very fast</b> → its copy arrives first, legit copies dropped as duplicates → interception / partition")], 260)]},
 {"id": "models", "k": K + "9.6", "t": "Data sensing &amp; collection models", "b": [
   ("cards", 4, [(1, "a", "Time-driven", "Regular intervals, changed or not.<br><i>Smart-grid PMUs at fixed rate</i>"), (2, "d", "Event-driven", "Only when an event occurs.<br><i>ITS alert when jam detected</i>"), (3, "c", "Query-driven", "Only on request.<br><i>\"Temperature of zone 3 now?\"</i>"), (4, "e", "Hybrid", "Mix of models.<br><i>time-driven → event-driven when special</i>")], 300),
   ("note", 5, "<b>Impact on routing:</b> energy (how often &amp; how much) · route stability (varying rates)")]},
 {"id": "scale", "k": K + "9.7–9.8", "t": "Scalability &amp; QoS", "b": [
   ("cards", 2, [(0, "a", "Scalability", "Huge numbers of sensors; efficient at any size.<br>• <b>Dynamic response</b>: join/leave/sleep<br>• <b>Energy mgmt</b>: route via awake nodes<br>• <b>Event-driven</b>: many nodes active at once (fire, intrusion)"),
                 (4, "d", "QoS — bounded latency", "Late data = useless data.<br>• <b>ITS:</b> speed drops sharply (jam) → send immediately<br>• Prefer <b>low-latency routes</b><br>• <b>Prioritise critical</b> data")], 420)]},
 {"id": "classify", "k": K + "10", "t": "Classification of routing protocols", "b": [("svg", "tree", 470), ("note", 4, "Covered in Parts 3–4: <b>location-based</b>, <b>data-centric</b>, <b>hierarchical</b>")]},
 {"id": "recap", "endl": 6, "k": "Exam recap", "t": "Remember these", "b": [
   ("bul", [(1, "a", "<b>5-layer:</b> sensing · data management · next-gen Internet · service-aware · application"),
            (2, "f", "<b>Healthcare:</b> sensors → gateway → cloud → observation centre → clinicians → decision → actuator"),
            (3, "b", "<b>Role of WSN:</b> 6 headings × 2 points"),
            (4, "c", "<b>E-D-M-R-S-D-S-Q</b> · energy ∝ d² → multi-hop · wormhole · Sybil · rushing"),
            (5, "e", "<b>Models:</b> time, event, query, hybrid · <b>classify:</b> addressing, operation, hierarchy")], 25)]},
]
JS = r"""
DIAG.ovr = (svg) => {
  const g1 = mk('g', {}, svg);
  boxS(g1, 0, 20, 300, 80, 'Sensors', 'spatially distributed', COL.a); boxS(g1, 560, 10, 480, 100, 'Decision-making system', 'cyber world', COL.e, 26); boxS(g1, 1300, 20, 300, 80, 'Actuators', '', COL.g);
  const a1 = arrow(svg, 305, 60, 555, 60, COL.a, { label: 'real-time inputs', fs: 19 }), a2 = arrow(svg, 1045, 60, 1295, 60, COL.g, { label: 'decisions', fs: 19 });
  const g2 = mk('g', {}, svg);
  boxS(g2, 0, 180, 460, 130, 'Physical world', 'infrastructure, hardware, humans, processes', COL.b, 26);
  boxS(g2, 600, 180, 480, 130, 'Cyberspace (controller)', 'networks, software, computing, storage', COL.e, 26);
  boxS(g2, 1220, 180, 380, 130, 'Actuators', 'execute decisions → change world', COL.g, 26);
  const b1 = arrow(svg, 465, 245, 595, 245, COL.a, { label: 'sensors', fs: 19 }), b2 = arrow(svg, 1085, 245, 1215, 245, COL.g);
  return (t, ctx) => { fade(g1, t, ctx, 2); a1(t, at(ctx, 3, 0)); a2(t, at(ctx, 3, .5)); fade(g2, t, ctx, 4); b1(t, at(ctx, 4, .4)); b2(t, at(ctx, 4, .7)); };
};
DIAG.five = (svg) => {
  const L = [['5 · Application module', 'deploys services, interfaces with devices', COL.f], ['4 · Service-aware module', 'analyses data, supports decision making', COL.e], ['3 · Next-generation Internet', 'communication between modules', COL.a], ['2 · Data management module', 'processes and stores collected data', COL.b], ['1 · Sensing module', 'collects data from the physical world', COL.c]];
  const gs = L.map(([a, b, c], k) => boxS(svg, 280, 10 + k * 100, 1120, 86, a, b, c, 28));
  const pw = boxS(svg, 600, 520, 480, 70, 'Physical world', '', COL.mut, 24);
  return (t, ctx) => { fade(pw, t, ctx, 0); gs.forEach((g, k) => fade(g, t, ctx, 5 - k)); };
};
DIAG.health = (svg) => {
  const P = node(svg, 120, 120, 70, 'Patient', COL.f, 24);
  const G = boxS(svg, 300, 80, 220, 80, 'Gateway', '', COL.mut);
  const C = boxS(svg, 640, 60, 300, 120, 'Cloud storage', '', COL.a, 26);
  const CS = boxS(svg, 1100, 60, 300, 120, 'Cloud server', 'real-time processing', COL.a, 26);
  const O = boxS(svg, 640, 300, 300, 100, 'Observation centre', 'results + alarms', COL.c, 24);
  const CL = boxS(svg, 1100, 290, 420, 120, 'Clinicians', '+ other health systems', COL.b, 26);
  const A = boxS(svg, 300, 470, 340, 100, 'Actuators', 'e.g. insulin pump', COL.g, 26);
  const st = (x, y, n) => { const g = mk('g', {}, svg); mk('circle', { cx: x, cy: y, r: 20, fill: COL.c }, g); mk('text', { x, y: y + 7, 'text-anchor': 'middle', fill: '#06101f', 'font-size': 18, 'font-weight': 800 }, g, n); return g; };
  const a = [arrow(svg, 195, 120, 295, 120, COL.f), arrow(svg, 525, 120, 635, 120, COL.mut), arrow(svg, 945, 100, 1095, 100, COL.a), arrow(svg, 1095, 145, 945, 145, COL.a), arrow(svg, 790, 185, 790, 295, COL.c), arrow(svg, 945, 350, 1095, 350, COL.b), arrow(svg, 1150, 415, 645, 515, COL.g), arrow(svg, 300, 500, 150, 195, COL.g)];
  const s = [st(240, 90, 1), st(1020, 75, 2), st(1020, 170, 3), st(820, 240, 4), st(1020, 325, '5–7'), st(900, 470, 8), st(200, 330, 9)];
  const sched = [[0, [P]], [1, [G, C]], [2, [CS]], [4, [O]], [5, [CL]], [6, [A]]];
  return (t, ctx) => {
    fade(P, t, ctx, 1); fade(G, t, ctx, 1); fade(C, t, ctx, 1, .3); a[0](t, at(ctx, 1, .2)); a[1](t, at(ctx, 1, .4)); fade(s[0], t, ctx, 1, .4);
    fade(CS, t, ctx, 2); a[2](t, at(ctx, 2, .1)); fade(s[1], t, ctx, 2, .1); a[3](t, at(ctx, 2, .6)); fade(s[2], t, ctx, 2, .6);
    fade(O, t, ctx, 3); a[4](t, at(ctx, 3, .1)); fade(s[3], t, ctx, 3, .1);
    fade(CL, t, ctx, 4); a[5](t, at(ctx, 4, .1)); fade(s[4], t, ctx, 4, .1);
    fade(A, t, ctx, 5); a[6](t, at(ctx, 5, .1)); fade(s[5], t, ctx, 5, .1);
    a[7](t, at(ctx, 6, .1)); fade(s[6], t, ctx, 6, .1);
  };
};
DIAG.smart = (svg) => {
  const T = boxS(svg, 0, 150, 300, 110, 'Temperature sensor', 'reads 35°C', COL.d, 24);
  const B = boxS(svg, 520, 140, 380, 130, 'Intelligent control box', 'Wi-Fi · Bluetooth · ZigBee · IR', COL.c, 26);
  const D = boxS(svg, 1180, 20, 480, 130, 'CPS analysis / decision', 'digital world (cloud)', COL.e, 26);
  const AC = boxS(svg, 1180, 280, 480, 110, 'Air conditioner', '', COL.a, 26);
  const a1 = arrow(svg, 305, 205, 515, 205, COL.d, { label: 'ZigBee: 35°C', fs: 21 }), a2 = arrow(svg, 905, 170, 1175, 90, COL.e, { label: 'Wi-Fi', fs: 21, lx: 1000, ly: 110 }), a3 = arrow(svg, 1175, 130, 905, 210, COL.b, { label: 'Wi-Fi: open AC', fs: 21, lx: 1100, ly: 200 }), a4 = arrow(svg, 905, 250, 1175, 330, COL.a, { label: 'infrared', fs: 21, lx: 1000, ly: 320 });
  return (t, ctx) => { fade(T, t, ctx, 1); fade(B, t, ctx, 1, .3); a1(t, at(ctx, 1, .4)); fade(D, t, ctx, 2); a2(t, at(ctx, 2, .2)); a3(t, at(ctx, 3, 0)); fade(AC, t, ctx, 3, .4); a4(t, at(ctx, 3, .5)); };
};
DIAG.its = (svg) => {
  const C = boxS(svg, 60, 160, 520, 180, 'CYBER', 'real-time models, information, speed & position', COL.e, 32);
  const P = boxS(svg, 1100, 160, 520, 180, 'PHYSICAL', 'traffic system: vehicles, signals, behaviour', COL.b, 32);
  const s = arrow(svg, 1095, 200, 585, 200, COL.a, { label: 'Sensing (speed, position)', fs: 24, ly: 180 });
  const c = arrow(svg, 585, 300, 1095, 300, COL.g, { label: 'Control / actuation (signals, alert drivers)', fs: 24, ly: 380 });
  const comp = boxS(svg, 60, 20, 520, 90, 'Computation', 'cloud computing, embedded systems', COL.c, 24);
  const comm = boxS(svg, 640, 410, 420, 90, 'Communication', 'sensor nets, mobile nets, DSRC, IoT', COL.c, 24);
  return (t, ctx) => { fade(C, t, ctx, 1); fade(P, t, ctx, 1, .4); s(t, at(ctx, 2, .1)); fade(comp, t, ctx, 3); fade(comm, t, ctx, 3, .5); c(t, at(ctx, 4, .1)); };
};
DIAG.energy = (svg) => {
  const rows = [['Direct 100 m', [100], '100² = 10,000', COL.d, 5], ['2 hops × 50 m', [50, 50], '2 × 2,500 = 5,000 (½)', COL.c, 7], ['4 hops × 25 m', [25, 25, 25, 25], '4 × 625 = 2,500 (¼)', COL.b, 8]];
  const gs = rows.map(([lab, hops, res, c, l], k) => {
    const g = mk('g', {}, svg); const y = 40 + k * 95;
    mk('text', { x: 0, y: y + 8, fill: COL.ink, 'font-size': 22, 'font-weight': 700 }, g, lab);
    let x = 230; hops.forEach((h, i) => { const w = h * 8; mk('line', { x1: x, y1: y, x2: x + w, y2: y, stroke: c, 'stroke-width': 6 }, g); mk('circle', { cx: x, cy: y, r: 9, fill: i ? COL.e : COL.a }, g); x += w; });
    mk('circle', { cx: x, cy: y, r: 11, fill: COL.ink }, g);
    mk('text', { x: 1080, y: y + 8, fill: c, 'font-size': 26, 'font-weight': 800 }, g, res);
    return [g, l];
  });
  return (t, ctx) => gs.forEach(([g, l]) => fade(g, t, ctx, l));
};
DIAG.worm = (svg) => {
  const xs = [200, 500, 800, 1100, 1400]; const ns = xs.map((x, k) => node(svg, x, 140, 30, 'ABCDE'[k], COL.a, 24));
  for (let i = 0; i < 4; i++) mk('line', { x1: xs[i] + 30, y1: 140, x2: xs[i + 1] - 30, y2: 140, stroke: COL.mut, 'stroke-width': 3 }, svg);
  const w = mk('g', {}, svg); mk('path', { d: 'M 230 115 Q 800 10 1370 115', stroke: COL.d, 'stroke-width': 6, fill: 'none', 'stroke-dasharray': '14 8' }, w);
  mk('text', { x: 800, y: 24, 'text-anchor': 'middle', fill: COL.d, 'font-size': 24, 'font-weight': 800 }, w, 'wormhole tunnel: A and E look like neighbours (really 4 hops)');
  return (t, ctx) => fade(w, t, ctx, 2);
};
DIAG.tree = (svg) => {
  const R = boxS(svg, 560, 0, 560, 80, 'Routing protocols in WSNs for CPS', '', COL.ink, 26);
  const P = [['Network addressing', 1, COL.a, ['Topology-based', 'Geographical / location-based']], ['Protocol operation / design', 2, COL.c, ['Query-based / data-centric', 'QoS-aware', 'Security-aware', 'Energy-aware']], ['Network hierarchy', 3, COL.b, ['Flat / non-hierarchical', 'Hierarchical']]];
  const gs = P.map(([n, l, c, kids], k) => {
    const g = mk('g', {}, svg); const x = 20 + k * 560;
    mk('line', { x1: 840, y1: 80, x2: x + 260, y2: 130, stroke: COL.mut, 'stroke-width': 2 }, g);
    boxS(g, x, 130, 520, 76, n, 'perspective', c, 25);
    kids.forEach((kd, i) => { boxS(g, x + 40, 240 + i * 56, 440, 46, kd, '', c, 21); });
    return [g, l];
  });
  return (t, ctx) => { fade(R, t, ctx, 0); gs.forEach(([g, l]) => fade(g, t, ctx, l)); };
};
"""
build("CCPS Module 3 Part 2", scenes, JS, "index.html")
