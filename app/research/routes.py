from __future__ import annotations

from dataclasses import asdict

from flask import Blueprint, jsonify, request

from app.agents.research_agent import ResearchAgent

bp = Blueprint("research", __name__, url_prefix="/api/v1/research")


@bp.route("/company", methods=["POST"])
def company_research():
    payload = request.get_json() or {}
    company_name = payload.get("company_name")
    website = payload.get("website")

    try:
        from app.ai.provider import get_ai_provider

        ai = get_ai_provider()
    except Exception as exc:
        return jsonify({"error": "AI provider not configured", "details": str(exc)}), 503

    agent = ResearchAgent(ai)

    # run async operation on event loop
    import asyncio

    result = asyncio.run(agent.analyze(company_name=company_name, website=website))
    return jsonify(asdict(result))
