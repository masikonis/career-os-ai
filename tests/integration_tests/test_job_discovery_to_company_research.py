import random
from datetime import datetime

import pytest

from src.agents.company_research.company_early_stage_validator import (
    CompanyEarlyStageValidator,
)
from src.agents.company_research.company_info_extractor import CompanyInfoExtractor
from src.agents.company_research.company_web_researcher import CompanyWebResearcher
from src.agents.job_discovery.job_ad_extractor import JobAdExtractor
from src.agents.job_discovery.job_ads_scraper import JobAdsScraper
from src.logger import get_logger
from src.models.company.company import Company
from src.models.job.job import Job
from src.models.job.job_location import JobLocation

logger = get_logger(__name__)


@pytest.mark.integration
@pytest.mark.slow
def test_job_discovery_to_company_research():
    """
    Integration test for the complete job discovery and company research pipeline.

    Flow:
    1. Discover job postings using JobAdsScraper
    2. Select and extract detailed info from a random job posting using JobAdExtractor
    3. Validate if it's an early-stage company using CompanyEarlyStageValidator
    4. Perform deep company research using CompanyWebResearcher
    5. Extract structured company data using CompanyInfoExtractor
    6. Return fully populated Job and Company models

    Success Criteria:
    - Successfully extracts job details
    - Identifies potential startup
    - Gathers comprehensive company information
    - Returns valid Job and Company model instances
    """
    try:
        # Step 1: Discover Jobs
        logger.info("Starting job discovery phase...")
        scraper = JobAdsScraper()
        job_urls = scraper.scrape_job_urls()
        assert len(job_urls) > 0, "No job URLs found"

        # Step 2: Select and Process Job
        job_url = random.choice(job_urls)
        logger.info(f"Processing job posting: {job_url}")

        job_extractor = JobAdExtractor()
        job = job_extractor.extract_details(job_url)
        assert job is not None, "Failed to extract job details"
        logger.info(
            f"Extracted job details for: {job.title} at {job.company.company_name}"
        )

        # Step 3: Early Stage Validation
        validator = CompanyEarlyStageValidator()
        is_early_stage = validator.validate(
            company=job.company, research_data=job.description
        )

        if not is_early_stage:
            logger.info(
                f"Company {job.company.company_name} is not early-stage (Series A or beyond). Skipping detailed research."
            )
            return None, None

        logger.info(
            f"Company {job.company.company_name} appears to be early-stage. Proceeding with detailed research."
        )

        # Step 4: Company Research
        logger.info(
            f"Starting detailed research for startup: {job.company.company_name}"
        )
        researcher = CompanyWebResearcher()
        research_result = researcher.research_company(job.company)

        # Step 5: Extract Structured Company Data
        info_extractor = CompanyInfoExtractor()
        company_info = info_extractor.extract_all_info(
            research_output={"comprehensive_summary": research_result},
            company_url=job.company.website_url,
        )

        # Step 6: Create Final Company Model
        company = Company(
            company_name=job.company.company_name,
            website_url=job.company.website_url,
            description=company_info.get("description"),
            founding_year=company_info.get("founding_year"),
            founders=company_info.get("founders"),
            location=company_info.get("location"),
            industry=company_info.get("industry"),
            growth_stage=company_info.get("growth_stage"),
            funding=company_info.get("funding"),
        )

        # Update job with enriched company info
        job.company = company

        # Validate Final Results
        assert job is not None, "Job should not be None"
        assert company is not None, "Company should not be None"
        assert job.company == company, "Job company reference mismatch"
        assert job.job_id, "Job ID not generated"
        assert job.description, "Job description should not be empty"
        assert company.description, "Company description should not be empty"
        assert company.industry is not None, "Company industry should be extracted"
        assert (
            company.growth_stage is not None
        ), "Company growth stage should be determined"

        logger.info(
            f"Successfully processed job {job.job_id} for startup {company.company_name}"
        )

        return job, company

    except Exception as e:
        logger.error(f"Integration test failed: {str(e)}")
        raise
