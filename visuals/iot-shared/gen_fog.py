import json
P = {"CPS":"C P S","IoT":"I o T","PLC":"P L C","PLCs":"P L Cs","GPU":"G P U","GPUs":"G P Us","CPU":"C P U","ML":"M L","V2I":"V 2 I","M2M":"M 2 M","AGVs":"A G Vs","AGV":"A G V","ERP":"E R P","SCADA":"Scada","OTA":"O T A","KPI":"K P I","AWS":"A W S","MCU":"M C U","5G":"five G","DB":"database","ms":"milliseconds"}
S = []
def sc(id, chapter, kicker, title, viz, lines, tip=None, **kw):
    d = {"id": id, "chapter": chapter, "kicker": kicker, "title": title, "viz": viz, "lines": lines}
    if tip: d["tip"] = {"t": tip[0], "at": tip[1]}
    d.update(kw); S.append(d)
def cards(items, cols=None, **kw):
    v = {"type": "cards", "items": [dict(zip(["icon","h","b","c","at"], it)) for it in items]}
    if cols: v["cols"] = cols
    v.update(kw); return v
EDGE, FOG, CLOUD = "c5", "c1", "c2"

sc("intro", "Intro", "Module 7", None,
   {"type": "hero", "icon": "🌫️", "big": "Fog & Edge Computing", "y": 160, "sub": "in Cyber-Physical Systems — every slide, explained simply", "subY": 300,
    "chips": [{"t": t, "c": c, "at": 2 + i*0.15} for i,(t,c) in enumerate([("Edge computing","c5"),("Fog computing","c1"),("Edge + Fog + Cloud","c2"),("Use cases","c3"),("Smart factory scenario","c6"),("Flows","c4"),("Edge vs Fog","c7")])]},
   ["A robot arm is about to hit a worker. Should it ask a cloud server in another country what to do? Of course not. There's no time.",
    "That's why cyber physical systems use edge computing and fog computing, close to the machines.",
    "We'll cover edge computing, fog computing, the combined edge fog cloud architecture, real use cases, a full smart factory scenario, and edge versus fog.",
    "Let's start."], pad=[0.6, 1.0])

sc("cps", "CPS and why fog/edge matter", "Slides 2 & 36 · Cyber-Physical Systems", "Cyber-Physical Systems (CPS)",
   cards([("🔄","What is a CPS?","**Real-time interaction** between **physical devices, sensors, actuators, networks** and **computational intelligence**.","c1",0),
          ("🏭","Examples","**Smart grids, autonomous cars, industrial automation, smart healthcare, robotics, smart agriculture**, smart factories.","c3",2),
          ("🌫️","Why Fog & Edge?","They improve **latency**, **bandwidth efficiency**, **security** and **real-time decision making**.","c5",3)], cols=3),
   ["A cyber physical system involves real time interaction between physical devices, sensors, actuators, networks, and computational intelligence.",
    "In simple words: sensors feel the world, computers think, and actuators act on the world.",
    "Examples: smart grids, autonomous cars, industrial automation, smart healthcare, robotics, smart agriculture, and smart factories.",
    "Fog and edge computing play a major role in four things: improving latency, bandwidth efficiency, security, and real time decision making.",
    "Latency is delay. Bandwidth is how much data the network can carry."],
   tip=("Fog & edge improve: **latency, bandwidth, security, real-time decisions**.", 3))

sc("edge", "Edge computing: what & why", "Slides 3 & 37 · Edge computing in CPS", "1. Edge computing",
   cards([("📍","What is edge?","Processing data **directly on or near the device** — **sensors, gateways, embedded controllers**.","c5",0),
          ("⏱️","Why #1: speed","CPS needs **millisecond-level** responses.","c3",2),
          ("🌊","Why #2: too much data","Sensors generate **huge data** → **can't send everything to the cloud**.","c6",3),
          ("🛡️","Why #3: local benefits","Local processing increases **speed, reliability and data privacy**.","c1",4)], cols=2),
   ["Edge computing processes data directly on or near the devices, such as sensors, gateways, or embedded controllers.",
    "Think of it as giving every machine its own small brain. Why does CPS need edge? Three reasons.",
    "One: CPS requires millisecond level responses.",
    "Two: sensors generate huge amounts of data, so we can't send everything to the cloud.",
    "Three: local processing increases speed, reliability, and data privacy, because the data never has to leave the building."],
   tip=("Edge = compute **on/near the device**. Why: **ms response, too much data, privacy**.", 0))

