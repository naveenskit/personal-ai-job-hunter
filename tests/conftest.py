import asyncio
import os

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database.connection import init_db
from app.database.models import Base


@pytest.fixture()
async def db_session() -> AsyncSession:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session

    await engine.dispose()


@pytest.fixture(scope="session", autouse=True)
def ensure_file_db():
    """Ensure the file-based SQLite DB is reset for tests that use the app factory.

    Removes `data/jobhunter.db` if present and runs `init_db()` to recreate schema.
    This runs once per test session automatically.
    """
    db_path = os.path.join("data", "jobhunter.db")
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except Exception:
            pass

    # run init_db synchronously
    asyncio.run(init_db())
    yield
