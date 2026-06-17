from main import create_app

app = create_app()
client = app.test_client()
payload = {
    "gaps": [
        {"skill": "Python", "resources": ["https://docs.python.org"]},
    ],
    "resume_id": 1,
    "opportunity_id": 2,
}
resp = client.post("/api/v1/learning/plan", json=payload)
print(resp.status_code)
print(resp.get_data(as_text=True))
