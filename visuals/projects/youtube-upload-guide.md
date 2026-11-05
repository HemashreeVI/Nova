# YouTube upload guide: SeatLock, RootLens, TriageIQ
For each video: upload the MP4, paste the title, description and tags, set the thumbnail, and add the captions file under Subtitles. Files are in each project's `out/` folder.

---

## seatlock

Files: `seatlock/out/seatlock.mp4`, `seatlock/out/thumbnail.png`, `seatlock/out/captions.srt`
### Title (100/100)

```
How I Built a Ticket Booking System That Never Double-Books a Seat | Java, Spring Boot, Redis, Kafka
```
### Description

```
Thousands of buyers. One seat. Zero double-bookings.

SeatLock is a ticket-booking backend built for the moment a big show goes on sale. In this video I explain the whole system: the double-booking race, why an if-check can't fix it, and the three layers that make sure exactly one buyer wins.

What's inside:
🔒 Three locking strategies: pessimistic (SELECT … FOR UPDATE), optimistic (version check) and a Redis lock
🧵 Deadlock prevention by always locking seats in sorted order
🛡️ @Version fencing and a PostgreSQL partial unique index as backups
🧪 Proof: 200 threads race for one seat, exactly 1 wins, 199 get 409 Conflict; a k6 load test with 500 users finds zero double-bookings
💳 Payments as a Kafka saga with a transactional outbox and idempotent consumers
🚦 A Redis waiting room, Lua rate limiting and a live seat map over Server-Sent Events
⚖️ Honest trade-offs and limits

🌐 Live demo: https://seatlock-7ba6.onrender.com
💻 Code: https://github.com/HemashreeVI/SeatLock
🗂️ Portfolio: https://hemashreevi.github.io

Chapters
0:00 SeatLock: overview
0:19 The problem: race conditions
0:42 Architecture
1:15 Seat holds & expiry
1:38 Layer 1: locking strategies
2:20 Avoiding deadlocks
2:41 Layers 2 & 3: version + unique index
3:11 Proving it: tests & load tests
4:00 Payments: Kafka saga + outbox
4:45 Handling the crowd
5:16 Demo
5:35 Observability
5:51 Trade-offs & limits

Built and explained by Hemashree V. I.

#SystemDesign #Java #SpringBoot
```
### Tags (about 365/500 characters)

```
system design, java spring boot project, spring boot, ticket booking system, concurrency, race condition, double booking, database locking, pessimistic locking, optimistic locking, redis distributed lock, kafka saga pattern, transactional outbox, postgresql, backend project, java backend, k6 load testing, testcontainers, software engineering interview, SeatLock
```

---

## rootlens

Files: `rootlens/out/rootlens.mp4`, `rootlens/out/thumbnail.png`, `rootlens/out/captions.srt`
### Title (96/100)

```
I Built a System That Fixes Production Outages by Itself | RootLens, Python, Prometheus, FastAPI
```
### Description

```
A bad release goes out at night and half of all orders start failing. RootLens notices, works out why, and rolls the release back, but only within strict limits, and it asks a human when it isn't sure.

In this video I explain the whole incident-response loop: detect, investigate, decide, act and verify, and show a real incident resolved in under two minutes.

What's inside:
🏗️ An 8-container lab: three FastAPI microservices, Prometheus, Grafana, Jaeger (OpenTelemetry), a detector and a controller
🚨 Detect: hysteresis on the order failure ratio so incidents never flicker
🔍 Investigate: scoring every possible cause from the evidence, with a confidence rule
🕐 Change correlation: "what changed?" and never rolling back a rollback
📜 Decide: a pure-function rulebook with rate limits and an allowlist
🔁 Act and verify: preflight checks, automatic rollback, recovery checks and an audit log
✅ 118 unit tests in GitHub Actions
⚖️ Honest limits

💻 Code: https://github.com/HemashreeVI/rootlens
🗂️ Portfolio: https://hemashreevi.github.io

Chapters
0:00 RootLens: overview
0:18 The problem
0:43 Architecture: 8 containers
1:32 Step 1: Detect
2:11 Step 2: Investigate
2:48 What changed? Change correlation
3:09 Step 3: Decide (the rulebook)
3:49 Steps 4 & 5: Act and verify
4:32 Demo: a real incident
5:09 Tests & CI
5:27 Honest limits
5:53 Recap

Built and explained by Hemashree V. I.

#SRE #DevOps #Python
```
### Tags (about 322/500 characters)

```
site reliability engineering, SRE project, incident response, root cause analysis, AIOps, self healing systems, automatic rollback, microservices, fastapi, python project, prometheus, grafana, opentelemetry, jaeger, observability, docker compose, devops project, backend project, software engineering interview, RootLens
```

---

## triageiq

Files: `triageiq/out/triageiq.mp4`, `triageiq/out/thumbnail.png`, `triageiq/out/captions.srt`
### Title (89/100)

```
I Built an AI Support Inbox That Runs Fully On My Laptop | Kafka, Local LLM, RAG, FastAPI
```
### Description

```
Every support email, read, ranked and answered in seconds, and nothing is sent until a human approves.

TriageIQ is an event-driven AI support inbox. It classifies every email by category, priority and mood with a local LLM, drafts a reply grounded in tickets you've already solved, and keeps customer text on your own machine.

What's inside:
📨 An event-driven pipeline: IMAP → Kafka → classifier + RAG → Kafka → live console → SMTP
🧠 Classification with Qwen 2.5 3B in Ollama, temperature 0 and a JSON schema
🛟 A safe fallback when the model is down or answers outside the rules
📚 RAG over solved tickets with nomic-embed-text and Qdrant (top 3, cosine, 0.55 threshold)
✍️ Grounded replies that may only use facts from past answers
🧑 Human in the loop: approve, edit, write your own or escalate
🛡️ Hardened for a real inbox: de-duplication, auto-reply loop protection, rate limits, sign-in lockout
⚖️ Honest limits

💻 Code: https://github.com/HemashreeVI/TriageIQ
🗂️ Portfolio: https://hemashreevi.github.io

Chapters
0:00 TriageIQ: overview
0:26 The problem
0:48 The pipeline
1:19 Why Kafka
1:38 Step 1: Classify with a local LLM
2:02 Never trust the model blindly
2:23 Step 2: RAG over past tickets
2:53 Grounded replies
3:13 Step 3: Human in the loop
3:36 Hardened for a real inbox
4:07 Demo: the console
4:32 Honest limits
5:00 Recap

Built and explained by Hemashree V. I.

#AI #LLM #RAG
```
### Tags (about 333/500 characters)

```
RAG project, retrieval augmented generation, local LLM, ollama, qwen, llm project, ai project, kafka project, event driven architecture, qdrant, vector database, fastapi, python project, customer support automation, ticket classification, human in the loop, ai engineering, backend project, software engineering interview, TriageIQ
```
