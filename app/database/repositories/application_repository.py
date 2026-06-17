from collections.abc import Sequence

from sqlalchemy import select

from app.core.types import ApplicationStatus, utc_now_iso
from app.database.base_repository import BaseRepository
from app.database.models import Application, ApplicationEvent


class ApplicationRepository(BaseRepository[Application]):
    model = Application

    async def get_for_pair(self, opportunity_id: int, resume_id: int) -> Application | None:
        return await self.first(
            select(Application).where(
                Application.opportunity_id == opportunity_id,
                Application.resume_id == resume_id,
            )
        )

    async def list_by_status(self, status: ApplicationStatus | str) -> Sequence[Application]:
        status_value = status.value if isinstance(status, ApplicationStatus) else status
        return await self.all(
            select(Application)
            .where(Application.status == status_value)
            .order_by(Application.updated_at.desc())
        )

    async def transition_status(
        self,
        application: Application,
        new_status: ApplicationStatus | str,
        *,
        details: str = "{}",
    ) -> Application:
        new_status_value = (
            new_status.value if isinstance(new_status, ApplicationStatus) else new_status
        )
        old_status = application.status
        application.status = new_status_value
        application.updated_at = utc_now_iso()
        self.session.add(
            ApplicationEvent(
                application_id=application.id,
                event_type="status_changed",
                from_status=old_status,
                to_status=new_status_value,
                details=details,
            )
        )
        await self.session.flush()
        return application
