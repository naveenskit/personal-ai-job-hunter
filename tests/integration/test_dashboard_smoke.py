import json

from main import create_app


def test_dashboard_smoke_loads_and_runs_job():
    app = create_app()
    client = app.test_client()

    # load dashboard page
    r = client.get('/dashboard/')
    assert r.status_code == 200
    assert b'NIRANTAR' in r.data or b'dashboard' in r.data.lower()

    # stats endpoint
    r = client.get('/dashboard/api/stats')
    assert r.status_code == 200
    data = r.get_json()
    assert 'resumes' in data

    # trigger a manual job run
    r = client.post('/dashboard/api/run-job', data=json.dumps({"job_name": "smoke_test"}), content_type='application/json')
    assert r.status_code == 200
    jr = r.get_json()
    assert jr.get('ok') is True
