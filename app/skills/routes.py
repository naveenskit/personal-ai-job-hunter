from __future__ import annotations

from dataclasses import asdict

from flask import Blueprint, jsonify, request

from app.agents.skill_gap_agent import SkillGapAgent
from app.ai.provider import get_ai_provider

bp = Blueprint("skills", __name__, url_prefix="/api/v1/skills")


@bp.post("/analyze")
async def analyze_skill_gap():
    payload = request.get_json(force=True) or {}
    resume = payload.get("resume", "")
    jd = payload.get("job_description", "")
    if not resume or not jd:
        return (
            jsonify(
                {"success": False, "error": {"message": "resume and job_description required"}}
            ),
            400,
        )
    agent = SkillGapAgent(get_ai_provider())
    result = await agent.analyze(
        resume,
        jd,
        resume_id=payload.get("resume_id"),
        opportunity_id=payload.get("opportunity_id"),
    )
    return (
        jsonify(
            {
                "success": True,
                "data": {
                    "resume_id": result.resume_id,
                    "opportunity_id": result.opportunity_id,
                    "gaps": [asdict(g) for g in result.gaps],
                    "analyzed_at": result.analyzed_at,
                },
            }
        ),
        200,
    )
