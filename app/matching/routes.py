from __future__ import annotations

from typing import Any

from flask import Blueprint, jsonify, request
from sqlalchemy import select

from app.agents.matching_agent import MatchingAgent
from app.database.connection import session_scope
from app.database.models import Opportunity, OpportunityScore
from app.matching import metrics
from app.matching.job import run_bulk_matching

bp = Blueprint("matching", __name__, url_prefix="/api/v1/match")


@bp.post("/resume/<int:resume_id>/opportunity/<int:opp_id>")
async def match_resume_opportunity(resume_id: int, opp_id: int) -> tuple[Any, int]:
    # resolve AI provider at call time to allow monkeypatching in tests
    try:
        from app.ai.provider import get_ai_provider

        ai = get_ai_provider()
    except Exception:
        return (
            jsonify(
                {"success": False, "data": None, "error": {"message": "AI provider not configured"}}
            ),
            503,
        )

    async with session_scope() as session:
        agent = MatchingAgent(session, ai)
        score = await agent.match_resume_to_opportunity(resume_id, opp_id)
        return jsonify({"success": True, "data": {"score": score}, "error": None}), 200


@bp.get("/resume/<int:resume_id>")
async def top_matches_for_resume(resume_id: int) -> tuple[object, int]:
    """Return top matching opportunities for a resume based on stored scores."""
    limit = int(request.args.get("limit", 10))
    async with session_scope() as session:
        stmt = (
            select(OpportunityScore, Opportunity)
            .join(Opportunity, Opportunity.id == OpportunityScore.opportunity_id)
            .where(OpportunityScore.resume_id == resume_id)
            .order_by(OpportunityScore.total_score.desc())
            .limit(limit)
        )
        res = await session.execute(stmt)
        rows = res.all()
        items = []
        for score_rec, opp in rows:
            items.append(
                {
                    "opportunity_id": opp.id,
                    "title": opp.title,
                    "company_id": opp.company_id,
                    "location": opp.location,
                    "job_url": opp.job_url,
                    "score": score_rec.total_score,
                    "scored_at": score_rec.scored_at,
                }
            )
        return jsonify({"success": True, "data": {"matches": items}, "error": None}), 200


@bp.post("/run_bulk")
async def trigger_bulk_matching() -> tuple[object, int]:
    try:
        from app.ai.provider import get_ai_provider

        ai = get_ai_provider()
    except Exception:
        return (
            jsonify(
                {
                    "success": False,
                    "data": None,
                    "error": {"message": "AI provider not configured"},
                }
            ),
            503,
        )

    async with session_scope() as session:
        from app.database.repositories.job_run_repository import JobRunRepository

        jr = JobRunRepository(session)
        run = await jr.create_run("bulk_matching")
        metrics.inc_counter("bulk_runs")
        processed, scored = await run_bulk_matching(session, ai, job_run_id=run.id)
        metrics.inc_counter("matches_scored", scored)
        return (
            jsonify(
                {
                    "success": True,
                    "data": {
                        "run_id": run.id,
                        "resumes_processed": processed,
                        "scores_created": scored,
                    },
                    "error": None,
                }
            ),
            200,
        )


@bp.get("/metrics")
def metrics_endpoint():
    # expose simple in-memory metrics or Prometheus if available
    try:
        from prometheus_client import CollectorRegistry, generate_latest

        registry = CollectorRegistry()
        # not registering dynamic counters here; fall back to text
        return generate_latest(registry), 200, {"Content-Type": "text/plain; version=0.0.4"}
    except Exception:
        return jsonify({"success": True, "data": metrics.get_metrics(), "error": None}), 200


@bp.get("/status")
async def job_status() -> tuple[object, int]:
    return jsonify({"success": True, "data": metrics.get_job_status(), "error": None}), 200


@bp.get("/history")
async def job_history() -> tuple[object, int]:
    async with session_scope() as session:
        from app.database.repositories.job_run_repository import JobRunRepository

        jr = JobRunRepository(session)
        runs = await jr.get_recent()
        out = [
            {
                "id": r.id,
                "job_name": r.job_name,
                "status": r.status,
                "started_at": r.started_at,
                "finished_at": r.finished_at,
                "processed": r.processed_count,
                "scored": r.scored_count,
                "error": r.error,
            }
            for r in runs
        ]
        return jsonify({"success": True, "data": out, "error": None}), 200


@bp.post("/cancel/<int:run_id>")
async def cancel_run(run_id: int) -> tuple[object, int]:
    async with session_scope() as session:
        from app.database.repositories.job_run_repository import JobRunRepository

        jr = JobRunRepository(session)
        await jr.request_cancel(run_id)
        return (
            jsonify(
                {"success": True, "data": {"run_id": run_id, "canceled": True}, "error": None}
            ),
            200,
        )
