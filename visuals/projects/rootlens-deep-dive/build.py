#!/usr/bin/env python3
"""RootLens deep dive: a ~40-minute interview-prep walkthrough.

    python3 visuals/projects/rootlens-deep-dive/build.py

Writes index.html and video.json next to this file (see ../deepdive_lib.py).
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from deepdive_lib import (Scene, write, text, center, pill, tag, card, node, row, rows, qa, code, shot,  # noqa: E402
                          table, svg, arrow, mover, bar)

S = []


def add(*a, **k):
    S.append(Scene(*a, **k))


# =========================================================== 00 INTRO
add("title", "Intro: what this video covers", "00 · INTRO", None, None, [
    "This is a complete deep dive into RootLens, an incident response lab I built around one question.",
    "When a service breaks in production, can software do what an on-call engineer does? Notice it, find out why, fix it safely, and prove that it worked.",
    "We will go through every decision, from the tiny shop it watches to the rulebook that decides when a robot is allowed to roll back a release.",
    "For each part: what I used, why I used it, and how an interviewer will ask about it.",
], [
    text(120, 220, 1100, '<span style="font:900 150px/1 Inter;letter-spacing:-.05em">Root<span style="color:var(--amber)">Lens</span></span>', "s0.3"),
    text(124, 390, 1100, '<span style="font:700 44px Inter;color:#d6cdf2">The complete deep dive · interview prep</span>', "s0.8"),
    text(120, 480, 1000, '<span style="font:900 54px/1.15 Inter">Something broke.<br><span style="color:var(--grn)">Why</span>, and is it <span style="color:var(--amber)">safe</span> to fix?</span>', "1"),
    text(120, 670, 1000, '<div style="display:flex;flex-wrap:wrap;gap:12px">' + "".join(
        pill(n, col) for n, col in [("Python", "blu"), ("FastAPI", "grn"), ("Prometheus", "org"), ("Grafana", "amber"),
                                    ("OpenTelemetry", "violet"), ("Jaeger", "cyan"), ("Docker", "blu"), ("SQLite", "pink")]) + "</div>", "2"),
    text(120, 830, 1100, '<span style="font:700 32px Inter;color:var(--amber)">what I used → why I used it → how it\'s asked</span>', "3"),
    card(1260, 260, 540, 560, '<div class="lbl">the loop, every time</div>' + "".join(
        f'<div class="row" data-at="{1 + i * 0.15:.2f}" style="--c:{col};margin-top:14px"><div class="num">{i + 1}</div><div>{w}</div></div>'
        for i, (w, col) in enumerate([("Detect", "var(--red)"), ("Investigate", "var(--amber)"), ("Decide", "var(--violet)"),
                                      ("Act", "var(--blu)"), ("Verify", "var(--grn)")])), "1"),
])

add("roadmap", "Roadmap", "00 · ROADMAP", "ROADMAP", "What we'll cover", [
    "Here's the plan. First the problem, and the five step loop that the whole project is built around.",
    "Then the lab: three small services with bugs I planted on purpose, plus the architecture and the observability stack.",
    "Then the core, one stage at a time: detect, investigate, find what changed, decide, act and verify.",
    "After that, a real incident from start to finish, the dashboard, the tests, and how it runs in the cloud.",
    "And we finish with the honest limits, the interview questions, and a thirty second pitch you can use.",
], [
    rows(120, 260, 820, [("0", 1, "The problem &amp; the 5-step loop", "violet"), ("1", 2, "The lab: a shop with planted bugs", "violet"),
                         ("1.4", 3, "Architecture &amp; observability", "violet"), ("2", 4, "<b>Detect</b>: thresholds, hysteresis", "red"),
                         ("2.3", 5, "<b>Investigate</b>: ranking causes", "amber"), ("2.6", 6, "<b>What changed?</b> releases", "amber")]),
    rows(980, 260, 820, [("2.8", 7, "<b>Decide</b>: the rulebook", "violet"), ("3", 8, "<b>Act &amp; verify</b> safely", "blu"),
                         ("3.3", 9, "A real incident, end to end", "grn"), ("3.6", 10, "Tests, CI &amp; deployment", "cyan"),
                         ("4", 11, "Honest limits", "pink"), ("4.3", 12, "<b>Interview questions</b>", "blu")]),
])

# =========================================================== 01 PROBLEM
add("problem", "The problem: 3 a.m. on call", "01 · PROBLEM", "THE PROBLEM", "Three in the morning, the pager goes off", [
    "Picture an online shop. At three in the morning, orders start failing, and an engineer's phone goes off.",
    "They open a dashboard. Half of all orders are failing. But which service is actually to blame?",
    "They check each dependency, they read logs, and they ask the question that solves most incidents: did anyone deploy something recently?",
    "If someone did, the usual fix is to roll that release back, and then watch the graphs to make sure it really recovered.",
    "That whole routine is slow when a tired human does it, and the time it takes is the time customers are seeing errors.",
    "RootLens automates that routine. Not with magic, but with the same steps an engineer follows, written down as code.",
], [
    card(120, 260, 520, 330, '<div class="lbl">03:00 · illustrative</div><div style="font-size:120px;text-align:center;margin-top:10px">📟</div>'
         '<div style="text-align:center;font:800 32px Inter;color:var(--red)">orders failing</div>', "0"),
    card(700, 260, 520, 330, '<div class="lbl">order failure ratio</div><div style="font:900 130px Inter;color:var(--red);text-align:center;margin-top:20px">'
         '<span data-count="1-1.6" data-to="52">0</span>%</div>', "1"),
    card(1280, 260, 520, 330, '<div class="lbl">the questions</div><div style="font:700 30px/1.6 Inter;margin-top:14px">which service?<br>'
         '<span style="color:var(--amber)">what changed?</span><br>roll back?<br>did it work?</div>', "2"),
    rows(120, 640, 1680, [("3", "↩️", "Usual fix: <b>roll back the recent release</b>, then watch the graphs", "amber"),
                          ("4", "⏱️", "Every minute of diagnosis is a minute of <b>customer-facing errors</b>", "red"),
                          ("5", "🤖", "RootLens: the same routine, <b>written down as code</b>", "grn")]),
])

add("mttr", "Why it matters: MTTR", "01 · PROBLEM", "WHY IT MATTERS", "Time to recover is what customers feel", [
    "Teams measure this with a number called mean time to recovery, or M T T R. It's the time from when something breaks to when it works again.",
    "It splits into stages. Time to notice, time to understand, and time to fix and confirm.",
    "Humans are slow at the first two stages, especially at night. A computer can check a metric every ten seconds without getting tired.",
    "So RootLens attacks all three stages. A detector notices, an investigator explains, and a controller fixes and verifies.",
    "In the real run you'll see later, the whole incident lasted one minute and fifty seconds, from detection to recovery.",
], [
    text(120, 270, 1680, '<div style="display:flex;height:120px;border-radius:20px;overflow:hidden;font:800 30px Inter">'
         '<div data-at="1" style="flex:3;background:rgba(248,113,113,.3);display:flex;align-items:center;justify-content:center">notice</div>'
         '<div data-at="1.4" style="flex:4;background:rgba(242,177,52,.3);display:flex;align-items:center;justify-content:center">understand</div>'
         '<div data-at="1.8" style="flex:3;background:rgba(96,165,250,.3);display:flex;align-items:center;justify-content:center">fix + confirm</div></div>', "0"),
    text(120, 410, 1680, '<div style="display:flex;gap:30px">'
         '<div style="flex:3" data-at="3"><span class="pill" style="--c:var(--red)">🔎 detector</span></div>'
         '<div style="flex:4" data-at="3.3"><span class="pill" style="--c:var(--amber)">🧠 investigator</span></div>'
         '<div style="flex:3" data-at="3.6"><span class="pill" style="--c:var(--blu)">🤖 controller</span></div></div>'),
    card(120, 520, 1680, 300, '<div class="lbl">mean time to recovery · M T T R</div><div style="display:flex;align-items:center;gap:60px;margin-top:20px">'
         '<div style="font:900 130px Inter;color:var(--grn)">1m 50s</div><div style="font:600 30px/1.5 Inter;color:#e6e0f6">'
         'real run: detection → rollback → three healthy checks<br><span class="note">payment-service v2, a planted 50% error bug</span></div></div>', "4"),
])

add("loop", "The five-step loop", "01 · THE LOOP", "THE BIG IDEA", "Detect → Investigate → Decide → Act → Verify", [
    "Here's the idea the whole project is built around. Five steps, in the same order, every time.",
    "Detect: notice that something is wrong, without crying wolf.",
    "Investigate: rank the possible causes, using evidence, and say how confident we are.",
    "Decide: a rulebook chooses whether to act, wait, or hand the problem to a human.",
    "Act: carry out exactly one safe action, like a rollback. And verify: check that it really recovered.",
    "Every step writes to an audit log, including the times it chose not to act. That record matters as much as the fix.",
], [
    svg(arrow("M330,470 L430,470", "amber", "1.5-2") + arrow("M650,470 L750,470", "amber", "2.5-3") + arrow("M970,470 L1070,470", "amber", "3.5-4")
        + arrow("M1290,470 L1390,470", "amber", "4-4.5") + arrow("M1500,580 C1500,720 260,720 220,590", "violet", "5-e5", dash="10 10")),
    node(120, 370, 210, 200, "🔎 Detect", "is it broken?", "red", "1"),
    node(440, 370, 210, 200, "🧠 Investigate", "why?", "amber", "2"),
    node(760, 370, 210, 200, "📘 Decide", "act · wait ·<br>escalate", "violet", "3"),
    node(1080, 370, 210, 200, "🛠️ Act", "one safe<br>action", "blu", "4"),
    node(1400, 370, 210, 200, "✅ Verify", "3 healthy<br>checks", "grn", "4.5"),
    center(760, pill("📜 audit log: every decision, including <b>not</b> acting", "pink"), "5"),
])

# =========================================================== 02 THE LAB
add("lab", "The lab: a tiny shop", "02 · THE LAB", "THE LAB", "Three FastAPI services form a tiny shop", [
    "To test any of this, I needed something to break. So the lab is a tiny shop made of three Python services, built with Fast A P I.",
    "The user service looks up a customer. The payment service charges the order.",
    "And the order service is the front door. For each order, it calls the user service, then the payment service.",
    "That dependency is the whole point. When payment breaks, the customer sees the order fail, even though the order service itself is fine.",
    "So the symptom shows up in one place, and the cause lives somewhere else. That's exactly what makes real incidents hard.",
], [
    svg(arrow("M500,520 L760,380", "blu", "2-2.6", pid="lb1") + arrow("M500,560 L760,700", "blu", "2.4-3", pid="lb2")
        + mover("lb1", "2.2-3", "blu") + mover("lb2", "2.6-3.4", "red")),
    node(150, 430, 340, 220, "🛒 order-service", ":8002 · front door", "amber", "2"),
    node(770, 260, 380, 200, "👤 user-service", ":8001 · who is buying", "grn", "1"),
    node(770, 620, 380, 200, "💳 payment-service", ":8003 · charge", "red", "1.4"),
    card(1230, 300, 570, 460, '<div class="lbl" style="color:var(--amber)">symptom vs cause</div>'
         '<div style="font:700 30px/1.6 Inter;margin-top:18px">symptom: <span style="color:var(--amber)">orders fail</span><br>cause: '
         '<span style="color:var(--red)">payment errors</span></div><div class="note" style="margin-top:24px">the service that hurts is not the service that\'s broken</div>', "3.5"),
])

add("timeouts", "Timeouts and failure kinds", "02 · THE LAB", "HOW ORDER CALLS ITS DEPENDENCIES", "A 3-second timeout, and three ways to fail", [
    "Here's a detail that matters later. The order service calls each dependency with an H T T P client, using a three second timeout.",
    "If the dependency doesn't answer in time, that's a timeout, and the order returns five oh four, gateway timeout.",
    "If it can't even connect, that's unreachable. If it answers with an error, that's an error. Both of those return five oh three.",
    "And crucially, every failure is counted with two labels: which dependency, and what kind of failure.",
    "That one counter is what lets the investigator later tell the difference between a service that is down, broken, or just slow.",
], [
    code(120, 260, 900, '<span class="k">async with</span> httpx.AsyncClient(timeout=<span class="s">3.0</span>) <span class="k">as</span> client:\n'
         '    r = <span class="k">await</span> client.post(payment_url)\n\n'
         '<span class="k">except</span> <span class="t">TimeoutException</span>:\n'
         '    FAILURES.labels(dependency, <span class="s">"timeout"</span>).inc()\n'
         '    <span class="k">return</span> <span class="r">504</span>\n'
         '<span class="k">except</span> <span class="t">HTTPError</span>:\n'
         '    FAILURES.labels(dependency, <span class="s">"unreachable"</span>).inc()\n'
         '    <span class="k">return</span> <span class="r">503</span>', "0", size=26),
    rows(1080, 260, 720, [("1", "⏳", "<b>timeout</b> · no answer in 3 s → 504", "amber"),
                          ("2", "🔌", "<b>unreachable</b> · can't connect → 503", "red"),
                          ("2.5", "💥", "<b>error</b> · answered 5xx → 503", "pink")]),
    card(1080, 640, 720, 200, '<div class="lbl">one counter, two labels</div><div class="kv" style="margin-top:14px">dependency_failures{<b>dependency</b>, <b>kind</b>}</div>', "3"),
])

add("bugs", "Planted bugs and chaos switches", "02 · THE LAB", "BREAKING THINGS ON PURPOSE", "Chaos switches and planted release bugs", [
    "Next, I needed ways to break the shop on demand. Every service has chaos switches: small H T T P endpoints that inject errors or latency.",
    "For example, posting to chaos errors with a rate of zero point five makes the payment service fail half of its requests.",
    "Then there are releases. Every service reads a version from an environment variable, and version two carries a bug I planted on purpose.",
    "User service version two adds four seconds of latency, which is longer than the three second timeout. Payment service version two fails fifty percent of requests.",
    "So I can simulate the two most common real incidents: a slow dependency, and a bad release that starts throwing errors.",
], [
    code(120, 260, 860, '<span class="c"># chaos switches (any service)</span>\n'
         'POST /chaos/errors?rate=<span class="s">0.5</span>\n'
         'POST /chaos/latency?seconds=<span class="s">4</span>\n'
         'POST /chaos/reset\n\n'
         '<span class="c"># planted release bugs</span>\n'
         'BUGS = {<span class="s">"v2"</span>: {<span class="s">"error_rate"</span>: <span class="r">0.5</span>}}', "0", size=26),
    node(1040, 260, 760, 190, "👤 user-service v2", "+4 s latency → beyond the 3 s timeout", "amber", "3"),
    node(1040, 480, 760, 190, "💳 payment-service v2", "fails 50% of requests", "red", "3.5"),
    center(760, pill("🐢 slow dependency", "amber") + "&nbsp;&nbsp;" + pill("💥 bad release", "red"), "4"),
])

add("traffic", "Fake customers and versioned deploys", "02 · THE LAB", "TRAFFIC AND RELEASES", "Fake customers, and a real release record", [
    "A broken service with no traffic looks perfectly healthy, so a small script called traffic dot py plays the customers, about five orders a second.",
    "Releases go through a deploy script. It updates the version in the environment file and recreates only that one container.",
    "It waits until the service reports the new version on its version endpoint.",
    "And then it records the deployment: which service, which version, and which version it replaced.",
    "That last step is easy to skip, and it's the most important one. Without a release record, nothing can ever answer the question, what changed?",
], [
    node(120, 290, 300, 200, "🧑‍🤝‍🧑 traffic.py", "≈5 orders / s", "cyan", "0"),
    rows(500, 270, 1300, [("1", 1, "update <b>.env</b>: PAYMENT_SERVICE_VERSION=v2", "violet"),
                          ("1.5", 2, "recreate <b>only that container</b>", "violet"),
                          ("2", 3, "wait for <b>/version</b> to report v2", "violet"),
                          ("3", 4, "<b>POST /deployments</b>: service · version · previous", "amber")]),
    card(120, 700, 1680, 140, '<div style="font:800 34px Inter;text-align:center;margin-top:18px">no release record → <span style="color:var(--red)">nobody can answer "what changed?"</span></div>', "4"),
])

# =========================================================== 03 ARCHITECTURE
add("arch", "Architecture overview", "03 · ARCHITECTURE", "ARCHITECTURE", "Eight containers, one Docker Compose file", [
    "Here's the whole system. Eight containers, started with one Docker Compose file.",
    "The three shop services expose metrics. Prometheus scrapes them every five seconds, and Grafana draws the graphs.",
    "Each service also sends traces to Jaeger through Open Telemetry, so one slow order can be followed across every service.",
    "Then come the two parts I'd call RootLens itself. The detector, which watches Prometheus, and the controller, which decides and acts.",
    "The order service also hosts the incident A P I, the investigator and the live dashboard, backed by a SQLite file on a Docker volume.",
], [
    node(120, 270, 330, 150, "🛒👤💳 3 services", "FastAPI · /metrics", "amber", "0"),
    node(560, 270, 300, 150, "📈 Prometheus", "scrape every 5 s", "org", "1"),
    node(960, 270, 280, 150, "📊 Grafana", ":3000", "amber", "1.5"),
    node(560, 470, 300, 150, "🧵 Jaeger", "OpenTelemetry traces", "cyan", "2"),
    node(1340, 270, 460, 150, "🔎 detector", "polls Prometheus · opens incidents", "red", "3"),
    node(1340, 470, 460, 150, "🤖 controller", "decide · act · verify", "blu", "3.4"),
    node(120, 670, 740, 170, "🗂️ order-service also hosts", "incidents API · investigator · dashboard", "violet", "4"),
    node(960, 670, 380, 170, "🐘 SQLite", "/data/incidents.db · volume", "pink", "4.4"),
    svg(arrow("M450,345 L550,345", "org", "1-1.4") + arrow("M860,345 L950,345", "amber", "1.5-2") + arrow("M285,420 L550,545", "cyan", "2-2.5")
        + arrow("M860,320 C1100,220 1200,280 1330,330", "red", "3-3.4") + arrow("M1570,620 L1180,670", "blu", "3.6-4")),
])

add("whysplit", "Why detector and controller are separate", "03 · ARCHITECTURE", "DESIGN DECISION", "Why separate processes?", [
    "An interviewer will ask: why is the detector a separate process, and why is the controller separate again?",
    "First, failure isolation. If the thing you're watching crashes, the watcher must keep running. A detector inside the order service would die with it.",
    "Second, least privilege. Only the controller is allowed to change the running system. The detector can only read metrics and write incidents.",
    "Third, the single responsibility principle. Noticing, explaining and acting are different jobs, with different tests and different risks.",
    "It's the same shape as Kubernetes: something observes, and a controller reconciles the real state towards the desired state.",
], [
    rows(120, 260, 1100, [("1", "🧯", "<b>Failure isolation</b> · the watcher survives what it watches", "red"),
                          ("2", "🔐", "<b>Least privilege</b> · only the controller can change things", "amber"),
                          ("3", "🧩", "<b>One job each</b> · notice ≠ explain ≠ act", "violet"),
                          ("4", "☸️", "<b>Controller pattern</b> · observe → reconcile", "cyan")]),
    card(1280, 260, 520, 560, '<div class="lbl">who may do what</div>'
         '<div style="font:700 28px/1.8 Inter;margin-top:16px">🔎 detector<br><span class="note">reads metrics · writes incidents</span><br>'
         '🧠 investigator<br><span class="note">reads evidence · ranks causes</span><br>🤖 controller<br>'
         '<span class="note" style="color:var(--amber)">the only one that acts</span></div>', "2"),
])

add("sqlite", "SQLite as the incident store", "03 · ARCHITECTURE", "THE DATA", "Three tables in SQLite", [
    "All state lives in three SQLite tables.",
    "Incidents: the fingerprint, the status, when it opened and resolved, and the evidence snapshot stored as JSON.",
    "Deployments: every release and every rollback, with the previous version. This is what change correlation reads.",
    "And the audit log: every decision the controller made, what it did, and what happened.",
    "Why SQLite and not Postgres? It's a single node lab, the write rate is tiny, and it needs zero setup. On a real team with many writers I'd move to Postgres, and that's on the roadmap.",
], [
    card(120, 260, 540, 400, '<div class="lbl" style="color:var(--red)">incidents</div><div class="kv" style="margin-top:14px;line-height:1.7">id<br>fingerprint<br>status<br>opened_at · resolved_at<br><b>evidence_json</b></div>', "1"),
    card(690, 260, 540, 400, '<div class="lbl" style="color:var(--amber)">deployments</div><div class="kv" style="margin-top:14px;line-height:1.7">service<br>version<br><b>previous_version</b><br>deployed_at<br>by (human · robot)</div>', "2"),
    card(1260, 260, 540, 400, '<div class="lbl" style="color:var(--pink)">audit_log</div><div class="kv" style="margin-top:14px;line-height:1.7">incident_id<br>decision<br>action · service<br><b>outcome</b><br>logged_at</div>', "3"),
    center(720, pill("single node · tiny write rate · zero setup → SQLite", "grn") + "&nbsp;&nbsp;" + pill("many writers → Postgres", "blu"), "4"),
])

# =========================================================== 04 OBSERVABILITY
add("metrics", "Metrics: counters and histograms", "04 · OBSERVABILITY", "OBSERVABILITY · METRICS", "Counters and histograms", [
    "RootLens can only be as smart as its data, so let's look at the observability stack, starting with metrics.",
    "Each service exposes a metrics endpoint using the Prometheus client library.",
    "A counter only goes up. For example, requests total, labelled with the endpoint and the status code. You never read a counter directly. You ask how fast it is growing.",
    "A histogram counts requests into latency buckets: under a tenth of a second, under half a second, and so on. That lets you compute percentiles later.",
    "One warning interviewers like: keep labels low cardinality. Status code is fine. A user I D as a label would explode the number of time series.",
], [
    code(120, 260, 940, '<span class="c"># GET /metrics</span>\n'
         'rootlens_order_requests_total{\n   endpoint=<span class="s">"/orders"</span>, status=<span class="s">"503"</span>} <span class="k">1342</span>\n\n'
         'rootlens_order_request_duration_seconds_bucket{\n   le=<span class="s">"0.5"</span>} <span class="k">9120</span>\n'
         'rootlens_order_request_duration_seconds_bucket{\n   le=<span class="s">"3.0"</span>} <span class="k">9874</span>', "1", size=25),
    rows(1120, 260, 680, [("2", "📈", "<b>Counter</b> · only goes up · read its <b>rate</b>", "org"),
                          ("3", "🪣", "<b>Histogram</b> · latency buckets → percentiles", "amber"),
                          ("4", "⚠️", "<b>Low cardinality</b> labels · status ✓ · user id ✗", "red")]),
])

add("prometheus", "Prometheus: the pull model", "04 · OBSERVABILITY", "OBSERVABILITY · PROMETHEUS", "Prometheus pulls every 5 seconds", [
    "Prometheus works on a pull model. Every five seconds it visits each service's metrics endpoint and stores the numbers as time series.",
    "Pull has a nice side effect. If a service is down, the scrape fails, and Prometheus records a metric called up, set to zero.",
    "So up equals zero is free evidence that a service is unreachable, and the investigator uses it directly.",
    "The alternative is push, where services send metrics to a collector. Push suits short lived jobs. For long running services, pull is simpler and tells you who is missing.",
], [
    node(760, 430, 400, 200, "📈 Prometheus", "scrape_interval: 5s", "org", "0"),
    node(140, 260, 330, 140, "👤 user", "up = 1", "grn", "0.3"),
    node(140, 470, 330, 140, "🛒 order", "up = 1", "amber", "0.5"),
    node(140, 680, 330, 140, "💳 payment", '<span style="color:var(--red)">up = 0 ✗</span>', "red", "1"),
    svg(arrow("M750,500 L480,330", "org", "0.3-0.8") + arrow("M750,530 L480,540", "org", "0.5-1") + arrow("M750,560 L480,750", "red", "1-1.5", dash="12 10")),
    card(1240, 300, 560, 460, '<div class="lbl">pull vs push</div><div style="font:700 28px/1.6 Inter;margin-top:16px">'
         '<span style="color:var(--org)">pull</span> · long-running services<br><span class="note">a missing target is visible</span><br><br>'
         '<span style="color:var(--blu)">push</span> · short-lived jobs<br><span class="note">e.g. batch jobs via a gateway</span></div>', "3"),
])

add("promql", "PromQL: the failure ratio", "04 · OBSERVABILITY", "THE ONE QUERY THAT MATTERS", "Failure ratio = 5xx rate ÷ all-requests rate", [
    "The detector is driven by one PromQL query. Let's read it.",
    "The top half takes the order requests counter, keeps only status codes starting with five, and asks for its per second rate over the last minute.",
    "The bottom half is the same rate for every order request.",
    "Divide one by the other, and you get the failure ratio: the share of orders that failed in the last minute. Zero is perfect. One means everything fails.",
    "Why a ratio and not a raw count? Because a count grows with traffic. Ten errors a second is a disaster at night and nothing during a sale. A ratio means the same thing at any load.",
], [
    code(120, 260, 1680, '<span class="k">sum</span>(<span class="k">rate</span>(rootlens_order_requests_total{endpoint=<span class="s">"/orders"</span>, status=~<span class="r">"5.."</span>}[<span class="t">1m</span>]))\n'
         '  <span class="h"> ÷ </span>\n'
         '<span class="k">sum</span>(<span class="k">rate</span>(rootlens_order_requests_total{endpoint=<span class="s">"/orders"</span>}[<span class="t">1m</span>]))', "0", size=30),
    text(120, 560, 820, row("<b>numerator</b>: failed orders / second", ic="🔴", color="red"), "1"),
    text(980, 560, 820, row("<b>denominator</b>: all orders / second", ic="⚪", color="mut"), "2"),
    card(120, 690, 820, 160, '<div class="lbl">failure ratio</div><div style="font:900 64px Inter;color:var(--amber)">0.00 → 1.00</div>', "3"),
    card(980, 690, 820, 160, '<div class="lbl">why a ratio?</div><div style="font:700 28px/1.4 Inter;margin-top:8px">a count scales with traffic · <span style="color:var(--grn)">a ratio doesn\'t</span></div>', "4"),
])

add("p95", "p95 latency with histogram_quantile", "04 · OBSERVABILITY", "LATENCY", "The 95th percentile, not the average", [
    "For latency, the detector also records the ninety fifth percentile, using histogram quantile over the latency buckets.",
    "P ninety five means ninety five percent of orders were faster than this number.",
    "Why not the average? Averages hide pain. If most orders take a tenth of a second and one in ten takes four seconds, the average looks fine, but every tenth customer is waiting.",
    "Percentiles show the tail, and the tail is where timeouts live. The investigator compares p ninety five with the three second timeout.",
], [
    code(120, 260, 1680, '<span class="k">histogram_quantile</span>(<span class="s">0.95</span>, <span class="k">sum by</span> (le) (\n   <span class="k">rate</span>(rootlens_order_request_duration_seconds_bucket{endpoint=<span class="s">"/orders"</span>}[<span class="t">1m</span>])))', "0", size=29),
    text(120, 480, 1680, '<div style="display:flex;align-items:flex-end;gap:10px;height:250px">' + "".join(
        f'<div data-at="{2 + i * 0.02:.2f}" style="flex:1;height:{240 if i % 10 == 9 else 30}px;border-radius:6px;background:{"#f87171" if i % 10 == 9 else "#34d399"}"></div>'
        for i in range(40)) + '</div>'),
    text(120, 760, 820, row("average ≈ 0.5 s · <b>looks fine</b>", ic="😌", color="grn"), "2.6"),
    text(980, 760, 820, row("p95 ≈ 4 s · <b>every 10th customer waits</b>", ic="😣", color="red"), "3"),
])

add("tracing", "Tracing with OpenTelemetry and Jaeger", "04 · OBSERVABILITY", "OBSERVABILITY · TRACES", "Follow one order across every service", [
    "Metrics tell you that something is slow. Traces tell you where.",
    "Each service runs with Open Telemetry auto instrumentation, so every incoming request and every outgoing call becomes a span, without changing the business code.",
    "The trace I D travels in an H T T P header from order to user to payment, so Jaeger can stitch the spans into one timeline.",
    "With the user service version two bug, you can open one slow order and see the user call taking four seconds while everything else is quick.",
    "I excluded noisy endpoints like metrics and health from tracing. Otherwise the scrapes every five seconds would drown out the real traffic.",
], [
    text(120, 280, 1680, '<div class="lbl" style="margin-bottom:16px">one trace · illustrative</div>'
         '<div style="position:relative;height:300px;font:700 24px JetBrains Mono">'
         '<div data-at="1" style="position:absolute;left:0;top:0;width:100%;height:62px;border-radius:12px;background:rgba(242,177,52,.3);border:2px solid var(--amber);padding:14px">POST /orders · 4.2 s</div>'
         '<div data-at="3" style="position:absolute;left:3%;top:80px;width:88%;height:62px;border-radius:12px;background:rgba(248,113,113,.3);border:2px solid var(--red);padding:14px">GET user-service /users/7 · 4.0 s ⚠</div>'
         '<div data-at="2" style="position:absolute;left:92%;top:160px;width:7%;height:62px;border-radius:12px;background:rgba(52,211,153,.3);border:2px solid var(--grn)"></div>'
         '<div data-at="2" style="position:absolute;left:60%;top:170px;font:700 22px JetBrains Mono;color:var(--grn)">payment · 0.1 s →</div></div>'),
    text(120, 640, 820, row("<b>traceparent</b> header carries the trace id", ic="🧵", color="cyan"), "2"),
    text(980, 640, 820, row("excluded: <b>/metrics, /health, /version</b>", ic="🔇", color="mut"), "4"),
])

add("grafana", "Grafana and the three signals", "04 · OBSERVABILITY", "OBSERVABILITY", "Metrics, traces, logs: who answers what", [
    "Grafana sits on top of Prometheus with a dashboard for request rates, failure ratios and latency.",
    "It helps to know the three pillars of observability and which question each one answers.",
    "Metrics answer: is something wrong, and how bad is it? They are cheap, so you keep them for a long time and alert on them.",
    "Traces answer: where in the chain is the time going? Logs answer: what exactly happened in this one request?",
    "RootLens uses metrics for detection and diagnosis, and traces for a human to confirm. Centralized logs are the next item on the roadmap.",
], [
    card(120, 270, 540, 420, '<div style="font-size:70px">📈</div><div style="font:900 40px Inter;color:var(--org)">Metrics</div><div class="note" style="margin-top:10px">is something wrong?<br>how bad?</div>', "2"),
    card(690, 270, 540, 420, '<div style="font-size:70px">🧵</div><div style="font:900 40px Inter;color:var(--cyan)">Traces</div><div class="note" style="margin-top:10px">where is the time going?</div>', "3"),
    card(1260, 270, 540, 420, '<div style="font-size:70px">📄</div><div style="font:900 40px Inter;color:var(--mut)">Logs</div><div class="note" style="margin-top:10px">what exactly happened?<br><span style="color:var(--amber)">roadmap: centralized</span></div>', "3.5"),
    center(740, pill("RootLens: metrics → detect + diagnose · traces → human confirms", "violet"), "4"),
])

# =========================================================== 05 DETECT
add("detect", "Detect: the detector loop", "05 · DETECT", "STEP 1 · DETECT", "Every 10 seconds: one question", [
    "Now, step one: detection. The detector is a small Python loop.",
    "Every ten seconds, it runs the failure ratio query against Prometheus.",
    "If the ratio is at or above zero point three, it counts a breach. If it's below zero point one, it counts an OK. Anything else resets both counters.",
    "Three breaches in a row open an incident. Three OKs in a row resolve it.",
    "So with ten second checks, an incident opens about thirty seconds after failures start. Plus up to a minute for the one minute rate window to fill.",
], [
    code(120, 260, 900, '<span class="k">while True</span>:\n'
         '    value = query_number(QUERY)\n'
         '    breaches = breaches + <span class="s">1</span> <span class="k">if</span> value >= <span class="r">0.3</span> <span class="k">else</span> <span class="s">0</span>\n'
         '    oks      = oks + <span class="s">1</span> <span class="k">if</span> value <  <span class="s">0.1</span> <span class="k">else</span> <span class="s">0</span>\n'
         '    <span class="k">if</span> breaches >= <span class="s">3</span>: open_incident()\n'
         '    <span class="k">if</span> oks >= <span class="s">3</span>:      resolve_incident()\n'
         '    time.sleep(<span class="s">10</span>)', "0", size=26),
    text(1080, 270, 720, '<div class="lbl" style="margin-bottom:14px">checks · illustrative</div><div style="display:flex;gap:12px">' + "".join(
        f'<div data-at="{3 + i * 0.12:.2f}" style="flex:1;height:120px;border-radius:14px;display:flex;align-items:flex-end;justify-content:center;padding-bottom:8px;'
        f'font:800 22px JetBrains Mono;background:{"rgba(248,113,113,.3)" if v >= .3 else "rgba(52,211,153,.25)"};border:2px solid {"#f87171" if v >= .3 else "#34d399"}">{v}</div>'
        for i, v in enumerate([0.02, 0.41, 0.52, 0.5])) + '</div>'),
    card(1080, 470, 720, 170, '<div style="font:800 32px Inter;margin-top:8px">3 in a row ≥ 0.3 → <span style="color:var(--red)">OPEN</span></div><div style="font:800 32px Inter;margin-top:10px">3 in a row &lt; 0.1 → <span style="color:var(--grn)">RESOLVE</span></div>', "3"),
    card(1080, 670, 720, 170, '<div class="lbl">time to detect</div><div style="font:800 32px Inter;margin-top:8px">≈30 s of checks + up to 1 min window</div>', "4"),
])

add("hysteresis", "Hysteresis: two thresholds", "05 · DETECT", "STEP 1 · DETECT", "Why two thresholds? Hysteresis", [
    "Why two thresholds, point three to open and point one to resolve? This is called hysteresis, and it's a favourite interview topic.",
    "Imagine a single threshold at point three, and a failure ratio wobbling around point three.",
    "The incident would open, close, open, close. Every flip pages someone. That's called flapping, and it destroys trust in alerts.",
    "With two thresholds, there's a dead zone between point one and point three. Once open, the incident stays open until the system is clearly healthy.",
    "A thermostat works the same way. It heats until twenty one degrees and doesn't start again until nineteen.",
], [
    svg('<rect x="120" y="300" width="1100" height="440" rx="18" fill="rgba(28,20,52,.9)" stroke="rgba(190,170,240,.22)" stroke-width="2"/>'
        '<line x1="140" x2="1200" y1="480" y2="480" stroke="#f87171" stroke-width="3" stroke-dasharray="10 8"/>'
        '<line x1="140" x2="1200" y1="640" y2="640" stroke="#34d399" stroke-width="3" stroke-dasharray="10 8"/>'
        '<text x="1210" y="488" fill="#f87171" font-family="JetBrains Mono" font-size="24" font-weight="800">0.3</text>'
        '<text x="1210" y="648" fill="#34d399" font-family="JetBrains Mono" font-size="24" font-weight="800">0.1</text>'
        + arrow("M150,700 L260,690 L330,500 L380,470 L430,490 L480,465 L530,495 L580,470 L640,500 L700,480 L760,560 L820,600 L880,660 L940,670 L1000,675 L1180,680",
                "amber", "1-3.5", head=False)),
    text(150, 320, 600, '<span class="lbl">failure ratio · illustrative</span>', "1"),
    rows(1320, 300, 480, [("2", "🔁", "one threshold → <b>flapping</b>", "red"),
                          ("3", "🟨", "dead zone 0.1–0.3 → <b>stays put</b>", "amber"),
                          ("4", "🌡️", "like a <b>thermostat</b>", "grn")]),
])

add("evidence", "Evidence snapshot at open", "05 · DETECT", "STEP 1 · DETECT", "Snapshot the evidence the moment it opens", [
    "When an incident opens, the detector immediately snapshots the evidence, because metrics change quickly and the interesting moment is now.",
    "For each dependency, it records: is it up, what share of its own requests are failing, and how calls to it failed, split into errors, timeouts and unreachable.",
    "It also records the order status rates and the p ninety five latency.",
    "And it pulls every deployment from the last thirty minutes, with how many seconds before detection each one happened.",
    "All of this is stored as JSON on the incident. That makes the diagnosis reproducible: you can re-run the investigator later on exactly the same evidence.",
], [
    code(120, 260, 1000, '{ <span class="s">"dependencies"</span>: {\n'
         '    <span class="s">"payment-service"</span>: {\n'
         '      <span class="s">"up"</span>: <span class="k">1</span>,\n'
         '      <span class="s">"own_error_ratio"</span>: <span class="r">0.51</span>,\n'
         '      <span class="s">"failure_rates_per_second"</span>: {<span class="s">"error"</span>: <span class="r">2.4</span>, <span class="s">"timeout"</span>: <span class="k">0</span>} } },\n'
         '  <span class="s">"order_p95_latency_seconds"</span>: <span class="k">0.21</span>,\n'
         '  <span class="s">"recent_deployments"</span>: [{ <span class="s">"service"</span>: <span class="s">"payment-service"</span>,\n'
         '      <span class="s">"version"</span>: <span class="s">"v2"</span>, <span class="s">"previous_version"</span>: <span class="s">"v1"</span>,\n'
         '      <span class="s">"seconds_before_detection"</span>: <span class="k">62</span> }] }', "1", size=23),
    rows(1170, 260, 630, [("1", "🩺", "per dependency: <b>up · own errors · how calls failed</b>", "blu"),
                          ("2", "⏱️", "order status rates + <b>p95</b>", "amber"),
                          ("3", "🚀", "<b>deployments</b> in the last 30 min", "violet"),
                          ("4", "🔁", "stored as JSON → <b>reproducible</b>", "grn")]),
    text(120, 790, 1000, '<span class="note">illustrative values, shaped like the real run</span>', "1"),
])

add("fingerprint", "Fingerprints: no duplicates", "05 · DETECT", "STEP 1 · DETECT", "One problem, one incident", [
    "One more detection detail: deduplication.",
    "While failures continue, the detector keeps seeing breaches. Without care, it would open a new incident every thirty seconds.",
    "So every incident has a fingerprint, a stable name for the problem, like order failure ratio high.",
    "Before opening, the A P I looks for an open incident with the same fingerprint. If there is one, nothing new is created.",
    "That's idempotency applied to alerting: sending the same signal twice has the same effect as sending it once.",
], [
    node(120, 300, 380, 200, "breach × 3", "t = 30 s", "red", "1"),
    node(120, 560, 380, 200, "breach × 3 again", "t = 60 s", "red", "1.5"),
    svg(arrow("M510,400 L760,470", "amber", "3-3.5") + arrow("M510,660 L760,540", "amber", "3.3-3.8")),
    node(780, 400, 500, 200, "fingerprint", "order-failure-ratio-high", "amber", "2"),
    node(1360, 300, 440, 200, "✅ incident #12", "opened once", "grn", "3.5"),
    node(1360, 560, 440, 200, "↩️ already open", "no duplicate", "mut", "3.8"),
    center(800, pill("same signal twice = same effect as once → idempotent", "violet"), "4"),
])

# =========================================================== 06 INVESTIGATE
add("investigate", "Investigate: three causes per dependency", "06 · INVESTIGATE", "STEP 2 · INVESTIGATE", "Three possible causes, for every dependency", [
    "Step two: investigate. We know orders are failing. Now, why?",
    "For every dependency, the investigator considers three possible causes. The service is down. The service is returning errors. Or the service is too slow and hitting timeouts.",
    "With two dependencies, that's six hypotheses. Each one gets a score between zero and one.",
    "And each score comes with its reasons: the evidence for it, and the evidence against it. The dashboard shows them, like four for, zero against.",
    "This is the key design choice. A ranked list with reasons, not a single guess. A human can check the reasoning in seconds.",
], [
    text(120, 270, 1680, '<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:22px">' + "".join(
        f'<div class="card" data-at="{1 + i * 0.25:.2f}" style="position:relative;text-align:center"><div style="font-size:64px">{ic}</div>'
        f'<div style="font:900 34px Inter;color:{col}">{nm}</div><div class="note">{why}</div></div>'
        for i, (ic, nm, col, why) in enumerate([("🔌", "is down", "var(--red)", "up = 0 · can't connect"),
                                                ("💥", "returning errors", "var(--pink)", "running, but answers 5xx"),
                                                ("🐢", "too slow", "var(--amber)", "timeouts · p95 near 3 s")])) + '</div>'),
    center(570, pill("2 dependencies × 3 causes = 6 hypotheses, each scored 0 → 1", "violet"), "2"),
    center(680, '<span class="pill" style="--c:var(--grn)">✓ 4 for</span>&nbsp;&nbsp;<span class="pill" style="--c:var(--red)">✗ 0 against</span>', "3"),
    center(790, '<span style="font:800 32px Inter;color:var(--amber)">a ranked list with reasons, not one guess</span>', "4"),
])

add("scoring", "How the scores add up", "06 · INVESTIGATE", "STEP 2 · INVESTIGATE", "Evidence adds points: 'returning errors'", [
    "Let's see how one score is built. Take the cause: payment service is returning errors.",
    "If the service is running, meaning up equals one, that adds zero point two five.",
    "If it is failing at least twenty percent of its own requests, that adds zero point four five. That's the strongest clue, because the error comes from inside the service.",
    "If almost all failed calls to it were error responses, not timeouts, add zero point one five.",
    "And if responses are not unusually slow, add another zero point one five. Together, that's a perfect one point zero.",
    "The weights are hand-tuned, and every rule is a unit test. That makes it explainable: you can point at the line of code that produced a score.",
], [
    text(120, 270, 1100, "".join(
        f'<div class="row" data-at="{at}" style="--c:var(--grn)"><div class="ic">+</div><div style="flex:1">{w}</div><div style="font:900 32px JetBrains Mono;color:var(--grn)">{p}</div></div>'
        for at, w, p in [("1", "running (up = 1)", "0.25"), ("2", "own error ratio ≥ 20%", "0.45"),
                         ("3", "≥ 80% of failures are error responses", "0.15"), ("4", "p95 well under the timeout", "0.15")])),
    card(1280, 270, 520, 420, '<div class="lbl">payment-service · returning errors</div><div style="font:900 140px Inter;color:var(--grn);text-align:center;margin-top:30px">'
         '<span data-count="1-4.6" data-to="1" data-dec="2">0</span></div>', "1"),
    center(790, pill("hand-tuned weights · every rule unit-tested · explainable", "violet"), "5"),
])

add("scoring2", "Competing hypotheses", "06 · INVESTIGATE", "STEP 2 · INVESTIGATE", "The other hypotheses lose points", [
    "Meanwhile, the competing hypotheses are scored from the same evidence.",
    "Payment service is down? The up metric is one, so it's running. That's evidence against, and it scores zero.",
    "Payment service too slow? It's running, which adds point two. But there are no timeouts, so that's evidence against. It ends at point two.",
    "User service? Calls to it aren't failing at all, so it isn't even implicated. It's skipped.",
    "So the final ranking is one point zero for errors, against point two for the runner up. A clear winner.",
], [
    table(120, 260, 1680, ["hypothesis", "for", "against", "score"], [
        ("0", ["💳 payment · <b>returning errors</b>", "running · 51% own errors · …", "none", '<b style="color:var(--grn)">1.00</b>'], "4"),
        ("1", ["💳 payment · down", "", "up = 1, it's running", '<b style="color:var(--red)">0.00</b>'], None),
        ("2", ["💳 payment · too slow", "running", "few or no timeouts", "0.20"], "4"),
        ("3", ['👤 user · <span class="note">any</span>', "", "no failed calls → not implicated", "—"], None),
    ], size=26),
    center(720, '<span style="font:900 60px Inter"><span style="color:var(--grn)">1.00</span> vs <span style="color:var(--mut)">0.20</span></span>', "4"),
])

add("confidence", "The confidence rule", "06 · INVESTIGATE", "STEP 2 · INVESTIGATE", "High confidence needs a score AND a gap", [
    "Next, how confident are we? This rule decides whether the robot may act at all.",
    "Confidence is high only when the top cause scores at least zero point seven five, and it beats the runner up by at least zero point three.",
    "Why the gap? Because a high score alone isn't enough. If two causes both score point eight, the evidence can't tell them apart, and acting on either one is a coin flip.",
    "Medium means the top score is at least point five. Anything lower is low.",
    "In the real run, the top score was one point zero against point two, a gap of point eight. So, high confidence.",
], [
    code(120, 260, 900, '<span class="k">def</span> _confidence(ranked):\n'
         '    top, second = ranked[<span class="s">0</span>], ranked[<span class="s">1</span>]\n'
         '    <span class="k">if</span> top >= <span class="s">0.75</span> <span class="k">and</span> top - second >= <span class="s">0.3</span>:\n'
         '        <span class="k">return</span> <span class="s">"high"</span>\n'
         '    <span class="k">if</span> top >= <span class="s">0.5</span>:\n'
         '        <span class="k">return</span> <span class="s">"medium"</span>\n'
         '    <span class="k">return</span> <span class="s">"low"</span>', "1", size=27),
    card(1080, 260, 720, 250, '<div class="lbl" style="color:var(--red)">high score, no gap</div><div style="font:800 34px Inter;margin-top:14px">0.80 vs 0.80 → <span style="color:var(--red)">coin flip</span></div>', "2"),
    card(1080, 540, 720, 250, '<div class="lbl" style="color:var(--grn)">real run</div><div style="font:800 34px Inter;margin-top:14px">1.00 vs 0.20 · gap 0.80 → <span style="color:var(--grn)">HIGH</span></div>', "4"),
])

add("slowcase", "Worked example: the slow release", "06 · INVESTIGATE", "STEP 2 · INVESTIGATE", "The other bug: user-service v2 is slow", [
    "Let's run the other planted bug through the same scoring, so you can explain both in an interview.",
    "User service version two sleeps four seconds. The order service gives up after three, so every call times out, and orders return five oh four.",
    "Too slow gets point two for running, point four because most failures are timeouts, and point three more because p ninety five is near the three second timeout. Plus point one for no errors of its own.",
    "That's one point zero again. And returning errors scores low, because the service itself reports no errors and responses are very slow.",
    "Same code, different evidence, different answer. That's the test of a good diagnosis rule.",
], [
    svg(arrow("M380,420 L900,420", "amber", "1-1.8", pid="sl1") + mover("sl1", "1-1.8", "amber")
        + '<line x1="700" x2="700" y1="330" y2="510" stroke="#f87171" stroke-width="4" stroke-dasharray="8 8"/>'),
    node(120, 330, 260, 180, "🛒 order", "timeout = 3 s", "amber", "1"),
    node(910, 330, 300, 180, "👤 user v2", "sleeps 4 s", "red", "1"),
    text(600, 520, 220, '<span class="lbl" style="color:var(--red)">3 s · gives up</span>', "1.5"),
    text(1280, 300, 520, "".join(f'<div class="row" data-at="{at}" style="--c:var(--amber)"><div style="flex:1">{w}</div><b>{p}</b></div>' for at, w, p in
                                 [("2", "running", "+0.2"), ("2.3", "mostly timeouts", "+0.4"), ("2.6", "p95 ≈ 3 s", "+0.3"), ("2.9", "no own errors", "+0.1")])),
    center(780, pill("too slow · <b>1.00</b>", "amber") + "&nbsp;&nbsp;" + pill("returning errors · low", "mut"), "3"),
])

add("blast", "Blast radius", "06 · INVESTIGATE", "STEP 2 · INVESTIGATE", "Blast radius: who else is hurt?", [
    "The investigator also reports the blast radius: which other services depend on the culprit.",
    "It reads a small dependency graph. Order service depends on user service and payment service.",
    "So if payment is the culprit, the blast radius is the order service. That's what the customer actually feels.",
    "In a bigger system, this tells you who to notify, and which other alerts are just symptoms of the same root cause.",
], [
    code(120, 270, 760, 'DEPENDENCY_GRAPH = {\n  <span class="s">"order-service"</span>: [\n     <span class="s">"user-service"</span>,\n     <span class="s">"payment-service"</span>] }', "1", size=28),
    node(1200, 270, 420, 170, "💳 payment-service", "root cause", "red", "2"),
    node(1200, 600, 420, 170, "🛒 order-service", "impacted", "amber", "2.4"),
    svg(arrow("M1410,440 L1410,590", "red", "2.2-2.6")),
    card(120, 560, 760, 230, '<div class="lbl">why it matters</div><div style="font:700 28px/1.5 Inter;margin-top:10px">who to notify · which alerts are <span style="color:var(--amber)">just symptoms</span></div>', "3"),
])

add("whyrules", "Why rules, not machine learning", "06 · INVESTIGATE", "DESIGN DECISION", "Why hand-written rules, not ML or an LLM?", [
    "An obvious question: why not use machine learning, or ask a large language model what went wrong?",
    "First, there's no training data. Incidents are rare, and every system's incidents look different.",
    "Second, explainability. When a robot is about to roll back production, someone will ask why. A rule with listed evidence answers that. A model's output doesn't.",
    "Third, testability. Every rule is a pure function with unit tests. You can't unit test an L L M's judgement the same way.",
    "Where an L L M would help is writing a friendly explanation from the evidence, after the decision is made. That's on the roadmap, and it should never be the thing that decides.",
], [
    rows(120, 260, 1100, [("1", "📉", "<b>No training data</b> · incidents are rare and unique", "red"),
                          ("2", "🗣️", "<b>Explainable</b> · \"why did you roll back?\"", "amber"),
                          ("3", "🧪", "<b>Testable</b> · pure functions, unit tests", "grn"),
                          ("4", "✍️", "LLM later: <b>explain</b>, never <b>decide</b>", "violet")]),
    card(1280, 260, 520, 500, '<div class="lbl">rule vs model</div><div style="font:700 28px/1.7 Inter;margin-top:16px">'
         'rule → <span style="color:var(--grn)">evidence listed</span><br>rule → <span style="color:var(--grn)">same input, same output</span><br>'
         'model → <span style="color:var(--red)">hard to audit</span><br>model → <span style="color:var(--red)">can be confidently wrong</span></div>', "2"),
])

# =========================================================== 07 WHAT CHANGED
add("changed", "What changed? Change correlation", "07 · WHAT CHANGED", "WHAT CHANGED?", "Link the failure to a recent release", [
    "Now the question that solves most real incidents. What changed?",
    "Studies of outages keep finding the same thing: a large share are caused by a change, usually a deployment or a config change.",
    "So for the culprit service, the investigator finds its most recent deployment from the evidence.",
    "A release up to five minutes before detection is a strong link. Up to fifteen minutes is moderate. Older than that is weak.",
    "In the real run, payment service version two went out sixty two seconds before detection. Strong. And the next step reads: roll back from v two to v one.",
], [
    svg('<line x1="160" x2="1760" y1="560" y2="560" stroke="rgba(255,255,255,.3)" stroke-width="4"/>'
        '<rect x="1060" y="520" width="560" height="80" fill="rgba(52,211,153,.18)" data-at="3"/>'
        '<rect x="560" y="520" width="500" height="80" fill="rgba(242,177,52,.15)" data-at="3.4"/>'),
    text(1060, 620, 560, '<div style="text-align:center;font:800 26px Inter;color:var(--grn)">≤ 5 min · strong</div>', "3"),
    text(560, 620, 500, '<div style="text-align:center;font:800 26px Inter;color:var(--amber)">≤ 15 min · moderate</div>', "3.4"),
    text(160, 620, 400, '<div style="text-align:center;font:800 26px Inter;color:var(--mut)">older · weak</div>', "3.6"),
    text(1580, 420, 240, '<div style="text-align:center;font:800 26px Inter;color:var(--red)">🚨 detected</div>', "2"),
    text(1420, 300, 300, '<div style="text-align:center;font:800 26px Inter;color:var(--violet)">🚀 v2 · 62 s before</div>', "4"),
    center(750, pill("→ roll back payment-service from v2 to v1", "amber"), "4.5"),
])

add("rollbackguard", "Never roll back a rollback", "07 · WHAT CHANGED", "WHAT CHANGED?", "Never roll back twice", [
    "There's a trap here. What if the most recent change was itself a rollback?",
    "Say we rolled payment back from v two to v one, and it still fails. The latest change is now the rollback.",
    "Rolling back again would mean going back to v two, the broken version, or to something even older. That's going in circles.",
    "So the investigator compares version numbers. If the new version is lower than the previous one, it's a rollback, and the advice changes to: investigate manually, do not roll back again.",
    "The rule: a rollback can't explain a new failure, so the robot hands over to a human.",
], [
    table(120, 270, 1680, ["time", "change", "kind"], [
        ("1", ["12:25", "payment v1 → <b>v2</b>", tag("release", "violet")], None),
        ("1.4", ["12:26", "payment v2 → <b>v1</b>", tag("rollback", "amber")], "2-3"),
        ("2", ["12:28", "still failing… roll back again?", '<span class="x">✗ no</span>'], None),
    ], size=28),
    code(120, 600, 900, 'is_rollback = current &lt; previous   <span class="c"># v1 &lt; v2</span>', "3", size=28),
    card(1080, 600, 720, 200, '<div style="font:800 32px/1.4 Inter;margin-top:16px">a rollback can\'t explain a new failure → <span style="color:var(--amber)">human</span></div>', "4"),
])

# =========================================================== 08 DECIDE
add("decide", "Decide: the rulebook is a pure function", "08 · DECIDE", "STEP 3 · DECIDE", "The rulebook: a pure function", [
    "Step three: decide. This lives in one file, policy dot py, and it's the most important design choice in the project.",
    "The rulebook is a pure function. It takes the diagnosis, the past attempts for this incident, and how many actions this service had in the last hour.",
    "It returns one of three decisions: act, wait, or escalate to a human.",
    "It never touches Docker, the network or the database. Same input, same output, every time.",
    "That means every rule can be unit tested in milliseconds, with no containers running. And you can read the whole policy in one screen.",
], [
    node(120, 360, 420, 300, "📥 input", "diagnosis<br>attempts so far<br>actions last hour", "blu", "1"),
    node(720, 330, 480, 360, "📘 decide()", "pure function<br>no Docker · no network<br>no database", "violet", "0"),
    svg(arrow("M540,510 L710,510", "blu", "1-1.5") + arrow("M1210,420 L1380,340", "grn", "2-2.4") + arrow("M1210,510 L1380,510", "amber", "2.2-2.6")
        + arrow("M1210,600 L1380,680", "red", "2.4-2.8")),
    node(1390, 270, 410, 140, "🛠️ act", "rollback · restart", "grn", "2"),
    node(1390, 440, 410, 140, "⏸️ wait", "cooldown", "amber", "2.2"),
    node(1390, 610, 410, 140, "🙋 escalate", "hand to a human", "red", "2.4"),
    center(790, pill("same input → same output · tested in milliseconds", "grn"), "4"),
])

add("tree", "The decision tree", "08 · DECIDE", "STEP 3 · DECIDE", "Walking the rulebook", [
    "Let's walk the rulebook in order. Every question that fails sends the incident to a human.",
    "Is a clear cause named? Is the target the user or payment service, the only ones the robot is allowed to touch?",
    "Is confidence high? And is only one service failing? If two are failing at once, it's probably something bigger, like the network.",
    "Are we under two attempts for this incident, and under three actions for this service in the last hour?",
    "Was the last attempt less than sixty seconds ago? Then wait, because the previous action might still be taking effect.",
    "Finally: is there a recent release to undo, which isn't itself a rollback and hasn't been tried? Roll back. Otherwise, if a restart hasn't been tried, restart. Otherwise, escalate.",
], [
    text(120, 255, 1100, "".join(
        f'<div class="row" data-at="{at}" style="--c:{col};padding:10px 20px;margin-bottom:10px;font-size:26px"><div class="ic">{ic}</div><div>{w}</div></div>'
        for at, ic, w, col in [("1", "❓", "clear cause named?", "var(--violet)"), ("1.5", "🎯", "target is user or payment service?", "var(--violet)"),
                               ("2", "💪", "confidence high?", "var(--violet)"), ("2.5", "1️⃣", "only one service failing?", "var(--violet)"),
                               ("3", "🔢", "&lt; 2 attempts · &lt; 3 actions / service / hour?", "var(--violet)"),
                               ("4", "⏸️", "last attempt &lt; 60 s ago → <b>wait</b>", "var(--amber)"),
                               ("5", "↩️", "recent release to undo → <b>roll back</b>", "var(--grn)"),
                               ("5.6", "🔄", "else restart not tried → <b>restart</b>", "var(--blu)")])),
    card(1280, 255, 520, 580, '<div style="font-size:90px;text-align:center;margin-top:60px">🙋</div><div style="text-align:center;font:900 40px Inter;color:var(--red)">any "no"</div>'
         '<div style="text-align:center;font:800 34px Inter;margin-top:12px">→ escalate to a human</div>', "0"),
])

add("guardrails", "Guardrails: attempts, rate limit, cooldown", "08 · DECIDE", "STEP 3 · DECIDE", "Three guardrails against a runaway robot", [
    "Three of those rules are guardrails, and each one stops a specific disaster.",
    "Max two attempts per incident. If two actions didn't fix it, a third one won't either. Stop and call a human.",
    "Max three actions per service per hour. This stops a restart loop, where the robot keeps restarting a service that crashes for a reason it can't see.",
    "And a sixty second cooldown. After an action, metrics need time to reflect it. Acting again too soon means acting on stale data.",
    "The general principle: automation should fail safe. When in doubt, it stops and asks, rather than doing more.",
], [
    text(120, 270, 1680, '<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:22px">' + "".join(
        f'<div class="card" data-at="{at}" style="position:relative;text-align:center;height:380px"><div style="font:900 110px Inter;color:{col}">{n}</div>'
        f'<div style="font:800 30px Inter">{w}</div><div class="note" style="margin-top:12px">{why}</div></div>'
        for at, n, w, why, col in [("1", "2", "attempts / incident", "two misses → a third won't help", "var(--amber)"),
                                   ("2", "3", "actions / service / hour", "no restart loops", "var(--red)"),
                                   ("3", "60s", "cooldown", "let metrics catch up", "var(--blu)")]) + '</div>'),
    center(720, pill("fail safe: when in doubt, stop and ask", "grn"), "4"),
])

add("rollbackvsrestart", "Rollback versus restart", "08 · DECIDE", "STEP 3 · DECIDE", "Why rollback first, then restart?", [
    "Why does the rulebook prefer a rollback over a restart?",
    "If a release just went out and things broke, the bug is most likely in the new code. Restarting the same buggy code just restarts the bug.",
    "A rollback removes the cause. It's the most reliable fix in operations, which is why good teams make rollbacks fast and boring.",
    "A restart helps when there's no recent release: a memory leak, a stuck connection pool, a process in a bad state.",
    "So: if a change explains it, undo the change. If not, try a restart once. If that fails too, it's a human's problem.",
], [
    card(120, 270, 820, 430, '<div style="font-size:70px">↩️</div><div style="font:900 44px Inter;color:var(--grn)">Rollback</div>'
         '<div style="font:600 28px/1.5 Inter;margin-top:14px">a recent release explains it<br><span class="note">removes the cause</span></div>', "2"),
    card(980, 270, 820, 430, '<div style="font-size:70px">🔄</div><div style="font:900 44px Inter;color:var(--blu)">Restart</div>'
         '<div style="font:600 28px/1.5 Inter;margin-top:14px">no recent change<br><span class="note">leak · stuck pool · bad state</span></div>', "3"),
    center(760, '<span style="font:800 32px Inter">change explains it → <span style="color:var(--grn)">undo</span> · else → <span style="color:var(--blu)">restart once</span> · else → <span style="color:var(--red)">human</span></span>', "4"),
])

# =========================================================== 09 ACT & VERIFY
add("modes", "Modes: off, dry-run, enforce", "09 · ACT", "STEP 4 · ACT", "Three modes: off, dry-run, enforce", [
    "Step four: act. But first, a safety switch. The controller has three modes.",
    "Off does nothing at all.",
    "Dry run makes every decision and records it in the audit log, but never acts. This is the default.",
    "Enforce actually carries out the decision.",
    "Dry run is how you build trust in automation. You run it for weeks, compare its suggestions with what the humans did, and only then switch it on. Real teams roll out auto remediation exactly like this.",
], [
    text(120, 280, 1680, '<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:22px">' + "".join(
        f'<div class="card" data-at="{at}" style="position:relative;text-align:center;height:380px{";border-color:var(--amber)" if d else ""}"><div style="font-size:80px">{ic}</div>'
        f'<div style="font:900 44px JetBrains Mono;color:{col}">{n}</div><div class="note" style="margin-top:12px">{w}</div>'
        f'{"<div style=margin-top:16px>" + pill("default", "amber") + "</div>" if d else ""}</div>'
        for at, ic, n, w, col, d in [("1", "⏻", "off", "does nothing", "var(--mut)", False),
                                     ("2", "📝", "dry-run", "decides + records<br>never acts", "var(--amber)", True),
                                     ("3", "🛠️", "enforce", "acts for real", "var(--grn)", False)]) + '</div>'),
    center(730, pill("build trust: weeks of dry-run → compare with humans → enforce", "violet"), "4"),
])

add("preflight", "Preflight checks", "09 · ACT", "STEP 4 · ACT", "Preflight: is it still true right now?", [
    "In enforce mode, there's one more gate: preflight checks. The decision was made from evidence, but evidence ages. So right before acting, it re-checks the world.",
    "Is the incident recent? More than thirty minutes old, and it won't act automatically.",
    "Is it still failing right now? If the live failure ratio has dropped below point three, the system already recovered, and acting would only cause risk.",
    "For a rollback: is the target really an earlier version? And is the bad version still the one running? If someone already rolled back by hand, the situation has changed, so do nothing.",
    "This is the classic time of check versus time of use problem. Decide on old data, re-verify on fresh data before you act.",
], [
    rows(120, 260, 1100, [("1", "⏳", "incident ≤ <b>30 min</b> old", "blu"),
                          ("2", "📉", "live failure ratio still ≥ <b>0.3</b>", "red"),
                          ("3", "🔢", "target version &lt; bad version", "violet"),
                          ("3.5", "🏷️", "bad version is <b>still running</b>", "amber")]),
    card(1280, 260, 520, 520, '<div class="lbl">TOCTOU</div><div style="font:800 32px/1.5 Inter;margin-top:16px">time of <span style="color:var(--amber)">check</span><br>≠<br>time of <span style="color:var(--grn)">use</span></div>'
         '<div class="note" style="margin-top:18px">decide on evidence,<br>re-verify on live data</div>', "4"),
])

add("executor", "The executor: the only code that acts", "09 · ACT", "STEP 4 · ACT", "executor.py: the only code allowed to act", [
    "Only one file is allowed to change the running system: the executor.",
    "It first checks the request against an allow list: only roll back or restart, and only on the user or payment service.",
    "It builds the command as a list of arguments, never as a shell string. So nothing from the incident data can ever be injected into a shell command.",
    "For a rollback, it writes the target version into the environment file, recreates just that container, waits until the version endpoint reports the right version, and records the deployment as done by the robot.",
    "Keeping all side effects in one small file means there's exactly one place to review, test and lock down.",
], [
    code(120, 260, 1000, '<span class="k">def</span> build_command(action, service):\n'
         '    <span class="c"># a list, never a shell string</span>\n'
         '    <span class="k">if</span> action == <span class="s">"rollback_deployment"</span>:\n'
         '        <span class="k">return</span> [<span class="s">"docker"</span>, <span class="s">"compose"</span>, <span class="s">"up"</span>, <span class="s">"-d"</span>,\n'
         '                <span class="s">"--no-deps"</span>, <span class="s">"--force-recreate"</span>, service]\n'
         '    <span class="k">if</span> action == <span class="s">"restart_service"</span>:\n'
         '        <span class="k">return</span> [<span class="s">"docker"</span>, <span class="s">"compose"</span>, <span class="s">"restart"</span>, service]', "2", size=24),
    rows(1170, 260, 630, [("1", "✅", "allow list: <b>2 actions · 2 services</b>", "grn"),
                          ("2", "🧱", "argument list → <b>no shell injection</b>", "red"),
                          ("3", "🏷️", "write version · recreate · <b>wait for /version</b>", "blu"),
                          ("3.6", "📜", "record deployment <b>by: robot</b>", "amber")]),
])

add("verify", "Verify recovery", "09 · VERIFY", "STEP 5 · VERIFY", "Did the fix actually work?", [
    "Step five: verify. Doing an action isn't the same as fixing the problem.",
    "After acting, the controller keeps reading the live failure ratio.",
    "Three readings in a row below zero point one means recovered.",
    "If two minutes pass without that, it decides. Still failing means failed, and it escalates to a human. Dropped but not for long enough means inconclusive. No data at all is also inconclusive.",
    "Notice the four outcomes. A lazy version would just say success or failure. Being honest about uncertainty is what makes the audit log trustworthy.",
], [
    text(120, 270, 1000, '<div class="lbl" style="margin-bottom:14px">live failure ratio after rollback · illustrative</div><div style="display:flex;gap:14px">' + "".join(
        f'<div data-at="{1 + i * 0.25:.2f}" style="flex:1;height:150px;border-radius:14px;display:flex;align-items:center;justify-content:center;'
        f'font:800 28px JetBrains Mono;background:{"rgba(248,113,113,.3)" if v >= .1 else "rgba(52,211,153,.25)"};border:2px solid {"#f87171" if v >= .1 else "#34d399"}">{v}</div>'
        for i, v in enumerate([0.48, 0.21, 0.04, 0.0, 0.01])) + '</div>'),
    text(120, 470, 1000, row("3 in a row &lt; 0.1 → <b>recovered</b>", ic="✅", color="grn"), "2"),
    table(1180, 260, 620, ["state", "when"], [
        ("2", ['<b style="color:var(--grn)">recovered</b>', "3 OKs in a row"], None),
        ("3", ["pending", "&lt; 120 s"], None),
        ("3.3", ['<b style="color:var(--red)">failed</b>', "still bad → human"], None),
        ("3.6", ['<b style="color:var(--amber)">inconclusive</b>', "brief dip · no data"], None)], size=25),
    center(760, pill("honest about uncertainty → a trustworthy audit log", "violet"), "4"),
])

add("audit", "The audit log", "09 · VERIFY", "RECORD EVERYTHING", "The audit log, including 'did nothing'", [
    "Every decision goes into the audit log, and that includes the decisions not to act.",
    "Escalated because confidence was medium. Waited because of the cooldown. Suggested a rollback, but in dry run. Refused by preflight, because the system had already recovered.",
    "Why log inaction? Because after an incident, the first question in the review is: why didn't the automation do anything? You need that answer written down.",
    "The audit log is also an input. The rulebook counts past attempts and actions per hour from it, so the guardrails survive a controller restart.",
], [
    table(120, 260, 1680, ["time", "decision", "outcome"], [
        ("1", ["12:26:05", "roll back payment-service to v1", tag("suggested · dry-run", "amber")], None),
        ("1.3", ["12:31:10", "escalate: confidence medium", tag("needs human", "red")], None),
        ("1.6", ["12:40:02", "wait: last attempt 20 s ago", tag("waiting", "blu")], None),
        ("1.9", ["12:52:44", "refused: live ratio 4%, already recovered", tag("no action", "mut")], None)], size=25),
    rows(120, 650, 1680, [("2", "❓", "post-incident review: <b>\"why didn't it act?\"</b> → written down", "amber"),
                          ("3", "🔁", "guardrails count from the log → <b>survive restarts</b>", "grn")]),
])

add("notify", "Telegram notifications to owners", "09 · VERIFY", "PEOPLE IN THE LOOP", "Telegram notices to the service owner", [
    "When a human is needed, the controller tells the right human. It sends Telegram messages through a bot.",
    "Routing is per service. An environment variable like notify chat payment service lists the owners of payment. If none is set, it falls back to a default chat.",
    "There are six kinds of message: opened, needs human, reminder, acted, fix failed, and resolved. A reminder goes out every fifteen minutes while a human is still needed.",
    "Old incidents aren't announced late, and messages are capped in length. If sending fails, it retries after sixty seconds, and a notification failure never blocks the remediation itself.",
], [
    card(120, 260, 760, 560, '<div class="lbl">📱 telegram · illustrative</div><div style="margin-top:18px;padding:22px;border-radius:18px;background:rgba(96,165,250,.15);border:2px solid var(--blu);font:600 26px/1.5 Inter">'
         '🚨 <b>payment-service</b> incident #12<br>returning errors · high confidence<br>trigger: v2, 62 s before<br>🤖 robot: roll back to v1</div>'
         '<div data-at="2" style="margin-top:16px;padding:22px;border-radius:18px;background:rgba(52,211,153,.15);border:2px solid var(--grn);font:600 26px/1.5 Inter">✅ resolved after 1 min 50 s</div>', "0"),
    code(940, 260, 860, 'NOTIFY_CHAT_PAYMENT_SERVICE=<span class="s">"1234,5678"</span>\nNOTIFY_CHAT_DEFAULT=<span class="s">"9999"</span>', "1", size=25),
    text(940, 420, 860, '<div style="display:flex;flex-wrap:wrap;gap:10px">' + "".join(tag(k, col) for k, col in [("opened", "red"), ("needs_human", "amber"), ("reminder · 15 min", "amber"),
                                                                                                                ("acted", "blu"), ("fix_failed", "red"), ("resolved", "grn")]) + '</div>', "2"),
    rows(940, 560, 860, [("3", "🔁", "retry after 60 s · <b>never blocks the fix</b>", "grn")]),
])

# =========================================================== 10 REAL RUN
add("realrun", "A real incident, start to finish", "10 · A REAL RUN", "A REAL INCIDENT", "12:25:02 → 12:27:54", [
    "Now let's put it all together with a real run of the lab.",
    "At twelve twenty five and two seconds, payment service version two is released.",
    "Sixty two seconds later, the incident opens with an order failure ratio of point five two.",
    "In the same second, the diagnosis: payment service is returning errors, one point zero against point two, high confidence, strong trigger. And within a second, the controller decides to roll back to v one.",
    "At twelve twenty six and fifty seconds, the rollback to v one happens.",
    "And at twelve twenty seven fifty four, after three healthy checks, the incident resolves. Total: one minute and fifty seconds.",
], [
    table(120, 260, 1680, ["time", "what happened"], [
        ("1", ["12:25:02", "🚀 payment-service <b>v2</b> released"], "1-e1"),
        ("2", ["12:26:04", "🚨 incident opened · failure ratio <b>0.52</b> · 62 s after release"], "2-e2"),
        ("3", ["12:26:04", "🧠 returning errors · <b>1.00 vs 0.20</b> · high · strong trigger"], "3-3.6"),
        ("3.6", ["12:26:05", "📘 decide: <b>roll back to v1</b>"], "3.6-e3"),
        ("4", ["12:26:50", "↩️ rollback to v1"], "4-e4"),
        ("5", ["12:27:54", '✅ resolved · total <b style="color:var(--grn)">1 min 50 s</b>'], "5-e5")], size=27),
])

add("dash1", "Dashboard: overview", "10 · DASHBOARD", "THE DASHBOARD", "Something looks wrong → problem detected", [
    "Here's what that looked like on the live dashboard, which is plain H T M L served by the order service.",
    "On the left, something looks wrong. Fifty two percent of orders fail, and the detector is still counting checks before it opens an incident.",
    "On the right, the problem is detected. Detect, investigate and decide are done. Payment service is returning errors, so roll back to v one.",
    "The steps light up in the same order as the five step loop, so anyone watching knows exactly where the automation is.",
], [
    shot(120, 260, 820, "shots/1-overview-something-wrong.png", "1 · something looks wrong", "1"),
    shot(980, 260, 820, "shots/2-overview-problem-detected.png", "2 · problem detected", "2"),
])

add("dash2", "Dashboard: incident detail", "10 · DASHBOARD", "THE DASHBOARD", "Incident detail and the decision log", [
    "Opening the incident shows the full diagnosis: score one point zero with high confidence, what changed, every cause that was considered with its reasons, and a timeline.",
    "The automation page shows the robot mode, the safety rules, and the decision log. Here: roll back payment service to v one, dry run, so suggested only.",
    "That's the explainability goal in practice. Everything the robot thinks is on screen, in plain English.",
], [
    shot(120, 260, 820, "shots/3-incident-detail.png", "3 · incident detail", "0"),
    shot(980, 260, 820, "shots/4-automation-decision-log.png", "4 · automation & decision log", "1"),
])

add("dash3", "Dashboard: deployments and recovery", "10 · DASHBOARD", "THE DASHBOARD", "Deployments, and healthy again", [
    "The deployments page lists every release and rollback, which is exactly the table that change correlation reads.",
    "And finally, healthy again. Three healthy checks resolve the incident, after one minute and fifty seconds.",
    "One detail about the hosted version: visitors get a read only view, so nobody on the internet can trigger chaos or deployments.",
], [
    shot(120, 260, 820, "shots/5-deployments.png", "5 · deployments", "0"),
    shot(980, 260, 820, "shots/6-overview-healthy-again.png", "6 · healthy again", "1"),
])

# =========================================================== 11 TESTING
add("testing", "Testing: 118 unit tests", "11 · TESTING", "TESTING", "118 unit tests, no Docker needed", [
    "Now testing. There are one hundred and eighteen unit tests across six files.",
    "They cover the investigator, the rulebook, the safety checks, the executor, the controller loop and the notifications.",
    "Because the rulebook and the safety checks are pure functions, their tests need no Docker and no network. You pass in a diagnosis and assert on the decision.",
    "The executor is tested with fakes. The command runner, the version probe and the deployment recorder are passed in as functions, so a test can pretend Docker failed, or the version never changed.",
    "That's dependency injection used for testability. The code that decides is pure, and the code with side effects takes its tools as parameters.",
], [
    card(120, 260, 520, 330, '<div class="lbl">unit tests</div><div style="font:900 150px Inter;color:var(--grn);text-align:center"><span data-count="0-0.8" data-to="118">0</span></div>', "0"),
    text(700, 260, 1100, '<div style="display:flex;flex-wrap:wrap;gap:12px">' + "".join(tag(f, "violet") for f in
         ["test_investigator", "test_policy", "test_safety", "test_executor", "test_controller", "test_notify"]) + '</div>', "1"),
    code(700, 380, 1100, '<span class="k">def</span> test_escalates_when_two_services_fail():\n'
         '    d = decide(diagnosis_with(<span class="s">"payment"</span>, <span class="s">"user"</span>))\n'
         '    <span class="k">assert</span> d[<span class="s">"kind"</span>] == <span class="s">"escalate"</span>', "2", size=25),
    code(120, 640, 1680, 'execute(action, service, runner=<span class="t">fake_runner</span>, probe=<span class="t">fake_probe</span>, recorder=<span class="t">fake_recorder</span>)   <span class="c"># Docker never runs</span>', "3", size=25),
])

add("ci", "CI with GitHub Actions", "11 · TESTING", "CONTINUOUS INTEGRATION", "Two jobs on every push", [
    "GitHub Actions runs two jobs on every push.",
    "The test job runs all six test files.",
    "The build job validates the compose file and builds every Docker image, so a broken Dockerfile is caught before anyone tries to run the lab.",
    "There's also a release workflow that publishes the all in one demo image to the GitHub container registry, which is what the one command docker run uses.",
], [
    node(120, 300, 520, 200, "🧪 test", "6 test files · 118 tests", "grn", "1"),
    node(700, 300, 520, 200, "🐳 build", "compose config · build images", "blu", "2"),
    node(1280, 300, 520, 200, "📦 release", "ghcr.io/hemashreevi/rootlens", "violet", "3"),
    code(120, 600, 1680, 'docker run --rm -p 10000:10000 ghcr.io/hemashreevi/rootlens:latest', "3", size=30),
])

# =========================================================== 12 DEPLOY
add("compose", "Running the full lab", "12 · DEPLOYMENT", "DEPLOYMENT", "The full lab: docker compose up", [
    "To run the full lab on a laptop, it's docker compose up, and eight containers start.",
    "The incident database lives in a named Docker volume, so it survives restarts. One warning in the docs: never run compose down with the volumes flag, because it deletes the incident history.",
    "The controller mounts the Docker socket, so it can recreate containers. On one laptop that's acceptable. In real production it's a big permission, and I'd replace it with a narrower one.",
    "There's also a Codespaces setup, so anyone can open the full lab in a browser with one click, with fake traffic already running.",
], [
    code(120, 260, 860, 'docker compose up -d\ndocker compose ps   <span class="c"># 8 containers</span>\n\n<span class="r">docker compose down -v</span>   <span class="c"># ✗ deletes incidents</span>', "0", size=28),
    rows(1040, 260, 760, [("1", "💾", "named volume <b>rootlens-data</b>", "grn"),
                          ("2", "⚠️", "Docker socket = <b>big permission</b>", "red"),
                          ("3", "☁️", "<b>Codespaces</b>: one click, traffic running", "cyan")]),
])

add("hosted", "The hosted demo: one container", "12 · DEPLOYMENT", "DEPLOYMENT", "Free hosting gives you one container", [
    "The hosted demo had an interesting constraint. A free web host gives you one container, not eight.",
    "So a supervisor script runs the whole lab as processes inside one image: Prometheus, the three services, the detector, the traffic generator, and the controller in enforce mode.",
    "The executor has a second runtime called process. Instead of docker compose, it asks the supervisor to recreate the service. The policy, the safety checks and the audit log are exactly the same code.",
    "A release train ships the buggy payment version two about every twenty minutes. That spacing respects the rule of three actions per service per hour.",
    "So any visitor can watch RootLens detect a bad release, blame it, and roll it back on its own.",
], [
    card(120, 260, 820, 560, '<div class="lbl">one container · demo/run.py supervisor</div><div style="display:flex;flex-wrap:wrap;gap:12px;margin-top:20px">' + "".join(
        pill(n, col) for n, col in [("prometheus", "org"), ("user", "grn"), ("order", "amber"), ("payment", "red"), ("detector", "red"),
                                    ("traffic", "cyan"), ("controller · enforce", "blu")]) + '</div>', "1"),
    code(1000, 260, 800, 'EXECUTOR_RUNTIME=<span class="s">process</span>\n<span class="c"># compose → supervisor</span>\n<span class="c"># same policy · safety · audit</span>', "2", size=26),
    card(1000, 560, 800, 260, '<div class="lbl">release train</div><div style="font:800 34px/1.4 Inter;margin-top:12px">v2 every ≈<span style="color:var(--amber)">20 min</span><br>'
         '<span class="note">≤ 3 actions / service / hour</span></div>', "3"),
])

# =========================================================== 13 LIMITS
add("limits", "Honest limits", "13 · LIMITS", "HONEST NOTES", "What RootLens doesn't do (yet)", [
    "Every good project has honest limits, and interviewers respect you for naming them before they do.",
    "The bugs are planted. The rollback is real release mechanics, but this is a simulated pipeline on one machine.",
    "The write endpoints, like recording a deployment, aren't authenticated yet.",
    "The controller mounts the Docker socket, which is too much permission for real production.",
    "And slowness that stays under the three second timeout isn't detected, because detection is based on failures, not latency.",
], [
    rows(120, 260, 1680, [("1", "🧪", "bugs are <b>planted</b> · simulated pipeline on one machine", "amber"),
                          ("2", "🔓", "write endpoints <b>not authenticated</b> yet", "red"),
                          ("3", "🐳", "Docker socket → <b>too much permission</b>", "red"),
                          ("4", "🐢", "slow but &lt; 3 s → <b>not detected</b>", "amber")]),
])

add("next", "What I'd build next", "13 · LIMITS", "ROADMAP", "What I'd build next", [
    "And here's what I'd build next, in order of value.",
    "A latency based detector, comparing p ninety five against a target, so slowness is caught before it becomes timeouts.",
    "Authentication on the write endpoints, Postgres instead of SQLite, and a narrower permission than the Docker socket.",
    "Kubernetes, where a rollback becomes a rollout undo on a deployment, and centralized logs.",
    "And finally, an L L M that writes a friendly explanation grounded in the stored evidence, never one that decides.",
], [
    rows(120, 260, 1680, [("1", 1, "<b>Latency detector</b> · p95 vs a target (SLO)", "amber"),
                          ("2", 2, "<b>Auth</b> · <b>Postgres</b> · narrower permissions", "red"),
                          ("3", 3, "<b>Kubernetes</b> · kubectl rollout undo · central logs", "cyan"),
                          ("4", 4, "<b>LLM explanations</b> grounded in evidence", "violet")]),
])

# =========================================================== 14 INTERVIEW
add("qa1", "Interview questions: core", "14 · INTERVIEW Q&A", "INTERVIEW · CORE", "Questions you will hear", [
    "Now, the interview. Here's how the core questions sound, and how to answer.",
    "How does it detect an incident? It polls a PromQL failure ratio every ten seconds. Three checks at or above point three open it, three below point one resolve it.",
    "Why two thresholds? Hysteresis. One threshold flaps open and closed. The gap keeps it stable.",
    "How does it find the root cause? It scores three causes per dependency from the evidence, with reasons for and against, and only calls it high confidence with a score of point seven five and a lead of point three.",
    "How does it know what changed? Every release is recorded. A release within five minutes of detection is a strong link.",
], [
    qa(120, 250, 1680, [("1", "How do you detect an incident?", "PromQL failure ratio every 10 s · 3 × ≥ 0.3 opens · 3 × &lt; 0.1 resolves."),
                        ("2", "Why two thresholds?", "Hysteresis: one threshold flaps; the gap keeps the state stable."),
                        ("3", "How do you find the root cause?", "Score 3 causes per dependency · reasons for and against · high = ≥ 0.75 and lead ≥ 0.3."),
                        ("4", "How do you know what changed?", "Every release is recorded · ≤ 5 min before detection = strong link.")]),
])

add("qa2", "Interview questions: safety", "14 · INTERVIEW Q&A", "INTERVIEW · SAFETY", "The questions about trust", [
    "Then they'll push on safety. How do you stop the robot making things worse?",
    "Answer: a pure function rulebook that escalates on any doubt, guardrails of two attempts per incident, three actions per service per hour and a sixty second cooldown, and preflight checks on live data right before acting.",
    "What if it rolls back and the problem continues? It verifies with three healthy checks within two minutes. If not, it marks the fix as failed and escalates. And it never rolls back a rollback.",
    "Why not let it act from day one? Dry run first. You compare its suggestions with what humans did, and switch to enforce only when it's earned trust.",
    "How did you test it? One hundred and eighteen unit tests. Pure functions for decisions, and injected fakes for anything that touches Docker.",
], [
    qa(120, 250, 1680, [("1", "How do you stop the robot making it worse?", "Pure rulebook · escalate on doubt · 2 attempts · 3/hour · 60 s cooldown · preflight."),
                        ("2", "Rolled back, still broken?", "Verify 3 healthy checks in 120 s · else fix_failed → human · never roll back a rollback."),
                        ("3", "Why not act from day one?", "Dry-run first, compare with humans, then enforce."),
                        ("4", "How did you test it?", "118 unit tests · pure decisions · injected fakes for Docker.")], color="red"),
])

add("qa3", "Interview questions: design", "14 · INTERVIEW Q&A", "INTERVIEW · DESIGN", "Follow-ups that test depth", [
    "And some design follow ups that test depth.",
    "Why a ratio instead of an error count? A count scales with traffic, so a fixed threshold would be wrong at night or during a sale. A ratio means the same thing at any load.",
    "Why p ninety five and not the average? Averages hide the tail, and the tail is where timeouts happen.",
    "How would this scale to a hundred services? Generate the dependency graph from traces instead of hard coding it, move to Postgres, run detection per service, and use Kubernetes rollouts as the actions.",
    "Why not use an L L M? No training data, decisions must be explainable and testable. I'd use an L L M to explain, not to decide.",
], [
    qa(120, 250, 1680, [("1", "Ratio, not count?", "A count scales with traffic; a ratio means the same at any load."),
                        ("2", "p95, not average?", "Averages hide the tail, and the tail is where timeouts live."),
                        ("3", "100 services?", "Dependency graph from traces · Postgres · per-service detection · k8s rollouts."),
                        ("4", "Why not an LLM?", "No data · must be explainable and testable · LLM explains, rules decide.")], color="violet"),
])

add("pitch", "Your 30-second pitch", "14 · PITCH", "THE PITCH", "RootLens in 30 seconds", [
    "If you get one minute to describe RootLens, say this.",
    "I built an incident response lab that does what an on call engineer does: detect, investigate, decide, act and verify.",
    "It detects failures with a PromQL ratio and hysteresis, ranks root causes from evidence with an explainable score, and links the failure to the release that caused it.",
    "A pure function rulebook decides whether to roll back, restart or escalate, with guardrails and preflight checks, and every decision is audited, including not acting.",
    "In a real run, it found a bad payment release and recovered in one minute fifty, and it's covered by one hundred and eighteen unit tests.",
], [
    card(120, 250, 1680, 600, '<div style="font:600 34px/1.6 Inter">'
         '<span data-at="1">An incident-response lab that does what an on-call engineer does: <b style="color:var(--amber)">detect → investigate → decide → act → verify</b>.</span><br><br>'
         '<span data-at="2">PromQL ratio with <b style="color:var(--red)">hysteresis</b> · <b style="color:var(--amber)">explainable</b> root-cause scores · <b style="color:var(--violet)">change correlation</b>.</span><br><br>'
         '<span data-at="3">Pure rulebook · <b style="color:var(--grn)">guardrails + preflight</b> · everything audited.</span><br><br>'
         '<span data-at="4">Real run: <b style="color:var(--grn)">1 min 50 s</b> to recover · <b>118</b> unit tests.</span></div>', "0"),
])

add("recap", "Recap", "RECAP", "RECAP", "Everything, in one screen", [
    "To recap. A tiny shop with planted bugs, watched by Prometheus and traced with Open Telemetry.",
    "A detector with hysteresis and fingerprints. An investigator that ranks causes with reasons, and links failures to releases.",
    "A pure function rulebook with guardrails, preflight checks, a single executor, verification, and an audit log that records even the decision to do nothing.",
    "The code, the screenshots and the one click demo are all on GitHub. Good luck in your interview.",
], [
    text(120, 250, 1680, '<div class="rows2">' + "".join(
        row(w, ic=ic, color=col, at=at, style="margin:0") for at, ic, w, col in [
            ("0", "🛒", "Shop with <b>planted bugs</b>", "violet"), ("0.5", "📈", "Prometheus + <b>OpenTelemetry</b>", "org"),
            ("1", "🔎", "Detector · <b>hysteresis · fingerprints</b>", "red"), ("1.5", "🧠", "Ranked causes <b>with reasons</b>", "amber"),
            ("1.8", "🚀", "<b>What changed?</b> release links", "violet"), ("2", "📘", "Pure <b>rulebook</b> + guardrails", "blu"),
            ("2.5", "🛡️", "Preflight · executor · <b>verify</b>", "grn"), ("2.8", "📜", "Audit log, <b>even inaction</b>", "pink")]) + '</div>'),
    center(720, '<span class="fv-endcard"></span>', "3"),
], pad=(0.4, 1.6))

META = {
    "title": "RootLens Deep Dive: automated incident response, explained (interview prep)",
    "slug": "rootlens-deep-dive",
    "description": "A complete walkthrough of RootLens, an incident-response lab that detects failures, finds the root cause, links it to the release that caused it, and rolls back safely. The lab and its planted bugs, Prometheus metrics and PromQL, p95 latency, OpenTelemetry tracing with Jaeger, detection with hysteresis and fingerprints, explainable root-cause scoring and confidence, change correlation, a pure-function rulebook with guardrails, dry-run and enforce modes, preflight checks, the executor, recovery verification, the audit log, Telegram notices, a real incident end to end, 118 unit tests, deployment, honest limits, and the interview questions you should expect.",
    "tags": ["sre", "incident response", "observability", "prometheus", "opentelemetry", "python", "fastapi", "docker", "devops", "interview preparation", "system design"],
    "voice": "am_michael", "speed": 1.07, "lineGap": 0.2, "captions": True,
    "endCard": "📘 code & demo → github.com/HemashreeVI/RootLens",
    "thumbnail": "title@5", "endHold": 0.6,
    "pronounce": {
        "RootLens": "Root Lens", "PromQL": "prom Q L", "FastAPI": "Fast A P I", "SQLite": "S Q L ite", "OpenTelemetry": "Open Telemetry",
        "Jaeger": "yay ger", "Grafana": "Gra fana", "MTTR": "M T T R", "JSON": "jason", "LLM": "L L M", "p95": "P ninety five",
        "v1": "V one", "v2": "V two", "TOCTOU": "tock too", "Codespaces": "code spaces", "SLO": "S L O", "dry run": "dry run",
        "idempotency": "eye dem potency", "Idempotency": "Eye dem potency", "idempotent": "eye dem potent",
    },
}

if __name__ == "__main__":
    write(HERE, META, "🔎", "RootLens", S)
