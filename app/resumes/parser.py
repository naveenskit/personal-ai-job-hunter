import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from app.ai.provider import AIProvider
from app.core.exceptions import ExternalServiceError, ValidationError


class ParsedResume(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    location: str | None = None
    summary: str | None = None
    education: list[dict[str, Any]] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    projects: list[dict[str, Any]] = Field(default_factory=list)
    experience: list[dict[str, Any]] = Field(default_factory=list)
    achievements: list[str] = Field(default_factory=list)
    role_signals: list[str] = Field(default_factory=list)
    seniority_signal: str | None = None


class ResumeParser:
    def __init__(self, ai_provider: AIProvider, *, prompt_path: Path | None = None) -> None:
        self.ai_provider = ai_provider
        self.prompt_path = prompt_path or Path("app/ai/prompts/resume_parser.txt")

    async def parse(self, raw_text: str) -> ParsedResume:
        if not raw_text.strip():
            raise ValidationError("Cannot parse an empty resume")

        prompt_template = self.prompt_path.read_text(encoding="utf-8")
        prompt = prompt_template.replace("{{RESUME_TEXT}}", raw_text[:16000])
        response = await self.ai_provider.complete(
            prompt,
            system="You are a precise resume parser. Return strict JSON only.",
            temperature=0.1,
            max_tokens=2500,
        )

        try:
            payload = _loads_json_object(response)
            return ParsedResume.model_validate(payload)
        except (json.JSONDecodeError, ValueError) as exc:
            raise ExternalServiceError(
                "AI resume parser returned invalid JSON",
                details={"response_preview": response[:500]},
            ) from exc


def _loads_json_object(text: str) -> dict[str, Any]:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.removeprefix("```json").removeprefix("```").strip()
        cleaned = cleaned.removesuffix("```").strip()

    payload = json.loads(cleaned)
    if not isinstance(payload, dict):
        raise ValueError("Expected a JSON object")
    return payload
