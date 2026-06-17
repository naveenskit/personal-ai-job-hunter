from __future__ import annotations

from dataclasses import dataclass

from app.ai.provider import AIProvider
from app.core.types import utc_now_iso


@dataclass(slots=True)
class LinkedinResult:
    message: str
    generated_at: str


class LinkedinAgent:
    def __init__(self, ai_provider: AIProvider) -> None:
        self.ai = ai_provider

    async def generate_message(
        self,
        opportunity: dict,
        resume_text: str,
        max_chars: int = 300,
    ) -> LinkedinResult:
        title = opportunity.get("title", "")
        company = opportunity.get("company", "")
        prompt = (
            "You are a LinkedIn outreach assistant. Craft a concise (<=300 characters) "
            f"connection note to send to a recruiter/hiring manager about applying for {title} "
            f"at {company}. "
            "Keep it professional, mention one key skill, and include a polite CTA. "
            f"Candidate resume:\n{resume_text}\nRespond with MESSAGE:\n<message>"
        )
        resp = await self.ai.complete(prompt, temperature=0.2, max_tokens=200)
        message = resp
        if "MESSAGE:" in resp:
            parts = resp.split("MESSAGE:", 1)[1]
            message = parts.strip()
        # enforce max length naively
        if len(message) > max_chars:
            message = message[: max_chars - 1]
        return LinkedinResult(
            message=message,
            generated_at=utc_now_iso(),
        )
