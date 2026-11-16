import json
P = {"IoT":"I o T","3GPP":"three G P P","LPWAN":"L P WAN","LPWA":"L P W A","NB-IoT":"N B I o T","LTE-M":"L T E M","EC-GSM":"E C G S M","LTE":"L T E","RPMA":"R P M A","M2M":"M 2 M","GHz":"gigahertz","MHz":"megahertz","kHz":"kilohertz","KHz":"kilohertz","Hz":"hertz",
"kbps":"kilobits per second","Kbps":"kilobits per second","bps":"bits per second","dBm":"d B m","dB":"d B","CSS":"C S S","SF":"S F","SF7":"S F seven","SF8":"S F eight","SF9":"S F nine","SF10":"S F ten","SF11":"S F eleven","SF12":"S F twelve","ADR":"A D R","GW":"gateway","GTW":"gateway","CDMA":"C D M A","3G":"three G","5G":"five G",
"TCP/IP":"T C P I P","SSL":"S S L","AES":"A E S","RSSI":"R S S I","SNR":"S N R","BW":"bandwidth","DL":"downlink","UL":"uplink","RX1":"R X one","RX2":"R X two","DevAddr":"Dev Address","AppEUI":"App E U I","EUI64":"E U I sixty four","NwkSKey":"Network session key","AppSKey":"App session key","MIC":"M I C","IEEE":"I triple E","MAC":"mac","ISM":"I S M","Cat":"category","LoS":"line of sight"}
S = []
def sc(id, chapter, kicker, title, viz, lines, tip=None, **kw):
    d = {"id": id, "chapter": chapter, "kicker": kicker, "title": title, "viz": viz, "lines": lines}
    if tip: d["tip"] = {"t": tip[0], "at": tip[1]}
    d.update(kw); S.append(d)
def cards(items, cols=None, **kw):
    v = {"type": "cards", "items": [dict(zip(["icon","h","b","c","at"], it)) for it in items]}
    if cols: v["cols"] = cols
    v.update(kw); return v

sc("intro", "Intro", "IoT long range technologies", None,
   {"type": "hero", "icon": "📡", "big": "LoRaWAN", "y": 160, "sub": "Long Range Wide Area Network — every slide, explained simply", "subY": 300,
    "chips": [{"t": t, "c": c, "at": 2 + i*0.15} for i,(t,c) in enumerate([("Long-range landscape","c1"),("LPWAN needs","c2"),("LoRa vs LoRaWAN","c5"),("Architecture","c3"),("Spread spectrum","c6"),("Spreading factor & ADR","c4"),("Classes A · B · C","c7"),("Device identity & keys","c9")])]},
   ["How can a soil sensor in a field send data fifteen kilometres away, on a battery that lasts years?",
    "The answer is LoRaWAN, one of the most important long range IoT technologies.",
    "We'll cover the long range landscape, LPWAN requirements, LoRa versus LoRaWAN, the architecture, spread spectrum, spreading factor, device classes, and device identity.",
    "Let's start."], pad=[0.6, 1.0])

sc("landscape", "Long-range technology landscape", "Slides 2–3 & 5 · Summary", "Where LoRaWAN fits",
   cards([("📶","Fixed & short range","Wi-Fi, Bluetooth, ZigBee… covered in other chapters.","c8",1),
          ("🆓","Non-3GPP standards (LPWAN)","**1. LoRa / LoRaWAN · 2. Sigfox · 3. Weightless · 4. Others** (e.g. **RPMA**). Usually **unlicensed** spectrum.","c3",2),
          ("📱","3GPP standards (cellular)","**1. LTE-M · 2. EC-GSM · 3. NB-IoT · 4. 5G**. Run on **licensed** mobile spectrum.","c1",4)], cols=3),
   ["The deck begins with a summary of IoT connectivity.",
    "First, fixed and short range technologies. Then long range technologies, which split into two families.",
    "Family one: non 3GPP standards, also called LPWAN. These are LoRa or LoRaWAN, Sigfox, Weightless, and others like RPMA.",
    "They are not made by the mobile phone standards body, and typically use unlicensed spectrum.",
    "Family two: 3GPP standards, made by the mobile standards body. These are LTE-M, EC-GSM, NB-IoT, and 5G.",
    "LoRaWAN is in the first family: a non 3GPP, low power wide area network."],
   tip=("Non-3GPP: **LoRa, Sigfox, Weightless, RPMA** · 3GPP: **LTE-M, EC-GSM, NB-IoT, 5G**", 2))

