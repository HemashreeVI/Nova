import json
P = {"CPCC":"C P C C","CPS":"C P S","IoT":"I o T","SNS":"S N S"}
S = []
def sc(id, chapter, kicker, title, viz, lines, tip=None, **kw):
    d = {"id": id, "chapter": chapter, "kicker": kicker, "title": title, "viz": viz, "lines": lines}
    if tip: d["tip"] = {"t": tip[0], "at": tip[1]}
    d.update(kw); S.append(d)
def cards(items, cols=None, **kw):
    v = {"type": "cards", "items": [dict(zip(["icon","h","b","c","at"], it)) for it in items]}
    if cols: v["cols"] = cols
    v.update(kw); return v

sc("intro", "Intro", "Module 7", None,
   {"type": "hero", "icon": "☁️", "big": "Cyber-Physical\nCloud Computing", "size": 92, "y": 120, "sub": "CPCC — opportunities and challenges", "subY": 340, "chipY": 440,
    "chips": [{"t": t, "c": c, "at": 2 + i*0.15} for i,(t,c) in enumerate([("What is CPCC","c1"),("Cyber + physical world","c2"),("Opportunities","c5"),("Challenges","c7"),("Real-time","c3"),("Big data","c6"),("Data mining","c4"),("Data integration","c9"),("Load balancing","c8")])]},
   ["A hospital has thousands of sensors on patients. A city has sensors on every road. Where does all that data go, and who thinks about it?",
    "The answer is the cloud. Joining cyber physical systems with cloud computing is called Cyber Physical Cloud Computing, or CPCC.",
    "This video covers every slide: the definition, how the cyber and physical worlds connect, opportunities, challenges, real time processing, big data, data mining, data integration, and load balancing.",
    "Let's begin."], pad=[0.6, 1.0])

sc("def", "What is CPCC?", "Slide 2 · Introduction to CPCC", "What is CPCC?",
   cards([("🏗️","Definition","A **system environment** to **rapidly build, modify and provision** CPS using **cloud computing**.","c1",0),
          ("🧩","Everything \"as a service\"","Integrates **computing, storage, networking and software** as a service — rent it, don't build it.","c2",2),
          ("🌍","Key feature 1","**Global intelligent systems** that **collect real-world data**.","c5",4),
          ("⚡","Key feature 2","**Rapid modification and deployment** of CPS applications.","c3",5)], cols=2),
   ["CPCC is defined as a system environment to rapidly build, modify, and provision cyber physical systems using cloud computing.",
    "Provision means setting up and supplying. So the cloud helps us create and launch CPS quickly.",
    "It integrates computing, storage, networking, and software as a service.",
    "As a service means you rent these from the cloud when you need them, instead of buying and managing your own machines.",
    "Key feature one: CPCC builds global intelligent systems that collect real world data.",
    "Key feature two: CPS applications can be modified and deployed rapidly. Change the software in the cloud, and every device benefits."],
   tip=("CPCC = CPS **built, modified and provisioned** using **cloud**, everything **as a service**.", 0))

sc("worlds", "Cyber world & physical world", "Slide 3 · How the two worlds connect", "The cyber world and the physical world",
   {"type": "tiers", "chipFs": 26, "tiers": [
     {"l": "Cyber world", "d": "in the cloud", "c": "c2", "at": 1, "chips": ["📊 Data", "⚙️ Processes", "📱 Apps", "🌐 Web", "💬 SNS (social networks)", "🛎️ Services"]},
     {"l": "Ubiquitous internet", "d": "connects both worlds", "c": "c1", "at": 3, "chips": ["⬆️ Monitor (physical → cyber)", "⬇️ Control (cyber → physical)", "🔁 Information flow"]},
     {"l": "Physical world", "d": "real things & people", "c": "c5", "at": 0, "chips": ["📡 Towers", "📱 Phones", "🏃 People", "🚌 Vehicles", "🖥️ Kiosks & screens"]}]},
   ["The slide shows two worlds. At the bottom, the physical world: phones, towers, people, vehicles, kiosks and screens.",
    "At the top, the cyber world: data, processes, apps, the web, social networking services, and other services.",
    "Ubiquitous means everywhere. The ubiquitous internet sits in the middle and links both worlds.",
    "Information flows in a loop. The cyber world monitors the physical world, collecting data from sensors.",
    "Then the cyber world controls the physical world, sending back decisions and commands.",
    "Monitor, then control, again and again. That loop is the heart of every cyber physical system."],
   tip=("Loop: physical **→ monitor →** cyber **→ control →** physical", 3))

