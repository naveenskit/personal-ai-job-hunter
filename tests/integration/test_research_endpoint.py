from main import create_app


def test_research_endpoint_monkeypatched(monkeypatch):
    class FakeAI:
        async def complete(self, prompt: str, **kwargs):
            return (
                '{"company_name":"Acme Co","website":"https://acme.co",'
                '"overview":"Acme makes things","industry":"Tools",'
                '"competitors":["Other Co"]}'
            )

    def fake_get_ai_provider(name: str = "gemini"):
        return FakeAI()

    monkeypatch.setattr("app.ai.provider.get_ai_provider", fake_get_ai_provider)
    app = create_app()
    client = app.test_client()
    resp = client.post("/api/v1/research/company", json={"company_name": "Acme Co"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["company_name"] == "Acme Co"
