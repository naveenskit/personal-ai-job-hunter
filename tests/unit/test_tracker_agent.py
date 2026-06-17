
from app.agents.tracker_agent import TrackerAgent
from app.database.repositories.opportunity_repository import OpportunityRepository
from app.database.repositories.resume_repository import ResumeRepository


async def test_create_and_transition_application(db_session):
    # create opportunity and resume
    opp_repo = OpportunityRepository(db_session)
    resume_repo = ResumeRepository(db_session)

    opp = await opp_repo.create(
        title="SDE Intern",
        role_type="intern",
        location="Remote",
        location_type="remote",
        job_url="http://example.com/1",
        source="test",
        description="",
        requirements="[]",
        content_hash="hash1",
    )

    resume = await resume_repo.create(name="Test Resume", file_path="/res.pdf", file_hash="h1")

    agent = TrackerAgent(db_session)
    app = await agent.create_application(opp.id, resume.id, source="test")
    assert app is not None
    assert app.status == "DISCOVERED"

    updated = await agent.transition(app.id, "APPLIED", details='{"note":"applied"}')
    assert updated.status == "APPLIED"
