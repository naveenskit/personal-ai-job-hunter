from __future__ import annotations

import csv
import io
from typing import Any

from flask import Blueprint, jsonify, request

from app.agents.research_agent import ResearchAgent
from app.ai.provider import get_ai_provider
from app.database.connection import session_scope
from app.database.repositories.company_repository import CompanyRepository

companies_bp = Blueprint("companies", __name__, url_prefix="/api/v1/companies")


@companies_bp.post("/<int:company_id>/research")
async def research_company(company_id: int) -> tuple[Any, int]:
    try:
        async with session_scope() as session:
            agent = ResearchAgent(get_ai_provider(), session)
            result = await agent.research_company(company_id)
            return jsonify({"success": True, "data": result, "error": None}), 200
    except Exception as exc:
        return jsonify({"success": False, "data": None, "error": {"message": str(exc)}}), 400


@companies_bp.get("/<int:company_id>/research")
async def get_company_research(company_id: int) -> tuple[Any, int]:
    async with session_scope() as session:
        repo = CompanyRepository(session)
        company = await repo.get(company_id)
        if company is None:
            return (
                jsonify(
                    {"success": False, "data": None, "error": {"message": "company not found"}}
                ),
                404,
            )

        data = {
            "id": company.id,
            "name": company.name,
            "domain": company.domain,
            "website": company.website,
            "research_data": company.research_data,
            "tech_stack": company.tech_stack,
            "culture_tags": company.culture_tags,
            "last_researched": company.last_researched,
        }
        return (jsonify({"success": True, "data": data, "error": None}), 200)


@companies_bp.post("/import")
async def import_companies() -> tuple[Any, int]:
    payload = request.get_json() or {}
    items = payload.get("companies") or []
    created = []
    skipped = []
    async with session_scope() as session:
        repo = CompanyRepository(session)
        for item in items:
            name = item.get("name")
            domain = item.get("domain")
            website = item.get("website")
            existing = None
            if domain:
                existing = await repo.get_by_domain(domain)
            if existing is not None:
                skipped.append({"domain": domain, "id": existing.id})
                continue
            created_item = await repo.create(
                name=name or "", domain=domain, website=website
            )
            created.append(
                {"id": created_item.id, "name": created_item.name, "domain": created_item.domain}
            )

    return (
        jsonify({"success": True, "data": {"created": created, "skipped": skipped}, "error": None}),
        200,
    )


@companies_bp.post("/import/csv")
async def import_companies_csv() -> tuple[Any, int]:
    # Accept multipart file upload 'file' or JSON with 'csv' content
    file = request.files.get("file") if hasattr(request, "files") else None
    csv_text = None
    if file:
        # read bytes and decode
        csv_text = file.stream.read().decode("utf-8")
    else:
        payload = request.get_json(silent=True) or {}
        csv_text = payload.get("csv")

    # options: delimiter and header_map
    payload = request.get_json(silent=True) or {}
    delimiter = payload.get("delimiter") or ","
    header_map = payload.get("header_map") or {}

    if not csv_text:
        return (
            jsonify({"success": False, "data": None, "error": {"message": "No CSV provided"}}),
            400,
        )

    reader = csv.DictReader(io.StringIO(csv_text), delimiter=delimiter)
    created = []
    skipped = []
    async with session_scope() as session:
        repo = CompanyRepository(session)
        for row in reader:
            # allow header mapping: external header -> internal field
            def lookup(row: dict, field: str) -> str | None:
                external = header_map.get(field, field)
                return row.get(external) or row.get(external.lower())

            name = lookup(row, "name") or lookup(row, "company")
            domain = lookup(row, "domain")
            website = lookup(row, "website")
            existing = None
            if domain:
                existing = await repo.get_by_domain(domain)
            if existing is not None:
                skipped.append({"domain": domain, "id": existing.id})
                continue
            created_item = await repo.create(name=name or "", domain=domain, website=website)
            created.append(
                {"id": created_item.id, "name": created_item.name, "domain": created_item.domain}
            )

    return (
        jsonify({"success": True, "data": {"created": created, "skipped": skipped}, "error": None}),
        200,
    )
