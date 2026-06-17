import io

from main import create_app


def test_companies_import_csv():
    app = create_app()
    client = app.test_client()

    csv_content = (
        "name,domain,website\n"
        "Alpha,alpha.csv,https://alpha.csv\n"
        "Beta,beta.csv,https://beta.csv\n"
    )
    data = {"file": (io.BytesIO(csv_content.encode("utf-8")), "companies.csv")}
    resp = client.post(
        "/api/v1/companies/import/csv", data=data, content_type="multipart/form-data"
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True
    assert len(data["data"]["created"]) == 2
