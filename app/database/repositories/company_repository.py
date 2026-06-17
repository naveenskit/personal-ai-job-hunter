from collections.abc import Sequence

from sqlalchemy import select

from app.database.base_repository import BaseRepository
from app.database.models import Company


class CompanyRepository(BaseRepository[Company]):
    model = Company

    async def get_by_domain(self, domain: str) -> Company | None:
        return await self.first(select(Company).where(Company.domain == domain))

    async def search_by_name(self, name: str, *, limit: int = 20) -> Sequence[Company]:
        return await self.all(
            select(Company).where(Company.name.ilike(f"%{name}%")).limit(limit)
        )

    async def needing_research(self, *, limit: int = 50) -> Sequence[Company]:
        return await self.all(
            select(Company)
            .where(Company.last_researched.is_(None))
            .order_by(Company.created_at.asc())
            .limit(limit)
        )
