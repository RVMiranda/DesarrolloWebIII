import pytest
import mongomock
from fastapi.testclient import TestClient

@pytest.fixture(autouse=True, scope="function")
def mock_mongo(monkeypatch):
    """Mock de MongoDB usando mongomock para todos los tests"""
    
    # CLAVE: Resetear el cliente global
    from app import deps
    deps._client = None
    
    # Crear mock client
    mock_client = mongomock.MongoClient()
    mock_db = mock_client["calcdb"]
    
    # Patchear get_db para que devuelva el mock
    def fake_get_db():
        return mock_db
    
    monkeypatch.setattr(deps, "get_db", fake_get_db)
    
    yield mock_db
    
    # Limpiar
    mock_client.drop_database("calcdb")
    deps._client = None


@pytest.fixture
def client():
    """Cliente de pruebas de FastAPI"""
    from app.main import app
    return TestClient(app)