import sys; sys.path.insert(0, '..'); sys.path.insert(0, '.')
exec(open('../m3-gen.py').read())
K = "Module 3 · "
scenes = [
 {"id": "intro", "hero": 1, "k": "CCPS MODULE 3 · PART 1", "t": "WSN, Topologies &amp; <span style='color:var(--a)'>CPS</span>", "b": [
   ("chips", 1, [("a", "Network topology design"), ("b", "Network operation")]),
   ("chips", 2, [("m", "WSN basics"), ("m", "Star · cluster-tree · mesh"), ("m", "CPS"), ("m", "WSN-CPS architecture"), ("m", "MANET · WSN · M2M · CPS")])]},
 {"id": "wsn", "k": K + "1.1–1.2", "t": "What is a WSN?", "b": [
   ("cards", 1, [(0, "a", "Definition", "A large network of small, <b>resource-constrained sensor nodes</b> that <b>sense, process and communicate wirelessly</b>, deployed in a sensing field to achieve an application objective.")]),
   ("bul", [(1, "a", "<b>Purpose:</b> implement application goals (monitor temperature, intrusion…) in a specific field"), (2, "a", "<b>Expansion:</b> extends the Internet into the physical world → <b>cyber-physical environment</b>")], 24),
   ("svg", "wsnfield", 170),
   ("cards", 3, [(4, "e", "Nodes / motes", "Spatially distributed autonomous devices using sensors to monitor conditions"), (5, "b", "Communication", "Node ↔ node (<b>multi-hop</b>) or directly to a base station"), (6, "c", "Base stations / gateways", "Forward sensor data to a monitoring centre / decision system (wireless or wired)")])]},
 {"id": "node", "k": K + "1.3", "t": "Structure of a sensor node", "b": [
   ("note", 0, "Basic functions: <b style='color:var(--a)'>Sensing</b> · <b style='color:var(--b)'>Data processing</b> · <b style='color:var(--c)'>Communication</b>"),
   ("svg", "nodeblk", 380),
   ("chips", 6, [("m", "optional: power generator (solar cell)"), ("m", "location finding (GPS)"), ("m", "mobilizer (moves the node)")])]},
 {"id": "bs", "k": K + "1.4", "t": "The base station (sink)", "b": [
   ("note", 0, "Gateway between the WSN and the outside world — <b>more powerful</b> than ordinary nodes"),
   ("cards", 3, [((2, 0), "a", "C · Collection", "Gather data from sensor nodes"), ((2, 0.35), "b", "P · Processing", "Analyse and organise the data"), ((2, 0.7), "c", "F · Forwarding", "Send processed data to a remote server over the Internet")]),
   ("svg", "bsd", 230),
   ("note", 5, "Dual interface → moves data from the <b>physical environment</b> to the <b>digital systems</b> that analyse it")]},
 {"id": "topo", "k": K + "2", "t": "Network topologies", "b": [
   ("note", 0, "Topology = connectivity graph: <b>vertices = nodes</b>, <b>edges = one-hop links</b>"),
   ("svg", "topo", 270),
   ("cards", 3, [(2, "a", "Star", "✓ simple, easy, low latency<br>✗ BS = single point of failure, limited scalability, far nodes use more energy<br><i>e.g. smart home, 6 sensors + hub</i>"),
                 (4, "c", "Cluster-tree", "✓ scalable, energy-efficient, less BS traffic<br>✗ multi-hop latency; CH failure cuts its cluster<br><i>e.g. forest monitoring by area</i>"),
                 (6, "b", "Mesh", "✓ reliable, robust, self-healing, scalable<br>✗ complex management, routing-overhead energy<br><i>e.g. industrial plant monitoring</i>")])]},
 {"id": "compare", "k": K + "2.4", "t": "Topology comparison", "b": [
   ("table", ["Feature", "Star", "Cluster-tree", "Mesh"], [
     (1, ["<b>Path to BS</b>", "Direct (1 hop)", "Member → CH → BS", "Multiple multi-hop paths"]),
     (2, ["<b>Latency</b>", "Lowest", "Medium", "Higher"]),
     (3, ["<b>Reliability</b>", "Low (BS failure kills all)", "Medium (CH failure)", "Highest (self-healing)"]),
     (4, ["<b>Scalability</b>", "Limited", "Good", "Good"]),
     (5, ["<b>Energy</b>", "High for far nodes", "Efficient", "Higher (routing overhead)"]),
     (5, ["<b>Complexity</b>", "Simple", "Moderate", "Complex"])], 25),
   ("note", 6, "Each topology trades off <b>reliability, latency and energy</b> → choice depends on application &amp; deployment")]},
 {"id": "apps", "k": K + "3", "t": "WSN applications &amp; challenges (E-M-H-H)", "b": [
   ("cards", 4, [(1, "b", "Environmental", "Crops &amp; livestock, irrigation, forest fires &amp; flooding, disasters &amp; pollution"),
                 (2, "d", "Military", "Target tracking, battlefield surveillance, intrusion detection, reconnaissance, NBC attack detection"),
                 (3, "f", "Health", "Patient monitoring, tracking patients &amp; staff, disabled assistance, body sensor networks (implants)"),
                 (4, "a", "Home automation", "Better living standard, enhanced security, energy efficiency")], 250),
   ("bul", [(5, "c", "<b>Resource constraints:</b> processing, bandwidth, connectivity, especially <b>battery</b>"),
            (6, "c", "<b>Develop:</b> communication protocols · OS &amp; hardware · power management · MAC &amp; routing"),
            (7, "c", "<b>Battery = network lifetime</b> → sleep scheduling, short-hop routing, data aggregation"),
            (8, "d", "<b>CPS integration</b> adds timing, heterogeneity &amp; reliability problems")], 24)]},
 {"id": "cps", "k": K + "4", "t": "Cyber-Physical Systems", "b": [
   ("cards", 1, [(0, "a", "Definition", "Integrate <b>computing, communication and storage</b> with the <b>monitoring and control of physical entities</b>. Vision: services that transcend time &amp; space (e.g. remote patient monitoring).")]),
   ("svg", "cpsloop", 120),
   ("cards", 3, [((3, 0), "e", "1 · Cybernetic capacity", "in every physical component"), ((3, .3), "e", "2 · Large-scale networking", "large / very large"), ((3, .6), "e", "3 · Heterogeneity", "diverse components"),
                 ((4, 0), "e", "4 · Dynamic reconfiguration", "at run time"), ((4, .3), "e", "5 · Closed-loop control", "high automation"), ((4, .6), "e", "6 · Dependability", "sometimes certified (avionics)")]),
   ("chips", 5, [("b", "efficient &amp; safe"), ("b", "lower production &amp; operational cost"), ("b", "entities combine → new capabilities")])]},
 {"id": "domains", "k": K + "4.4", "t": "CPS application domains", "b": [
   ("table", ["Domain", "What CPS does there"], [
     (1, ["<b>Transportation</b>", "Reduce environmental impact, complex traffic control, high dependability"]),
     (1, ["<b>Energy</b>", "Higher efficiency &amp; security via smart grids"]),
     (2, ["<b>Civil infrastructure</b>", "Precise control, warning &amp; prevention (bridge health)"]),
     (2, ["<b>Environment monitoring</b>", "Minimal energy use, accurate data collection"]),
     (3, ["<b>Defense</b>", "Precise control, high security, high computing power"]),
     (3, ["<b>Smart buildings</b>", "Lower energy, better security &amp; safety"]),
     (4, ["<b>Health &amp; biomedical</b>", "New analysis/integration technologies, new medical devices"]),
     (5, ["<b>Manufacturing</b>", "Intelligent control, automatic assembly, safe human-robot environments, competitiveness"])], 24)]},
 {"id": "arch2", "k": K + "5.1–5.2", "t": "Two-layer WSN-CPS architecture", "b": [
   ("note", 0, "CPS = embedded systems + sensor networks + actuators + <b>intelligent decision systems</b>"),
   ("note", 1, "<b>Role of WSN:</b> collects physical information for the CPS, often with <b>actuation</b>"),
   ("svg", "arch2", 400),
   ("note", 5, "Must handle <b>delays, time differences, heterogeneity</b>; support <b>dynamic reconfiguration</b> for dependability &amp; security")]},
 {"id": "arch3", "k": K + "5.3–5.4", "t": "Three-layer WSN-CPS architecture", "b": [
   ("svg", "arch3", 470),
   ("note", 5, "Middle layer: ensures <b>dependability &amp; security</b>, gives control/monitoring decisions, complex analysis for end-users"),
   ("chips", 8, [("m", "critical infrastructures"), ("m", "environment"), ("m", "smart buildings"), ("m", "manufacturing · transport · healthcare")])]},
 {"id": "chal", "k": K + "5.5", "t": "Challenges in CPS", "b": [
   ("cards", 3, [(1, "a", "1 · Abstraction &amp; architecture", "Formalisms/architectures that <b>integrate heterogeneous</b> components and ensure <b>interoperability</b>"),
                 (2, "c", "2 · Distributed computation &amp; networked control", "Time- and event-driven computing, delays, failures, reconfiguration; <b>distributed decision support</b> for reliability &amp; security"),
                 (3, "b", "3 · Verification &amp; validation", "Guarantee <b>QoS of software and hardware</b> from early design stages")], 420)]},
 {"id": "manet", "k": K + "6.1–6.3", "t": "MANET, WSN and M2M", "b": [
   ("cards", 3, [(0, "g", "MANET", "<b>Self-configuring</b> network of mobile devices that move freely.<br>• Every device is a <b>router</b><br>• No fixed infrastructure, dynamic topology<br>• Heterogeneous protocols<br><i>e.g. soldiers' radios, VANET</i>"),
                 (3, "a", "WSN = special MANET", "Spatially distributed <b>sensing</b> devices monitoring conditions.<br>• Sensors <b>collaborate</b> beyond any single sensor<br>• Mobility improves tracking &amp; data collection<br><i>e.g. environment, disaster response</i>"),
                 (4, "c", "M2M", "Devices exchange info and <b>act without human intervention</b>.<br>• <b>RFID</b> · sensors<br>• links: ZigBee, WiMAX, Wi-Fi, cellular<br>• computing software decides<br><i>e.g. smart meter → utility server</i>")], 520)]},
 {"id": "table", "k": K + "6.4 · most important table", "t": "MANET vs WSN vs M2M vs CPS", "b": [
   ("table", ["Aspect", "MANET", "WSN", "M2M", "CPS"], [
     (1, ["<b>Goal</b>", "Ad-hoc comm. / extend coverage", "Situational data on events &amp; objects", "Task/device-specific machine comm.", "Sensor nets + Internet → intelligence across domains"]),
     (2, ["<b>Composition</b>", "Mobile devices", "Sensors (static/mobile), limited", "Sensors, RFID, networked devices", "Physical parts + cyber parts"]),
     (3, ["<b>Topology</b>", "Random, highly dynamic", "Random/predefined; clustering", "Random/predefined/field-specific", "Highly dynamic; clustering"]),
     (4, ["<b>Communication</b>", "Unicast/multicast/broadcast", "Collective among sensors", "Heterogeneous devices", "Inter/intra-WSN, cross-domain"]),
     (5, ["<b>Power</b>", "Energy saving, sleep", "Conservation, long sleep/wake", "Not a major concern", "Mission-oriented activation"]),
     (6, ["<b>Mobility</b>", "Arbitrary, unrestricted", "Limited; (un)controlled", "Field-specific", "Controllable &amp; uncontrollable"]),
     (7, ["<b>Coverage</b>", "Precise connectivity", "Connectivity + sensing", "Connectivity essential", "Multiple levels"]),
     (8, ["<b>Knowledge</b>", "Not a focus", "Acquire/manage sensing data", "Supports machine comm.", "Extract new knowledge"])], 18),
   ("note", 9, "MANET = <b>move &amp; talk</b> · WSN = <b>sense</b> · M2M = <b>machines act alone</b> · CPS = <b>sense + think + act</b>")]},
 {"id": "recap", "endl": 5, "k": "Exam recap", "t": "Remember these", "b": [
   ("bul", [(1, "a", "<b>Node:</b> sensing (sensor+ADC) · processing &amp; storage · transceiver · power · <b>BS:</b> C-P-F + 2 interfaces"),
            (2, "c", "<b>Star</b> simple, single point of failure · <b>Cluster-tree</b> efficient · <b>Mesh</b> reliable, complex"),
            (3, "e", "<b>CPS:</b> 6 characteristics · <b>2-layer:</b> physical + cyber · <b>3-layer:</b> physical, middle (storage, knowledge base, agents), cyberspace services"),
            (4, "g", "MANET move &amp; talk · WSN sense · M2M machines alone · CPS sense, think, act")], 25)]},
]
JS = r"""
DIAG.wsnfield = (svg) => {
  const pts = [[80,60],[220,120],[340,50],[470,110],[600,60]]; const g = mk('g', {}, svg);
  for (let i = 0; i < 4; i++) mk('line', { x1: pts[i][0], y1: pts[i][1], x2: pts[i+1][0], y2: pts[i+1][1], stroke: COL.mut, 'stroke-width': 2 }, g);
  pts.forEach(([x,y]) => node(g, x, y, 20, '', COL.e));
  mk('text', { x: 340, y: 160, 'text-anchor': 'middle', fill: COL.mut, 'font-size': 20 }, g, 'sensing field · e.g. 200 soil-moisture sensors (farm)');
  const bs = boxS(g, 760, 40, 220, 80, 'Base station', 'gateway', COL.c); const inet = boxS(g, 1060, 40, 200, 80, 'Internet', '', COL.a); const u = boxS(g, 1340, 40, 300, 80, 'User / monitoring', 'irrigation pumps on/off', COL.b);
  mk('line', { x1: 620, y1: 80, x2: 755, y2: 80, stroke: COL.mut, 'stroke-width': 3 }, g); mk('line', { x1: 985, y1: 80, x2: 1055, y2: 80, stroke: COL.mut, 'stroke-width': 3 }, g); mk('line', { x1: 1265, y1: 80, x2: 1335, y2: 80, stroke: COL.mut, 'stroke-width': 3 }, g);
  const tv = traveller(svg, 'M 80 60 L 220 120 L 340 50 L 470 110 L 600 60 L 870 80 L 1160 80 L 1490 80', COL.c, 9);
  return (t, ctx) => { fade(g, t, ctx, 3); tv(t, at(ctx, 3, 0.3), 3.5); };
};
DIAG.nodeblk = (svg) => {
  const S = boxS(svg, 40, 40, 420, 130, 'Sensing unit', 'sensor + ADC: senses, analog → digital', COL.a, 28);
  const P = boxS(svg, 620, 40, 440, 130, 'Processing & storage', 'microcontroller + memory, runs protocols', COL.b, 28);
  const T = boxS(svg, 1220, 40, 420, 130, 'Transceiver', 'radio: sends / receives', COL.c, 28);
  const B = boxS(svg, 620, 250, 440, 110, 'Power supply', 'battery powers all units', COL.d, 28);
  const a = [arrow(svg, 465, 105, 615, 105, COL.mut), arrow(svg, 1065, 105, 1215, 105, COL.mut), arrow(svg, 700, 245, 300, 175, COL.d), arrow(svg, 840, 245, 840, 175, COL.d), arrow(svg, 980, 245, 1400, 175, COL.d)];
  return (t, ctx) => { fade(S, t, ctx, 2); fade(P, t, ctx, 3); fade(T, t, ctx, 4); fade(B, t, ctx, 5); a[0](t, at(ctx, 3, .3)); a[1](t, at(ctx, 4, .3)); a.slice(2).forEach((f, k) => f(t, at(ctx, 5, .3 + k * .1))); };
};
DIAG.bsd = (svg) => {
  const f = mk('g', {}, svg); [[60,60],[140,150],[230,80],[90,190]].forEach(([x,y]) => node(f, x, y, 16, '', COL.e));
  const bs = boxS(svg, 600, 75, 420, 110, 'Base station', 'collect · process · forward', COL.c, 28);
  const srv = boxS(svg, 1360, 75, 300, 110, 'Remote server', 'application', COL.a, 26);
  const a1 = arrow(svg, 260, 130, 590, 130, COL.e, { label: 'in-field (short range, ZigBee)', fs: 20, ly: 60 });
  const a2 = arrow(svg, 1025, 130, 1355, 130, COL.a, { label: 'out-of-field long-range (cellular)', fs: 20, ly: 60 });
  return (t, ctx) => { fade(f, t, ctx, 0); fade(bs, t, ctx, 0, .3); fade(srv, t, ctx, 4); a1(t, at(ctx, 3, .2)); a2(t, at(ctx, 4, .2)); };
};
DIAG.topo = (svg) => {
  const star = mk('g', {}, svg), cl = mk('g', {}, svg), me = mk('g', {}, svg);
  const c = [280, 130]; [[0,-100],[95,-30],[60,85],[-60,85],[-95,-30]].forEach(([dx,dy], k) => { mk('line', { x1: c[0], y1: c[1], x2: c[0]+dx, y2: c[1]+dy, stroke: COL.a, 'stroke-width': 3 }, star); node(star, c[0]+dx, c[1]+dy, 18, 'N' + (k+1), COL.mut, 14); });
  node(star, c[0], c[1], 30, 'BS', COL.a, 20); mk('text', { x: 280, y: 262, 'text-anchor': 'middle', fill: COL.a, 'font-size': 22, 'font-weight': 700 }, star, 'Star');
  const bs = [840, 40]; const chs = [[740,130],[940,130]];
  chs.forEach(([x,y], k) => { mk('line', { x1: x, y1: y, x2: bs[0], y2: bs[1], stroke: COL.c, 'stroke-width': 3 }, cl); [-60,0,60].forEach((dx) => { mk('line', { x1: x, y1: y, x2: x+dx, y2: 215, stroke: COL.mut, 'stroke-width': 2 }, cl); node(cl, x+dx, 215, 14, '', COL.mut); }); node(cl, x, y, 24, 'CH', COL.c, 16); });
  node(cl, bs[0], bs[1], 26, 'BS', COL.a, 18); mk('text', { x: 840, y: 262, 'text-anchor': 'middle', fill: COL.c, 'font-size': 22, 'font-weight': 700 }, cl, 'Cluster-tree');
  const mp = [[1300,60],[1300,200],[1420,130],[1540,60],[1540,200]]; [[0,1],[0,2],[1,2],[2,3],[2,4],[3,4],[0,3],[1,4]].forEach(([a,b]) => mk('line', { x1: mp[a][0], y1: mp[a][1], x2: mp[b][0], y2: mp[b][1], stroke: COL.b, 'stroke-width': 2.5 }, me));
  mp.forEach(([x,y], k) => node(me, x, y, k === 4 ? 26 : 18, k === 4 ? 'BS' : '', k === 4 ? COL.a : COL.mut, 18));
  mk('text', { x: 1420, y: 262, 'text-anchor': 'middle', fill: COL.b, 'font-size': 22, 'font-weight': 700 }, me, 'Mesh');
  return (t, ctx) => { fade(star, t, ctx, 1); fade(cl, t, ctx, 3); fade(me, t, ctx, 5); };
};
DIAG.cpsloop = (svg) => {
  const p = boxS(svg, 200, 20, 420, 80, 'Physical world', '', COL.b, 28), c = boxS(svg, 1060, 20, 420, 80, 'Cyber world', 'compute + decide', COL.e, 28);
  const a = arrow(svg, 625, 45, 1055, 45, COL.a, { label: 'sense (sensors)', fs: 22, ly: 30 }), b = arrow(svg, 1055, 85, 625, 85, COL.g, { label: 'act (actuators)', fs: 22, ly: 118 });
  return (t, ctx) => { fade(p, t, ctx, 2); fade(c, t, ctx, 2, .3); a(t, at(ctx, 2, .3)); b(t, at(ctx, 2, .7)); };
};
DIAG.arch2 = (svg) => {
  const cy = mk('g', {}, svg); mk('rect', { x: 40, y: 10, width: 1600, height: 110, rx: 18, fill: 'rgba(167,139,250,.08)', stroke: COL.e, 'stroke-width': 3 }, cy);
  mk('text', { x: 70, y: 50, fill: COL.e, 'font-size': 26, 'font-weight': 800 }, cy, 'CYBER LAYER'); mk('text', { x: 70, y: 82, fill: COL.mut, 'font-size': 19 }, cy, 'real-time decisions; raw data → high-level knowledge');
  ['Storage platforms', 'Knowledge', 'Decision system'].forEach((n, k) => boxS(cy, 560 + k * 360, 30, 320, 70, n, '', COL.e, 24));
  const net = boxS(svg, 690, 170, 300, 70, 'Network', '', COL.c, 26);
  const ph = mk('g', {}, svg); mk('rect', { x: 40, y: 290, width: 1600, height: 105, rx: 18, fill: 'rgba(52,211,153,.08)', stroke: COL.b, 'stroke-width': 3 }, ph);
  mk('text', { x: 70, y: 330, fill: COL.b, 'font-size': 26, 'font-weight': 800 }, ph, 'PHYSICAL LAYER'); mk('text', { x: 70, y: 362, fill: COL.mut, 'font-size': 19 }, ph, 'collect data from / control processes');
  ['Sensor 1', 'Sensor n', 'Actuator 1', 'Actuator n'].forEach((n, k) => boxS(ph, 520 + k * 280, 310, 240, 66, n, '', k < 2 ? COL.a : COL.g, 22));
  const up = arrow(svg, 760, 305, 800, 245, COL.a, { label: 'sensing', fs: 20, lx: 700, ly: 280 }), dn = arrow(svg, 880, 245, 1060, 305, COL.g, { label: 'control', fs: 20, lx: 1040, ly: 270 }), c2 = arrow(svg, 840, 165, 840, 125, COL.c);
  return (t, ctx) => { fade(ph, t, ctx, 2); fade(cy, t, ctx, 3); fade(net, t, ctx, 4); up(t, at(ctx, 4, .2)); c2(t, at(ctx, 4, .4)); dn(t, at(ctx, 4, .6)); };
};
DIAG.arch3 = (svg) => {
  const top = mk('g', {}, svg); mk('rect', { x: 40, y: 10, width: 1600, height: 100, rx: 18, fill: 'rgba(56,189,248,.08)', stroke: COL.a, 'stroke-width': 3 }, top);
  mk('text', { x: 70, y: 50, fill: COL.a, 'font-size': 26, 'font-weight': 800 }, top, 'TOP · Cyberspace services'); mk('text', { x: 70, y: 84, fill: COL.ink, 'font-size': 21 }, top, 'Monitoring, control & analysis as SaaS + client apps (web services)');
  const mid = mk('g', {}, svg); mk('rect', { x: 40, y: 150, width: 1600, height: 170, rx: 18, fill: 'rgba(251,191,36,.07)', stroke: COL.c, 'stroke-width': 3 }, mid);
  mk('text', { x: 70, y: 188, fill: COL.c, 'font-size': 26, 'font-weight': 800 }, mid, 'MIDDLE');
  const mids = [['Data storage', 'distributed sensor DBs', 2], ['Knowledge base', 'ontology: decisions, negotiation rules', 3], ['Multi-agent society', 'storage, negotiation, processing, testing, diagnosis, decisions', 4]].map(([a, b, l], k) => [boxS(svg, 70 + k * 525, 205, 500, 100, a, b, COL.c, 25), l]);
  const ph = mk('g', {}, svg); mk('rect', { x: 40, y: 360, width: 1600, height: 100, rx: 18, fill: 'rgba(52,211,153,.08)', stroke: COL.b, 'stroke-width': 3 }, ph);
  mk('text', { x: 70, y: 400, fill: COL.b, 'font-size': 26, 'font-weight': 800 }, ph, 'PHYSICAL · WSNs of sensors + actuators'); mk('text', { x: 70, y: 434, fill: COL.ink, 'font-size': 21 }, ph, 'concerns: energy efficiency, data movement, heterogeneous communication');
  const up = arrow(svg, 1500, 355, 1500, 325, COL.b, { label: 'sensing data', fs: 18, lx: 1400, ly: 345 }), dn = arrow(svg, 1580, 325, 1580, 355, COL.g);
  return (t, ctx) => { fade(ph, t, ctx, 1); fade(mid, t, ctx, 2); mids.forEach(([g, l]) => fade(g, t, ctx, l)); fade(top, t, ctx, 6); up(t, at(ctx, 7, .1)); dn(t, at(ctx, 7, .5)); };
};
"""
build("CCPS Module 3 Part 1", scenes, JS, "index.html")
