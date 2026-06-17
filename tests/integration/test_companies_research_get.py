from main import create_app


def test_companies_research_get_flow():
    app = create_app()
    client = app.test_client()

    # create company via import
    payload = {"companies": [{"name": "Gamma", "domain": "gamma.test", "website": "https://gamma.test"}]}
    resp = client.post("/api/v1/companies/import", json=payload)
    assert resp.status_code == 200
    data = resp.get_json()
    created = data["data"]["created"]
    assert len(created) == 1
    company_id = created[0]["id"]

    # fetch research (empty initially)
    resp2 = client.get(f"/api/v1/companies/{company_id}/research")
    assert resp2.status_code == 200
    data2 = resp2.get_json()
    assert data2["success"] is True
    assert data2["data"]["id"] == company_id
