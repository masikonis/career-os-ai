from abc import ABC, abstractmethod
from typing import List


class ScraperInterface(ABC):
    """Base interface for job board scrapers.

    Requirements:
    - Handle network errors gracefully
    - Implement logging
    - Return empty list on errors
    - Respect rate limits
    """

    @abstractmethod
    def scrape_job_urls(self) -> List[str]:
        """Scrape job listing URLs from the source.

        Returns:
            List[str]: List of job posting URLs
        """
        raise NotImplementedError
