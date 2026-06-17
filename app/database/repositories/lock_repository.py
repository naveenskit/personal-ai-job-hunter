from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy import delete, select, update

from app.database.models import SchedulerLock


class LockAcquireError(RuntimeError):
    pass


class LockRepository:
    def __init__(self, session) -> None:
        self.session = session

    async def acquire_lock(self, name: str, owner: str, ttl_seconds: int = 3600) -> bool:
        now = datetime.utcnow()
        expires = now + timedelta(seconds=ttl_seconds)
        # try insert; if exists, check expiry
        try:
            lock = SchedulerLock(
                name=name,
                owner=owner,
                acquired_at=now.isoformat(),
                expires_at=expires.isoformat(),
            )
            self.session.add(lock)
            await self.session.flush()
            return True
        except Exception:
            # existing lock - check if expired
            stmt = select(SchedulerLock).where(SchedulerLock.name == name)
            res = await self.session.execute(stmt)
            existing = res.scalar_one_or_none()
            if existing:
                try:
                    exp = (
                        datetime.fromisoformat(existing.expires_at)
                        if existing.expires_at
                        else None
                    )
                except Exception:
                    exp = None
                if exp is None or exp < now:
                    # steal lock
                    stmt = (
                        update(SchedulerLock)
                        .where(SchedulerLock.id == existing.id)
                        .values(
                            owner=owner,
                            acquired_at=now.isoformat(),
                            expires_at=expires.isoformat(),
                        )
                    )
                    await self.session.execute(stmt)
                    await self.session.flush()
                    return True
            return False

    async def release_lock(self, name: str, owner: str) -> None:
        stmt = select(SchedulerLock).where(SchedulerLock.name == name)
        res = await self.session.execute(stmt)
        existing = res.scalar_one_or_none()
        if existing and existing.owner == owner:
            await self.session.execute(delete(SchedulerLock).where(SchedulerLock.id == existing.id))
            await self.session.flush()

    async def is_locked(self, name: str) -> bool:
        stmt = select(SchedulerLock).where(SchedulerLock.name == name)
        res = await self.session.execute(stmt)
        existing = res.scalar_one_or_none()
        return existing is not None

    async def renew_lock(self, name: str, owner: str, ttl_seconds: int = 3600) -> bool:
        """Extend the lock TTL if we are the owner. Returns True if renewed."""
        now = datetime.utcnow()
        expires = now + timedelta(seconds=ttl_seconds)
        stmt = (
            update(SchedulerLock)
            .where(SchedulerLock.name == name)
            .where(SchedulerLock.owner == owner)
            .values(acquired_at=now.isoformat(), expires_at=expires.isoformat())
        )
        await self.session.execute(stmt)
        await self.session.flush()
        # SQLAlchemy with SQLite may not populate rowcount reliably; check by selecting
        check = select(SchedulerLock).where(SchedulerLock.name == name)
        r = await self.session.execute(check)
        existing = r.scalar_one_or_none()
        return existing is not None and existing.owner == owner
