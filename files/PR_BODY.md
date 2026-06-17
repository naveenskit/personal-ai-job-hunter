Consolidate outreach agent and routes

This PR consolidates duplicate `OutreachAgent` implementations, unifies the outreach routes, and adds unit tests for the outreach generation logic.

Summary of changes:
- Consolidated `app/agents/outreach_agent.py` into a single DB-backed agent and AI generator.
- Unified routes in `app/outreach/routes.py` for templates, send, email, and linkedin endpoints.
- Added `tests/unit/test_outreach_agent.py` to validate email generation.
- Fixed lint issues reported by `ruff` and applied formatting.

Verification:
- `python -m ruff check .` passes locally.
- `python -m pytest -q` passes locally (35 tests).

Notes:
- If the PR build shows failures related to environment, ensure async Flask dependencies are installed (Flask[async], asgiref).

Checklist:
- [ ] Reviewed by at least one backend maintainer
- [ ] CI passes
- [ ] Merge when ready
