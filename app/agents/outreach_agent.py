from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.ai.provider import AIProvider
from app.core.types import utc_now_iso
from app.database.repositories.outreach_repository import OutreachRepository


@dataclass(slots=True)
class OutreachResult:
    subject: str
    body: str
    generated_at: str


class OutreachDBAgent:
    """DB-backed outreach sender which persists OutreachMessage records.

    Used by the `/send` endpoint to create and mark messages as sent.
    """

    def __init__(self, session) -> None:
        self.session = session
        self.repo = OutreachRepository(session)

    async def send_outreach(self, application_id: int, template_id: int) -> dict[str, Any]:
        tpl = await self.repo.get_template(template_id)
        if tpl is None:
            raise ValueError("template not found")

        app = await self.repo.get_application(application_id)
        if app is None:
            raise ValueError("application not found")

        recipient_name = getattr(app.resume, "name", None)
        company = getattr(app.opportunity, "company", None)
        company_name = getattr(company, "name", None) if company else None

        subject = tpl.subject or f"About {app.opportunity.title}"
        body = tpl.body or ""
        body = body.replace("{name}", recipient_name or "")
        body = body.replace("{company}", company_name or "")

        msg = await self.repo.create_message(
            application_id=application_id,
            message_type="outbound",
            recipient_name=recipient_name,
            recipient_email=None,
            recipient_title=None,
            subject=subject,
            body=body,
            is_sent=1,
        )

        return {"message_id": msg.id, "sent": True}


class OutreachAgent:
    """AI-backed outreach generator. Produces subject/body using an `AIProvider`."""

    def __init__(self, ai_provider: AIProvider) -> None:
        self.ai = ai_provider

    async def generate_email(self, opportunity: dict, resume_text: str) -> OutreachResult:
        title = opportunity.get("title", "")
        company = opportunity.get("company", "")
        prompt = (
            "You are a hiring outreach assistant. Craft a concise, personalized cold "
            f"email subject and body to apply for {title} at {company}. The candidate "
            f"resume is:\n{resume_text}\nRespond with SUBJECT:\n<subject>\nBODY:\n<body>"
        )
        resp = await self.ai.complete(prompt, temperature=0.2, max_tokens=600)
        subject = ""
        body = resp
        if "SUBJECT:" in resp:
            parts = resp.split("SUBJECT:", 1)[1]
            if "BODY:" in parts:
                subject_part, body_part = parts.split("BODY:", 1)
                subject = subject_part.strip()
                body = body_part.strip()
        return OutreachResult(
            subject=subject or f"Application: {title}",
            body=body,
            generated_at=utc_now_iso(),
        )