sc("m2mtable", "Wide-area M2M comparison", "Slide 4 · Wide-area M2M technologies (Dhillon et al., IEEE Comm. Mag.)", "Wide-area M2M technologies compared",
   {"type": "table", "fs": 24, "cols": ["Spectrum", "Technology", "Bandwidth", "Data rate", "Link budget / range"], "widths": ["16%","24%","14%","24%","22%"], "rows": [
     {"c": ["Licensed", "LTE Cat. 0", "20 MHz", "DL 1 Mb/s · UL 1 Mb/s", "140 dB"], "color": "c1", "at": 1},
     {"c": ["Licensed", "LTE Cat. M", "1.4 MHz", "DL 1 Mb/s · UL 1 Mb/s", "155 dB"], "color": "c1", "at": 1.5},
     {"c": ["Licensed", "NB-IoT", "200 kHz", "DL 128 kb/s · UL 64 kb/s", "164 dB"], "color": "c1", "at": 2},
     {"c": ["Licensed", "EC-GSM", "200 kHz", "DL 74 kb/s · UL 74 kb/s", "164 dB"], "color": "c1", "at": 2.5},
     {"c": ["2.4 GHz", "Ingenu RPMA", "1 MHz", "UL 624 kb/s · DL 156 kb/s", "500 km line of sight"], "color": "c5", "at": 3},
     {"c": ["Sub-1 GHz", "LoRa chirp spread spectrum", "125 kHz", "UL 100 kb/s · DL 100 kb/s", "15 km rural · 5 km urban"], "color": "c3", "at": 4},
     {"c": ["Sub-1 GHz", "Weightless-N", "200 Hz", "UL 100 b/s", "3 km urban"], "color": "c5", "at": 5},
     {"c": ["Sub-1 GHz", "Sigfox", "160 Hz", "UL 100 b/s", "50 km rural · 10 km urban"], "color": "c5", "at": 5.5}]},
   ["This table, from Dhillon and others in IEEE Communications Magazine, compares wide area M2M technologies.",
    "Licensed cellular: LTE category 0 uses 20 megahertz, and LTE category M uses 1.4 megahertz. Both give about 1 megabit per second.",
    "NB-IoT and EC-GSM use just 200 kilohertz, with a link budget of 164 d B. Link budget is how much signal loss a link can survive. Higher means longer reach.",
    "Unlicensed: Ingenu RPMA at 2.4 gigahertz, with 1 megahertz bandwidth, reaching 500 kilometres line of sight.",
    "LoRa, chirp spread spectrum, in sub 1 gigahertz, with a 125 kilohertz channel. Range: 15 kilometres rural, 5 kilometres urban.",
    "And the ultra narrowband ones, Weightless-N at 200 hertz, and Sigfox at 160 hertz, both sending about 100 bits per second. Sigfox reaches 50 kilometres rural."],
   tip=("LoRa: **125 kHz**, **15 km rural / 5 km urban**. Sigfox: **160 Hz, 100 b/s**.", 4))

sc("lpwanreq", "LPWAN requirements", "Slide 6 · LPWAN requirements", "Five requirements of every LPWAN",
   cards([("🔋","Long battery life","Devices run for **years** on one battery.","c5",1),
          ("💲","Low device cost","Cheap radios → deploy thousands.","c3",2),
          ("🛠️","Low cost & easy deployment","Few gateways, simple setup.","c1",3),
          ("📡","Extended coverage","**10–15 km in rural areas**, **2–5 km in urban areas**.","c6",4),
          ("🌐","Massive number of devices","One network supports **huge numbers** of devices.","c2",5)], cols=3),
   ["Every LPWAN must meet five requirements.",
    "One: long battery life.",
    "Two: low device cost.",
    "Three: low cost and easy deployment of the network.",
    "Four: extended coverage. 10 to 15 kilometres in rural areas, and 2 to 5 kilometres in urban areas.",
    "Five: support for a massive number of devices."],
   tip=("Coverage: **10–15 km rural**, **2–5 km urban**.", 4))

sc("lvl", "LoRa vs LoRaWAN", "Slides 7–8 · LoRaWAN", "LoRa vs LoRaWAN — not the same thing!",
   {"type": "stack", "w": 760, "layers": [
     {"l": "Application", "c": "c8", "at": 4},
     {"l": "LoRaWAN — network layer / MAC (protocol)", "c": "c3", "at": 2},
     {"l": "LoRa — physical / link layer (radio modulation)", "c": "c1", "at": 0}],
    "brackets": [{"from": 2, "to": 2, "l": "**LoRa**: only the link layer · modules a little **cheaper**", "c": "c1", "at": 0},
                 {"from": 1, "to": 1, "l": "**LoRaWAN**: adds the **network layer** → send to **any base station** connected to a **cloud** platform", "c": "c3", "at": 2}]},
   ["Now section one, LoRaWAN. First, an important difference: LoRa is not the same as LoRaWAN.",
    "LoRa contains only the link layer protocol. It is the radio technique itself. LoRa modules are a little cheaper than LoRaWAN ones.",
    "LoRaWAN includes the network layer too.",
    "So it is possible to send information to any base station that is already connected to a cloud platform.",
    "Simple analogy: LoRa is the voice. LoRaWAN is the language and the phone network that carries it to the right place."],
   tip=("LoRa = **radio (link layer)**. LoRaWAN = **network protocol on top**.", 1))

