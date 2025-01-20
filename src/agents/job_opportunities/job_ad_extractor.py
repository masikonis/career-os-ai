from typing import Dict

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, HttpUrl

from src.logger import get_logger
from src.models.company.company_info import CompanyInfo
from src.models.job.job_details import JobDetails
from src.models.job.job_location import LocationType, LocationTypeResponse
from src.services.llm.factory import LLMFactory
from src.utilities.url import get_domain

from .data_sources.extractor_interface import ExtractorInterface
from .data_sources.weworkremotely_extractor import WeWorkRemotelyExtractor

logger = get_logger(__name__)


class JobAdExtractor:
    """Delegates job ad extraction to specific extractors based on URL."""

    def __init__(self, model_type: str = "basic", temperature: float = 0.0):
        self.extractors: Dict[str, ExtractorInterface] = {
            "weworkremotely.com": WeWorkRemotelyExtractor(),
        }
        self.llm = LLMFactory.get_provider()
        self.model_type = model_type
        self.temperature = temperature
        logger.info("JobAdExtractor initialized with extractors and LLM provider")

    def extract_details(self, job_ad_url: str) -> JobDetails:
        """Extract job details from URL."""
        if not job_ad_url:
            logger.error("Empty URL provided")
            return self._empty_response(job_ad_url)

        try:
            domain = get_domain(job_ad_url)
            extractor = self.get_extractor(domain)

            if not extractor:
                logger.error(f"No extractor for domain: {domain}")
                return self._empty_response(job_ad_url)

            # Get job details
            job_details = extractor.extract_details(job_ad_url)

            # Only use LLM if the extractor needs location analysis
            if extractor.needs_location_analysis():
                logger.info(f"Using LLM to determine location type for {domain}")
                job_details.location_type = self._determine_location_type(
                    job_details.description
                )
            else:
                logger.info(f"Using extractor's location type for {domain}")

            return job_details
        except Exception as e:
            logger.error(f"Error extracting details: {str(e)}")
            return self._empty_response(job_ad_url)

    def _determine_location_type(self, description: str) -> LocationType:
        """Use LLM to determine the location type from job description."""
        try:
            messages = [
                SystemMessage(
                    content=(
                        "You are an expert at analyzing job descriptions and determining "
                        "the work location type. You will categorize the location as either "
                        "Remote (fully remote work), Hybrid (mix of remote and office work), "
                        "or Onsite (fully office-based work)."
                    )
                ),
                HumanMessage(
                    content=f"""Analyze the following job description and determine if the position is Remote, Hybrid, or Onsite.
                    Consider mentions of:
                    - "remote work", "work from home", "remote-first"
                    - "hybrid schedule", "flexible location", "partially remote"
                    - "in office", "on-site", "at our location"

                    Job Description:
                    {description}
                    """
                ),
            ]

            response = self.llm.generate_structured_response(
                messages,
                LocationType,
                model_type=self.model_type,
                temperature=self.temperature,
            )

            return response

        except Exception as e:
            logger.error(f"Error determining location type: {str(e)}")
            return LocationType(type="Onsite")  # Default to Onsite

    def get_extractor(self, domain: str) -> ExtractorInterface | None:
        """Get extractor for domain."""
        return self.extractors.get(domain)

    @staticmethod
    def _empty_response(url: str = "") -> JobDetails:
        """Return empty response."""
        return JobDetails(
            company=CompanyInfo(
                company_name="", website_url="https://example.com"  # Default valid URL
            ),
            title="",
            description="",
            url=url or "https://example.com",  # Ensure valid URL
            location_type=LocationType(type="Onsite"),
        )
