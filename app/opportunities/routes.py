from __future__ import annotations

from typing import Any

import yaml
from flask import Blueprint, jsonify

from app.agents.discovery_service import DiscoveryService
from app.database.connection import session_scope
from app.database.repositories.opportunity_repository import OpportunityRepository
from app.sources.remoteok_source import RemoteOKSource
from config.settings import get_settings

opps_bp = Blueprint("opportunities", __name__, url_prefix="/api/v1/opportunities")


@opps_bp.get("")
async def list_opportunities() -> tuple[Any, int]:
    async with session_scope() as session:
        repo = OpportunityRepository(session)
        items = await repo.list_active(limit=200)
        return _success([_to_dict(i) for i in items])


@opps_bp.post("/search")
async def trigger_search() -> tuple[Any, int]:
    # Load configured sources and run discovery. Minimal implementation for Phase 3.
    settings = get_settings()
    cfg = yaml.safe_load(settings.job_sources_path.read_text(encoding="utf-8")) or {}
    sources_cfg = {s.get("name"): s for s in cfg.get("sources", [])}

    sources: list[object] = []
    remote_cfg = sources_cfg.get("remoteok", {})
    if remote_cfg.get("enabled"):
        sources.append(RemoteOKSource())

    try:
        async with session_scope() as session:
            svc = DiscoveryService(session)
            created = await svc.run(sources)
            return _success({"created_ids": created})
    except Exception as exc:
        return _error(str(exc))


def _to_dict(item) -> dict[str, Any]:
    return {
        "id": item.id,
        "title": item.title,
        "job_url": item.job_url,
        "source": item.source,
        "location": item.location,
        "is_active": bool(item.is_active),
        "created_at": item.created_at,
    }


def _success(data: Any, *, status_code: int = 200) -> tuple[Any, int]:
    return jsonify({"success": True, "data": data, "error": None}), status_code


def _error(message: str) -> tuple[Any, int]:
    return (jsonify({"success": False, "data": None, "error": {"message": message}}), 500)
