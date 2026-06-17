from main import create_app


def test_companies_import_csv_with_header_map():
    app = create_app()
    client = app.test_client()

    # CSV uses headers CompanyName and DomainName which need mapping
    csv_content = (
        "CompanyName,DomainName,Site\n"
        "Alpha,alpha.opt,https://alpha.opt\n"
        "Beta,beta.opt,https://beta.opt\n"
    )
    payload = {
        "csv": csv_content,
        "header_map": {"name": "CompanyName", "domain": "DomainName", "website": "Site"},
    }
    resp = client.post("/api/v1/companies/import/csv", json=payload)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True
    assert len(data["data"]["created"]) == 2
