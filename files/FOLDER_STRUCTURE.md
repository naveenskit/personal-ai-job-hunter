# Folder Structure
# Personal AI Job Hunter

```
ai-job-hunter/
│
├── .env                          ← Secrets (never commit)
├── .env.example                  ← Template (committed)
├── .gitignore
├── README.md
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
├── main.py                       ← Entry point
│
├── config/
│   ├── settings.py               ← Pydantic Settings (loads .env)
│   ├── location_preferences.yaml ← Editable location config
│   ├── role_preferences.yaml     ← Target roles config
│   ├── job_sources.yaml          ← Source configs (APIs, RSS)
│   └── scoring_weights.yaml      ← Score formula weights
│
├── app/
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── logging.py            ← structlog setup
│   │   ├── exceptions.py         ← Custom exception hierarchy
│   │   ├── types.py              ← Shared type aliases
│   │   ├── rate_limiter.py       ← Token bucket rate limiter
│   │   └── retry.py              ← Exponential backoff decorator
│   │
│   ├── ai/
│   │   ├── __init__.py
│   │   ├── provider.py           ← AIProvider Protocol
│   │   ├── gemini_provider.py    ← Gemini implementation
│   │   ├── openai_provider.py    ← OpenAI (future)
│   │   └── prompts/
│   │       ├── resume_parser.txt
│   │       ├── company_research.txt
│   │       ├── job_matching.txt
│   │       ├── cold_email.txt
│   │       ├── linkedin_note.txt
│   │       ├── skill_gap.txt
│   │       └── weekly_report.txt
│   │
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py         ← SQLAlchemy engine + session factory
│   │   ├── models.py             ← All ORM models
│   │   ├── base_repository.py    ← Generic BaseRepository[T]
│   │   └── repositories/
│   │       ├── __init__.py
│   │       ├── resume_repository.py
│   │       ├── company_repository.py
│   │       ├── opportunity_repository.py
│   │       ├── score_repository.py
│   │       ├── application_repository.py
│   │       ├── outreach_repository.py
│   │       ├── skill_gap_repository.py
│   │       └── report_repository.py
│   │
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base_agent.py         ← Abstract BaseAgent
│   │   ├── orchestrator.py       ← Coordinates all agents
│   │   ├── discovery_agent.py    ← Job discovery
│   │   ├── research_agent.py     ← Company intelligence
│   │   ├── matching_agent.py     ← Resume ↔ JD matching
│   │   ├── scoring_engine.py     ← 6-factor scorer
│   │   ├── outreach_agent.py     ← Email + LinkedIn generation
│   │   ├── tracker_agent.py      ← Application state machine
│   │   ├── learning_agent.py     ← Outcome feedback loop
│   │   └── skill_gap_agent.py    ← Gap analysis
│   │
│   ├── sources/
│   │   ├── __init__.py
│   │   ├── base_source.py        ← JobSource Protocol
│   │   ├── linkedin_source.py
│   │   ├── naukri_source.py
│   │   ├── indeed_source.py
│   │   ├── remoteok_source.py
│   │   └── company_career_source.py
│   │
│   ├── scheduler/
│   │   ├── __init__.py
│   │   └── scheduler.py          ← APScheduler job definitions
│   │
│   ├── telegram/
│   │   ├── __init__.py
│   │   ├── bot.py                ← Bot initialization
│   │   ├── handlers.py           ← Command handlers
│   │   └── formatters.py         ← Message formatting helpers
│   │
│   ├── reports/
│   │   ├── __init__.py
│   │   ├── weekly_report.py      ← Weekly career report generator
│   │   └── templates/
│   │       └── weekly_report.md.j2
│   │
│   ├── exports/
│   │   ├── __init__.py
│   │   └── excel_exporter.py     ← openpyxl export
│   │
│   └── dashboard/
│       ├── __init__.py
│       ├── app.py                ← Flask application factory
│       ├── routes/
│       │   ├── __init__.py
│       │   ├── opportunities.py
│       │   ├── applications.py
│       │   ├── companies.py
│       │   ├── resumes.py
│       │   ├── agents.py
│       │   └── config.py
│       ├── templates/
│       │   ├── base.html
│       │   ├── dashboard.html
│       │   ├── opportunities.html
│       │   ├── applications.html
│       │   ├── companies.html
│       │   └── resumes.html
│       └── static/
│           ├── css/
│           │   └── app.css
│           └── js/
│               └── app.js
│
├── resume/
│   └── .gitkeep                  ← Place your PDFs here
│
├── logs/
│   └── .gitkeep
│
├── exports/
│   └── .gitkeep
│
├── tests/
│   ├── conftest.py               ← Shared fixtures
│   ├── unit/
│   │   ├── test_scoring_engine.py
│   │   ├── test_resume_parser.py
│   │   ├── test_dedup.py
│   │   └── test_outreach.py
│   └── integration/
│       ├── test_db_repositories.py
│       ├── test_discovery_agent.py
│       └── test_api_endpoints.py
│
└── docs/
    ├── PRD.md
    ├── ARCHITECTURE_SUMMARY.md
    ├── DATABASE_SUMMARY.md
    ├── API_DESIGN.md
    ├── FOLDER_STRUCTURE.md
    ├── ROADMAP.md
    └── PROJECT_MEMORY.md
```
