from unittest.mock import AsyncMock, patch

import httpx
import pytest
import pytest_asyncio

from src.config import config
from src.convex.client import ConvexClient


@pytest.fixture
def mock_httpx_client():
    with patch("src.convex.client.httpx.AsyncClient") as mock_client:
        mock_instance = AsyncMock()
        mock_client.return_value = mock_instance
        yield mock_instance


@pytest_asyncio.fixture
async def convex_client(mock_httpx_client):
    test_config = {"CONVEX_URL": "https://test.deployment.convex.cloud"}
    with patch.dict(config, test_config, clear=True):
        async with ConvexClient() as client:
            yield client


@pytest.mark.asyncio
async def test_ping_success(convex_client: ConvexClient, mock_httpx_client):
    mock_httpx_client.post.return_value = httpx.Response(200, json={})
    assert await convex_client.ping() is True


@pytest.mark.asyncio
async def test_ping_failure(convex_client: ConvexClient, mock_httpx_client):
    mock_httpx_client.post.return_value = httpx.Response(400, json={})
    assert await convex_client.ping() is False