sc("loraov", "LoRa technology overview", "Slide 9 · LoRa technology overview", "LoRa technology overview",
   cards([("🌍","Low Power Wide Area Network","LoRaWAN is an **LPWAN**.","c1",0),
          ("〰️","Chirp Spread Spectrum (CSS)","LoRa modulation is a version of **CSS**, typical channel **bandwidth 125 kHz**.","c3",1),
          ("👂","High sensitivity","End nodes: up to **−137 dBm** · Gateways: up to **−142 dBm**.","c5",3),
          ("📏","Long range","Up to **15 km**.","c6",5),
          ("🏢","Strong indoor penetration","With **high spreading factor**, up to **20 dB** extra penetration (**deep indoor**).","c2",6),
          ("🛡️","Robust","Uses the **entire channel bandwidth** → robust to noise. **Resistant to Doppler, multipath and signal weakening**.","c4",7)], cols=3),
   ["Here's the LoRa technology overview. LoRaWAN is a low power wide area network.",
    "LoRa modulation is a version of chirp spread spectrum, or CSS, with a typical channel bandwidth of 125 kilohertz.",
    "A chirp is a signal whose frequency sweeps up or down, like a bird's chirp.",
    "It has very high sensitivity: end nodes can hear signals down to minus 137 dBm, and gateways down to minus 142 dBm.",
    "dBm measures signal power. The more negative the number a receiver can still hear, the weaker the signals it can catch, so the longer the range.",
    "It supports long range communication, up to 15 kilometres.",
    "It has strong indoor penetration. With a high spreading factor, up to 20 d B more, for deep indoor devices.",
    "It occupies the entire bandwidth of the channel, making it robust to channel noise. And it resists the Doppler effect, multipath, and signal weakening."],
   tip=("Sensitivity: **−137 dBm** node, **−142 dBm** gateway · **125 kHz** · **15 km**", 3))

sc("arch", "LoRaWAN architecture", "Slide 10 · Architecture", "LoRaWAN architecture",
   {"type": "flow", "nodeY": 0, "listY": 250, "listW": 980, "nodeW": 260,
    "nodes": [{"icon": "🌡️", "l": "End devices", "s": "sensors", "c": "c5", "at": 1}, {"icon": "🗼", "l": "LoRa gateways", "c": "c3", "at": 2},
              {"icon": "🖥️", "l": "Network server", "s": "in the cloud", "c": "c1", "at": 3}, {"icon": "📊", "l": "Application server", "c": "c2", "at": 4},
              {"icon": "📧", "l": "Email · IT · monitoring", "c": "c4", "at": 5}],
    "steps": [{"t": "End device sends over **LoRa RF** — heard by **one or more gateways**", "at": 1, "from": 0, "to": 1, "c": "c5"},
              {"t": "Gateways forward over **TCP/IP SSL** (secure internet) to the **network server**", "at": 2, "from": 1, "to": 2, "c": "c3"},
              {"t": "Network server passes data to the **application server**", "at": 4, "from": 2, "to": 3, "c": "c1"},
              {"t": "Apps deliver to **email, customer IT, remote monitoring**", "at": 5, "from": 3, "to": 4, "c": "c2"}]},
   ["Here is the LoRaWAN architecture. On the left are end devices, the sensors.",
    "They send data using LoRa radio to LoRa gateways. One message can be heard by several gateways at once. No pairing needed.",
    "The gateways forward the data over TCP/IP with SSL, which is a secure internet connection, to the network server in the cloud.",
    "This is a star of stars: devices form stars around gateways, and gateways form a star around the network server.",
    "The network server passes the data to the application server.",
    "Which finally delivers it to users: email alerts, customer IT systems, or remote monitoring dashboards."],
   extra=[{"x": 1020, "y": 250, "w": 700, "h": 390, "viz": {"type": "table", "fs": 26, "rows": [
       {"c": ["Modulation", "LoRa RF (spread spectrum)"], "at": 6}, {"c": ["Range", "~ 15 km"], "at": 6.3}, {"c": ["Throughput", "0.3 to 27 kbps"], "at": 6.6},
       {"c": ["Type of traffic", "Data packet"], "at": 6.9}, {"c": ["Payload", "~ 243 bytes"], "at": 7.2}, {"c": ["Security", "AES encryption"], "at": 7.5}]}}],
   tip=("Key specs: **~15 km**, **0.3–27 kbps**, payload **~243 bytes**, **AES** security.", 6))
S[-1]["lines"] += ["Key specs from the slide: LoRa RF spread spectrum modulation, a range of about 15 kilometres, and throughput of 0.3 to 27 kilobits per second.",
                   "Traffic type is data packets, payload is about 243 bytes, and security is AES encryption."]

