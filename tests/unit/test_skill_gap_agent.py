import pytest

from app.agents.skill_gap_agent import SkillGapAgent


class DummyAI:
    async def complete(self, prompt: str, temperature=0.0, max_tokens=300):
        # return two skills in the simple pipe format
        return "Python|missing|critical|https://docs.python.org\nSQL|weak|important|https://www.sqltutorial.org"


@pytest.mark.asyncio
async def test_skill_gap_agent_basic():
    ai = DummyAI()
    agent = SkillGapAgent(ai)
    res = await agent.analyze(
        "I have experience with Java",
        "We need Python and SQL experience",
        resume_id=1,
        opportunity_id=2,
    )
    assert res.resume_id == 1
    assert res.opportunity_id == 2
    assert len(res.gaps) == 2
    assert any(g.skill == "Python" for g in res.gaps)
    assert any(g.skill == "SQL" for g in res.gaps)
