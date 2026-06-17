from sqlalchemy import select

from app.database.base_repository import BaseRepository
from app.database.models import LearningPlan


class LearningRepository(BaseRepository[LearningPlan]):
    model = LearningPlan

    async def create_plan(
        self, resume_id: int | None, opportunity_id: int | None, steps: str
    ) -> LearningPlan:
        return await self.create(
            resume_id=resume_id, opportunity_id=opportunity_id, steps=steps
        )

    async def get(self, plan_id: int) -> LearningPlan | None:
        return await super().get(plan_id)

    async def list_for_resume(self, resume_id: int) -> list[LearningPlan]:
        return await self.all(select(LearningPlan).where(LearningPlan.resume_id == resume_id))