sc("opps", "Opportunities in CPCC", "Slide 4 · Opportunities", "Opportunities in CPCC",
   {"type": "multi", "parts": [
     {"x": 0, "w": 840, "viz": cards([("🏥","Healthcare systems","Patient monitoring, remote care.","c7",1),
                                       ("🌪️","Smart disaster info systems","Early warnings, rescue coordination.","c6",2),
                                       ("🏙️","Smart city applications","Traffic, lighting, waste, parking.","c1",3),
                                       ("👥","Social life networks","Connecting people's real-world activity.","c4",4)], cols=1, compact=True, fs=26)},
     {"x": 880, "w": 840, "viz": cards([("📈","Scalability & flexibility","Add more computers instantly when demand grows.","c5",6),
                                         ("🗄️","Efficient data management","Store and organise huge sensor data.","c3",7),
                                         ("⏱️","Real-time processing","Process streams quickly for fast decisions.","c2",8)], cols=1, compact=True, fs=26)}]},
   ["Now the opportunities. CPCC supports four kinds of applications.",
    "Healthcare systems, like monitoring patients remotely.",
    "Smart disaster information systems, for early warnings and rescue.",
    "Smart city applications, like traffic and street lighting.",
    "And social life networks, connecting people's real world activity.",
    "It also brings three benefits.",
    "One: scalability and flexibility. Need more computing power? The cloud adds it in minutes.",
    "Two: efficient data management. The cloud stores and organises huge amounts of sensor data.",
    "Three: real time processing capabilities, so decisions can be made fast."],
   tip=("Apps: **healthcare, disaster, smart city, social**. Benefits: **scalable, data mgmt, real-time**.", 1))

sc("chall", "Challenges in CPCC", "Slide 5 · Challenges", "Challenges in CPCC",
   cards([("🧬","Complex CPS","The **complex structure and behaviour** of CPS makes **integration** with the cloud hard.","c7",1),
          ("⏱️","Real-time, safety, reliability","Must guarantee **real-time**, **safety** and **reliability** requirements.","c6",2),
          ("🔐","Data security","Critical in **healthcare** and **military** applications.","c4",4),
          ("⚖️","Load balancing","Spreading work **effectively** across CPS cloud platforms.","c3",5)], cols=2),
   ["Now the challenges. There are two general ones, and two specific issues.",
    "General challenge one: CPS have a complex structure and behaviour, which makes integrating them with the cloud difficult.",
    "General challenge two: we must still ensure real time, safety, and reliability requirements. A cloud far away can add delay.",
    "Now the specific issues.",
    "Issue one: data security, especially in critical applications like healthcare and military. A leak or a hack could cost lives.",
    "Issue two: effective load balancing for CPS cloud platforms. We'll see this again at the end."],
   tip=("Specific issues: **data security** (healthcare, military) + **load balancing**.", 4))

sc("rt", "Real-time processing", "Slide 6 · Real-time processing", "Real-time processing",
   {"type": "flow", "nodeY": 0, "listY": 260, "nodes": [
     {"icon": "🌡️", "l": "Sense", "s": "sensor reading", "c": "c5", "at": 0}, {"icon": "📶", "l": "Send", "s": "network", "c": "c1", "at": 0.3},
     {"icon": "☁️", "l": "Process", "s": "cloud", "c": "c2", "at": 0.6}, {"icon": "🦾", "l": "Act", "s": "actuator", "c": "c3", "at": 0.9}],
    "steps": [{"t": "**Data streams** must be processed with **minimal delay**.", "at": 1, "from": 0, "to": 2, "d": 2, "c": "c1"},
              {"t": "CPS relies heavily on **real-time operations** for **accurate and fast decision-making**.", "at": 2, "from": 2, "to": 3, "c": "c2"},
              {"t": "Challenge: **delay in sensing and processing must be minimized**.", "at": 4, "hl": [0, 2], "c": "c7"}]},
   ["Every CPS loop has four steps: sense, send, process, and act.",
    "Key requirement one: data streams must be processed with minimal delay.",
    "Key requirement two: CPS relies heavily on real time operations, for accurate and fast decision making.",
    "Imagine a car's braking system. A decision that arrives one second late is useless.",
    "So the challenge is: the delay in sensing and in processing must both be minimized."],
   tip=("Real-time = **minimal delay** in **sensing + processing**.", 4))

