from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import select

from app.core.types import utc_now_iso
from app.database.base_repository import BaseRepository
from app.database.models import Application, OutreachMessage


class OutreachRepository(BaseRepository[OutreachMessage]):
    model = OutreachMessage

    async def get_template(self, template_id: int):
        # For now templates are not persisted; return a small default template object
        class T:
            def __init__(self, id: int, subject: str | None, body: str | None):
                self.id = id
                self.subject = subject
                self.body = body

        return T(
            template_id,
            "Hello from Job Hunter",
            "Hi {name},\n\nI thought you'd be a fit at {company}.",
        )

    async def get_application(self, application_id: int) -> Application | None:
        stmt = select(Application).where(Application.id == application_id)
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def create_message(
        self,
        application_id: int,
        message_type: str,
        recipient_name: str | None,
        recipient_email: str | None,
        recipient_title: str | None,
        subject: str | None,
        body: str,
        is_sent: int = 0,
    ):
        msg = OutreachMessage(
            application_id=application_id,
            message_type=message_type,
            recipient_name=recipient_name,
            recipient_email=recipient_email,
            recipient_title=recipient_title,
            subject=subject,
            body=body,
            is_sent=is_sent,
        )
        self.session.add(msg)
        await self.session.flush()
        return msg

    async def list_for_application(self, application_id: int) -> Sequence[OutreachMessage]:
        return await self.all(
            select(OutreachMessage)
            .where(OutreachMessage.application_id == application_id)
            .order_by(OutreachMessage.created_at.desc())
        )

    async def mark_sent(self, message: OutreachMessage) -> OutreachMessage:
        message.is_sent = 1
        message.sent_at = utc_now_iso()
        await self.session.flush()
        return message
