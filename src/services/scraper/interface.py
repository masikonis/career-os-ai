from abc import ABC, abstractmethod
from typing import Optional


class ScraperInterface(ABC):
    """Base interface for web scraping providers."""

    @abstractmethod
    def fetch_content(self, url: str, timeout: int = 10) -> Optional[str]:
        """Fetch content from URL with error handling and retries.

        Args:
            url: URL to fetch
            timeout: Request timeout in seconds

        Returns:
            str: HTML content if successful, None if failed
        """
        pass
