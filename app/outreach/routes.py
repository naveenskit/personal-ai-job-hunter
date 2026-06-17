from __future__ import annotations

from typing import Any

from flask import Blueprint, jsonify, request

from app.agents.linkedin_agent import LinkedinAgent
from app.agents.outreach_agent import OutreachAgent, OutreachDBAgent
from app.ai.provider import get_ai_provider
from app.database.connection import session_scope

outreach_bp = Blueprint("outreach", __name__, url_prefix="/api/v1/outreach")


@outreach_bp.get("/templates")
async def list_templates():
    templates = [
        {
            "id": 1,
            "name": "intro",
            "subject": "Hello from Job Hunter",
            "body": "Hi {name},\n\nI thought you'd be a fit at {company}.",
        }
    ]
    return jsonify({"success": True, "data": templates, "error": None}), 200


@outreach_bp.post("/send")
async def send_outreach():
    payload = await request.get_json()
    application_id = int(payload.get("application_id"))
    template_id = int(payload.get("template_id", 1))

    async with session_scope() as session:
        agent = OutreachDBAgent(session)
        try:
            res = await agent.send_outreach(application_id, template_id)
        except Exception as exc:
            return jsonify({"success": False, "data": None, "error": {"message": str(exc)}}), 400
        return jsonify({"success": True, "data": res, "error": None}), 200


@outreach_bp.post("/email")
async def generate_email() -> tuple[Any, int]:
    try:
        payload = request.get_json(force=True)
        opportunity = payload.get("opportunity")
        resume_text = payload.get("resume_text", "")
        agent = OutreachAgent(get_ai_provider())
        result = await agent.generate_email(opportunity, resume_text)
        return (
            jsonify(
                {
                    "success": True,
                    "data": {
                        "subject": result.subject,
                        "body": result.body,
                        "generated_at": result.generated_at,
                    },
                    "error": None,
                }
            ),
            200,
        )
    except Exception as exc:
        return jsonify({"success": False, "data": None, "error": {"message": str(exc)}}), 400


@outreach_bp.post("/linkedin")
async def generate_linkedin() -> tuple[Any, int]:
    try:
        payload = request.get_json(force=True)
        opportunity = payload.get("opportunity")
        resume_text = payload.get("resume_text", "")
        agent = LinkedinAgent(get_ai_provider())
        result = await agent.generate_message(opportunity, resume_text)
        return (
            jsonify(
                {
                    "success": True,
                    "data": {
                        "message": result.message,
                        "generated_at": result.generated_at,
                    },
                    "error": None,
                }
            ),
            200,
        )
    except Exception as exc:
        return jsonify({"success": False, "data": None, "error": {"message": str(exc)}}), 400
