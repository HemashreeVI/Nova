# Naukri profile: ready to paste

Everything below comes from your resume. Each section matches a field under **Naukri → Profile**.
Fill them in this order: Naukri ranks profiles by completeness and by how well your **Key skills** and **Resume headline** match a recruiter's search.

---

## 1. Resume headline (max 250 characters)

> B.Tech CSE (Cyber-Physical Systems), VIT Chennai '27 | Python, SQL, Java | FastAPI, Spring Boot, Kafka, PostgreSQL, Docker | Data analysis, ML (PyTorch, YOLO) | Seeking Data Analyst / Backend / ML internships

Want only Data Analyst roles? Use this one instead:

> VIT Chennai CSE '27 | Aspiring Data Analyst | Python (Pandas), SQL, PostgreSQL, Excel, Grafana dashboards | Built data pipelines with Kafka & FastAPI | Open to Data Analyst internships & 2027 roles

---

## 2. Key skills (add each one as a separate chip)

Naukri matches these words exactly against recruiter searches, so spell them the common way:

`Python` · `SQL` · `Java` · `JavaScript` · `PostgreSQL` · `MySQL` · `Data Analysis` · `Pandas` · `NumPy` · `Matplotlib` · `Excel` · `FastAPI` · `Spring Boot` · `REST API` · `Apache Kafka` · `Redis` · `Docker` · `Git` · `GitHub Actions` · `Linux` · `Grafana` · `Prometheus` · `Machine Learning` · `PyTorch` · `OpenCV` · `Computer Vision` · `LLM` · `RAG`

> Only add skills you can talk about in an interview. Learn **Power BI** or **Tableau** before you add them; they're the most common skills in Data Analyst postings, and the extension will show you how often they come up.

---

## 3. IT skills (software name · version · last used · experience)

| Skill | Version | Last used | Experience |
|---|---|---|---|
| Python | 3.x | 2026 | 2 years |
| SQL / PostgreSQL | 16 | 2026 | 1 year |
| Java | 21 | 2026 | 1 year |
| Spring Boot | 3.x | 2026 | 0–1 year |
| FastAPI | – | 2026 | 1 year |
| Apache Kafka | – | 2026 | 0–1 year |
| Docker / Docker Compose | – | 2026 | 1 year |
| Redis | – | 2026 | 0–1 year |
| PyTorch | – | 2026 | 1 year |
| OpenCV | – | 2025 | 1 year |
| Git / GitHub Actions | – | 2026 | 2 years |
| Grafana / Prometheus | – | 2026 | 0–1 year |

Change the experience values if they're off; Naukri filters on them.

---

## 4. Employment

Add it as an **internship**:

- **Designation:** Research Intern
- **Company:** VIT Chennai (Prof. Pavithra)
- **Duration:** May 2025 – Jul 2025
- **Description:**
  Implemented heatmap-based human pose estimation in MMPose to detect per-joint keypoints and validated them against Kinovea motion-analysis measurements as ground truth. Visualised and analysed joint-confidence heatmaps with OpenCV and Matplotlib to find where keypoint localisation became unreliable.

---

## 5. Education

- **B.Tech, Computer Science & Engineering (Cyber-Physical Systems)**, Vellore Institute of Technology, Chennai: 2023–2027, CGPA 7.81, full time
- **Class XII**, Maharishi International Residential School: 79%
- **Class X**, Maharishi International Residential School: 89%

---

## 6. Projects (add each separately; Client = "Academic / Personal", Status = Finished)

### SeatLock: double-booking-proof ticketing backend (Oct 2026)
**Skills:** Java 21, Spring Boot, PostgreSQL, Redis, Kafka, k6
Built a ticket-booking backend that never sells a seat twice, using configurable locking (pessimistic SELECT FOR UPDATE, optimistic versioning, or Redis locks) plus a partial unique index. Verified with concurrency tests racing 200 threads for one seat and a k6 load test; a Redis-cached pre-check raised pessimistic throughput from 897 to 2,171 req/s. Payments and notifications run as a Kafka saga with a transactional outbox and idempotency keys.
**Project link:** your SeatLock GitHub / live link

