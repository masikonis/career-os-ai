from abc import ABC, abstractmethod
from typing import Dict


class ExtractorInterface(ABC):
    """Interface for data source extractors."""

    @abstractmethod
    def extract_details(self, html_content: str) -> Dict[str, str]:
        """
        Extract company name and website URL from the HTML content.

        Returns:
            A dictionary with keys 'company_name' and 'website_url'.
        """
        pass
