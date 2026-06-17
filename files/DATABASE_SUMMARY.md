# Database Schema Summary
# Personal AI Job Hunter

**Version:** 1.0.0 | **Engine:** SQLite (PostgreSQL-ready)

---

## Schema Overview

```
resumes ──────────────────────────────────┐
                                          │
companies ◄─── opportunities ◄────────── │
                    │                     │
                    ├── opportunity_scores│
                    │                     │
                    └── applications ─────┘
                              │
                        ┌─────┴──────┐
                        │            │
                  outreach_messages  application_events
                  
skill_gaps (linked to resumes + opportunities)
weekly_reports
telegram_subscriptions
```

---

## Tables

### `resumes`
```sql
CREATE TABLE resumes (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT NOT NULL,               -- "SWE Intern v2", "Backend Focus"
    file_path       TEXT NOT NULL,               -- /resume/swe_intern_v2.pdf
    file_hash       TEXT NOT NULL UNIQUE,        -- SHA256 for change detection
    role_tags       TEXT NOT NULL DEFAULT '[]',  -- JSON array: ["intern","backend"]
    raw_text        TEXT,                        -- Extracted plain text
    parsed_data     TEXT NOT NULL DEFAULT '{}',  -- JSON: skills, projects, experience
    embedding       BLOB,                        -- Vector for semantic matching
    is_active       INTEGER NOT NULL DEFAULT 1,  -- 1 = primary resume
    created_at      TEXT NOT NULL,
    updated_at      TEXT NOT NULL
);
```

### `companies`
```sql
CREATE TABLE companies (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT NOT NULL,
    domain          TEXT,
    website         TEXT,
    linkedin_url    TEXT,
    hq_location     TEXT,
    india_presence  INTEGER DEFAULT 0,           -- boolean
    company_type    TEXT,                        -- "startup","unicorn","mnc","product","saas"
    employee_count  TEXT,                        -- "1-50","51-200","201-1000","1000+"
    funding_stage   TEXT,                        -- "bootstrapped","series-a",...
    tech_stack      TEXT DEFAULT '[]',           -- JSON array
    culture_tags    TEXT DEFAULT '[]',           -- JSON array
    quality_score   REAL DEFAULT 0.0,            -- 0-100, computed
    research_data   TEXT DEFAULT '{}',           -- Full Gemini research JSON
    last_researched TEXT,
    created_at      TEXT NOT NULL,
    updated_at      TEXT NOT NULL
);
CREATE UNIQUE INDEX idx_companies_domain ON companies(domain);
```

### `opportunities`
```sql
CREATE TABLE opportunities (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id      INTEGER REFERENCES companies(id),
    title           TEXT NOT NULL,
    role_type       TEXT NOT NULL,               -- "intern","new_grad","associate"
    location        TEXT NOT NULL,               -- "Bengaluru, India"
    location_type   TEXT NOT NULL,               -- "onsite","remote","hybrid"
    country         TEXT NOT NULL DEFAULT 'India',
    job_url         TEXT NOT NULL UNIQUE,
    source          TEXT NOT NULL,               -- "linkedin","naukri","company_site"
    description     TEXT,
    requirements    TEXT DEFAULT '[]',           -- JSON array of skills/requirements
    content_hash    TEXT NOT NULL UNIQUE,        -- SHA256 of title+company+location
    posted_date     TEXT,
    deadline        TEXT,
    stipend_min     INTEGER,                     -- monthly INR
    stipend_max     INTEGER,
    duration_months INTEGER,                     -- for internships
    is_active       INTEGER NOT NULL DEFAULT 1,
    created_at      TEXT NOT NULL,
    updated_at      TEXT NOT NULL
);
CREATE INDEX idx_opp_company ON opportunities(company_id);
CREATE INDEX idx_opp_role_type ON opportunities(role_type);
CREATE INDEX idx_opp_country ON opportunities(country);
CREATE INDEX idx_opp_posted ON opportunities(posted_date);
```

### `opportunity_scores`
```sql
CREATE TABLE opportunity_scores (
    id                   INTEGER PRIMARY KEY AUTOINCREMENT,
    opportunity_id       INTEGER NOT NULL REFERENCES opportunities(id),
    resume_id            INTEGER NOT NULL REFERENCES resumes(id),
    total_score          REAL NOT NULL,          -- 0-100
    score_band           TEXT NOT NULL,          -- "Dream Match","Excellent",...
    resume_match         REAL NOT NULL,          -- component scores
    hiring_probability   REAL NOT NULL,
    location_preference  REAL NOT NULL,
    freshness            REAL NOT NULL,
    company_quality      REAL NOT NULL,
    competition_estimate REAL NOT NULL,
    reasoning            TEXT,                  -- Gemini explanation
    scored_at            TEXT NOT NULL,
    UNIQUE(opportunity_id, resume_id)
);
CREATE INDEX idx_scores_total ON opportunity_scores(total_score DESC);
```