sc("spread", "Spread spectrum basics", "Slide 11 · Spread spectrum basics", "Spread spectrum & the correlator",
   {"type": "frame", "rows": [
     {"l": "Information symbol (1 bit)", "c": "c3", "y": 40, "h": 80, "at": 1, "f": [{"l": "1", "c": "c3"}]},
     {"l": "Spreading code (chips)", "c": "c1", "y": 190, "h": 80, "at": 2, "f": [{"l": x, "c": "c1"} for x in "0 0 1 1 0 0 1 1".split()]},
     {"l": "Spread information (sent on air)", "c": "c5", "y": 340, "h": 80, "at": 3, "f": [{"l": x, "c": "c5"} for x in "1 1 0 0 1 1 0 0".split()]}],
    "notes": [{"t": "🎯 **Correlator** at the receiver: multiply by the **same code** and **integrate** → the **own signal** adds up into a big clear peak; **other signals** (different code) average out to near zero.", "y": 470, "at": 5, "fs": 27}]},
   ["Now spread spectrum basics. LoRa is a spread spectrum technique.",
    "Instead of sending one bit as one short signal, the transmitter takes the information symbol, say a 1.",
    "And combines it with a fast spreading code made of many small pieces called chips.",
    "The result is the spread information. One bit becomes many chips, spread over a wider bandwidth.",
    "At the receiver, a correlator detects its own signal.",
    "It multiplies the received signal by the same code, and integrates, meaning adds up over time. Its own signal builds into a strong peak.",
    "A signal from another device, with a different code, does not line up, so it averages out to almost nothing.",
    "This is why spread spectrum works even below the noise level."],
   tip=("Correlator: **own signal → peak**, other signals → **noise**.", 4))

sc("sfcontrol", "Who controls SF and frequency?", "Slide 12 · SF & frequency control", "Who chooses SF and frequency?",
   {"type": "flow", "nodeY": 0, "listY": 260, "nodeW": 320,
    "nodes": [{"icon": "🌡️", "l": "End device", "s": "picks initial SF & frequency", "c": "c5", "at": 0}, {"icon": "🗼", "l": "Gateway", "s": "listens passively", "c": "c3", "at": 3}, {"icon": "🖥️", "l": "Network server", "s": "optimises SF via ADR", "c": "c1", "at": 1}],
    "steps": [{"t": "**Spreading Factor (SF)** is chosen **initially by the device**, but the **network server** can adjust it dynamically using **ADR** (Adaptive Data Rate).", "at": 0, "from": 2, "to": 0, "d": 2, "c": "c1"},
              {"t": "**Frequency** is chosen by the **device**, following the network's **frequency plan**. Devices can use **frequency hopping** over different channels.", "at": 2, "hl": 0, "c": "c5"},
              {"t": "The **gateway does not allocate** SF or frequency. It **listens passively** on many frequencies and SFs, and **relays** data to and from the network server.", "at": 3, "hl": 1, "c": "c3"},
              {"t": "**Summary:** network server optimises **SF via ADR**; devices follow **frequency plans**.", "at": 5, "c": "c2"}]},
   ["Who decides the spreading factor and the frequency? First, the spreading factor, SF, is chosen initially by the device.",
    "But the network server can adjust it dynamically using the ADR mechanism, adaptive data rate, to optimize communication.",
    "The frequency is determined by the device, based on the network's frequency plan. Devices can use frequency hopping to transmit on different channels.",
    "The gateway does not actively allocate SF or frequency.",
    "Instead it listens passively to multiple frequencies and spreading factors at the same time, and relays data to and from the network server.",
    "In summary: the gateway doesn't control SF or frequency. The network server optimizes SF via ADR, and devices follow frequency plans."],
   tip=("Gateway = **passive relay**. **Network server** sets SF via **ADR**.", 3))

sc("spectrum", "Spreading factor & orthogonality", "Slide 13 · Spectrum", "Spreading factor: gain vs data rate",
   cards([("🔀","Orthogonal sequences","**2 messages** from **2 devices** arriving **at the same time** at a gateway → **no interference** (like **CDMA**, also used in **3G**).","c2",0),
          ("🛡️","Spread spectrum = robust","**The more it is spread, the more robust** → less sensitive to **interference** and **selective frequency fading**.","c5",2),
          ("🐢","SF 12","**High gain, low data rate** → **far devices & deep indoor**.","c7",4),
          ("⚖️","SF 9","**Average gain, average data rate**.","c3",5),
          ("🚀","SF 7","**Low gain, high data rate** → close devices.","c1",6),
          ("🆓","Unlicensed spectrum","**915 MHz ISM** band in the **US**, **868 MHz** in **Europe**.","c6",7)], cols=3),
   ["Now the spectrum. Different spreading factors create orthogonal sequences.",
    "So two messages, from two different devices, arriving at the gateway at the same time, do not interfere. This is the code division multiple access idea, CDMA, also used in 3G.",
    "Spread spectrum makes the signal more robust. The more the signal is spread, the more robust it is.",
    "It becomes less sensitive to interference and to selective frequency fading, where only some frequencies get weakened.",
    "The spreading factor controls how much spreading happens. SF 12 gives high gain but low data rate. It's for far devices and deep indoor.",
    "SF 9 gives average gain and average data rate.",
    "SF 7 gives low gain but high data rate, for close devices.",
    "The spectrum used is unlicensed: the 915 megahertz ISM band in the US, and 868 megahertz in Europe."],
   tip=("**High SF** = far, slow, robust · **Low SF** = near, fast", 4))

