# tts-service/tests/test_tts.py
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_tts_empty_text_http():
    response = client.post("/api/tts", json={"text": ""})
    assert response.status_code == 200
    data = response.json()
    assert "error" in data
    assert data["error"] == "empty text"


def test_tts_whitespace_text_http():
    response = client.post("/api/tts", json={"text": "   "})
    assert response.status_code == 200
    data = response.json()
    assert "error" in data
    assert data["error"] == "empty text"