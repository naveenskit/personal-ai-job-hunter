from collections.abc import Sequence

from sqlalchemy import select

from app.database.base_repository import BaseRepository
from app.database.models import OpportunityScore


class ScoreRepository(BaseRepository[OpportunityScore]):
    model = OpportunityScore

    async def get_for_pair(
        self,
        opportunity_id: int,
        resume_id: int,
    ) -> OpportunityScore | None:
        return await self.first(
            select(OpportunityScore).where(
                OpportunityScore.opportunity_id == opportunity_id,
                OpportunityScore.resume_id == resume_id,
            )
        )

    async def top_scores(
        self,
        *,
        resume_id: int | None = None,
        min_score: float | None = None,
        limit: int = 25,
    ) -> Sequence[OpportunityScore]:
        statement = select(OpportunityScore)
        if resume_id is not None:
            statement = statement.where(OpportunityScore.resume_id == resume_id)
        if min_score is not None:
            statement = statement.where(OpportunityScore.total_score >= min_score)
        return await self.all(statement.order_by(OpportunityScore.total_score.desc()).limit(limit))
