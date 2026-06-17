from __future__ import annotations

import json
from dataclasses import dataclass

from app.ai.provider import AIProvider
from app.core.types import utc_now_iso


@dataclass(slots=True)
class SkillGap:
    skill: str
    gap_type: str  # 'missing'|'weak'|'outdated'
    importance: str  # 'critical'|'important'|'nice'
    resources: list[str]


@dataclass(slots=True)
class SkillGapResult:
    resume_id: int | None
    opportunity_id: int | None
    gaps: list[SkillGap]
    analyzed_at: str


class SkillGapAgent:
    def __init__(self, ai_provider: AIProvider) -> None:
        self.ai = ai_provider

    async def analyze(
        self,
        resume_text: str,
        jd_text: str,
        resume_id: int | None = None,
        opportunity_id: int | None = None,
    ) -> SkillGapResult:
        # Prompt the AI to extract missing skills. Keep simple for tests.
        prompt = (
            "Extract the top 5 skills from the job description and compare "
            "with the resume. Return a JSON list of missing or weak skills "
            "with importance and a short learning resource. "
            f"Job description:\n{jd_text}\nResume:\n{resume_text}"
        )
        resp = await self.ai.complete(prompt, temperature=0.2, max_tokens=600)
        # robust parsing: try JSON first, then pipe-delimited lines, then comma list
        gaps: list[SkillGap] = []
        try:
            parsed = json.loads(resp)
            if isinstance(parsed, list):
                for item in parsed:
                    if isinstance(item, dict) and "skill" in item:
                        gaps.append(
                            SkillGap(
                                skill=item.get("skill"),
                                gap_type=item.get("gap_type", "missing"),
                                importance=item.get("importance", "important"),
                                resources=item.get("resources", []) or [],
                            )
                        )
                
                return SkillGapResult(
                    resume_id=resume_id,
                    opportunity_id=opportunity_id,
                    gaps=gaps,
                    analyzed_at=utc_now_iso(),
                )
        except Exception:
            # fall back to line-based parsing
            pass

        for line in resp.splitlines():
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 4:
                gaps.append(
                    SkillGap(
                        skill=parts[0],
                        gap_type=parts[1],
                        importance=parts[2],
                        resources=[parts[3]],
                    )
                )
        return SkillGapResult(
            resume_id=resume_id,
            opportunity_id=opportunity_id,
            gaps=gaps,
            analyzed_at=utc_now_iso(),
        )