sc("edgeA", "Edge use A: real-time control", "Slide 4 · Where edge is used (A)", "A. Real-time control & decision making",
   {"type": "multi", "parts": [
     {"x": 0, "w": 760, "viz": cards([("🧠","Edge nodes","**PLCs, microcontrollers, embedded GPUs**.","c5",1)], cols=1)},
     {"x": 800, "w": 920, "viz": cards([("🚗","Collision detection","in autonomous vehicles","c7",2),("🛑","Adaptive braking","","c6",2.3),("🦾","Real-time robotic movement","","c3",2.6),("🏭","Industrial machine failure detection","","c4",2.9)], cols=2, compact=True)}],
    },
   ["Where is edge used? First, real time control and decision making. CPS requires immediate feedback.",
    "Edge nodes, like PLCs, microcontrollers, and embedded GPUs, do the computing. A PLC is a programmable logic controller, a rugged factory computer.",
    "They compute things like collision detection in autonomous vehicles, adaptive braking, real time robotic movement, and industrial machine failure detection.",
    "Edge ensures latency below 10 milliseconds. That's faster than a blink."],
   tip=("Edge latency: **< 10 ms**.", 3))

sc("edgeB", "Edge use B: local analytics", "Slide 5 · Where edge is used (B)", "B. Local analytics & preprocessing",
   {"type": "flow", "nodeY": 0, "listY": 260, "nodes": [
     {"icon": "🌡️", "l": "Raw sensor data", "s": "noisy, huge", "c": "c8", "at": 0}, {"icon": "🧹", "l": "Edge device", "s": "cleans & checks", "c": EDGE, "at": 0.4}, {"icon": "☁️", "l": "Cloud", "s": "gets only results", "c": CLOUD, "at": 5}],
    "steps": [{"t": "**Data filtering** — keep only what matters", "at": 1, "from": 0, "to": 1, "c": EDGE},
              {"t": "**Noise removal** — clean up jittery readings", "at": 2, "hl": 1, "c": EDGE},
              {"t": "**Feature extraction** — e.g. \"average vibration = 4.2\"", "at": 3, "hl": 1, "c": EDGE},
              {"t": "**Event detection** — abnormal vibration, overheating, voltage fluctuations", "at": 4, "hl": 1, "c": "c7"},
              {"t": "→ **Avoids sending raw sensor data to the cloud**", "at": 5, "from": 1, "to": 2, "c": CLOUD}]},
   ["Second, local analytics and preprocessing. Edge devices perform four jobs.",
    "Data filtering: keeping only the readings that matter.",
    "Noise removal: cleaning up jittery, random errors in the readings.",
    "Feature extraction: turning thousands of numbers into a few useful values, like the average vibration.",
    "Event detection: spotting abnormal vibration, overheating, or voltage fluctuations.",
    "This avoids sending raw sensor data to the cloud. Only the useful results travel."],
   tip=("Edge preprocessing: **filter, de-noise, extract features, detect events**.", 1))

