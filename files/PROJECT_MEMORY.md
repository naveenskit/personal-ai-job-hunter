# PROJECT_MEMORY.md
# Personal AI Job Hunter - Source of Truth

**Version:** 0.3.0 | **Current Phase:** 5 Complete -> Ready for Phase 6  
**Last Updated:** 2026-06-17 — Phases 3–5 implemented and verified

---

## Completed Phases

### Phase 0 - Planning (COMPLETE)
Planning documents generated in `files/`:
- `PRD.md` - Requirements, scoring model, state machine, constraints
- `ARCHITECTURE_SUMMARY.md` - Layered architecture, agent graph, data flow, AI abstraction
- `DATABASE_SUMMARY.md` - Full schema, repository pattern, migration path
- `API_DESIGN.md` - REST endpoints, Telegram commands, service contracts
- `FOLDER_STRUCTURE.md` - Complete file tree
- `ROADMAP.md` - 15-phase plan with deliverables per phase
- `PROJECT_MEMORY.md` - This file

### Phase 1 - Core Foundation (COMPLETE)
Implemented foundation files at the project root:
- Dependency and tool config: `requirements.txt`, `requirements-dev.txt`, `pyproject.toml`
- Runtime config: `.env.example`, `.gitignore`, `config/settings.py`, YAML preference files
- Core utilities: structured logging, exceptions, shared types, retry, rate limiter
- Database layer: SQLAlchemy async models, connection/session helpers, Alembic scaffold
- Repositories: resume, company, opportunity, score, application, outreach, skill gap, report
- AI layer: provider protocol/factory and Gemini provider
- Entry point: `main.py` with health endpoint and DB bootstrap
- Tests: pytest config and foundation repository/status tests

### Phase 2 - Resume Intelligence (COMPLETE)
Implemented resume ingestion and parsing:
- Resume text extraction for `.pdf`, `.txt`, and `.md`
- `ParsedResume` schema and Gemini-backed `ResumeParser`
- Resume parser prompt at `app/ai/prompts/resume_parser.txt`
- Embedding pack/unpack helpers for storing vectors in SQLite BLOB fields
- `ResumeIngestionService` for ingesting, deduplicating, parsing, embedding, and reanalyzing resumes
- Resume repository helpers for active resume, tag lookup, and primary resume
- Flask resume blueprint for list/detail/upload-by-path/reanalyze routes
- Offline tests with a fake AI provider

---

## Pending Phases

| Phase | Name | Status |
|-------|------|--------|
| 1 | Core Foundation | COMPLETE |
| 2 | Resume Intelligence | COMPLETE |
| 3 | Job Discovery Engine | COMPLETE |
| 4 | Company Research Agent | COMPLETE |
| 5 | Matching & Scoring Engine | COMPLETE |
| 6 | Email Generator | Pending |
| 7 | LinkedIn Generator | Pending |
| 8 | Application Tracker | Pending |
| 9 | Learning Engine | Pending |
| 10 | Skill Gap Engine | Pending |
| 11 | Telegram Bot | Pending |
| 12 | Reporting System | Pending |
| 13 | Dashboard UI | Pending |
| 14 | Testing | Pending |
| 15 | Deployment | Pending |

---

## Architecture Decisions

| ID | Decision | Rationale |
|----|----------|-----------|
| AD-01 | SQLAlchemy 2.0 async + aiosqlite | PostgreSQL-ready, zero code change to migrate |
| AD-02 | Pydantic v2 for settings and future data models | Type safety, validation, JSON serialization |
| AD-03 | structlog for logging | JSON-structured, machine-parseable, per-module |
| AD-04 | AIProvider Protocol abstraction | Swap Gemini -> OpenAI -> Claude without changing agents |
| AD-05 | JobSource Protocol abstraction | Add new sources without modifying discovery agent |
| AD-06 | Repository Pattern for all DB ops | Testable, no raw SQL in business logic |
| AD-07 | httpx for HTTP (async) | Async-native |
| AD-08 | PyMuPDF for PDF parsing | Good text extraction quality |
| AD-09 | APScheduler 3.x | Lightweight, in-process scheduler |
| AD-10 | Flask + Flask-RESTX for API/UI | Simple, hackable, no async overhead for UI |
| AD-11 | Gemini API primary, OpenAI/Claude future | Provider abstraction handles this |
| AD-12 | Content hash for dedup | SHA256(title + company + location) supports fast exact dedup |

---

## Database Schema

Tables implemented: `resumes`, `companies`, `opportunities`, `opportunity_scores`, `applications`, `application_events`, `outreach_messages`, `skill_gaps`, `weekly_reports`, `telegram_subscriptions`.

Full DDL remains in `files/DATABASE_SUMMARY.md`.

---

## API Contracts

### AIProvider Protocol
```python
async def complete(prompt: str, system: str, temperature: float, max_tokens: int) -> str
async def embed(text: str) -> list[float]
```

### JobSource Protocol
```python
async def fetch(query: JobQuery, limit: int) -> list[RawOpportunity]
async def health_check() -> bool
```

### BaseAgent Protocol
```python
async def run() -> AgentResult
async def health_check() -> bool
```

---

## Scoring Formula

```text
Score = resume_match(0.35) + hiring_probability(0.20)
      + location_preference(0.15) + freshness(0.15)
      + company_quality(0.10) + competition_estimate(0.05)
```

Bands: 95-100 Dream | 90-94 Excellent | 80-89 Strong | 70-79 Good | <70 Low

---

## Application State Machine

```text
DISCOVERED -> RESEARCHED -> MATCHED -> OUTREACH_SENT -> APPLIED
-> ACKNOWLEDGED -> INTERVIEWING -> OFFERED / REJECTED / GHOSTED / WITHDRAWN
```

