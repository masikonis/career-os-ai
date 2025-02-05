from typing import Dict, Optional

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, HttpUrl

from src.agents.copywriting.brand_voice_text_editor import BrandVoiceTextEditor
from src.cache import CacheManager
from src.logger import get_logger
from src.models.company.company import Company
from src.models.job.job import Job
from src.models.job.job_location import JobLocation
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
        self.cache = CacheManager()
        self.brand_voice_editor = BrandVoiceTextEditor()
        logger.info(
            "JobAdExtractor initialized with extractors, LLM provider, and brand voice editor"
        )

    def extract_details(self, job_ad_url: str) -> Job:
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

            # Generate and cache summary
            job_details.summary = self._generate_summary(job_details)
            if job_details.summary:
                logger.info("Generated job summary:\n" + job_details.summary)

            # Determine if job offers equity
            job_details.offers_equity = self._determine_equity_offering(
                job_details.description
            )
            logger.debug(f"Equity offering determined: {job_details.offers_equity}")

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

    def _generate_summary(self, job: Job) -> Optional[str]:
        """Generate a concise one-paragraph summary focusing on key responsibilities and required skills."""
        cache_key = f"job_summary:{job.job_id}"

        # Check cache first
        if cached_summary := self.cache.get(cache_key):
            logger.debug("Using cached job summary")
            return cached_summary

        try:
            messages = [
                SystemMessage(
                    content="""You are an expert at summarizing job postings. Create a concise one-paragraph summary that focuses ONLY on:
                    - Key responsibilities
                    - Required skills/qualifications
                    Exclude all other details like company name, location type, or job title."""
                ),
                HumanMessage(
                    content=f"""Job Description:
                    {job.description}"""
                ),
            ]

            summary = self.llm.generate_response(
                messages,
                model_type=self.model_type,
                temperature=0.3,  # Lower temperature for more consistent results
            )

            # Edit summary with brand voice
            edited_summary = self.brand_voice_editor.edit_text(
                summary, context="job summary"
            )
            logger.debug("Edited summary with brand voice")

            # Cache the edited summary
            self.cache.set(
                cache_key, edited_summary, expire=86400
            )  # Cache for 24 hours
            logger.debug("Generated and cached new job summary")
            return edited_summary

        except Exception as e:
            logger.error(f"Error generating job summary: {str(e)}")
            return None

    def _determine_location_type(self, description: str) -> JobLocation:
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
                JobLocation,
                model_type=self.model_type,
                temperature=self.temperature,
            )

            return response

        except Exception as e:
            logger.error(f"Error determining location type: {str(e)}")
            return JobLocation(type="Onsite")  # Default to Onsite

    def _determine_equity_offering(self, description: str) -> bool:
        """Use LLM to determine if job offers equity."""
        try:
            messages = [
                SystemMessage(
                    content="""You are an expert at analyzing job descriptions. Determine if the job offers equity compensation.
                    Look for phrases like:
                    - "equity compensation"
                    - "stock options"
                    - "equity package"
                    - "ownership stake"
                    Return True if equity is mentioned, False otherwise."""
                ),
                HumanMessage(
                    content=f"""Job Description:
                    {description}"""
                ),
            ]

            response = self.llm.generate_response(
                messages,
                model_type=self.model_type,
                temperature=0.0,  # Use 0 temperature for consistent boolean results
            )

            return "true" in response.lower()

        except Exception as e:
            logger.error(f"Error determining equity offering: {str(e)}")
            return False

    def get_extractor(self, domain: str) -> ExtractorInterface | None:
        """Get extractor for domain."""
        return self.extractors.get(domain)

    @staticmethod
    def _empty_response(url: str = "") -> Job:
        """Return empty response."""
        return Job(
            company=Company.from_basic_info(company_name=""),
            title="",
            description="",
            url=url or "",
            location_type=JobLocation(type="Onsite"),
        )