sc("edgeCD", "Edge uses C & D: reliability, security", "Slides 6–7 · Where edge is used (C, D)", "C. Reliability & D. Security at the source",
   cards([("📴","C. Works when network fails","CPS **cannot stop** if the cloud is unreachable. Edge gives **local autonomy** — machines **keep functioning** even with **connectivity loss**.","c3",0),
          ("💾","D. Secure data storage","Data is stored safely **on site**.","c7",2),
          ("🕵️","D. Early attack detection","Spots **cyber anomalies** right at the source.","c6",3),
          ("🔑","D. Authentication at gateway","Only **trusted devices** get in. Protects **industrial CPS** and **smart grids** from cyber-attacks.","c4",4)], cols=2),
   ["Third, reliability when the network fails. A CPS cannot stop working just because the cloud is unreachable.",
    "Edge ensures local autonomy. Machines continue functioning even with connectivity loss. A factory keeps running even if the internet goes down.",
    "Fourth, security at the source. Edge adds secure data storage.",
    "Early attack detection, by spotting cyber anomalies.",
    "And authentication at the gateway, so only trusted devices can connect. This helps protect industrial CPS and the smart grid from cyber attacks."],
   tip=("Edge = **local autonomy** when cloud is down + **security at the source**.", 1))

sc("fog", "Fog computing: what & why", "Slides 8 & 38 · Fog computing in CPS", "2. Fog computing",
   {"type": "tiers", "chipFs": 25, "tiers": [
     {"l": "☁️ Cloud", "d": "too far → delay", "c": CLOUD, "at": 3, "chips": ["huge power", "but slow to reach"]},
     {"l": "🌫️ Fog", "d": "between edge & cloud", "c": FOG, "at": 0, "chips": ["routers", "switches", "gateways", "local servers", "larger computation", "still low latency"]},
     {"l": "📍 Edge", "d": "too small", "c": EDGE, "at": 4, "chips": ["very fast", "limited processing"]}]},
   ["Fog computing sits between the edge and the cloud. Like real fog, it's a cloud that is close to the ground.",
    "It provides a distributed layer of intermediate computing nodes, usually close to the physical environment.",
    "These nodes are routers, switches, gateways, and local servers.",
    "Why does CPS need fog? Because the cloud is too far away, which adds delay.",
    "And the edge is too small, with limited processing power.",
    "Fog provides larger computation, but still with low latency. It also supports regional coordination, reduces bandwidth, and keeps latency under a second."],
   tip=("Cloud **too far**, edge **too small** → fog is **in between**.", 3))

sc("fogA", "Fog use A: coordination", "Slide 9 · Where fog is used (A)", "A. Coordinating many CPS devices",
   cards([("🤖","Factory robots","Multiple robots on a factory floor.","c5",1),
          ("🚦","Smart transportation","Traffic signals **+** vehicles together.","c3",2),
          ("⚡","Smart grid","Energy balancing across a neighbourhood.","c6",3),
          ("🚁","Drone swarms","Multi-drone coordination.","c4",4)], cols=4),
   ["Where is fog used? First, distributed coordination of multiple CPS devices. One edge device only knows about itself. Fog sees the whole area.",
    "Fog nodes coordinate multiple robots on a factory floor,",
    "traffic signals together with vehicles in smart transportation,",
    "energy balancing in the smart grid,",
    "and multiple drones flying together.",
    "So fog gives region level processing."],
   tip=("Fog = **region-level** processing.", 5))

sc("fogB", "Fog use B: heavy analytics", "Slide 10 · Where fog is used (B)", "B. Heavy analytics not possible at the edge",
   cards([("🔮","Predictive maintenance ML","Machine-learning models that predict failures.","c1",1),
          ("🧩","Large-scale sensor fusion","Combine data from **many** sensors.","c5",2),
          ("📹","Multi-camera video analytics","Video from **many cameras** at once.","c3",3),
          ("🗺️","Optimization","**Scheduling, routing, energy balancing**.","c6",4)], cols=2),
   ["Second, heavy analytics that are not possible at the edge.",
    "Examples: predictive maintenance machine learning models.",
    "Large scale sensor fusion, combining data from many sensors.",
    "Video analytics from multiple cameras.",
    "And optimization tasks, like scheduling, routing, and energy balancing.",
    "Fog servers run GPU and CPU clusters near the CPS environment."],
   tip=("Fog runs **GPU/CPU clusters near** the CPS.", 5))

