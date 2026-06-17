import pytest

from app.agents.linkedin_agent import LinkedinAgent


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
        return (
            "MESSAGE:\nHi, I'm interested in this role. I have experience in Python. "
            "Can we connect?"
        )


@pytest.mark.asyncio
async def test_linkedin_agent_generates_short_message():
    agent = LinkedinAgent(FakeAI())
    opportunity = {"title": "SDE Intern", "company": "TestCo"}
    result = await agent.generate_message(opportunity, "Resume text here")
    assert "Hi, I'm interested" in result.message
    assert len(result.message) <= 300
