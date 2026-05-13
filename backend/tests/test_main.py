"""
Automated tests for the Sentiment Analysis API.
These tests run with USE_MOCK_LLM=true to bypass the Gemini API.

Usage:
    cd backend
    USE_MOCK_LLM=true pytest tests/test_main.py -v
"""
import os
import pytest
from httpx import AsyncClient, ASGITransport

# Force mock mode BEFORE importing the app
os.environ["USE_MOCK_LLM"] = "true"

from main import app  # noqa: E402


@pytest.mark.asyncio
async def test_analyze_returns_valid_structure():
    """Verify the /analyze endpoint returns the expected JSON structure."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/analyze", json={"text": "I am happy. I am sad."})

    assert response.status_code == 200
    data = response.json()

    # Top-level keys must exist
    assert "segments" in data
    assert "sentiment" in data
    assert "entropy" in data
    assert "analyses" in data

    # Arrays must be non-empty and equal length
    assert len(data["segments"]) > 0
    assert len(data["segments"]) == len(data["sentiment"])
    assert len(data["segments"]) == len(data["entropy"])

    # Analyses must contain all 3 personas
    assert "friend" in data["analyses"]
    assert "mentor" in data["analyses"]
    assert "expert" in data["analyses"]

    # Each persona analysis must be a non-empty string
    for persona in ["friend", "mentor", "expert"]:
        assert isinstance(data["analyses"][persona], str)
        assert len(data["analyses"][persona]) > 0


@pytest.mark.asyncio
async def test_analyze_empty_text_returns_400():
    """Verify that submitting empty text returns a 400 error."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/analyze", json={"text": ""})

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_sentiment_scores_in_valid_range():
    """Verify all sentiment scores are within the [-1.0, 1.0] range."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/analyze", json={"text": "Great day. Terrible weather. Okay mood."})

    data = response.json()
    for score in data["sentiment"]:
        assert -1.0 <= score <= 1.0


@pytest.mark.asyncio
async def test_entropy_scores_are_non_negative():
    """Verify all entropy scores are >= 0 (Shannon entropy cannot be negative)."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/analyze", json={"text": "Hello world. Goodbye world."})

    data = response.json()
    for score in data["entropy"]:
        assert score >= 0.0
