import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    # TestClient позволяет делать HTTP-запросы напрямую к FastAPI без реального запуска сервера
    with TestClient(app) as test_client:
        yield test_client