sc("bigdata", "Big data in CPCC", "Slide 7 · Big data", "Big data in CPCC",
   cards([("🗄️","Opportunity: handles large volumes","Cloud computing **effectively handles large data volumes**.","c5",1),
          ("📤","Opportunity: storage & offloading","Enables **data storage** and **computation offloading** — devices send heavy work to the cloud.","c1",2),
          ("⏳","Challenge: real-time latency","Moving big data to the cloud takes time → **managing latency** is hard.","c7",4),
          ("🔎","Challenge: storage, analysis, mining","Where to **store** it, and how to **analyse** and **mine** it.","c6",5)], cols=2),
   ["Next, big data. CPS sensors produce enormous amounts of data, every second.",
    "Opportunity one: cloud computing handles large data volumes effectively.",
    "Opportunity two: it enables data storage, and computation offloading. Offloading means a small device sends heavy calculations to the cloud.",
    "But there are challenges.",
    "Challenge one: managing real time latency. Sending big data to a far cloud is slow.",
    "Challenge two: addressing storage, data analysis, and data mining for all this data."],
   tip=("Offloading = small device sends **heavy computation** to the cloud.", 2))

sc("mining", "Data mining", "Slide 8 · Data mining", "Data mining: finding meaning in data",
   cards([("🧩","Extract patterns","Find **useful patterns and correlations** — e.g. \"pressure rises before every failure\".","c1",0),
          ("🚨","Detect anomalies","Spot **unusual readings in real-time data** — e.g. a sudden heart-rate spike.","c7",2),
          ("📐","Pattern-based algorithms","Algorithms that **search for known shapes** in the data.","c5",3),
          ("🔤","Symbolic data abstraction","Turn long number streams into **short symbols** (\"low, normal, HIGH\") that are easy to search.","c3",4)], cols=2),
   ["Data mining means digging useful knowledge out of raw data. Key benefit one: extracting useful patterns and correlations.",
    "For example, discovering that pressure always rises before a machine fails.",
    "Key benefit two: detecting anomalies, meaning unusual values, in real time data. Like a sudden spike in a patient's heart rate.",
    "Technique one: pattern based algorithms, which search the data for known patterns.",
    "Technique two: symbolic data abstraction. Long streams of numbers are turned into short symbols, like low, normal, and high, which are much easier to search."],
   tip=("Benefits: **patterns** + **anomalies**. Techniques: **pattern-based**, **symbolic abstraction**.", 3))

sc("integ", "Data integration", "Slide 9 · Data integration", "Data integration: one common language",
   cards([("🔗","Opportunity: unified representation","**Unify how data is represented** so all systems read it the same way.","c5",0),
          ("🗣️","Opportunity: semantic interoperability","Systems **understand the meaning** of each other's data.","c1",1),
          ("🧮","Challenge: heterogeneous data","Different **units** (°C vs °F), **uncertainties** (accuracy), **structures** (formats).","c7",3),
          ("🧠","Challenge: smart filtering","Needs **intelligent filtering and interpretation** techniques.","c6",5)], cols=2),
   ["Data integration means combining data from many different sources.",
    "Opportunities: unifying data representation, and improving semantic interoperability. Semantic interoperability means systems understand the meaning of each other's data, not just the bytes.",
    "Now the challenges.",
    "Challenge one: handling heterogeneous data. Heterogeneous means mixed. Data comes in different units, with different uncertainties, and in different structures.",
    "For example, one sensor reports Celsius, another Fahrenheit. One is very accurate, another is rough.",
    "Challenge two: we need intelligent filtering and interpretation techniques to make sense of it all."],
   tip=("Heterogeneous = different **units, uncertainties, structures**.", 3))

