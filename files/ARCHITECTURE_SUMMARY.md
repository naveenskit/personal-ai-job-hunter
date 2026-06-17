# System Architecture Summary
# Personal AI Job Hunter

**Version:** 1.0.0 | **Last Updated:** Phase 0

---

## Architecture Style

**Clean Architecture** with explicit layers:

```
┌─────────────────────────────────────────────────────────────┐
│                      PRESENTATION LAYER                     │
│          Dashboard UI (Flask)  │  Telegram Bot              │
├─────────────────────────────────────────────────────────────┤
│                      APPLICATION LAYER                      │
│    Agents │ Schedulers │ Report Generators │ Exporters      │
├─────────────────────────────────────────────────────────────┤
│                       DOMAIN LAYER                          │
│    Models │ Scoring Engine │ Matching Logic │ State Machine  │
├─────────────────────────────────────────────────────────────┤
│                    INFRASTRUCTURE LAYER                     │
│   SQLite/DB │ Gemini API │ Telegram API │ File System       │
└─────────────────────────────────────────────────────────────┘
```

---

## Agent Architecture

```
                    ┌─────────────────┐
                    │  Orchestrator   │  ← APScheduler triggers
                    │     Agent       │
                    └────────┬────────┘
                             │
           ┌─────────────────┼──────────────────┐
           │                 │                  │
    ┌──────▼──────┐  ┌───────▼──────┐  ┌────────▼──────┐
    │  Discovery  │  │   Research   │  │   Matching    │
    │    Agent    │  │    Agent     │  │    Agent      │
    └──────┬──────┘  └───────┬──────┘  └────────┬──────┘
           │                 │                  │
    ┌──────▼──────┐  ┌───────▼──────┐  ┌────────▼──────┐
    │ Job Sources │  │ Company Intel│  │ Resume Match  │
    │ (APIs/RSS)  │  │ (Gemini AI)  │  │ (Gemini AI)   │
    └─────────────┘  └─────────────┘  └───────────────┘
           │
    ┌──────▼───────────────────────────────────────────┐
    │              Scoring Engine                      │
    │  resume_match + hiring_prob + location +         │
    │  freshness + company_quality + competition       │
    └──────────────────────┬───────────────────────────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
   ┌──────▼─────┐  ┌───────▼──────┐  ┌─────▼──────────┐
   │  Outreach  │  │ Application  │  │  Report +      │
   │ Generator  │  │   Tracker    │  │  Telegram Bot  │
   └────────────┘  └─────────────┘  └────────────────┘
```

---

## Component Map

| Component | Module Path | Responsibility |
|-----------|-------------|----------------|
| Orchestrator | `app/agents/orchestrator.py` | Schedules + coordinates all agents |
| Discovery Agent | `app/agents/discovery_agent.py` | Fetches jobs from sources |
| Research Agent | `app/agents/research_agent.py` | Company intel via Gemini |
| Matching Agent | `app/agents/matching_agent.py` | Resume ↔ JD scoring |
| Outreach Agent | `app/agents/outreach_agent.py` | Email + LinkedIn generation |
| Learning Agent | `app/agents/learning_agent.py` | Outcome → ranking feedback |
| Skill Gap Agent | `app/agents/skill_gap_agent.py` | Resume vs JD gap analysis |
| Scoring Engine | `app/agents/scoring_engine.py` | 6-factor opportunity score |
| DB Layer | `app/database/` | Repository pattern, SQLite |
| Telegram Bot | `app/telegram/bot.py` | Commands + daily digest |
| Scheduler | `app/scheduler/scheduler.py` | APScheduler job definitions |
| Report Engine | `app/reports/` | Weekly reports + Excel export |
| Dashboard | `app/dashboard/` | Flask UI |
| Config | `config/` | YAML + .env management |

---

## Data Flow

```
[Job Sources] ──► [Discovery Agent] ──► [Dedup Check] ──► [DB: opportunities]
                                                                    │
                                                    ┌───────────────▼───────┐
                                                    │  [Research Agent]      │
                                                    │  Gemini enrichment     │
                                                    └───────────────┬───────┘
                                                                    │
[Resume Store] ──► [Matching Agent] ◄─────────────────────────────┘
                         │
                   [Scoring Engine]
                         │
                   [DB: scored_opportunities]
                         │
          ┌──────────────┼──────────────┐
          │              │              │
   [Outreach Gen]  [Application    [Reports +
                    Tracker]        Telegram]
```

---

## AI Provider Abstraction

```python
# app/ai/provider.py - Single interface, swappable backends

class AIProvider(Protocol):
    async def complete(self, prompt: str, system: str) -> str: ...
    async def embed(self, text: str) -> list[float]: ...

class GeminiProvider(AIProvider): ...     # Default
class OpenAIProvider(AIProvider): ...     # Future
class ClaudeProvider(AIProvider): ...     # Future
```

---

## Job Source Abstraction

```python
class JobSource(Protocol):
    async def fetch(self, query: JobQuery) -> list[RawOpportunity]: ...

class LinkedInSource(JobSource): ...     # LinkedIn Jobs API
class NaukriSource(JobSource): ...       # Naukri RSS/API
class IndeedSource(JobSource): ...       # Indeed API
class GithubJobsSource(JobSource): ...   # GitHub Jobs
class CompanyCareerSource(JobSource):... # Direct career pages
class RemoteOKSource(JobSource): ...     # Remote OK API
```

---

## Scheduler Design

```
Cron Jobs:
  - Every 4h:  Discovery Agent (job fetch)
  - Every 6h:  Research Agent (company enrichment)
  - Every 12h: Matching + Scoring
  - 08:00 IST: Daily Telegram digest
  - Sunday 09:00 IST: Weekly career report
  - On demand: Outreach generation (user-triggered)
```

---

## Security Model

- All API keys in `.env` (never committed)
- `.env.example` committed with placeholder values
- SQLite WAL mode for concurrent reads
- Input sanitization on all external data
- Rate limiting on all API calls (per-provider)
- Retry with exponential backoff (max 3 retries)

---

## Migration Path: SQLite → PostgreSQL

- Repository Pattern abstracts all DB calls
- SQLAlchemy ORM (no raw SQL in business logic)
- Alembic for migrations
- Switch: change `DATABASE_URL` in `.env`
- Zero business logic changes required
