from collections.abc import Sequence

from sqlalchemy import select

from app.database.base_repository import BaseRepository
from app.database.models import SkillGap


class SkillGapRepository(BaseRepository[SkillGap]):
    model = SkillGap

    async def list_for_resume(self, resume_id: int) -> Sequence[SkillGap]:
        return await self.all(
            select(SkillGap)
            .where(SkillGap.resume_id == resume_id)
            .order_by(SkillGap.created_at.desc())
        )

    async def list_for_opportunity(self, opportunity_id: int) -> Sequence[SkillGap]:
        return await self.all(
            select(SkillGap)
            .where(SkillGap.opportunity_id == opportunity_id)
            .order_by(SkillGap.created_at.desc())
        )