sc("adr", "Influence of SF & ADR", "Slide 14 · Influence of the spreading factor", "Adaptive Data Rate (ADR): far vs close",
   {"type": "bars", "top": 0, "labelW": 200, "max": 1.5,
    "items": [{"l": "SF12", "v": 1.4, "txt": "1.4 s on air · 290 bps", "c": "c7", "at": 1}, {"l": "SF11", "v": 0.74, "txt": "0.74 s · 530 bps", "c": "c6", "at": 1.3},
              {"l": "SF10", "v": 0.37, "txt": "0.37 s · 970 bps", "c": "c3", "at": 1.6}, {"l": "SF9", "v": 0.2, "txt": "0.2 s · higher bit rate", "c": "c5", "at": 1.9}],
    "notes": [{"t": "Bars = **time on air** for a **10-byte payload** (slide's 2D simulation; ranges shown ≈ 14 km → 4 km). Longer on air = **more energy used**.", "y": 400, "at": 2, "fs": 25},
              {"t": "📍 **Far, with obstacles** → high sensitivity needed → network **increases SF** → throughput ↓ but **connection maintained**.", "y": 470, "at": 3, "fs": 26, "c": "c7"},
              {"t": "🏠 **Close** → low sensitivity is enough → network **decreases SF** → **throughput ↑**, less energy.", "y": 540, "at": 5, "fs": 26, "c": "c5"}]},
   ["How does the spreading factor affect a real device? The slide shows a seesaw: spreading factor on one side, data rate and sensitivity on the other.",
    "For a 10 byte payload, SF 12 takes 1.4 seconds on air, at about 290 bits per second. SF 11 takes 0.74 seconds, SF 10 takes 0.37 seconds, and SF 9 about 0.2 seconds.",
    "Longer time on air means more energy used.",
    "Case one: a device that is far away, with obstacles. It needs high sensitivity, so the network increases the SF.",
    "Throughput decreases, but the connection is maintained.",
    "Case two: a device that is close. Low sensitivity is sufficient, so the network decreases the SF, and throughput increases.",
    "This automatic tuning is called adaptive throughput, or ADR, adaptive data rate."],
   tip=("**ADR**: far → **raise SF**; close → **lower SF**.", 3))

sc("sftable", "SF, bit rate, sensitivity, SNR", "Slide 16 · SF table (125 kHz channel)", "SF table: bit rate, sensitivity, SNR",
   {"type": "table", "fs": 28, "cols": ["Spreading factor (chips)", "Bit rate", "Sensitivity", "Demodulator SNR"], "rows": [
     {"c": ["SF 7 (128)", "5 469 bit/s", "−124 dBm", "−7.5 dB"], "color": "c1", "at": 1},
     {"c": ["SF 8 (256)", "3 125 bit/s", "−127 dBm", "−10 dB"], "color": "c9", "at": 2},
     {"c": ["SF 9 (512)", "1 758 bit/s", "−130 dBm", "−12.5 dB"], "color": "c5", "at": 2.4},
     {"c": ["SF 10 (1024)", "977 bit/s", "−133 dBm", "−15 dB"], "color": "c3", "at": 2.8},
     {"c": ["SF 11 (2048)", "537 bit/s", "−135 dBm", "−17.5 dB"], "color": "c6", "at": 3.2},
     {"c": ["SF 12 (4096)", "293 bit/s", "−137 dBm", "−20 dB"], "color": "c7", "at": 4}]},
   ["This table gives exact numbers for a 125 kilohertz channel. The number in brackets is chips per symbol, which is 2 to the power SF.",
    "SF 7: 128 chips, 5469 bits per second, sensitivity minus 124 dBm, and signal to noise ratio minus 7.5 d B.",
    "Each step up halves roughly the bit rate: SF 8 at 3125, SF 9 at 1758, SF 10 at 977, SF 11 at 537 bits per second.",
    "Meanwhile sensitivity improves by about 2 to 3 dBm per step, and the required SNR drops by 2.5 d B per step.",
    "At SF 12: 4096 chips, only 293 bits per second, but sensitivity of minus 137 dBm, and it works even at minus 20 d B SNR, below the noise.",
    "SF and repetitions can be set manually by the end device, or automatically, managed by the network."],
   tip=("SF↑ → bit rate ↓ (halves), sensitivity better (−124 → −137 dBm)", 3))

