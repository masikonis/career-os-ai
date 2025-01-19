from typing import Dict
from urllib.parse import urlparse

from src.logger import get_logger

from .data_sources.extractor_interface import ExtractorInterface
from .data_sources.weworkremotely_extractor import WeWorkRemotelyExtractor

logger = get_logger(__name__)


class JobAdExtractor:
    """Central extractor that delegates to specific extractors based on the job ad URL."""

    def __init__(self):
        logger.info("JobAdExtractor initialized.")
        # Map domain names to their corresponding extractor instances
        self.extractors: Dict[str, ExtractorInterface] = {
            "weworkremotely.com": WeWorkRemotelyExtractor(),
        }

    def extract_details(self, job_ad_url: str) -> Dict[str, str]:
        """Extract company details from a job advertisement URL.

        Args:
            job_ad_url (str): The URL of the job advertisement.

        Returns:
            Dict[str, str]: A dictionary containing 'company_name' and 'website_url'.
        """
        domain = self.get_domain(job_ad_url)
        extractor = self.get_extractor(domain)

        if not extractor:
            logger.error(f"No extractor found for domain: {domain}")
            return {"company_name": "", "website_url": ""}

        return extractor.extract_details(job_ad_url)

    def get_extractor(self, domain: str) -> ExtractorInterface:
        """Retrieve the appropriate extractor based on the domain.

        Args:
            domain (str): The domain extracted from the job ad URL.

        Returns:
            ExtractorInterface: An instance of the corresponding extractor, or None if not found.
        """
        return self.extractors.get(domain)

    @staticmethod
    def get_domain(url: str) -> str:
        """Extract the domain from a given URL.

        Args:
            url (str): The URL to extract the domain from.

        Returns:
            str: The extracted domain in lowercase.
        """
        parsed_url = urlparse(url)
        return parsed_url.netloc.lower()
