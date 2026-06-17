from __future__ import annotations

from app.core.types import ApplicationStatus
from app.database.repositories.application_repository import ApplicationRepository


class TrackerAgent:
    def __init__(self, session) -> None:
        self.session = session
        self.repo = ApplicationRepository(session)

    async def create_application(
        self, opportunity_id: int, resume_id: int, source: str | None = None
    ):
        # create or return existing application for (opportunity,resume)
        existing = await self.repo.get_for_pair(opportunity_id, resume_id)
        if existing is not None:
            return existing
        app = await self.repo.create(
            opportunity_id=opportunity_id,
            resume_id=resume_id,
            status=ApplicationStatus.DISCOVERED.value,
            source=source,
        )
        await self.session.flush()
        return app

    async def transition(
        self, application_id: int, new_status: ApplicationStatus | str, details: str = "{}"
    ):
        application = await self.repo.get(application_id)
        if application is None:
            raise ValueError("Application not found")
        updated = await self.repo.transition_status(application, new_status, details=details)
        return updated