sc("rssi", "Sensitivity vs bandwidth", "Slide 15 · RSSI and SF versus BW", "Sensitivity (dBm) vs SF and bandwidth",
   {"type": "table", "fs": 30, "cols": ["BW \\ SF", "7", "8", "9", "10", "11", "12"], "rows": [
     {"c": ["125 kHz", "−123", "−126", "−129", "−132", "−133", "−136"], "color": "c5", "at": 1},
     {"c": ["250 kHz", "−120", "−123", "−125", "−128", "−130", "−133"], "color": "c3", "at": 2},
     {"c": ["500 kHz", "−116", "−119", "−122", "−125", "−128", "−130"], "color": "c7", "at": 3}]},
   ["This table shows receiver sensitivity, in dBm, for each spreading factor and bandwidth. RSSI means received signal strength indicator.",
    "At 125 kilohertz, sensitivity goes from minus 123 at SF 7 down to minus 136 at SF 12.",
    "At 250 kilohertz, it goes from minus 120 to minus 133.",
    "At 500 kilohertz, from minus 116 to minus 130.",
    "Two patterns to remember: higher SF means better sensitivity. And wider bandwidth means worse sensitivity, but faster data."],
   tip=("**Higher SF → better** sensitivity · **wider BW → worse** sensitivity", 4))

sc("classes", "Device classes A, B, C", "Slide 17 · LoRaWAN device classes", "Three device classes: A, B and C",
   {"type": "table", "fs": 25, "cols": ["Class", "How it listens", "Intended use", "Consumption", "Examples"], "widths": ["13%","22%","24%","22%","19%"], "rows": [
     {"c": ["A (\"all\")", "Listens **only after** it transmits", "No latency constraint", "**Most economic**; supported by **all** modules; battery", "Fire detection, earthquake early detection"], "color": "c5", "at": 1},
     {"c": ["B (\"beacon\")", "Listens at a **regular, adjustable** interval", "Downlink latency of **a few seconds**", "**Optimised**; battery", "Smart metering, temperature rise"], "color": "c3", "at": 3},
     {"c": ["C (\"continuous\")", "**Always** listening", "Strong latency need: **< 1 second**", "Needs **mains power** (grid)", "Fleet management, real-time traffic"], "color": "c7", "at": 5}]},
   ["LoRaWAN defines three device classes. Any LoRa object can transmit and receive data. The classes differ in when the device listens.",
    "Class A, for all. It listens only after it transmits. It suits devices with no latency constraint.",
    "It is the most energy economical class, supported by all modules, and suited to battery power. Examples: fire detection, earthquake early detection.",
    "Class B, for beacon. The module listens at a regular, adjustable frequency. It suits devices that need downlink messages within a few seconds.",
    "Its consumption is optimized and suits batteries. Examples: smart metering, and temperature rise alerts.",
    "Class C, for continuous. The module is always listening. It suits devices with a strong latency requirement, less than one second.",
    "It needs mains power from the grid, or no power constraint. Examples: fleet management, and real time traffic management."],
   tip=("A = **All** (listen after send) · B = **Beacon** (scheduled) · C = **Continuous**", 1))

sc("classA", "Class A in detail", "Slide 18 · Class A", "Class A: two receive windows",
   {"type": "timeline", "x": 230, "laneH": 120, "y": 20, "lanes": ["End device", ""],
    "blocks": [{"x0": 0, "x1": 22, "l": "📤 TX: one packet sent", "c": "c1", "solid": True, "at": 1},
               {"x0": 22, "x1": 45, "l": "wait 1 s ± 20 µs", "c": "c8", "at": 2},
               {"x0": 45, "x1": 55, "l": "RX1", "c": "c5", "solid": True, "at": 2.5, "hl": 2.5, "hlEnd": 3},
               {"x0": 55, "x1": 78, "l": "wait 1 s ± 20 µs", "c": "c8", "at": 3},
               {"x0": 78, "x1": 88, "l": "RX2", "c": "c5", "solid": True, "at": 3.5, "hl": 3.5, "hlEnd": 4},
               {"x0": 88, "x1": 100, "l": "😴 sleep", "c": "c2", "at": 4}],
    "notes": [{"t": "**Listening period** depends on SF: **5.1 ms at SF7** (outdoor, close) · **10.2 ms at SF8** · … · **164 ms at SF12** (deep indoor, far)", "y": 190, "at": 5, "fs": 28},
              {"t": "Downlink in RX1/RX2: **acknowledgments, MAC commands, application commands**", "y": 290, "at": 4.5, "fs": 28},
              {"t": "✅ **Very economic energetically** · ✅ **Communication triggered by the end device**", "y": 380, "at": 7, "fs": 30, "c": "c5"}]},
   ["Class A in detail. The end device sends one packet. This is the uplink.",
    "Then it waits 1 second, plus or minus 20 microseconds,",
    "and opens the first receive window, RX1.",
    "It waits another second, and opens the second receive window, RX2.",
    "Then it goes back to sleep. Only in these two windows can the gateway send downlink: acknowledgments, MAC commands, or application commands.",
    "Each listening period depends on the spreading factor: 5.1 milliseconds at SF 7, for outdoor close devices, 10.2 milliseconds at SF 8.",
    "And up to 164 milliseconds at SF 12, for deep indoor or far devices.",
    "Class A is very economic energetically, because communication is always triggered by the end device. The server must wait until the device speaks first."],
   tip=("Uplink → **1 s → RX1** → **1 s → RX2** → sleep", 2))

