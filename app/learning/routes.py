from __future__ import annotations

from flask import Blueprint, jsonify, request

from app.agents.learning_agent import LearningAgent

bp = Blueprint("learning", __name__, url_prefix="/api/v1/learning")


@bp.post("/plan")
async def create_learning_plan():
    payload = request.get_json(force=True) or {}
    gaps = payload.get("gaps")
    if not gaps:
        return jsonify({"success": False, "error": {"message": "gaps required"}}), 400
    from app.database.connection import session_scope

    try:
        async with session_scope() as session:
            agent = LearningAgent(session)
            saved = await agent.create_plan(
                gaps=gaps,
                resume_id=payload.get("resume_id"),
                opportunity_id=payload.get("opportunity_id"),
            )
            return (
                jsonify(
                    {"success": True, "data": {"id": saved.id, "created_at": saved.created_at}}
                ),
                201,
            )
    except Exception as exc:
        return jsonify({"success": False, "error": {"message": str(exc)}}), 500
