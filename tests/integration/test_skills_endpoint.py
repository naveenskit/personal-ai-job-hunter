from main import create_app


class DummyAI:
    async def complete(self, prompt: str, temperature=0.0, max_tokens=300):
        return "Python|missing|critical|https://docs.python.org\nSQL|weak|important|https://www.sqltutorial.org"


def test_skills_analyze_endpoint(monkeypatch):
    app = create_app()
    monkeypatch.setattr("app.skills.routes.get_ai_provider", lambda: DummyAI())
    client = app.test_client()
    payload = {"resume": "Experienced Java dev", "job_description": "We need Python and SQL"}
    resp = client.post("/api/v1/skills/analyze", json=payload)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True
    assert "gaps" in data["data"]
    assert any(g["skill"] == "Python" for g in data["data"]["gaps"])
