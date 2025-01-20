from typing import Dict
from urllib.parse import urlparse

from pydantic import HttpUrl

from src.logger import get_logger
from src.models.company.company_info import CompanyInfo
from src.models.job.job_details import JobDetails

from .data_sources.extractor_interface import ExtractorInterface
from .data_sources.weworkremotely_extractor import WeWorkRemotelyExtractor

logger = get_logger(__name__)


class JobAdExtractor:
    """Delegates job ad extraction to specific extractors based on URL."""

    def __init__(self):
        self.extractors: Dict[str, ExtractorInterface] = {
            "weworkremotely.com": WeWorkRemotelyExtractor(),
        }
        logger.info("JobAdExtractor initialized")

    def extract_details(self, job_ad_url: str) -> JobDetails:
        """Extract job details from URL."""
        if not job_ad_url:
            logger.error("Empty URL provided")
            return self._empty_response()

        try:
            domain = self.get_domain(job_ad_url)
            extractor = self.get_extractor(domain)

            if not extractor:
                logger.error(f"No extractor for domain: {domain}")
                return self._empty_response()

            return extractor.extract_details(job_ad_url)
        except Exception as e:
            logger.error(f"Error extracting details: {str(e)}")
            return self._empty_response()

    def get_extractor(self, domain: str) -> ExtractorInterface | None:
        """Get extractor for domain."""
        return self.extractors.get(domain)

    @staticmethod
    def get_domain(url: str) -> str:
        """Extract domain from URL."""
        return urlparse(url).netloc.lower()

    @staticmethod
    def _empty_response() -> JobDetails:
        """Return empty response."""
        return JobDetails(
            company=CompanyInfo(company_name="", website_url=""),
            title="",
            description="",
            url="",
        )
