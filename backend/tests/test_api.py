"""
API Tests using pytest + httpx
Run: pytest backend/tests/ -v
"""

import pytest
import asyncio
from httpx import AsyncClient, ASGITransport

# We import the app but skip DB connection in tests
import os
os.environ["MONGODB_URI"] = "mongodb://localhost:27017"

from app.main import app


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


@pytest.mark.asyncio
async def test_health(client):
    r = await client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_predict_fake(client):
    payload = {
        "headline": "SHOCKING: Deep state conspiracy revealed!!!",
        "article": (
            "Anonymous sources confirm that the government has been hiding a massive conspiracy "
            "from the public. This bombshell revelation will shock you. Share before deleted! "
            "The mainstream media does not want you to know this truth. Wake up sheeple! "
            "They are lying to all of us every single day about everything."
        ),
    }
    r = await client.post("/api/predict/", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert "prediction" in data
    assert data["prediction"] in ("FAKE", "REAL")
    assert 0 <= data["confidence"] <= 1
    assert "emotion_score" in data
    assert "feature_importance" in data


@pytest.mark.asyncio
async def test_predict_real(client):
    payload = {
        "headline": "Federal Reserve raises interest rates by 0.25%",
        "article": (
            "The Federal Reserve raised its benchmark interest rate by 0.25 percentage points on "
            "Wednesday, as policymakers continued their campaign to bring inflation down. "
            "Chair Jerome Powell said the committee would continue to monitor data carefully."
        ),
        "source_url": "https://reuters.com",
    }
    r = await client.post("/api/predict/", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert "credibility_score" in data
    assert "contradiction_score" in data


@pytest.mark.asyncio
async def test_predict_short_article(client):
    r = await client.post("/api/predict/", json={
        "headline": "Test", "article": "Too short"
    })
    assert r.status_code == 422  # Pydantic validation error


@pytest.mark.asyncio
async def test_analytics_summary(client):
    r = await client.get("/api/analytics/summary")
    assert r.status_code == 200
    data = r.json()
    assert "total_predictions" in data
    assert "fake_percentage" in data


@pytest.mark.asyncio
async def test_source_check(client):
    r = await client.get("/api/sources/check?url=https://reuters.com/article")
    assert r.status_code == 200
    data = r.json()
    assert data["trust_score"] >= 0.8


@pytest.mark.asyncio
async def test_source_leaderboard(client):
    r = await client.get("/api/sources/leaderboard")
    assert r.status_code == 200
    data = r.json()
    assert "most_trusted" in data
    assert "least_trusted" in data
    assert len(data["most_trusted"]) > 0


@pytest.mark.asyncio
async def test_model_metrics(client):
    r = await client.get("/api/metrics/evaluation")
    assert r.status_code == 200
    data = r.json()
    assert "models" in data
    assert "bert" in data["models"]


@pytest.mark.asyncio
async def test_sample_graph(client):
    r = await client.get("/api/graphs/sample")
    assert r.status_code == 200
    data = r.json()
    assert "nodes" in data
    assert "edges" in data
