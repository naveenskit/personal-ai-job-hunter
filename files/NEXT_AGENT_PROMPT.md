# NEXT_AGENT_PROMPT

Purpose: Short, machine-readable handoff that tells the next agent what changed, current status, blockers, and immediate next steps.

Last Updated: 2026-06-17
Current Phase: Phase 4 (Company Research) started — Phase 9 (Learning Engine) persisted; Phase 10 (Skill Gap) implemented

--SUMMARY--
- Brief: Learning Engine and Skill Gap Engine added; Application Tracker implemented earlier. All unit and integration tests pass locally (33 passed).

--COMPLETED_RECENTLY--
- Added `app/agents/skill_gap_agent.py` and `app/skills/routes.py` (POST /api/v1/skills/analyze)
- Added `app/agents/learning_agent.py` and `app/learning/routes.py` (POST /api/v1/learning/plan)
- Integration test: `tests/integration/test_skills_endpoint.py`
- Unit tests for learning and skills agents
- Registered blueprints in `main.py`
 - Persisted `LearningPlan` model and repository; integration test `tests/integration/test_learning_endpoint.py` added

- Scaffolding for Phase 4 added: `app/agents/research_agent.py`, `app/research/routes.py`, and tests.

--BLOCKERS--
- None blocking CI; local pytest warns about pytest cache permissions on this machine (use `--basetemp` if needed).

--NEXT_AGENT--
Name: Company-Research-Agent (suggested)
Responsibility: Expand company enrichment: enrich company profiles (overview, tech stack, funding, competitors), add bulk import/persistence, connect enrichment to `companies` repository, and provide API endpoints for research.

--NEXT_STEPS (do these in order)--
1. Read `files/PROJECT_MEMORY.md` and this file to understand recent context.
2. Implement richer enrichment fields in `ResearchAgent` and persist results to `companies` table.
3. Add endpoints: `POST /api/v1/companies/import` (CSV/JSON bulk import) and `GET /api/v1/research/company?company_id=<id>` to return persisted research.
4. Add integration tests for enrichment persistence and import flows.
5. Run lint and full test-suite: `python -m ruff check .` then `python -m pytest -q --basetemp=.pytest_basetemp`.

--QUICK_RUN_COMMANDS--
- Lint: python -m ruff check .
- Tests: python -m pytest -q --basetemp=.pytest_basetemp

--NOTE--
This file MUST be updated after any substantive code change. The agent starting work should always read this file first for context and the immediate next steps.