sc("fogCD", "Fog uses C & D", "Slides 11–12 · Where fog is used (C, D)", "C. Aggregation & D. Low-latency comms",
   {"type": "multi", "parts": [
     {"x": 0, "w": 840, "viz": cards([("📦","C. Data aggregation & hierarchy","**Batch analytics** · **time-series storage** · **local backup** · **edge data consolidation**. Saves bandwidth → **only refined results** go to the cloud.","c1",0)], cols=1)},
     {"x": 880, "w": 840, "viz": cards([("📡","D. Latency-sensitive communication","Fog manages **vehicle-to-infrastructure (V2I)**, **drone-to-base-station**, **machine-to-machine (M2M)**. Keeps latency within **10–100 ms**.","c3",3)], cols=1)}]},
   ["Third, data aggregation and hierarchical processing. Fog performs batch analytics, time series storage, local backup, and consolidation of edge data.",
    "Time series means readings stored in time order, like temperature every second.",
    "This saves bandwidth, and only refined results are sent to the cloud.",
    "Fourth, latency sensitive communication. Fog nodes manage vehicle to infrastructure, drone to base station, and machine to machine communication.",
    "Fog keeps latency within 10 to 100 milliseconds."],
   tip=("Fog latency: **10–100 ms**.", 4))

sc("arch", "Edge + Fog + Cloud architecture", "Slides 13 & 39 · Combined architecture", "Edge + Fog + Cloud architecture",
   {"type": "stack", "w": 760, "layers": [
     {"l": "☁️ CLOUD layer — storage, global analytics", "c": CLOUD, "at": 4},
     {"l": "🌫️ FOG layer — local server / router / gateway", "c": FOG, "at": 3},
     {"l": "📍 EDGE layer — MCU, PLC, IoT device", "c": EDGE, "at": 2},
     {"l": "🔧 SENSORS / ACTUATORS — physical layer", "c": "c8", "at": 1}],
    "brackets": [{"from": 0, "to": 0, "l": "→ **long-term learning**", "c": CLOUD, "at": 4},
                 {"from": 1, "to": 1, "l": "→ **regional intelligence**", "c": FOG, "at": 3},
                 {"from": 2, "to": 2, "l": "→ **immediate actions**", "c": EDGE, "at": 2},
                 {"from": 3, "to": 3, "l": "senses & acts on the world", "c": "c8", "at": 1}]},
   ["Now put it all together. This is the combined edge, fog and cloud architecture.",
    "At the bottom, sensors and actuators, the physical layer.",
    "Above them, the edge layer: microcontrollers, PLCs, and IoT devices. Edge means immediate actions.",
    "Then the fog layer: local servers, routers and gateways. Fog means regional intelligence and coordination.",
    "At the top, the cloud layer, for storage and global analytics. Cloud means long term learning.",
    "Memory line: edge acts now, fog coordinates the region, cloud learns for the long term."],
   tip=("Edge → **immediate** · Fog → **regional** · Cloud → **long-term learning**", 2))

sc("usecases", "Use cases", "Slides 14–15 & 40 · Examples of fog & edge in CPS", "Four use cases, three layers each",
   {"type": "table", "fs": 26, "cols": ["Use case", "📍 Edge", "🌫️ Fog", "☁️ Cloud"], "widths": ["22%","28%","26%","24%"], "rows": [
     {"c": ["Smart manufacturing (Industry 4.0)", "Real-time machine vibration monitoring", "Predictive maintenance (ML)", "Long-term analysis & planning"], "color": "c6", "at": 1},
     {"c": ["Autonomous vehicles", "Object detection, lane tracking", "Traffic coordination", "Fleet analytics & software updates"], "color": "c3", "at": 2},
     {"c": ["Smart grid", "Meter readings, local fault detection", "Substation monitoring / analytics", "Load forecasting"], "color": "c5", "at": 3},
     {"c": ["Smart healthcare", "Patient vitals monitoring", "Emergency alert processing", "Medical record storage"], "color": "c7", "at": 4}]},
   ["Let's see four real examples. In each, notice how the job gets bigger and slower as we go up the layers.",
    "Smart manufacturing, or Industry 4.0: edge monitors machine vibration in real time. Fog runs predictive maintenance with machine learning. Cloud does long term analysis and planning.",
    "Autonomous vehicles: edge does object detection and lane tracking. Fog coordinates traffic. Cloud does fleet analytics and software updates.",
    "Smart grid: edge takes meter readings and detects local faults. Fog monitors substations. Cloud does load forecasting.",
    "Smart healthcare: edge monitors patient vitals. Fog processes emergency alerts. Cloud stores medical records."],
   tip=("Learn one row well — e.g. **smart grid: meter → substation → forecasting**.", 3))

