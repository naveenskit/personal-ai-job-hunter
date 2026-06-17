import asyncio

from app.agents.research_agent import ResearchAgent


class FakeAI:
    async def complete(self, prompt: str, **kwargs):
        return (
            '{"company_name":"TestCo","website":"https://test.co","overview":"we do x",'
            '"tech_stack":["Py","python ","JS","JavaScript","React.js","node.js"]}'
        )


def test_normalize_tech_stack_and_analyze():
    ai = FakeAI()
    agent = ResearchAgent(ai)
    res = asyncio.run(agent.analyze(company_name="TestCo"))
    # normalized tech stack should be lowercase, deduped and canonical
    assert isinstance(res.tech_stack, list)
    normalized = agent._normalize_tech_stack(res.tech_stack)
    assert "python" in normalized
    assert "javascript" in normalized
    assert "react" in normalized
    assert "node" in normalized