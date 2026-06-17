import json
from pathlib import Path

from app.database.repositories.resume_repository import ResumeRepository
from app.resumes.embeddings import pack_embedding, unpack_embedding
from app.resumes.parser import ResumeParser
from app.resumes.service import ResumeIngestionService
from app.resumes.text_extractor import extract_resume_text


class FakeAIProvider:
    @property
    def model_name(self) -> str:
        return "fake"

    async def complete(
        self,
        prompt: str,
        system: str = "",
        temperature: float = 0.3,
        max_tokens: int = 2000,
    ) -> str:
        return json.dumps(
            {
                "name": "Arjun Sharma",
                "email": "arjun@example.com",
                "phone": None,
                "location": "Jaipur",
                "summary": "Backend-focused CS student",
                "education": [],
                "skills": ["Python", "FastAPI", "Docker"],
                "projects": [
                    {
                        "name": "Job Agent",
                        "description": "AI job search assistant",
                        "technologies": ["Python"],
                        "impact": "Automated tracking",
                    }
                ],
                "experience": [],
                "achievements": [],
                "role_signals": ["backend", "devops"],
                "seniority_signal": "student",
            }
        )

    async def embed(self, text: str) -> list[float]:
        return [0.1, 0.2, 0.3]


async def test_resume_parser_returns_structured_data(tmp_path: Path):
    prompt_path = tmp_path / "prompt.txt"
    prompt_path.write_text("Parse this: {{RESUME_TEXT}}", encoding="utf-8")
    parser = ResumeParser(FakeAIProvider(), prompt_path=prompt_path)

    parsed = await parser.parse("Python Docker backend developer")

    assert parsed.name == "Arjun Sharma"
    assert "Python" in parsed.skills
    assert parsed.role_signals == ["backend", "devops"]


async def test_resume_ingestion_persists_resume(db_session, tmp_path: Path):
    resume_path = tmp_path / "resume.txt"
    resume_path.write_text("Arjun\nPython Docker backend developer", encoding="utf-8")
    service = ResumeIngestionService(db_session, FakeAIProvider())
    service.parser.prompt_path = tmp_path / "prompt.txt"
    service.parser.prompt_path.write_text("Parse this: {{RESUME_TEXT}}", encoding="utf-8")

    result = await service.ingest_file(resume_path, role_tags=["backend"])

    repo = ResumeRepository(db_session)
    stored = await repo.get_by_hash(result.resume.file_hash)
    assert result.created is True
    assert stored is not None
    assert stored.raw_text == "Arjun\nPython Docker backend developer"
    assert unpack_embedding(stored.embedding) == unpack_embedding(pack_embedding([0.1, 0.2, 0.3]))


def test_text_extractor_reads_text_resume(tmp_path: Path):
    resume_path = tmp_path / "resume.txt"
    resume_path.write_text("hello resume", encoding="utf-8")

    assert extract_resume_text(resume_path) == "hello resume"
