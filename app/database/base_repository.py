from collections.abc import Sequence
from typing import Any, Generic, TypeVar

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    model: type[ModelT]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, item_id: int) -> ModelT | None:
        return await self.session.get(self.model, item_id)

    async def list(self, *, limit: int = 100, offset: int = 0) -> Sequence[ModelT]:
        result = await self.session.execute(select(self.model).limit(limit).offset(offset))
        return result.scalars().all()

    async def create(self, **values: Any) -> ModelT:
        item = self.model(**values)
        self.session.add(item)
        await self.session.flush()
        return item

    async def update(self, item: ModelT, **values: Any) -> ModelT:
        for key, value in values.items():
            setattr(item, key, value)
        await self.session.flush()
        return item

    async def delete(self, item: ModelT) -> None:
        await self.session.delete(item)
        await self.session.flush()

    async def first(self, statement: Select[tuple[ModelT]]) -> ModelT | None:
        result = await self.session.execute(statement)
        return result.scalars().first()

    async def all(self, statement: Select[tuple[ModelT]]) -> Sequence[ModelT]:
        result = await self.session.execute(statement)
        return result.scalars().all()
