from __future__ import annotations

import json
import re
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.provider import AIProvider
from app.core.types import utc_now_iso
from app.database.repositories.company_repository import CompanyRepository


@dataclass(slots=True)
class CompanyResearchResult:
    company_name: str | None
    website: str | None
    overview: str | None
    industry: str | None
    size: str | None
    headquarters: str | None
    employees: str | None
    funding: str | None
    competitors: list[str]
    tech_stack: list[str]
    culture_tags: list[str]
    linkedin: str | None
    researched_at: str


class ResearchAgent:
    def __init__(self, ai_provider: AIProvider, session: AsyncSession | None = None) -> None:
        self.ai = ai_provider
        self.session = session
        self.repo: CompanyRepository | None = (
            CompanyRepository(session) if session is not None else None
        )

    async def analyze(
        self,
        company_name: str | None = None,
        website: str | None = None,
    ) -> CompanyResearchResult:
        prompt = (
            "Provide a JSON object with company details: company_name, website, overview,"
            " industry, size, headquarters, employees, funding, competitors (list),"
            " tech_stack (list of technologies), culture_tags (list),"
            " linkedin. Keep values concise."
        )
        if company_name:
            prompt += f"\nCompany name: {company_name}"
        if website:
            prompt += f"\nWebsite: {website}"

        resp = await self.ai.complete(prompt, temperature=0.2, max_tokens=800)

        # Try JSON parse first
        try:
            parsed = json.loads(resp)
            if isinstance(parsed, dict):
                return CompanyResearchResult(
                    company_name=parsed.get("company_name") or company_name,
                    website=parsed.get("website") or website,
                    overview=parsed.get("overview"),
                    industry=parsed.get("industry"),
                    size=parsed.get("size"),
                    headquarters=parsed.get("headquarters"),
                    employees=parsed.get("employees"),
                    funding=parsed.get("funding"),
                    competitors=parsed.get("competitors") or [],
                    tech_stack=parsed.get("tech_stack") or parsed.get("tech") or [],
                    culture_tags=parsed.get("culture_tags") or parsed.get("culture") or [],
                    linkedin=parsed.get("linkedin"),
                    researched_at=utc_now_iso(),
                )
        except Exception:
            pass

        # Fallback: return minimal object with raw text in overview
        return CompanyResearchResult(
            company_name=company_name,
            website=website,
            overview=resp.strip(),
            industry=None,
            size=None,
            headquarters=None,
            employees=None,
            funding=None,
            competitors=[],
            tech_stack=[],
            culture_tags=[],
            linkedin=None,
            researched_at=utc_now_iso(),
        )

    def _parse_number_millions(self, value: str | None) -> float | None:
        if not value:
            return None
        try:
            text = value.replace(",", "").strip().lower()
            # capture expressions like $1.2M, 2B, 500k, 3 million
            m = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*([kmb]|thousand|million|billion)?", text)
            if not m:
                return None
            num = float(m.group(1))
            unit = m.group(2) or ""
            if unit.startswith("k") or unit == "thousand":
                return num / 1000.0
            if unit.startswith("m") or unit == "million":
                return num
            if unit.startswith("b") or unit == "billion":
                return num * 1000.0
            # bare number assume dollars -> treat as millions if large
            if num > 1000:
                return num / 1_000_000.0
            return num
        except Exception:
            return None

    def _normalize_size(self, size: str | None, employees: str | None) -> str | None:
        candidate = (size or "").lower()
        if not candidate and employees:
            candidate = employees.lower()

        # check numeric ranges
        m = re.search(r"(\d+)(?:\s*-\s*(\d+))?", candidate)
        if m:
            lo = int(m.group(1))
            hi = int(m.group(2)) if m.group(2) else lo
            avg = (lo + hi) / 2
            if avg < 10:
                return "micro"
            if avg < 50:
                return "small"
            if avg < 250:
                return "medium"
            if avg < 1000:
                return "large"
            return "enterprise"

        if "startup" in candidate or "early" in candidate:
            return "small"
        if "scale" in candidate or "growing" in candidate:
            return "medium"
        if "enterprise" in candidate or "large" in candidate:
            return "enterprise"
        return None

    def _compute_quality_score(
        self,
        funding: str | None,
        size_bucket: str | None,
        tech_stack: list[str],
        overview: str | None,
        linkedin: str | None,
    ) -> int:
        score = 0
        funding_m = self._parse_number_millions(funding)
        if funding_m is not None:
            if funding_m >= 1000:
                score += 30
            elif funding_m >= 100:
                score += 25
            elif funding_m >= 10:
                score += 20
            elif funding_m >= 1:
                score += 10
            else:
                score += 5

        if size_bucket in ("medium", "large", "enterprise"):
            score += 15
        elif size_bucket in ("small", "micro"):
            score += 5

        tech_bonus = min(20, len(tech_stack) * 3)
        score += tech_bonus

        if overview:
            score += 10
        if linkedin:
            score += 10

        return max(0, min(100, int(score)))

    async def research_company(self, company_id: int) -> dict:
        if self.repo is None:
            raise RuntimeError(
                "Repository not available; provide a DB session when constructing ResearchAgent"
            )

        company = await self.repo.get(company_id)
        if company is None:
            raise ValueError("Company not found")

        # run enrichment with company name and domain/website
        resp = await self.analyze(
            company_name=company.name, website=company.website or company.domain
        )

        # persist research_data and update metadata
        research_payload = {
            "company_name": resp.company_name,
            "website": resp.website,
            "overview": resp.overview,
            "industry": resp.industry,
            "size": resp.size,
            "headquarters": resp.headquarters,
            "employees": resp.employees,
            "funding": resp.funding,
            "competitors": resp.competitors,
            "tech_stack": resp.tech_stack,
            "culture_tags": resp.culture_tags,
            "linkedin": resp.linkedin,
            "researched_at": resp.researched_at,
        }

        # normalization and scoring
        normalized_size = self._normalize_size(resp.size, resp.employees)
        funding_millions = self._parse_number_millions(resp.funding)
        quality_score = self._compute_quality_score(
            resp.funding,
            normalized_size,
            resp.tech_stack,
            resp.overview,
            resp.linkedin,
        )

        research_payload["normalized_size"] = normalized_size
        research_payload["funding_millions"] = funding_millions
        research_payload["quality_score"] = quality_score

        # persist research_data and update parsed fields
        # normalize tech stack before persisting
        norm_tech = self._normalize_tech_stack(resp.tech_stack)

        await self.repo.update(
            company,
            research_data=json.dumps(research_payload),
            tech_stack=json.dumps(norm_tech),
            culture_tags=json.dumps(resp.culture_tags),
            last_researched=utc_now_iso(),
            quality_score=quality_score,
        )
        return {"company_id": company.id, "research": research_payload}

    def _normalize_tech_stack(self, techs: list[str] | None) -> list[str]:
        if not techs:
            return []
        canonical = {
            "py": "python",
            "python3": "python",
            "js": "javascript",
            "react.js": "react",
            "reactjs": "react",
            "nodejs": "node",
            "node.js": "node",
            "ts": "typescript",
            "tsc": "typescript",
        }
        seen: set[str] = set()
        out: list[str] = []
        for t in techs:
            if not t:
                continue
            s = t.strip().lower()
            # remove common punctuation
            s = re.sub(r"[^a-z0-9]+", "", s)
            s = canonical.get(s, s)
            if s and s not in seen:
                seen.add(s)
                out.append(s)
        return out
