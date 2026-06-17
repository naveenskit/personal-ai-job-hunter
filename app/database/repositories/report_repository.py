from collections.abc import Sequence

from sqlalchemy import select

from app.database.base_repository import BaseRepository
from app.database.models import WeeklyReport


class ReportRepository(BaseRepository[WeeklyReport]):
    model = WeeklyReport

    async def get_by_week_start(self, week_start: str) -> WeeklyReport | None:
        return await self.first(select(WeeklyReport).where(WeeklyReport.week_start == week_start))

    async def latest(self) -> WeeklyReport | None:
        return await self.first(select(WeeklyReport).order_by(WeeklyReport.created_at.desc()))

    async def recent(self, *, limit: int = 10) -> Sequence[WeeklyReport]:
        return await self.all(
            select(WeeklyReport).order_by(WeeklyReport.created_at.desc()).limit(limit)
        )
