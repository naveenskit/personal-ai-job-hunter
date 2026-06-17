from __future__ import annotations

from typing import Any

from flask import Blueprint, jsonify, request

from app.agents.tracker_agent import TrackerAgent
from app.core.types import ApplicationStatus
from app.database.connection import session_scope
from app.database.repositories.application_repository import ApplicationRepository

applications_bp = Blueprint("applications", __name__, url_prefix="/api/v1/applications")


@applications_bp.post("")
async def create_application() -> tuple[Any, int]:
    try:
        payload = request.get_json(force=True)
        opportunity_id = int(payload["opportunity_id"])
        resume_id = int(payload["resume_id"])
        source = payload.get("source")
        async with session_scope() as session:
            agent = TrackerAgent(session)
            app = await agent.create_application(opportunity_id, resume_id, source)
            return jsonify({"success": True, "data": {"id": app.id}, "error": None}), 200
    except Exception as exc:
        return jsonify({"success": False, "data": None, "error": {"message": str(exc)}}), 400


@applications_bp.get("")
async def list_applications() -> tuple[Any, int]:
    status = request.args.get("status")
    async with session_scope() as session:
        repo = ApplicationRepository(session)
        items = await repo.list_by_status(status or ApplicationStatus.DISCOVERED.value)
        data = [
            {
                "id": i.id,
                "opportunity_id": i.opportunity_id,
                "resume_id": i.resume_id,
                "status": i.status,
                "created_at": i.created_at,
                "updated_at": i.updated_at,
            }
            for i in items
        ]
        return jsonify({"success": True, "data": data, "error": None}), 200


@applications_bp.put("/<int:app_id>/status")
async def update_status(app_id: int) -> tuple[Any, int]:
    try:
        payload = request.get_json(force=True)
        new_status = payload.get("status")
        if new_status is None:
            return (
                jsonify({"success": False, "data": None, "error": {"message": "status required"}}),
                400,
            )
        async with session_scope() as session:
            agent = TrackerAgent(session)
            updated = await agent.transition(
                app_id, new_status, details=payload.get("details", "{}")
            )
            return (
                jsonify(
                    {
                        "success": True,
                        "data": {"id": updated.id, "status": updated.status},
                        "error": None,
                    }
                ),
                200,
            )
    except Exception as exc:
        return jsonify({"success": False, "data": None, "error": {"message": str(exc)}}), 400
