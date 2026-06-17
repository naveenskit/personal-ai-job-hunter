from __future__ import annotations

import hashlib
from collections.abc import Iterable

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repositories.opportunity_repository import OpportunityRepository
from app.sources.base_source import JobQuery


def _normalize_field(value: str) -> str:
    return " ".join(value.strip().split())


def _role_type_from_title(title: str) -> str:
    t = title.lower()
    if "intern" in t or "internship" in t:
        return "intern"
    if "senior" in t or "sr." in t:
        return "senior"
    return "associate"


def _location_type_from_location(location: str) -> str:
    loc_lower = location.lower()
    if "remote" in loc_lower:
        return "remote"
    if "hybrid" in loc_lower:
        return "hybrid"
    return "onsite"


def _content_hash(title: str, company: str, location: str) -> str:
    key = f"{title}|{company}|{location}".encode()
    return hashlib.sha256(key).hexdigest()


class DiscoveryService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = OpportunityRepository(session)

    async def run(self, sources: Iterable[object], query: JobQuery | None = None) -> list[int]:
        q = query or JobQuery()
        created_ids: list[int] = []
        for s in sources:
            try:
                fetched = await s.fetch(q)
            except Exception:
                continue

            for raw in fetched:
                title = _normalize_field(raw.title)
                company = _normalize_field(raw.company)
                location = _normalize_field(raw.location or "")
                content_hash = _content_hash(title, company, location)

                existing = await self.repo.get_by_content_hash(content_hash)
                if existing is not None:
                    continue

                # simple role/location heuristics; more advanced normalization later
                role_type = _role_type_from_title(title)
                location_type = _location_type_from_location(location)

                opp = await self.repo.create(
                    title=title,
                    company_id=None,
                    role_type=role_type,
                    location=location or "",
                    location_type=location_type,
                    country="India",
                    job_url=raw.job_url,
                    source=raw.source,
                    description=raw.description,
                    requirements="[]",
                    content_hash=content_hash,
                    posted_date=raw.posted_date,
                    is_active=1,
                )
                await self.session.flush()
                created_ids.append(opp.id)

        return created_ids