sc("scenario", "Smart factory scenario", "Slide 16 · Industrial CPS scenario", "Scenario: one smart manufacturing plant",
   {"type": "hero", "icon": "🏭", "big": "A smart factory", "size": 90, "y": 150, "sub": "machines · robots · sensors · quality-control cameras", "subY": 280, "chipY": 380,
    "chips": [{"t": "Real-time control", "c": EDGE, "at": 2}, {"t": "Safety", "c": "c7", "at": 2.2}, {"t": "Optimization", "c": FOG, "at": 2.4}, {"t": "Long-term analytics", "c": CLOUD, "at": 2.6}]},
   ["Now the deck walks through one complete example: the coordination of edge, fog and cloud in an industrial CPS.",
    "Imagine a smart manufacturing plant, with machines, robots, sensors, and quality control cameras.",
    "Different layers coordinate to ensure real time control, safety, optimization, and long term analytics.",
    "We'll go layer by layer, from the bottom up."])

sc("phys", "Layer 1: physical", "Slide 17 · 1. Physical layer", "Layer 1 — Physical: sensors & machines",
   cards([("📳","Vibration sensors","","c6",1),("🌡️","Temperature sensors","","c7",1.2),("📏","Proximity sensors","","c3",1.4),
          ("📷","Cameras (AI vision)","","c4",1.6),("🦾","Robots, conveyors, motors","","c1",1.8),("🌊","Output","They continuously produce **high-speed operational data**.","c5",2)], cols=3),
   ["Layer one is the physical layer: the sensors and machines.",
    "Machines have vibration sensors, temperature sensors, proximity sensors, AI vision cameras, and robots, conveyors and motors.",
    "Together they continuously produce high speed operational data."])

sc("edgeL", "Layer 2: edge", "Slides 18–20 · 2. Edge layer", "Layer 2 — Edge: real-time control",
   {"type": "multi", "parts": [
     {"x": 0, "w": 560, "viz": cards([("🧠","Edge devices","**PLCs** · **industrial controllers** · **embedded processors** · **Edge AI boxes** (NVIDIA Jetson, Intel Movidius)","c5",0)], cols=1)},
     {"x": 600, "w": 1120, "viz": {"type": "steps", "listW": 1120, "fs": 26, "steps": [
        {"t": "✔ **Real-time actions (1–10 ms)**: shut down a machine if vibration crosses a threshold · robot path correction · adjust motor speed · reject a defective workpiece on the spot", "at": 1, "c": EDGE},
        {"t": "**On-device vision defect detection** · **overheating prediction** · **sensor fusion**", "at": 4, "c": EDGE},
        {"t": "**Operation continuity** — even in network failure, machines keep working", "at": 6, "c": "c3"},
        {"t": "➡ Outcome: **Safety + real-time responsiveness**", "at": 7, "c": "c7"}]}}]},
   ["Layer two is the edge layer, for real time, machine level control. Edge devices include PLCs, industrial controllers, embedded processors, and edge AI boxes like NVIDIA Jetson and Intel Movidius.",
    "Its first responsibility: real time actions, within 1 to 10 milliseconds.",
    "For example: shut down a machine if vibration crosses a threshold, correct a robot's path, or adjust motor speed.",
    "Or reject a defective workpiece on the spot.",
    "It also does on device vision defect detection, overheating prediction, and sensor fusion.",
    "Sensor fusion means combining several sensors to get a better picture.",
    "And operation continuity: even if the network fails, the machines keep working.",
    "Outcome: safety, and real time responsiveness."],
   tip=("Edge: **1–10 ms** actions · outcome **safety + responsiveness**", 1))

