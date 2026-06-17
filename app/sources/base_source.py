from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(slots=True)
class JobQuery:
    q: str | None = None
    role_type: str | None = None
    location: str | None = None
    country: str | None = None


@dataclass(slots=True)
class RawOpportunity:
    title: str
    company: str
    location: str
    job_url: str
    source: str
    description: str | None = None
    posted_date: str | None = None
    extra: dict[str, Any] | None = None


class JobSource(Protocol):
    @property
    def source_name(self) -> str: ...

    async def fetch(self, query: JobQuery, limit: int = 50) -> list[RawOpportunity]: ...

    async def health_check(self) -> bool: ...