### RootLens: automated incident root-cause analysis (Oct 2026)
**Skills:** Python, FastAPI, Docker, Prometheus, Grafana, OpenTelemetry
An 8-container incident-response lab: a Prometheus-based detector opens an incident in ~30 s, a root-cause investigator ranks failing dependencies by confidence using metrics (error ratio, p95 latency) and recent releases, and a policy-gated controller automatically rolled back a faulty release. 118 unit tests in GitHub Actions.
**Project link:** your RootLens GitHub / demo video

### TriageIQ: on-device AI email triage (Oct 2026)
**Skills:** Python, Kafka, Ollama (LLM), Qdrant, FastAPI, Docker
Event-driven pipeline (IMAP → Kafka → local LLM) that classifies support emails by category, priority and sentiment and drafts replies grounded in similar past tickets via RAG. Human-in-the-loop approval console with Server-Sent Events, de-duplication and rate limiting.
**Project link:** your TriageIQ GitHub / demo video

### RL-driven autonomous rover for disaster reconnaissance (2026)
**Skills:** Python, Raspberry Pi 5, BreezySLAM, YOLOv8, A*, reinforcement learning
LiDAR SLAM on a Raspberry Pi 5 to map an area in real time, overlaid with a hazard risk heatmap from a gas sensor and a YOLO camera model; a modified A* planner finds the safest exit and RL re-plans the sweep around new hazards.

> If you're targeting Data Analyst roles, also add one small data project (e.g. an EDA + SQL + dashboard on a public dataset). None of the four above is a pure analytics project, and recruiters notice.

---

## 7. Profile summary (max ~1000 characters)

> Computer Science (Cyber-Physical Systems) student at VIT Chennai, graduating in 2027, who likes turning messy systems and data into something measurable. I've built backends that hold up under load: a Spring Boot ticketing service that stays correct under 200 concurrent buyers and doubled its throughput (897 → 2,171 req/s), and a FastAPI + Prometheus lab that detects incidents, ranks root causes from metrics and rolls back faulty releases automatically. I also work with data and ML: a research internship on human pose estimation (MMPose, OpenCV, Matplotlib), an on-device LLM + RAG email triage pipeline, and a LiDAR-SLAM disaster-response rover. I'm strongest in Python, SQL and Java, and comfortable with Kafka, PostgreSQL, Redis, Docker and Grafana. Co-inventor on a patent filing for an IoT fall-risk walker. Looking for Data Analyst, Backend or ML internships and 2027 graduate roles.

---

## 8. Accomplishments

- **Online profile:** add LinkedIn, Portfolio, LeetCode and YouTube (one entry each).
- **Work sample:** GitHub links to SeatLock, RootLens and TriageIQ.
- **Patent:** "IoT Smart Walker with Sensor-Fusion Fall-Risk Prediction", Co-Inventor, Status: *Patent pending / filing in progress*, disclosure filed with IIPRD (Khurana & Khurana). Describe it in one line: a fall-risk engine fusing tilt, weight asymmetry and obstacle distance into a Dynamic Stability Reserve metric, running standalone on an Arduino Uno for under USD 30.
- **Certification:** IBM Generative AI with watsonx (Jun 2025); NUS Industry 4.0 (Jun 2025).
- **Presentation / other:** SuperAI 2025 (Singapore).

---

## 9. Career profile (sets which jobs Naukri recommends to you)

- **Desired job type:** Internship + Permanent · **Employment type:** Full time
- **Preferred roles:** Data Analyst, Business Analyst, Backend Developer, Software Engineer, ML Engineer
- **Preferred locations:** Chennai, Bengaluru, Hyderabad, Remote
- **Industry:** IT Services & Consulting, Software Product, Analytics / KPO

## 10. Languages

Tamil (native, read/write/speak) · English (fluent) · Hindi (intermediate) · Japanese (basic)

---

### Naukri tips that matter
- **Edit your profile every few days**, even just one word. Naukri ranks recently updated profiles higher in recruiter searches.
- Upload the resume PDF in **Resume → Update** as well.
- Turn on **Job alerts** with these keywords: `data analyst fresher`, `python developer fresher`, `backend developer intern`, `machine learning intern`.
