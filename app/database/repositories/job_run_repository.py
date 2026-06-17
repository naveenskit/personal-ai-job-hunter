from __future__ import annotations

from sqlalchemy import select, update

from app.database.models import JobRun


class JobRunRepository:
    def __init__(self, session) -> None:
        self.session = session

    async def create_run(self, job_name: str) -> JobRun:
        run = JobRun(job_name=job_name, status="running")
        self.session.add(run)
        await self.session.flush()
        return run

    async def mark_finished(
        self,
        run_id: int,
        processed: int | None = None,
        scored: int | None = None,
        duration: float | None = None,
    ) -> None:
        from datetime import datetime

        finished_at = datetime.utcnow().isoformat()
        stmt = (
            update(JobRun)
            .where(JobRun.id == run_id)
            .values(
                status="finished",
                finished_at=finished_at,
                processed_count=processed,
                scored_count=scored,
                duration_seconds=duration,
            )
        )
        await self.session.execute(stmt)
        await self.session.flush()

    async def mark_error(self, run_id: int, error: str) -> None:
        stmt = (
            update(JobRun).where(JobRun.id == run_id).values(status="error", error=error)
        )
        await self.session.execute(stmt)
        await self.session.flush()

    async def request_cancel(self, run_id: int) -> None:
        stmt = update(JobRun).where(JobRun.id == run_id).values(cancel_requested=1)
        await self.session.execute(stmt)
        await self.session.flush()

    async def get_recent(self, limit: int = 20) -> list[JobRun]:
        stmt = select(JobRun).order_by(JobRun.started_at.desc()).limit(limit)
        res = await self.session.execute(stmt)
        return [r for r in res.scalars().all()]

    async def get(self, run_id: int) -> JobRun | None:
        stmt = select(JobRun).where(JobRun.id == run_id)
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()
