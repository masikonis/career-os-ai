from abc import ABC, abstractmethod
from typing import Dict


class ExtractorInterface(ABC):
    """Interface for data source extractors."""

    @abstractmethod
    def extract_details(self, job_ad_url: str) -> Dict[str, str]:
        """
        Extract company name and website URL from the given job ad URL.

        Args:
            job_ad_url (str): The URL of the job advertisement.

        Returns:
            Dict[str, str]: A dictionary with keys 'company_name' and 'website_url'.
        """
        pass
