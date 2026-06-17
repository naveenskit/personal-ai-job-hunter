import pytest

from app.agents.outreach_agent import OutreachAgent


class FakeAI:
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
        return "SUBJECT:\nHi hiring team\nBODY:\nI am excited to apply.\nRegards"


@pytest.mark.asyncio
async def test_outreach_agent_generates_subject_and_body():
    agent = OutreachAgent(FakeAI())
    opportunity = {"title": "SDE Intern", "company": "TestCo", "role_type": "intern"}
    result = await agent.generate_email(opportunity, "Resume text here")
    assert "Hi hiring team" in result.subject
    assert "I am excited to apply" in result.body
