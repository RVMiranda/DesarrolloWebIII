import pytest, mongomock
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture(autouse=True)
def mock_mongo(monkeypatch):
    client = mongomock.MongoClient()
    db = client["calcdb"]
    def fake_get_db():
        return db
    from app import deps
    monkeypatch.setattr(deps, "get_db", fake_get_db)
    yield

@pytest.fixture
def client():
    return TestClient(app)
