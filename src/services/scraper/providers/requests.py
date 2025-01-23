from typing import Optional

import requests

from src.logger import get_logger
from src.services.scraper.interface import ScraperInterface

logger = get_logger(__name__)


class RequestsProvider(ScraperInterface):
    def fetch_content(self, url: str, timeout: int = 10) -> Optional[str]:
        """Fetch content from URL using requests library."""
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logger.error(f"Error fetching URL {url}: {str(e)}")
            return None