sc("classB", "Class B in detail", "Slide 19 · Class B (synchronized mode)", "Class B: scheduled listening windows",
   {"type": "timeline", "x": 230, "laneH": 120, "y": 20, "lanes": ["Gateway beacons", "End device"],
    "blocks": [{"lane": 0, "x0": 0, "x1": 6, "l": "📣", "c": "c3", "solid": True, "at": 1}, {"lane": 0, "x0": 94, "x1": 100, "l": "📣", "c": "c3", "solid": True, "at": 1},
               {"lane": 1, "x0": 14, "x1": 20, "l": "Rx1", "c": "c5", "solid": True, "at": 3}, {"lane": 1, "x0": 34, "x1": 40, "l": "Rx2", "c": "c5", "solid": True, "at": 3.3},
               {"lane": 1, "x0": 54, "x1": 60, "l": "Rx3", "c": "c5", "solid": True, "at": 3.6}, {"lane": 1, "x0": 76, "x1": 82, "l": "RxN", "c": "c5", "solid": True, "at": 3.9}],
    "spans": [{"x0": 0, "x1": 6, "l": "beginning tag", "y": 290, "c": "c3", "at": 1}, {"x0": 92, "x1": 100, "l": "end tag", "y": 290, "c": "c3", "at": 1}, {"x0": 10, "x1": 86, "l": "N reception windows between the two tags · each lasts a time that depends on SF", "y": 290, "c": "c5", "at": 3}],
    "notes": [{"t": "✅ **Optimized energy consumption** · ✅ **Communication can be initiated by the gateway** (no need to wait for an uplink)", "y": 410, "at": 5, "fs": 30, "c": "c3"}]},
   ["Class B is the synchronized mode. The gateway sends regular beacons, and the device synchronizes its clock to them.",
    "The two beacons act as a beginning tag and an end tag.",
    "Between them, the device opens N reception windows at regular intervals: Rx 1, Rx 2, Rx 3, up to Rx N.",
    "Each listening duration depends on the spreading factor.",
    "So the server knows exactly when the device is listening, and can send downlink without waiting for an uplink.",
    "Result: optimized energy consumption, and communication can be initiated by the gateway."],
   tip=("Class B = **synced to beacons**, **N scheduled windows**, gateway can start talking.", 2))

sc("classC", "Class C in detail", "Slide 20 · Class C", "Class C: always listening",
   {"type": "timeline", "x": 230, "laneH": 120, "y": 20, "lanes": ["End device"],
    "blocks": [{"x0": 0, "x1": 45, "l": "👂 Reception window open — packet reception possible", "c": "c5", "at": 1, "fs": 24},
               {"x0": 45, "x1": 58, "l": "📤 TX (RX closed)", "c": "c1", "solid": True, "at": 2, "hl": 2, "hlEnd": 3},
               {"x0": 58, "x1": 100, "l": "👂 Reception window open again", "c": "c5", "at": 3, "fs": 24}],
    "notes": [{"t": "**Permanent listening** · closes the receive window **only while transmitting** · lowest latency, **highest power** → **adapted to devices on the power grid** (e.g. street lights, fleet systems).", "y": 200, "at": 4, "fs": 30}]},
   ["Class C means permanent listening.",
    "The reception window is always open, so a packet can be received at almost any time.",
    "It closes the receive window only while it is transmitting. Then it opens again immediately.",
    "This gives the lowest latency, but uses the most power. So class C is adapted to devices connected to the power grid."],
   tip=("Class C = **always on**, needs **grid power**.", 1))

sc("ident", "Device identification & keys", "Slide 21 · Identification of an end device", "How a LoRaWAN device is identified",
   {"type": "multi", "parts": [
     {"y": 0, "h": 200, "viz": {"type": "frame", "rows": [{"l": "End-device address (DevAddr) — 32 bits", "c": "c3", "y": 70, "h": 90, "at": 0, "f": [{"l": "Network identifier", "sz": "7 bits", "w": 7, "c": "c1", "at": 1}, {"l": "Network address of the end-device", "sz": "25 bits", "w": 25, "c": "c3", "at": 2}]}]}},
     {"y": 250, "h": 390, "viz": cards([("🏷️","AppEUI — Application identifier","A **global application ID** in the **IEEE EUI64** address space that uniquely **identifies the owner** of the end-device.","c2",3),
                                          ("🛡️","NwkSKey — Network session key","Used by network server & device to **calculate and verify the message integrity code (MIC)** → **data integrity**.","c5",5),
                                          ("🔐","AppSKey — Application session key","Used to **encrypt and decrypt the payload** of data messages → **privacy**.","c4",7)], cols=3)}]},
   ["Finally, how is an end device identified? First, the end device address, DevAddr.",
    "It has two parts: a 7 bit network identifier,",
    "and a 25 bit network address of the end device. 32 bits in total.",
    "Second, AppEUI, the application identifier. It's a global application ID in the IEEE EUI64 address space.",
    "It uniquely identifies the owner of the end device.",
    "Third, NwkSKey, the network session key. The network server and the device use it to calculate and verify the message integrity code of every data message.",
    "That ensures data integrity, meaning nobody changed the message on the way.",
    "Fourth, AppSKey, the application session key. It is used to encrypt and decrypt the payload of data messages.",
    "Memory trick: network key protects integrity, application key protects privacy."],
   tip=("DevAddr = **7-bit NwkID + 25-bit address** · NwkSKey → **integrity** · AppSKey → **encryption**", 5))

