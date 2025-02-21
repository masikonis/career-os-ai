import os
from typing import Any, Optional

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from src.config import config
from src.logger import get_logger

logger = get_logger(__name__)


class ConvexAPIError(Exception):
    """Base exception for Convex API errors"""

    def __init__(self, message: str, code: Optional[str] = None):
        self.code = code
        super().__init__(message)


class ConvexClient:
    def __init__(self, deployment_url: Optional[str] = None):
        self.deployment_url = deployment_url or config.get("CONVEX_URL")
        self._client = httpx.AsyncClient()

        if not self.deployment_url:
            raise ValueError("Missing CONVEX_URL in config")

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self._client.aclose()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True,
    )
    async def _request(
        self, action: str, table: Optional[str] = None, data: Optional[dict] = None
    ) -> dict:
        """Base request handler with retry logic"""
        url = f"{self.deployment_url}/{action}"
        headers = {
            "Content-Type": "application/json",
        }

        logger.debug("Sending request to Convex: %s", url)
        response = await self._client.post(url, json=data, headers=headers)

        if not response.is_success:
            error_data = response.json()
            logger.error("Convex API error: %s", error_data)
            raise ConvexAPIError(
                error_data.get("message", "Unknown error"), code=error_data.get("code")
            )

        return response.json()

    async def query(self, table: str, **filters) -> list[dict]:
        """Base query method for table operations"""
        return await self._request("query", data={"table": table, "filters": filters})

    async def mutation(self, table: str, data: dict) -> str:
        """Base mutation method for insert/update operations"""
        result = await self._request(
            "mutation", data={"table": table, "operation": "insert", "data": data}
        )
        return result["_id"]

    async def ping(self) -> bool:
        """Test connection to Convex"""
        try:
            await self._request("ping")
            return True
        except ConvexAPIError:
            return False
