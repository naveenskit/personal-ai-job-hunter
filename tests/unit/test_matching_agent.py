from app.agents.matching_agent import MatchingAgent


class FakeAIForMatching:
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
        return "75.0"


async def test_matching_agent_returns_score_in_range(db_session):
    # create a resume and opportunity
    from app.database.repositories.opportunity_repository import OpportunityRepository
    from app.database.repositories.resume_repository import ResumeRepository

    resume_repo = ResumeRepository(db_session)
    opp_repo = OpportunityRepository(db_session)

    resume = await resume_repo.create(
        name="Test Resume",
        file_path="/tmp/test.txt",
        file_hash="abc123",
        raw_text="Python backend engineer",
        parsed_data="{}",
        is_active=1,
    )
    opp = await opp_repo.create(
        title="Senior Python Engineer",
        company_id=None,
        role_type="senior",
        location="Bengaluru",
        location_type="onsite",
        country="India",
        job_url="http://example.com/job1",
        source="test",
        description="Looking for Python expert",
        content_hash="def456",
        is_active=1,
    )

    agent = MatchingAgent(db_session, FakeAIForMatching())
    score = await agent.match_resume_to_opportunity(resume.id, opp.id)
    assert 0.0 <= score <= 100.0


async def test_matching_agent_returns_zero_for_missing_resume(db_session):
    agent = MatchingAgent(db_session, FakeAIForMatching())
    score = await agent.match_resume_to_opportunity(999, 999)
    assert score == 0.0
