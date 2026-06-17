from pathlib import Path
from typing import Any

from flask import Blueprint, jsonify, request

from app.ai.provider import get_ai_provider
from app.core.exceptions import JobHunterError, ValidationError
from app.database.connection import session_scope
from app.database.repositories.resume_repository import ResumeRepository
from app.resumes.embeddings import unpack_embedding
from app.resumes.service import ResumeIngestionService, ResumeParseResult

resumes_bp = Blueprint("resumes", __name__, url_prefix="/api/v1/resumes")


@resumes_bp.get("")
async def list_resumes() -> tuple[Any, int]:
    async with session_scope() as session:
        repo = ResumeRepository(session)
        resumes = await repo.list(limit=200)
        return _success([_resume_to_dict(resume, include_raw=False) for resume in resumes])


@resumes_bp.get("/<int:resume_id>")
async def get_resume(resume_id: int) -> tuple[Any, int]:
    async with session_scope() as session:
        repo = ResumeRepository(session)
        resume = await repo.get(resume_id)
        if resume is None:
            return _error(ValidationError("Resume not found", details={"resume_id": resume_id}))
        return _success(_resume_to_dict(resume, include_raw=True))


@resumes_bp.post("")
async def upload_resume() -> tuple[Any, int]:
    payload = request.get_json(silent=True) or {}
    file_path = payload.get("file_path")
    if not file_path:
        return _error(ValidationError("file_path is required"))

    try:
        async with session_scope() as session:
            service = ResumeIngestionService(session, get_ai_provider())
            result = await service.ingest_file(
                Path(file_path),
                name=payload.get("name"),
                role_tags=payload.get("role_tags") or [],
                set_active=bool(payload.get("set_active", True)),
            )
            status_code = 201 if result.created else 200
            return _success(_parse_result_to_dict(result), status_code=status_code)
    except JobHunterError as exc:
        return _error(exc)


@resumes_bp.post("/<int:resume_id>/analyze")
async def analyze_resume(resume_id: int) -> tuple[Any, int]:
    try:
        async with session_scope() as session:
            service = ResumeIngestionService(session, get_ai_provider())
            result = await service.reanalyze(resume_id)
            return _success(_parse_result_to_dict(result))
    except JobHunterError as exc:
        return _error(exc)


def _parse_result_to_dict(result: ResumeParseResult) -> dict[str, Any]:
    return {
        "resume": _resume_to_dict(result.resume, include_raw=False),
        "parsed": result.parsed.model_dump(),
        "created": result.created,
    }


def _resume_to_dict(resume, *, include_raw: bool) -> dict[str, Any]:
    payload = {
        "id": resume.id,
        "name": resume.name,
        "file_path": resume.file_path,
        "file_hash": resume.file_hash,
        "role_tags": resume.role_tags,
        "parsed_data": resume.parsed_data,
        "has_embedding": bool(unpack_embedding(resume.embedding)),
        "is_active": bool(resume.is_active),
        "created_at": resume.created_at,
        "updated_at": resume.updated_at,
    }
    if include_raw:
        payload["raw_text"] = resume.raw_text
    return payload


def _success(data: Any, *, status_code: int = 200) -> tuple[Any, int]:
    return jsonify({"success": True, "data": data, "error": None}), status_code


def _error(error: JobHunterError) -> tuple[Any, int]:
    return (
        jsonify({"success": False, "data": None, "error": error.to_dict()}),
        int(error.status_code),
    )
