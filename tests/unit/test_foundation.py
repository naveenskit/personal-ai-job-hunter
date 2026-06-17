from app.core.types import ApplicationStatus
from app.database.models import Application
from app.database.repositories.resume_repository import ResumeRepository


async def test_resume_repository_create_and_lookup(db_session):
    repo = ResumeRepository(db_session)
    resume = await repo.create(
        name="Backend Resume",
        file_path="resume/backend.pdf",
        file_hash="abc123",
    )

    found = await repo.get_by_hash("abc123")

    assert found is not None
    assert found.id == resume.id
    assert found.name == "Backend Resume"


def test_application_status_values_are_stable():
    assert ApplicationStatus.DISCOVERED.value == "DISCOVERED"
    application = Application(
        status=ApplicationStatus.MATCHED.value,
        opportunity_id=1,
        resume_id=1,
    )
    assert application.status == "MATCHED"
