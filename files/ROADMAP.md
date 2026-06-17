# Development Roadmap
# Personal AI Job Hunter

---

## Phase Timeline

```
PHASE 0  ✅  Planning & Architecture (this document)
PHASE 1  ⏳  Core Foundation (Week 1)
PHASE 2  ⏳  Resume Intelligence (Week 1-2)
PHASE 3  ⏳  Job Discovery Engine (Week 2)
PHASE 4  ⏳  Company Research Agent (Week 2-3)
PHASE 5  ⏳  Matching & Scoring Engine (Week 3)
PHASE 6  ⏳  Email Generator (Week 3-4)
PHASE 7  ⏳  LinkedIn Generator (Week 4)
PHASE 8  ⏳  Application Tracker (Week 4)
PHASE 9  ⏳  Learning Engine (Week 5)
PHASE 10 ⏳  Skill Gap Engine (Week 5)
PHASE 11 ⏳  Telegram Bot (Week 5-6)
PHASE 12 ⏳  Reporting System (Week 6)
PHASE 13 ⏳  Dashboard UI (Week 6-7)
PHASE 14 ⏳  Testing (Week 7)
PHASE 15 ⏳  Deployment (Week 7-8)
```

---

## Phase 0 — Planning ✅

**Deliverables:**
- [x] PRD.md
- [x] ARCHITECTURE_SUMMARY.md
- [x] DATABASE_SUMMARY.md
- [x] API_DESIGN.md
- [x] ROADMAP.md
- [x] PROJECT_MEMORY.md
- [x] Folder structure scaffolded

---

## Phase 1 — Core Foundation

**Deliverables:**
- `requirements.txt` + `pyproject.toml`
- `config/` — settings, location_preferences.yaml, sources.yaml
- `.env.example`
- `app/database/` — SQLAlchemy models, base repo, session
- `app/database/migrations/` — Alembic setup
- `app/ai/` — AIProvider abstraction + GeminiProvider
- `app/core/` — logging setup, exceptions, types
- `app/core/rate_limiter.py`
- `app/core/retry.py`
- `tests/` — pytest config, fixtures

**Key decisions:**
- SQLAlchemy 2.0 async with aiosqlite
- Pydantic v2 for all data models
- Structlog for structured logging
- APScheduler 3.x for scheduling

---

## Phase 2 — Resume Intelligence

**Deliverables:**
- `app/agents/resume_agent.py`
- `resume/` — PDF parser + text extractor
- Gemini prompt: skills + experience extraction
- Resume embedding for semantic search
- `POST /resumes` → parse → store → embed

---

## Phase 3 — Job Discovery Engine

**Deliverables:**
- `app/agents/discovery_agent.py`
- `app/sources/` — JobSource implementations
  - LinkedIn Jobs (unofficial search)
  - Naukri RSS/API
  - Indeed India
  - Company career pages (configurable list)
  - RemoteOK (for remote roles)
- Dedup engine (hash + semantic)
- `config/job_sources.yaml`

---

## Phase 4 — Company Research Agent

**Deliverables:**
- `app/agents/research_agent.py`
- Gemini-powered company profile builder
- Tech stack inference
- Hiring signal detection
- India presence scoring
- `POST /companies/import` → bulk CSV

---

## Phase 5 — Matching & Scoring Engine

**Deliverables:**
- `app/agents/matching_agent.py`
- `app/agents/scoring_engine.py`
- 6-factor score computation
- Semantic similarity (resume ↔ JD)
- Daily shortlist generation

## Matching & Scoring (Phase 5)

- Bulk matching job: periodic batch job to score all active resumes against opportunities. Implemented as `app/matching/job.py` with a trigger endpoint `POST /api/v1/match/run_bulk`.
- In-memory metrics for matching in `app/matching/metrics.py` and a simple metrics endpoint `GET /api/v1/match/metrics`.
- Matching persistence: `opportunity_scores` table stores per-resume per-opportunity scores and breakdowns.
- CI workflow added to run `ruff` and `pytest` on push: `.github/workflows/ci.yml`.


---

## Phase 6 — Email Generator

**Deliverables:**
- `app/agents/outreach_agent.py` (email)
- Gemini prompt: cold email templates
- Resume-aware personalization
- `POST /outreach/email`

---

## Phase 7 — LinkedIn Generator

**Deliverables:**
- `app/agents/outreach_agent.py` (LinkedIn)
- 300-char connection note
- InMail template
- `POST /outreach/linkedin`

---

## Phase 8 — Application Tracker

**Deliverables:**
- `app/agents/tracker_agent.py`
- State machine implementation
- Event logging
- `GET/PUT /applications`

---

## Phase 9 — Learning Engine

**Deliverables:**
- `app/agents/learning_agent.py`
- Outcome → score adjustment
- Pattern detection (what works)
- Feedback loop into scoring

---

## Phase 10 — Skill Gap Engine

**Deliverables:**
- `app/agents/skill_gap_agent.py`
- JD → required skills extraction
- Resume → current skills
- Gap classification (critical/important/nice)
- Learning resource suggestions

---

## Phase 11 — Telegram Bot

**Deliverables:**
- `app/telegram/bot.py`
- `app/telegram/handlers.py`
- All 9 commands implemented
- Daily digest scheduling (08:00 IST)
- Inline keyboards for actions

---

## Phase 12 — Reporting System

**Deliverables:**
- `app/reports/weekly_report.py`
- `app/exports/excel_exporter.py`
- Weekly career intelligence summary
- Excel export with multiple sheets

---

## Phase 13 — Dashboard UI

**Deliverables:**
- `app/dashboard/` — Flask app
- Templates: Linear-inspired design
- Real-time stats (application pipeline)
- Resume manager
- Opportunity browser with scoring

---

## Phase 14 — Testing

**Deliverables:**
- Unit tests for all agents
- Integration tests (DB + API)
- Gemini mock fixtures
- Coverage ≥ 80%

---

## Phase 15 — Deployment

**Deliverables:**
- `Dockerfile` + `docker-compose.yml`
- systemd service file (VPS)
- PM2 config (alternative)
- `deploy.sh`
- Operations runbook

---

## Technology Decisions Log

| Decision | Choice | Reason |
|----------|--------|--------|
| ORM | SQLAlchemy 2.0 async | PostgreSQL migration path |
| Validation | Pydantic v2 | Type safety + speed |
| Logging | structlog | JSON-structured, searchable |
| HTTP client | httpx (async) | Async-native |
| PDF parsing | PyMuPDF (fitz) | Best quality extraction |
| Scheduling | APScheduler 3 | Battle-tested, lightweight |
| Web framework | Flask + Flask-RESTX | Simple, hackable |
| Testing | pytest + pytest-asyncio | Async test support |
