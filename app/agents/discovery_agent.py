from __future__ import annotations

from dataclasses import dataclass

from app.core.types import utc_now_iso
from app.sources.base_source import JobQuery, RawOpportunity


@dataclass(slots=True)
class DiscoveryResult:
    opportunities: list[RawOpportunity]
    run_at: str


class DiscoveryAgent:
    """Discovery agent skeleton for Phase 3.

    The agent will be expanded to load configured sources, fetch, normalize,
    hash and deduplicate opportunities and persist them via repositories.
    """

    name = "discovery"

    def __init__(self, sources: list[object]) -> None:
        self.sources = sources

    async def run(self, query: JobQuery | None = None) -> DiscoveryResult:
        q = query or JobQuery()
        out: list[RawOpportunity] = []
        for s in self.sources:
            try:
                fetched = await s.fetch(q)
                out.extend(fetched)
            except Exception:
                # keep agent resilient; real code will log
                continue

        return DiscoveryResult(opportunities=out, run_at=utc_now_iso())

    async def health_check(self) -> bool:
        ok = True
        for s in self.sources:
            try:
                res = await s.health_check()
                ok = ok and bool(res)
            except Exception:
                ok = False
        return ok
        return ok