sc("lb", "Load balancing", "Slide 10 · Load balancing", "Load balancing",
   {"type": "bars", "top": 20, "labelW": 300, "max": 100, "items": [
     {"l": "Server 1", "v": 98, "txt": "😵 overloaded (before)", "c": "c7", "at": 1},
     {"l": "Server 2", "v": 15, "txt": "😴 idle (before)", "c": "c8", "at": 1.2},
     {"l": "Server 1", "v": 55, "txt": "✅ balanced (after)", "c": "c5", "at": 2},
     {"l": "Server 2", "v": 55, "txt": "✅ balanced (after)", "c": "c5", "at": 2.2}],
    "notes": [{"t": "✔ **Prevents system overload** · ✔ **Optimizes communication and storage processes**", "y": 440, "at": 2, "fs": 30},
              {"t": "🔬 Research focus: **efficient load balancing techniques for CPS in cloud environments**", "y": 520, "at": 4, "fs": 30, "c": "c3"}]},
   ["Finally, load balancing. It means spreading work evenly across many servers.",
    "Without it, one server is overloaded while another sits idle.",
    "Its importance: it prevents system overload, and it optimizes communication and storage processes.",
    "For a CPS, an overloaded server means delayed decisions, which can be dangerous.",
    "That's why research focuses on efficient load balancing techniques for CPS in cloud environments."],
   tip=("Load balancing: **prevents overload**, **optimizes communication & storage**.", 2))

sc("recap", "Recap", "Recap", "CPCC on one page",
   {"type": "table", "fs": 27, "cols": ["Topic", "Remember"], "widths": ["24%", "76%"], "rows": [
     {"c": ["Definition", "Environment to rapidly build, modify & provision CPS using cloud; computing, storage, networking, software as a service"], "color": "c1", "at": 0},
     {"c": ["Two worlds", "Physical ↔ ubiquitous internet ↔ cyber · monitor up, control down"], "color": "c2", "at": 1},
     {"c": ["Opportunities", "Healthcare, disaster, smart city, social networks · scalable, data management, real-time"], "color": "c5", "at": 2},
     {"c": ["Challenges", "Complex CPS integration · real-time, safety, reliability · data security · load balancing"], "color": "c7", "at": 3},
     {"c": ["Real-time & big data", "Minimal delay · cloud stores & offloads, but latency + storage/analysis/mining are hard"], "color": "c3", "at": 4},
     {"c": ["Mining & integration", "Patterns, anomalies · pattern-based, symbolic abstraction · unify data, semantic interoperability"], "color": "c6", "at": 5},
     {"c": ["Load balancing", "Prevents overload, optimizes communication & storage"], "color": "c4", "at": 6}]},
   ["Let's recap. CPCC is an environment to rapidly build, modify and provision CPS using the cloud, with everything as a service.",
    "The physical world is monitored by the cyber world, and the cyber world controls the physical world.",
    "Opportunities: healthcare, disaster systems, smart cities and social networks, with scalability, data management and real time processing.",
    "Challenges: complex integration, real time safety and reliability, data security, and load balancing.",
    "Real time means minimal delay. Big data needs storage and offloading.",
    "Data mining finds patterns and anomalies, and data integration makes mixed data speak one language.",
    "And load balancing prevents overload. You're ready. Good luck!"],
   endcard=True, hold=3)

L = {"title": "Cyber-Physical Cloud Computing (CPCC) Explained Simply — Module 7",
     "slug": "iot-cpcc", "description": "CPCC explained simply: definition, cyber and physical worlds, opportunities, challenges, real-time processing, big data, data mining, data integration and load balancing.",
     "tags": ["CPCC", "cyber-physical systems", "cloud computing", "exam revision"], "voice": "am_michael", "speed": 1.0, "fps": 24, "captions": True,
     "endCard": "📘 Opportunities vs challenges — know both lists", "thumbnail": "intro@4", "pronounce": P, "scenes": S}
json.dump(L, open('/home/user/JarvisAI/visuals/iot-cpcc/lesson.json', 'w'), indent=1, ensure_ascii=False)
