from __future__ import annotations

import httpx

from app.sources.base_source import JobQuery, RawOpportunity


class RemoteOKSource:
    """RemoteOK source implementation (basic).

    Fetches the RemoteOK public API and returns normalized RawOpportunity items.
    Errors are swallowed and an empty list is returned to keep the discovery agent
    resilient during transient network failures.
    """

    API_URL = "https://remoteok.com/api"

    @property
    def source_name(self) -> str:
        return "remoteok"

    async def fetch(self, query: JobQuery, limit: int = 50) -> list[RawOpportunity]:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(self.API_URL, headers={"User-Agent": "job-agent/1.0"})
                resp.raise_for_status()
                data = resp.json()

            # remoteok returns a list where first item is metadata; filter dict entries
            jobs = []
            for item in data:
                if not isinstance(item, dict):
                    continue
                # skip metadata rows
                if item.get("id") is None and item.get("position") is None:
                    continue

                title = item.get("position") or item.get("title") or ""
                company = item.get("company") or item.get("company_name") or ""
                location = item.get("location") or item.get("country") or ""
                job_url = item.get("url") or item.get("link") or item.get("apply_url") or ""
                posted_date = item.get("date") or item.get("created_at")
                description = item.get("description") or item.get("tags") or ""

                jobs.append(
                    RawOpportunity(
                        title=str(title),
                        company=str(company),
                        location=str(location),
                        job_url=str(job_url),
                        source=self.source_name,
                        description=str(description) if description is not None else None,
                        posted_date=str(posted_date) if posted_date is not None else None,
                    )
                )

            return jobs[:limit]
        except Exception:
            return []

    async def health_check(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                r = await client.head(self.API_URL, headers={"User-Agent": "job-agent/1.0"})
                return r.status_code == 200
        except Exception:
            return False