sc("fogL", "Layer 3: fog", "Slides 21–24 · 3. Fog layer", "Layer 3 — Fog: shop-floor coordination",
   cards([("🖥️","Fog nodes","**Industrial gateways** · **local servers** · **on-premises clusters** · **5G base station** in the factory.","c1",0),
          ("🤝","Coordinate machines","Robot-to-robot **scheduling** · **prevent collisions** of arms · **synchronize conveyors & AGVs** · **load balancing** between lines.","c5",2),
          ("📊","Regional analytics","**Batch analytics** for the whole line · **energy optimization** · **predictive maintenance** ML · **shop-floor dashboards**.","c3",4),
          ("📦","Aggregation & filtering","Collect from **hundreds** of edge devices · **store locally** (fast DB) · send **only insights** to cloud.","c6",6),
          ("⏱️","Medium-latency decisions (10–100 ms)","**Line-level quality deviation** · **production rate tuning** · **dynamic resource allocation**.","c4",8),
          ("➡","Outcome","**Smart coordination + production optimization**.","c2",9)], cols=2, compact=True, fs=25),
   ["Layer three is the fog layer, for shop floor or plant level coordination. It sits between edge and cloud. Fog nodes are industrial gateways, local servers, on premises clusters, and even a 5G base station inside the factory.",
    "Responsibility one: coordinating multiple machines.",
    "That means robot to robot scheduling, preventing collisions between automated arms, synchronizing conveyors and AGVs, which are automated guided vehicles, and load balancing between production lines.",
    "Responsibility two: regional analytics.",
    "Batch analytics for the entire line, energy optimization for all machines, predictive maintenance using machine learning models, and shop floor dashboards.",
    "Responsibility three: aggregation and filtering.",
    "It collects data from hundreds of edge devices, stores it locally in a fast database, and sends only insights to the cloud.",
    "Responsibility four: medium latency decisions, in 10 to 100 milliseconds.",
    "Such as line level quality deviation, production rate tuning, and dynamic resource allocation.",
    "Outcome: smart coordination, and production optimization."],
   tip=("Fog: **10–100 ms** decisions · outcome **coordination + optimization**", 8))

sc("cloudL", "Layer 4: cloud", "Slides 25–28 · 4. Cloud layer", "Layer 4 — Cloud: enterprise brain",
   cards([("☁️","Cloud systems","**Azure IoT Hub** · **AWS IoT Core** · **Google Cloud IoT** · **ERP/SCADA** integrated cloud modules.","c2",0),
          ("🌍","Global decision-making","**Long-term production forecasting** · **supply chain optimization** · **inventory planning** · **enterprise analytics across many factories**.","c1",2),
          ("💪","High-power analytics","**Training ML models** for predictive maintenance · **digital twins** · **big data storage** · **cross-factory KPI comparison**.","c3",4),
          ("📲","OTA (Over-The-Air) updates","Update **edge AI models** · update **machine firmware** · push **load-balancing policies to fog**.","c6",6),
          ("➡","Outcome","**Strategic decisions + global optimization**.","c5",8)], cols=2, compact=True, fs=26),
   ["Layer four is the cloud layer, for plant to enterprise intelligence. Cloud systems include Azure IoT Hub, AWS IoT Core, Google Cloud IoT, and ERP or SCADA integrated cloud modules.",
    "ERP is the company's business software. SCADA is supervisory control and data acquisition, the system that oversees industrial processes.",
    "Responsibility one: global decision making.",
    "Long term production forecasting, supply chain optimization, inventory planning, and enterprise analytics across many factories.",
    "Responsibility two: high power analytics.",
    "Training machine learning models for predictive maintenance, digital twins, which are virtual copies of real machines, big data storage, and comparing KPIs, key performance indicators, across factories.",
    "Responsibility three: OTA, over the air updates.",
    "The cloud updates edge AI models, updates machine firmware, and pushes load balancing policies down to the fog.",
    "Outcome: strategic decisions, and global optimization."],
   tip=("Cloud: **train ML, digital twins, OTA updates** · outcome **strategy + global optimization**", 2))