---

## Key Environment Variables

```env
GEMINI_API_KEY=
GEMINI_MODEL=gemini-1.5-flash
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
DATABASE_URL=sqlite+aiosqlite:///./data/jobhunter.db
APP_SECRET_KEY=
API_SECRET_KEY=
LOG_LEVEL=INFO
ENVIRONMENT=development
TIMEZONE=Asia/Kolkata
```

---

## Verification

Verification run: 2026-06-17

Runner: `C:\Users\navee\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`

Results:
- `python -m compileall app config tests main.py` — succeeded (no syntax errors).
- `python -m ruff check .` — 10 issues found (8 auto-fixable). Notable problems: import ordering and module-level imports (`E402`), unused imports (`F401`), and an undefined name (`F821`) in `app/agents/discovery_service.py`.
- `python -m pytest -q` — test run produced failures and environment errors: 4 failed, 19 passed, 3 warnings, 4 errors. Details:
      - Failures: several tests in `tests/unit/test_opportunities_api.py` failed because Flask async views require Flask installed with the `async` extra (or the app to be adapted to sync testing). Error message: "Install Flask with the 'async' extra in order to use async views." 
      - Errors: multiple tests raised `PermissionError` while pytest attempted to create temporary/cache directories (access denied to `C:\Users\navee\AppData\Local\Temp\pytest-of-navee` and repository `.pytest_cache`). This is an environment permission issue that blocks test runs.

Notes and next actions:
- Environment: the default shell Python at `D:\vsCode\MG\mingw64\bin\python.exe` is missing project dependencies; tests were run using the runner above.
- Suggested immediate fixes (in order):
      1. Run `ruff --fix` and review remaining lints (organize imports, remove unused imports, fix undefined names).
      2. Resolve pytest permission issue (ensure `C:\Users\navee\AppData\Local\Temp` and the repository `.pytest_cache` are writable by the test runner, or run pytest with `--basetemp` pointing to a writable folder).
      3. Install Flask with the `async` extra in the test environment (`pip install "Flask[async]"`) or adjust async view usage to be testable in current environment.

Planned next step: fix lint issues and environment blockers, then re-run the verification commands before implementing Phase 3 (Discovery Engine).

## Verification Update — 2026-06-17 (post-fixes)

- Actions taken:
      - Ran `ruff --fix` and resolved remaining import-order and unused-name issues.
      - Fixed `app/agents/discovery_agent.py` (moved `AsyncSession` and `get_settings` imports to module top and organized imports).
      - Fixed `app/agents/discovery_service.py` by importing `RawOpportunity` for type annotations.
      - Installed `Flask[async]` in the verified runtime to allow async views in tests.

- Final verification (runner: `C:\Users\navee\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`):
      - `python -m compileall app config tests main.py` — succeeded (no syntax errors).
      - `python -m ruff check .` — All checks passed after fixes.
      - `python -m pytest -q --basetemp=.pytest_basetemp` — 27 passed, 2 warnings (pytest cache directory not writable). All tests pass.

Notes:
- The repository `.pytest_cache` path still produced warnings due to permissions on this machine. Tests pass when using `--basetemp` or when cache writes are not strictly required.
- The codebase is now ready for Phase 3 development: Discovery Engine integration and additional sources.

---

## Next: Phase 3 Instructions

Build Job Discovery Engine:
1. `app/sources/base_source.py` with `JobSource` protocol and source DTOs
2. Initial compliant source implementation, starting with Remote OK
3. Discovery agent to fetch, normalize, hash, and deduplicate opportunities
4. Source configuration loading from `config/job_sources.yaml`
5. Manual discovery service or API entry point
6. Tests for normalization, content hashing, and dedup behavior

### Current Blockers (recorded)
- Lint issues detected by `ruff` (import ordering, unused imports, E402). See linter output for file hints.
- Pytest environment permission errors when creating temp/cache directories — tests may fail on this machine until permission is fixed or `--basetemp` is used.
- Flask async view runtime error in tests — either install `Flask[async]` or adapt testing approach.

Record: verification run on 2026-06-17 uncovered the above; the team will address these before Phase 3 integration.
## Next: Phase 4 Instructions

Build Company Research Agent:
1. `app/agents/research_agent.py` to support deep enrichment of company data
2. Gemini prompts for company research, culture analysis, and tech stack inference
3. Bulk company list import capabilities from CSV/JSON at `/api/v1/companies/import`
4. Automated and manual enrichment pipelines
5. Tests for company research enrichment and parsing behavior


### Current Blockers (recorded)
- Lint issues detected by `ruff` (import ordering, unused imports, E402). See linter output for file hints.
- Pytest environment permission errors when creating temp/cache directories — tests may fail on this machine until permission is fixed or `--basetemp` is used.
- Flask async view runtime error in tests — either install `Flask[async]` or adapt testing approach.

## Agent Handoff File

We maintain a short, required handoff file at [files/NEXT_AGENT_PROMPT.md](files/NEXT_AGENT_PROMPT.md#L1) that each agent MUST read before starting work. It contains:
- a concise summary of recent changes
- completed tasks and blockers
- a 3-5 step immediate next-actions list for the next agent

Policy: After any substantive change (code, routes, tests, or docs), update both `files/PROJECT_MEMORY.md` and [files/NEXT_AGENT_PROMPT.md](files/NEXT_AGENT_PROMPT.md#L1) with the current state and next steps. This is enforced by the project maintainer and automated agents.

Record: verification run on 2026-06-17 uncovered the above; the team will address these before Phase 3 integration.
