import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.provider import AIProvider
from app.core.exceptions import ValidationError
from app.core.types import utc_now_iso
from app.database.models import Resume
from app.database.repositories.resume_repository import ResumeRepository
from app.resumes.embeddings import pack_embedding
from app.resumes.parser import ParsedResume, ResumeParser
from app.resumes.text_extractor import extract_resume_text


@dataclass(slots=True)
class ResumeParseResult:
    resume: Resume
    parsed: ParsedResume
    created: bool


class ResumeIngestionService:
    def __init__(self, session: AsyncSession, ai_provider: AIProvider) -> None:
        self.session = session
        self.ai_provider = ai_provider
        self.repository = ResumeRepository(session)
        self.parser = ResumeParser(ai_provider)

    async def ingest_file(
        self,
        file_path: Path,
        *,
        name: str | None = None,
        role_tags: list[str] | None = None,
        set_active: bool = True,
    ) -> ResumeParseResult:
        raw_bytes = file_path.read_bytes()
        file_hash = hashlib.sha256(raw_bytes).hexdigest()
        existing = await self.repository.get_by_hash(file_hash)
        if existing is not None:
            parsed = _parsed_from_resume(existing)
            return ResumeParseResult(resume=existing, parsed=parsed, created=False)

        raw_text = extract_resume_text(file_path)
        parsed = await self.parser.parse(raw_text)
        embedding = await self.ai_provider.embed(_embedding_text(raw_text, parsed))

        resume = await self.repository.create(
            name=name or _default_resume_name(file_path, parsed),
            file_path=str(file_path),
            file_hash=file_hash,
            role_tags=json.dumps(role_tags or []),
            raw_text=raw_text,
            parsed_data=parsed.model_dump_json(),
            embedding=pack_embedding(embedding),
            is_active=1 if set_active else 0,
        )

        if set_active:
            await self.repository.set_active(resume.id)

        return ResumeParseResult(resume=resume, parsed=parsed, created=True)

    async def reanalyze(self, resume_id: int) -> ResumeParseResult:
        resume = await self.repository.get(resume_id)
        if resume is None:
            raise ValidationError("Resume not found", details={"resume_id": resume_id})
        if not resume.raw_text:
            raise ValidationError(
                "Resume has no raw text to analyze",
                details={"resume_id": resume_id},
            )

        parsed = await self.parser.parse(resume.raw_text)
        embedding = await self.ai_provider.embed(_embedding_text(resume.raw_text, parsed))
        await self.repository.update(
            resume,
            parsed_data=parsed.model_dump_json(),
            embedding=pack_embedding(embedding),
            updated_at=utc_now_iso(),
        )
        return ResumeParseResult(resume=resume, parsed=parsed, created=False)


def _default_resume_name(file_path: Path, parsed: ParsedResume) -> str:
    if parsed.name:
        return f"{parsed.name} Resume"
    return file_path.stem.replace("_", " ").replace("-", " ").title()


def _embedding_text(raw_text: str, parsed: ParsedResume) -> str:
    skills = ", ".join(parsed.skills)
    projects = " ".join(str(project.get("name", "")) for project in parsed.projects)
    return f"{parsed.summary or ''}\nSkills: {skills}\nProjects: {projects}\n\n{raw_text[:4000]}"


def _parsed_from_resume(resume: Resume) -> ParsedResume:
    try:
        return ParsedResume.model_validate_json(resume.parsed_data)
    except ValueError:
        return ParsedResume()