sc("state", "Current state of LoRaWAN", "Slide 22 · Current state", "LoRaWAN in the real world",
   {"type": "hero", "icon": "🏙️", "big": "Amsterdam: whole city covered\nwith only **10 gateways**", "size": 70, "y": 120, "sub": "at about **$1200 per gateway** — the first LoRaWAN city", "subY": 300, "subAt": 1, "chipY": 380,
    "chips": [{"t": t, "c": "c1", "at": 3 + i*0.08} for i,t in enumerate(["Boston","São Paulo","Cape Town","Buenos Aires","Kochi","Manchester","Port of Rotterdam","Eindhoven","Zurich","Den Haag","Utrecht","Poznan","Groningen","Ottawa","Montevideo","Perth","Mexico City","Belfast","Austin","Johannesburg"])]},
   ["What about the real world? Amsterdam was the first city covered by LoRaWAN.",
    "It needed only 10 gateways for the whole city, at about 1200 dollars per unit. That shows how far LoRa reaches, and how cheap deployment is.",
    "Since then, several cities have followed the trend.",
    "Boston, São Paulo, Cape Town, Buenos Aires, Kochi in India, Manchester, Rotterdam, Zurich, Ottawa, Perth, Mexico City, Johannesburg, and many more."])

sc("recap", "Recap", "Recap", "LoRaWAN on one page",
   {"type": "table", "fs": 25, "cols": ["Topic", "Remember"], "widths": ["24%", "76%"], "rows": [
     {"c": ["Landscape", "Non-3GPP LPWAN (LoRa, Sigfox, Weightless, RPMA) vs 3GPP (LTE-M, EC-GSM, NB-IoT, 5G)"], "color": "c1", "at": 0},
     {"c": ["LPWAN needs", "Battery life · low device cost · cheap easy deployment · 10–15 km rural, 2–5 km urban · massive devices"], "color": "c2", "at": 1},
     {"c": ["LoRa vs LoRaWAN", "LoRa = link layer radio (CSS, 125 kHz) · LoRaWAN = adds network layer"], "color": "c5", "at": 2},
     {"c": ["Architecture", "Star of stars: devices → gateways → network server → app server · ~15 km · 0.3–27 kbps · 243 B · AES"], "color": "c3", "at": 3},
     {"c": ["SF & ADR", "SF7 fast/near … SF12 slow/far (−137 dBm) · orthogonal SFs (CDMA) · network server sets SF via ADR"], "color": "c6", "at": 4},
     {"c": ["Classes", "A: RX1/RX2 after uplink (most economic) · B: beacon-scheduled windows · C: always listening (grid)"], "color": "c7", "at": 5},
     {"c": ["Identity", "DevAddr 7 + 25 bits · AppEUI (owner) · NwkSKey (integrity/MIC) · AppSKey (payload encryption)"], "color": "c4", "at": 6}]},
   ["Let's recap. LoRaWAN is a non 3GPP LPWAN, unlike LTE-M, EC-GSM, NB-IoT and 5G.",
    "Every LPWAN needs long battery life, low cost, easy deployment, wide coverage, and massive device support.",
    "LoRa is the radio, using chirp spread spectrum at 125 kilohertz. LoRaWAN adds the network layer.",
    "The architecture is a star of stars: devices, gateways, network server, application server.",
    "Spreading factor trades speed for range, and the network server tunes it with ADR.",
    "Class A listens after sending, class B on a beacon schedule, class C all the time.",
    "And each device has a DevAddr, an AppEUI, and two session keys. You've got this. Good luck!"],
   endcard=True, hold=3)

L = {"title": "LoRaWAN Explained Simply — Full Chapter Revision (SF, ADR, Classes A/B/C)",
     "slug": "iot-lorawan", "description": "The LoRaWAN chapter explained simply: long-range landscape, LPWAN requirements, LoRa vs LoRaWAN, architecture, spread spectrum, spreading factor & ADR, sensitivity tables, classes A/B/C and device identity.",
     "tags": ["LoRaWAN", "LoRa", "LPWAN", "IoT", "spreading factor", "exam revision"], "voice": "am_michael", "speed": 1.0, "fps": 24, "captions": True,
     "endCard": "📘 Remember: SF ↑ = range ↑, speed ↓ · A / B / C classes", "thumbnail": "arch@12", "pronounce": P, "scenes": S}
json.dump(L, open('/home/user/JarvisAI/visuals/iot-lorawan/lesson.json', 'w'), indent=1, ensure_ascii=False)
