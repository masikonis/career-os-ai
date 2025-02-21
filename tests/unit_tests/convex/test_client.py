from unittest.mock import AsyncMock, patch

import httpx
import pytest
import pytest_asyncio

from src.config import config
from src.convex.client import ConvexAPIError, ConvexClient


@pytest.fixture
def mock_httpx_client():
    with patch("src.convex.client.httpx.AsyncClient") as mock_client:
        mock_instance = AsyncMock()
        mock_client.return_value = mock_instance
        yield mock_instance


@pytest_asyncio.fixture
async def convex_client(mock_httpx_client):
    test_config = {
        "CONVEX_DEPLOYMENT_URL": "https://test.deployment.convex.cloud",
        "CONVEX_API_KEY": "test_api_key",
    }
    with patch.dict(config, test_config, clear=True):
        async with ConvexClient() as client:
            yield client


@pytest.mark.asyncio
async def test_client_initialization_failure():
    with patch.dict(config, {}, clear=True), pytest.raises(ValueError):
        ConvexClient()


@pytest.mark.asyncio
async def test_ping_success(convex_client: ConvexClient, mock_httpx_client):
    mock_httpx_client.post.return_value = httpx.Response(200, json={})
    assert await convex_client.ping() is True


@pytest.mark.asyncio
async def test_ping_failure(convex_client: ConvexClient, mock_httpx_client):
    mock_httpx_client.post.return_value = httpx.Response(400, json={})
    assert await convex_client.ping() is False


@pytest.mark.asyncio
async def test_query_success(convex_client: ConvexClient, mock_httpx_client):
    test_data = [{"_id": "123", "name": "Test Co"}]
    mock_httpx_client.post.return_value = httpx.Response(200, json=test_data)

    result = await convex_client.query("companies", name="Test Co")
    assert result == test_data


@pytest.mark.asyncio
async def test_mutation_success(convex_client: ConvexClient, mock_httpx_client):
    test_data = {"_id": "abc123"}
    mock_httpx_client.post.return_value = httpx.Response(200, json=test_data)

    doc_id = await convex_client.mutation("companies", {"name": "Test Co"})
    assert doc_id == "abc123"


@pytest.mark.asyncio
async def test_api_error_handling(convex_client: ConvexClient, mock_httpx_client):
    mock_httpx_client.post.return_value = httpx.Response(
        400, json={"code": "invalid_request", "message": "Test error"}
    )

    with pytest.raises(ConvexAPIError) as exc_info:
        await convex_client.query("companies")

    assert exc_info.value.code == "invalid_request"
    assert "Test error" in str(exc_info.value)


@pytest.mark.asyncio
async def test_retry_logic(convex_client: ConvexClient, mock_httpx_client):
    mock_httpx_client.post.side_effect = [
        httpx.Response(502, json={}),
        httpx.Response(503, json={}),
        httpx.Response(200, json=[]),
    ]

    result = await convex_client.query("companies")
    assert mock_httpx_client.post.call_count == 3
    assert result == []
