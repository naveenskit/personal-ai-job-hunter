from __future__ import annotations

from time import time

from app.agents.matching_agent import MatchingAgent
from app.database.repositories.job_run_repository import JobRunRepository
from app.database.repositories.opportunity_repository import OpportunityRepository
from app.database.repositories.resume_repository import ResumeRepository


async def run_bulk_matching(
    session,
    ai_provider,
    job_run_id: int | None = None,
    max_opps_per_resume: int = 50,
) -> tuple[int, int]:
    """Run matching for all active resumes against active opportunities.

    Returns (matches_created, scores_updated)
    """
    rr = ResumeRepository(session)
    orr = OpportunityRepository(session)
    jr = JobRunRepository(session)

    resumes = await rr.list_active()
    total_processed = 0
    total_scores = 0

    start_ts = time()

    for resume in resumes:
        # check for cancel request
        if job_run_id is not None:
            run = await jr.get(job_run_id)
            if run and getattr(run, "cancel_requested", 0):
                break

        opps = await orr.list_active(limit=max_opps_per_resume)
        agent = MatchingAgent(session, ai_provider)
        for opp in opps:
            # check cancel inside inner loop too
            if job_run_id is not None:
                run = await jr.get(job_run_id)
                if run and getattr(run, "cancel_requested", 0):
                    break

            await agent.match_resume_to_opportunity(resume.id, opp.id)
            total_scores += 1
        total_processed += 1

    duration = time() - start_ts
    if job_run_id is not None:
        await jr.mark_finished(
            job_run_id, processed=total_processed, scored=total_scores, duration=duration
        )

    return total_processed, total_scores
