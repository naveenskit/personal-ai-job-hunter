from collections.abc import Sequence

from sqlalchemy import select

from app.database.base_repository import BaseRepository
from app.database.models import Opportunity


class OpportunityRepository(BaseRepository[Opportunity]):
    model = Opportunity

    async def get_by_url(self, job_url: str) -> Opportunity | None:
        return await self.first(select(Opportunity).where(Opportunity.job_url == job_url))

    async def get_by_content_hash(self, content_hash: str) -> Opportunity | None:
        return await self.first(
            select(Opportunity).where(Opportunity.content_hash == content_hash)
        )

    async def list_active(
        self,
        *,
        role_type: str | None = None,
        country: str | None = None,
        limit: int = 100,
    ) -> Sequence[Opportunity]:
        statement = select(Opportunity).where(Opportunity.is_active == 1)
        if role_type:
            statement = statement.where(Opportunity.role_type == role_type)
        if country:
            statement = statement.where(Opportunity.country == country)
        return await self.all(statement.order_by(Opportunity.created_at.desc()).limit(limit))

    async def soft_delete(self, opportunity: Opportunity) -> Opportunity:
        opportunity.is_active = 0
        await self.session.flush()
        return opportunity