sc("flows", "How the layers coordinate", "Slide 29 · Flow summary", "Four flows between the layers",
   {"type": "flow", "nodeY": 0, "listY": 250, "nodes": [
     {"icon": "⚙️", "l": "Machines", "c": "c8", "at": 0}, {"icon": "📍", "l": "Edge", "c": EDGE, "at": 0}, {"icon": "🌫️", "l": "Fog", "c": FOG, "at": 0}, {"icon": "☁️", "l": "Cloud", "c": CLOUD, "at": 0}],
    "steps": [{"t": "**Flow 1 — Real-time operation:** Machines → Edge → **immediate action** (ms-level)", "at": 1, "from": 0, "to": 1, "c": EDGE},
              {"t": "**Flow 2 — Local coordination:** Edge → Fog → **shop-floor optimization**", "at": 2, "from": 1, "to": 2, "c": FOG},
              {"t": "**Flow 3 — Enterprise intelligence:** Fog → Cloud → analysis & **ML training** → updates back to Fog → Edge", "at": 3, "from": 2, "to": 3, "c": CLOUD},
              {"t": "**Flow 4 — Control feedback:** Cloud → Fog → Edge → Machine", "at": 5, "from": 3, "to": 0, "d": 2.6, "c": "c3"}]},
   ["How do the layers work together? There are four flows.",
    "Flow one, real time operation: machines send data to the edge, and the edge takes immediate action, at millisecond level.",
    "Flow two, local coordination: the edge sends to the fog, and the fog does shop floor optimization.",
    "Flow three, enterprise level intelligence: fog sends to the cloud. The cloud does analysis and machine learning training.",
    "Then the cloud sends updates back down to the fog, and on to the edge.",
    "Flow four, control feedback: commands travel from cloud, to fog, to edge, and finally to the machine."],
   tip=("Data goes **up**, smarter rules come **down**.", 5))

sc("pm", "Example: predictive maintenance", "Slide 30 · Example scenario", "Example: predictive maintenance",
   {"type": "flow", "nodeY": 0, "listY": 250, "nodes": [
     {"icon": "📍", "l": "Edge", "c": EDGE, "at": 0}, {"icon": "🌫️", "l": "Fog", "c": FOG, "at": 0}, {"icon": "☁️", "l": "Cloud", "c": CLOUD, "at": 0}],
    "steps": [{"t": "**Edge:** motor vibration **exceeds threshold** → sends **alert to Fog**", "at": 1, "from": 0, "to": 1, "c": EDGE},
              {"t": "**Fog:** combines vibration data from **all motors** · analyzes the pattern with **ML** · **predicts which motor will fail** soon", "at": 2, "hl": 1, "c": FOG},
              {"t": "**Fog → Cloud:** sends a **maintenance request**", "at": 4, "from": 1, "to": 2, "c": FOG},
              {"t": "**Cloud:** schedules maintenance by **inventory** · **orders spare parts** · **updates ERP**", "at": 5, "hl": 2, "c": CLOUD},
              {"t": "**Cloud → Fog/Edge:** sends a **new model**", "at": 6, "from": 2, "to": 0, "d": 2.2, "c": CLOUD}]},
   ["Here's a full example: predictive maintenance.",
    "At the edge: a motor's vibration exceeds its limit, so the edge sends an alert to the fog.",
    "At the fog: it combines vibration data from all the motors, and analyzes the pattern using machine learning.",
    "It predicts which motor will fail soon.",
    "Then it sends a maintenance request to the cloud.",
    "At the cloud: it schedules maintenance based on inventory, orders spare parts, and updates the ERP system.",
    "Finally, it sends a new, improved model back to the fog and edge."])

