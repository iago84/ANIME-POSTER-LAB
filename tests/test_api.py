"""Smoke tests de la API FastAPI (`web/backend/main.py`)."""
from fastapi.testclient import TestClient

from web.backend.main import app

client = TestClient(app)


def test_root_ok():
    r = client.get("/")
    assert r.status_code == 200
    body = r.json()
    assert body["version"] == "2.5-AI"
    assert "es" in body["languages"]


def test_root_language_switch():
    es = client.get("/", params={"lang": "es"}).json()["message"]
    en = client.get("/", params={"lang": "en"}).json()["message"]
    assert es == "API del Laboratorio de Pósters Anime Experimentales"
    assert es != en


def test_i18n_languages():
    r = client.get("/i18n/languages")
    assert r.status_code == 200
    assert r.json()["languages"] == ["es", "en", "fr", "ja", "hi"]


def test_health_ok():
    r = client.get("/health/")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["checks"]["engine"] is True
    assert r.headers["cache-control"] == "no-store"


def test_techniques_catalog():
    r = client.get("/techniques")
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 11
    assert {"id", "name", "description", "keywords", "palette_example"} <= set(data[0])
    for item in data:
        assert len(item["palette_example"]) == 3


def test_generate_is_deterministic_with_seed():
    payload = {"concept": "cyberpunk samurai", "seed": 42}
    r1 = client.post("/generate", json=payload)
    r2 = client.post("/generate", json=payload)
    assert r1.status_code == 200
    assert r1.json()["success"] is True
    assert r1.json()["data"] == r2.json()["data"]


def test_generate_video_prompt():
    r = client.post("/generate/video-prompt", json={"concept": "vaporwave sunset"})
    assert r.status_code == 200
    body = r.json()
    assert body["success"] is True
    assert "TikTok autocut" in body["video_prompt"]
    assert body["technique"] == "VAPORWAVE"


def test_cors_only_allows_listed_origins():
    # Un origen local permitido recibe la cabecera...
    ok = client.get("/", headers={"Origin": "http://localhost:5173"})
    assert ok.headers.get("access-control-allow-origin") == "http://localhost:5173"
    # ...y un origen arbitrario NO queda abierto.
    malo = client.get("/", headers={"Origin": "http://evil.example"})
    assert malo.headers.get("access-control-allow-origin") != "http://evil.example"
