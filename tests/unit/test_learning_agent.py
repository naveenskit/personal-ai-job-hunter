import pytest

from app.agents.learning_agent import LearningAgent


@pytest.mark.asyncio
async def test_learning_agent_creates_plan_from_gaps():
    agent = LearningAgent()
    gaps = [
        {"skill": "Python", "resources": ["https://docs.python.org"]},
        {"skill": "SQL", "resources": ["https://sql.com"]},
    ]
    plan = await agent.create_plan(gaps=gaps, resume_id=1, opportunity_id=2)
    assert plan.resume_id == 1
    assert plan.opportunity_id == 2
    assert len(plan.steps) == 2
    assert any(s.topic == "Python" for s in plan.steps)