sc("robots", "Example: robotic assembly line", "Slide 31 · Example scenario", "Example: smart robotic assembly line",
   {"type": "tiers", "chipFs": 25, "tiers": [
     {"l": "☁️ Cloud", "d": "", "c": CLOUD, "at": 4, "chips": ["optimizes production rate", "analyzes historical performance", "pushes new control policy"]},
     {"l": "🌫️ Fog", "d": "", "c": FOG, "at": 2, "chips": ["coordinates robots to avoid collision", "adjusts robot speed by workload"]},
     {"l": "📍 Edge", "d": "", "c": EDGE, "at": 0, "chips": ["each robot avoids hitting objects", "checks joint torque & position"]}]},
   ["Second example: a smart robotic assembly line. At the edge, each robot avoids hitting objects,",
    "and checks its own joint torque and position.",
    "At the fog, multiple robots are coordinated so they don't collide with each other,",
    "and robot speed is adjusted based on workload.",
    "At the cloud, the production rate is optimized, historical performance is analyzed,",
    "and a new control policy is pushed down to the robots."])

sc("edgevsfog", "Edge vs Fog", "Slides 32–33 & 41 · Comparison", "Edge vs Fog vs Cloud",
   {"type": "table", "fs": 28, "cols": ["", "📍 Edge", "🌫️ Fog", "☁️ Cloud"], "widths": ["16%","28%","28%","28%"], "rows": [
     {"c": ["Where", "Local, device-level", "Regional (shop floor)", "Global, enterprise"], "color": "c8", "at": 1},
     {"c": ["Latency", "Ultra-low **< 10 ms**", "Medium **10–100 ms**", "Seconds or more"], "color": "c3", "at": 2},
     {"c": ["Handles", "Real-time machine control", "Coordination & heavy analytics", "Global optimization, storage, ML training, enterprise integration"], "color": "c1", "at": 3},
     {"c": ["Enables", "Millisecond control", "Smart coordination, predictive maintenance", "Enterprise-wide optimization"], "color": "c5", "at": 5}]},
   ["Let's compare the layers side by side.",
    "Edge is local, device level computing. Fog is regional computing. Cloud is global.",
    "Edge has ultra low latency, under 10 milliseconds. Fog has medium latency, 10 to 100 milliseconds.",
    "Edge handles real time machine control. Fog handles factory floor coordination and medium latency analytics.",
    "Cloud handles global optimization, storage, machine learning training, and enterprise integration.",
    "Together they create a hierarchical CPS architecture, enabling millisecond control, smart coordination, predictive maintenance, and enterprise wide optimization."],
   tip=("Edge **< 10 ms** · Fog **10–100 ms**", 2))

sc("summary", "Summary", "Slide 42 · Summary", "How fog & edge enhance CPS",
   cards([("⏱️","Reducing latency","","c3",1),("⚡","Real-time decision making","","c5",2),("🛡️","Improving reliability","","c1",3),("🏛️","Hierarchical processing","","c2",4),("🤖","Supporting smart automation","","c6",5)], cols=5),
   ["To summarize, fog and edge computing enhance CPS in five ways.",
    "Reducing latency.",
    "Enabling real time decision making.",
    "Improving reliability.",
    "Providing hierarchical processing.",
    "And supporting smart automation. Remember: edge acts now, fog coordinates, cloud learns. Good luck!"],
   endcard=True, hold=3)

L = {"title": "Fog & Edge Computing in CPS Explained Simply — Module 7 Full Revision",
     "slug": "iot-fog-edge", "description": "Fog and edge computing in cyber-physical systems: edge uses, fog uses, edge-fog-cloud architecture, use cases, a full smart-factory scenario, coordination flows and edge vs fog.",
     "tags": ["fog computing", "edge computing", "CPS", "Industry 4.0", "exam revision"], "voice": "am_michael", "speed": 1.0, "fps": 24, "captions": True,
     "endCard": "📘 Edge < 10 ms · Fog 10–100 ms · Cloud learns", "thumbnail": "arch@20", "pronounce": P, "scenes": S}
json.dump(L, open('/home/user/JarvisAI/visuals/iot-fog-edge/lesson.json', 'w'), indent=1, ensure_ascii=False)
