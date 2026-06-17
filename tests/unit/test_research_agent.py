import asyncio

from app.agents.research_agent import ResearchAgent


class FakeAI:
    def __init__(self, resp: str) -> None:
        self._resp = resp

    async def complete(self, prompt: str, **kwargs) -> str:
        return self._resp


def test_research_agent_parses_json():
    resp = (
        '{"company_name":"Acme Corp","website":"https://acme.example",'
        '"overview":"Makes anvils","industry":"Manufacturing",'
        '"competitors":["Roadrunner Inc"]}'
    )
    ai = FakeAI(resp)
    agent = ResearchAgent(ai)

    result = asyncio.run(agent.analyze(company_name="Acme Corp"))
    assert result.company_name == "Acme Corp"
    assert "anvils" in result.overview
    assert result.competitors == ["Roadrunner Inc"]
