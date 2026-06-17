from main import create_app


def test_matching_endpoint(monkeypatch):
    class FakeAI:
        async def complete(self, prompt: str, **kwargs):
            return "85.0"

    def fake_get_ai_provider(name: str = "gemini"):
        return FakeAI()

    monkeypatch.setattr("app.ai.provider.get_ai_provider", fake_get_ai_provider)

    app = create_app()
    client = app.test_client()

    # create resume and opportunity via DB session
    import asyncio

    from app.database.connection import session_scope
    from app.database.repositories.opportunity_repository import OpportunityRepository
    from app.database.repositories.resume_repository import ResumeRepository

    async def setup():
        async with session_scope() as session:
            rr = ResumeRepository(session)
            orr = OpportunityRepository(session)
            resume = await rr.create(
                name="Test Resume",
                file_path="/tmp/test.txt",
                file_hash="xyz",
                raw_text="Experienced python engineer",
                parsed_data="{}",
                is_active=1,
            )
            opp = await orr.create(
                title="Python Dev",
                company_id=None,
                role_type="mid",
                location="Remote",
                location_type="remote",
                country="India",
                job_url="http://example.com/job",
                source="test",
                description="Build APIs",
                content_hash="chash",
                is_active=1,
            )
            return resume.id, opp.id

    resume_id, opp_id = asyncio.run(setup())

    resp = client.post(f"/api/v1/match/resume/{resume_id}/opportunity/{opp_id}")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True
    assert "score" in data["data"]
    assert 0 <= data["data"]["score"] <= 100
