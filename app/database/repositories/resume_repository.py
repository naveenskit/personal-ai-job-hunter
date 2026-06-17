from collections.abc import Sequence

from sqlalchemy import select

from app.database.base_repository import BaseRepository
from app.database.models import Resume


class ResumeRepository(BaseRepository[Resume]):
    model = Resume

    async def get_by_hash(self, file_hash: str) -> Resume | None:
        return await self.first(select(Resume).where(Resume.file_hash == file_hash))

    async def list_active(self) -> Sequence[Resume]:
        return await self.all(select(Resume).where(Resume.is_active == 1))

    async def list_by_tag(self, role_tag: str) -> Sequence[Resume]:
        return await self.all(
            select(Resume)
            .where(Resume.role_tags.ilike(f"%{role_tag}%"))
            .order_by(Resume.updated_at.desc())
        )

    async def primary(self) -> Resume | None:
        return await self.first(
            select(Resume).where(Resume.is_active == 1).order_by(Resume.updated_at.desc())
        )

    async def set_active(self, resume_id: int) -> Resume | None:
        resumes = await self.list_active()
        for resume in resumes:
            resume.is_active = 0
        target = await self.get(resume_id)
        if target is not None:
            target.is_active = 1
        await self.session.flush()
        return target
