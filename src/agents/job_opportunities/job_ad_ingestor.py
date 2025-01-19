from typing import Dict

from src.logger import get_logger

from .data_sources.extractor_interface import ExtractorInterface
from .data_sources.weworkremotely_extractor import WeWorkRemotelyExtractor

logger = get_logger(__name__)


class JobAdIngestor:
    """Agent that ingests raw content from a job advertisement."""

    def __init__(self):
        logger.info("JobAdIngestor initialized.")
        self.extractors = {
            "weworkremotely.com": WeWorkRemotelyExtractor(),
        }

    def get_extractor(self, domain: str) -> ExtractorInterface:
        extractor = self.extractors.get(domain)
        if not extractor:
            logger.error(f"No extractor found for domain: {domain}")
            raise ValueError(f"No extractor available for domain: {domain}")
        return extractor

    def ingest_content(self, job_ad_url: str) -> Dict[str, str]:
        """Ingest the raw content from a job advertisement URL and extract company details."""
        try:
            logger.info(f"Ingesting job ad from URL: {job_ad_url}")
            domain = self.get_domain(job_ad_url)
            extractor = self.get_extractor(domain)
            details = extractor.extract_details(job_ad_url)
            logger.info(
                "Completed ingestion and extraction of job advertisement content."
            )
            return details
        except Exception as e:
            logger.error(f"Error ingesting job ad content: {str(e)}")
            raise

    def get_domain(self, url: str) -> str:
        from urllib.parse import urlparse

        parsed_url = urlparse(url)
        return parsed_url.netloc.lower()
