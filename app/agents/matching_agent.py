from __future__ import annotations

import json
import math
import re

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.provider import AIProvider
from app.core.types import utc_now_iso
from app.database.models import OpportunityScore
from app.database.repositories.opportunity_repository import OpportunityRepository
from app.database.repositories.resume_repository import ResumeRepository
from app.resumes.embeddings import unpack_embedding


class MatchingAgent:
    def __init__(self, session: AsyncSession, ai_provider: AIProvider) -> None:
        self.session = session
        self.ai = ai_provider
        self.resume_repo = ResumeRepository(session)
        self.opp_repo = OpportunityRepository(session)

    async def match_resume_to_opportunity(
        self,
        resume_id: int,
        opportunity_id: int,
    ) -> float:
        """Compute resume match score (0-100) using AI similarity.

        Strategy:
        - If the resume has a stored embedding, compute an embedding for the
          opportunity text and use cosine similarity (mapped to 0..100).
        - Otherwise fall back to `AIProvider.complete()` which should return
          a numeric score string.
        - Persist an `OpportunityScore` record (create or update) with a
          simple breakdown so we can inspect match history.
        """

        resume = await self.resume_repo.get(resume_id)
        opp = await self.opp_repo.get(opportunity_id)

        if resume is None or opp is None:
            return 0.0

        # prefer embedding-based similarity when resume has an embedding
        resume_vec = unpack_embedding(resume.embedding)
        final: float
        if resume_vec:
            text = f"{opp.title} {opp.description or ''}"
            try:
                opp_vec = await self.ai.embed(text)
                if opp_vec and len(opp_vec) == len(resume_vec):
                    # cosine similarity
                    dot = sum(a * b for a, b in zip(resume_vec, opp_vec, strict=False))
                    norm_a = math.sqrt(sum(a * a for a in resume_vec))
                    norm_b = math.sqrt(sum(b * b for b in opp_vec))
                    if norm_a > 0 and norm_b > 0:
                        cosine = dot / (norm_a * norm_b)
                        # map cosine (-1..1) to 0..100
                        score = (cosine + 1.0) * 50.0
                        final = min(100.0, max(0.0, score))
                    else:
                        final = 50.0
                else:
                    final = 50.0
            except Exception:
                final = 50.0
        else:
            # fallback: use AI to compute semantic similarity
            prompt = (
                "You are an assistant that rates how well a resume matches a job.\n"
                "Return a JSON object ONLY (no extra commentary) with the following fields:\n"
                "- total_score: number 0-100\n"
                "- resume_match: number 0-100 (how well resume matches the job)\n"
                "- hiring_probability: number 0-100\n"
                "- location_preference: number 0-100\n"
                "- freshness: number 0-100\n"
                "- company_quality: number 0-100\n"
                "- competition_estimate: number 0-100\n"
                "- reasoning: string (brief explanation)\n\n"
                f"Resume: {resume.raw_text[:2000]}\n\n"
                f"Job title: {opp.title}\n"
                f"Company: {opp.company or 'unknown'}\n"
                f"Job description: {opp.description or ''}\n"
            )

            result = await self.ai.complete(prompt, max_tokens=500)

            # try to parse JSON object from the model output
            parsed = None
            # defaults for parsed values
            resume_match_val = None
            hiring_probability_val = 0.0
            location_preference_val = 0.0
            freshness_val = 0.0
            company_quality_val = 0.0
            competition_estimate_val = 0.0
            reasoning_val = None
            try:
                parsed = json.loads(result)
            except Exception:
                # attempt to extract a JSON snippet
                m = re.search(r"\{.*\}", result, re.S)
                if m:
                    try:
                        parsed = json.loads(m.group(0))
                    except Exception:
                        parsed = None

            if parsed and isinstance(parsed, dict):
                def num(v, default=50.0):
                    try:
                        return float(v) if v is not None else default
                    except Exception:
                        return default

                total = num(parsed.get("total_score", parsed.get("score", None)))
                resume_match_val = num(parsed.get("resume_match", total))
                hiring_probability_val = num(parsed.get("hiring_probability", 0.0))
                location_preference_val = num(parsed.get("location_preference", 0.0))
                freshness_val = num(parsed.get("freshness", 0.0))
                company_quality_val = num(parsed.get("company_quality", 0.0))
                competition_estimate_val = num(parsed.get("competition_estimate", 0.0))
                reasoning_val = parsed.get("reasoning")
                final = min(100.0, max(0.0, total))
            else:
                # fallback to extracting a number from the response
                m = re.search(r"(\d+(?:\.\d+)?)", result or "")
                if m:
                    final = min(100.0, max(0.0, float(m.group(1))))
                else:
                    final = 50.0

        # persist score record (create or update)
        try:
            stmt = select(OpportunityScore).where(
                OpportunityScore.opportunity_id == opp.id,
                OpportunityScore.resume_id == resume.id,
            )
            res = await self.session.execute(stmt)
            existing = res.scalar_one_or_none()
            band = "high" if final >= 80 else "medium" if final >= 50 else "low"
            if resume_match_val is None:
                resume_match_val = final

            if existing:
                existing.total_score = final
                existing.score_band = band
                existing.resume_match = resume_match_val
                existing.hiring_probability = hiring_probability_val
                existing.location_preference = location_preference_val
                existing.freshness = freshness_val
                existing.company_quality = company_quality_val
                existing.competition_estimate = competition_estimate_val
                existing.reasoning = reasoning_val
                existing.scored_at = utc_now_iso()
            else:
                record = OpportunityScore(
                    opportunity_id=opp.id,
                    resume_id=resume.id,
                    total_score=final,
                    score_band=band,
                    resume_match=resume_match_val,
                    hiring_probability=hiring_probability_val,
                    location_preference=location_preference_val,
                    freshness=freshness_val,
                    company_quality=company_quality_val,
                    competition_estimate=competition_estimate_val,
                    reasoning=reasoning_val,
                )
                self.session.add(record)
            await self.session.flush()
        except Exception:
            # persistence failure should not block returning a score
            pass

        return final
