from main import create_app

app = create_app()
client = app.test_client()

payload = {"companies": [{"name": "Alpha", "domain": "alpha.test", "website": "https://alpha.test"}]}
resp = client.post("/api/v1/companies/import", json=payload)
print('status', resp.status_code)
print('json', resp.get_json())
