from main import create_app


def test_companies_import(monkeypatch):
    app = create_app()
    client = app.test_client()

    # import two companies, one duplicate domain
    payload = {
        "companies": [
            {"name": "Alpha", "domain": "alpha.test", "website": "https://alpha.test"},
            {"name": "Beta", "domain": "beta.test", "website": "https://beta.test"},
        ]
    }

    resp = client.post("/api/v1/companies/import", json=payload)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True
    assert len(data["data"]["created"]) == 2
