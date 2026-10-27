import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    assert client.get("/health").json()["status"] == "ok"


def test_summary_endpoint():
    s = client.get("/api/summary").json()
    assert s["jumlah_paket"] == 24
    assert s["jumlah_berbendera"] > 0


def test_search_endpoint():
    d = client.get("/api/packages", params={"q": "laboratorium"}).json()
    assert d["count"] >= 1
    assert all("laboratorium" in p["nama_paket"].lower() for p in d["packages"])


def test_flagged_only_endpoint():
    d = client.get("/api/packages", params={"hanya_berbendera": True}).json()
    assert d["count"] > 0
    assert all(p["flags"] for p in d["packages"])


def test_map_endpoint():
    d = client.get("/api/map").json()
    provinces = [p["provinsi"] for p in d["points"]]
    assert "Jawa Timur" in provinces
    assert all("latitude" in p and "longitude" in p for p in d["points"])
