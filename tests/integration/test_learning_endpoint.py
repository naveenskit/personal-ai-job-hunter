import asyncio

from app.database.connection import init_db
from main import create_app


def test_learning_plan_persistence():
    app = create_app()
    # ensure DB tables present
    asyncio.run(init_db())
    client = app.test_client()
    payload = {
        "gaps": [
            {"skill": "Python", "resources": ["https://docs.python.org"]},
            {"skill": "SQL", "resources": ["https://sql.com"]},
        ],
        "resume_id": 1,
        "opportunity_id": 2,
    }
    resp = client.post("/api/v1/learning/plan", json=payload)
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["success"] is True
    plan_id = data["data"]["id"]

    async def fetch():
        from app.database.connection import session_scope
        from app.database.repositories.learning_repository import LearningRepository

        async with session_scope() as session:
            repo = LearningRepository(session)
            item = await repo.get(plan_id)
            return item

    item = asyncio.run(fetch())
    assert item is not None
    assert item.id == plan_id
 