### `applications`
```sql
CREATE TABLE applications (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    opportunity_id    INTEGER NOT NULL REFERENCES opportunities(id),
    resume_id         INTEGER NOT NULL REFERENCES resumes(id),
    status            TEXT NOT NULL DEFAULT 'DISCOVERED',
    -- States: DISCOVERED|RESEARCHED|MATCHED|OUTREACH_SENT|APPLIED|
    --         ACKNOWLEDGED|INTERVIEWING|OFFERED|REJECTED|GHOSTED|WITHDRAWN
    applied_date      TEXT,
    response_date     TEXT,
    offer_date        TEXT,
    notes             TEXT,
    priority          INTEGER DEFAULT 5,         -- 1-10
    source            TEXT,                      -- how discovered
    referral_contact  TEXT,
    created_at        TEXT NOT NULL,
    updated_at        TEXT NOT NULL,
    UNIQUE(opportunity_id, resume_id)
);
CREATE INDEX idx_apps_status ON applications(status);
CREATE INDEX idx_apps_applied_date ON applications(applied_date);
```

### `application_events`
```sql
CREATE TABLE application_events (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    application_id  INTEGER NOT NULL REFERENCES applications(id),
    event_type      TEXT NOT NULL,               -- "status_changed","email_sent",...
    from_status     TEXT,
    to_status       TEXT,
    details         TEXT DEFAULT '{}',           -- JSON
    created_at      TEXT NOT NULL
);
```

### `outreach_messages`
```sql
CREATE TABLE outreach_messages (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    application_id  INTEGER NOT NULL REFERENCES applications(id),
    message_type    TEXT NOT NULL,               -- "cold_email","linkedin_note","inmail"
    recipient_name  TEXT,
    recipient_email TEXT,
    recipient_title TEXT,
    subject         TEXT,
    body            TEXT NOT NULL,
    is_sent         INTEGER DEFAULT 0,
    sent_at         TEXT,
    created_at      TEXT NOT NULL
);
```

### `skill_gaps`
```sql
CREATE TABLE skill_gaps (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    resume_id       INTEGER NOT NULL REFERENCES resumes(id),
    opportunity_id  INTEGER REFERENCES opportunities(id),   -- NULL = aggregate
    skill           TEXT NOT NULL,
    gap_type        TEXT NOT NULL,               -- "missing","weak","outdated"
    importance      TEXT NOT NULL,               -- "critical","important","nice"
    resources       TEXT DEFAULT '[]',           -- JSON: learning resources
    created_at      TEXT NOT NULL,
    UNIQUE(resume_id, opportunity_id, skill)
);
```

### `weekly_reports`
```sql
CREATE TABLE weekly_reports (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    week_start      TEXT NOT NULL UNIQUE,
    report_data     TEXT NOT NULL,               -- JSON: full report
    telegram_sent   INTEGER DEFAULT 0,
    file_path       TEXT,                        -- exported report path
    created_at      TEXT NOT NULL
);
```

### `telegram_subscriptions`
```sql
CREATE TABLE telegram_subscriptions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id         TEXT NOT NULL UNIQUE,
    is_active       INTEGER DEFAULT 1,
    digest_time     TEXT DEFAULT '08:00',        -- IST
    created_at      TEXT NOT NULL
);
```

---

## Repository Pattern

```python
# app/database/repositories/
base_repository.py          # BaseRepository[T]
resume_repository.py        # ResumeRepository
company_repository.py       # CompanyRepository  
opportunity_repository.py   # OpportunityRepository
score_repository.py         # ScoreRepository
application_repository.py   # ApplicationRepository
outreach_repository.py      # OutreachRepository
skill_gap_repository.py     # SkillGapRepository
report_repository.py        # ReportRepository
```

---

## Migration Strategy

**Phase 1 (SQLite):**
- SQLAlchemy ORM models in `app/database/models.py`
- Alembic for schema versioning

**Phase 2 (PostgreSQL migration):**
```bash
# Change in .env:
DATABASE_URL=postgresql://user:pass@host/dbname
# Run: alembic upgrade head
```
Zero code changes in business logic.
