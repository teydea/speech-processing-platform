# asr-service/tests/test_asr.py
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_asr_empty_audio():
    response = client.post(
        "/api/stt/bytes",
        params={"sr": 16000, "ch": 1},
        content=b""
    )
    assert response.status_code == 200
    data = response.json()
    assert "error" in data
    assert data["error"] == "empty audio"


def test_asr_too_long_audio():
    long_audio = b"\x00" * (16 * 16000 * 2)
    response = client.post(
        "/api/stt/bytes",
        params={"sr": 16000, "ch": 1},
        content=long_audio
    )
    assert response.status_code == 200
    data = response.json()
    assert "error" in data
    assert "audio too long" in data["error"]