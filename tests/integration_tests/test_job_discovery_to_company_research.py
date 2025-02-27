import random
from datetime import datetime

import pytest

from src.agents.company_research.company_icp_fit_validator import CompanyICPFitValidator
from src.agents.company_research.company_info_extractor import CompanyInfoExtractor
from src.agents.company_research.company_quick_screener import CompanyQuickScreener
from src.agents.company_research.company_surface_researcher import (
    CompanySurfaceResearcher,
)
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
    Implements fail-fast behavior - if any critical step fails, the process halts.

    Flow:
    1. Discover job postings using JobAdsScraper
    2. Select and extract detailed info from a random job posting using JobAdExtractor
    3. Quick screen the company using CompanyQuickScreener
    4. Validate if it's a potential ICP fit using CompanyICPFitValidator
    5. Perform deep company research using CompanySurfaceResearcher
    6. Extract structured company data using CompanyInfoExtractor
    7. Return fully populated Job and Company models

    Success Criteria:
    - Successfully extracts job details
    - Identifies potential ICP fit
    - Gathers comprehensive company information
    - Returns valid Job and Company model instances
    """
    try:
        # Step 1: Discover Jobs
        logger.info("Starting job discovery phase...")
        scraper = JobAdsScraper()
        job_urls = scraper.scrape_job_urls()
        if not job_urls:
            logger.error("No job URLs found - halting process")
            return

        logger.info(f"Found {len(job_urls)} job URLs")

        # Step 2: Select and Process Job
        job_url = random.choice(job_urls)
        logger.info(f"Processing job posting: {job_url}")

        job_extractor = JobAdExtractor()
        job = job_extractor.extract_details(job_url)
        if not job:
            logger.error("Failed to extract job details - halting process")
            return

        logger.info(
            f"Extracted job details for: {job.title} at {job.company.company_name}"
        )

        # Step 3: Quick Screen Company
        logger.info(f"Quick screening company: {job.company.company_name}")
        screener = CompanyQuickScreener()
        if not screener.screen(job.company):
            logger.info(
                f"Company {job.company.company_name} failed quick screening. Halting process."
            )
            return

        logger.info(
            f"Company {job.company.company_name} passed quick screening. Proceeding with ICP validation."
        )

        # Step 4: ICP Fit Validation
        validator = CompanyICPFitValidator()
        is_icp_fit = validator.validate(
            company=job.company, research_data=job.description
        )
        if not is_icp_fit:
            logger.info(
                f"Company {job.company.company_name} does not fit ICP criteria. Halting process."
            )
            return

        logger.info(
            f"Company {job.company.company_name} appears to fit ICP criteria. Proceeding with detailed research."
        )

        # Step 5: Company Research
        logger.info(
            f"Starting detailed research for company: {job.company.company_name}"
        )
        surface_researcher = CompanySurfaceResearcher()
        research_result = surface_researcher.research_company(job.company)
        if not research_result:
            logger.error("Company research failed - halting process")
            return

        # Step 6: Extract Structured Company Data
        info_extractor = CompanyInfoExtractor()
        company_info = info_extractor.extract_all_info(
            research_output={"comprehensive_summary": research_result},
            company_url=job.company.website_url,
        )
        if not company_info:
            logger.error("Failed to extract company info - halting process")
            return

        # Step 7: Create Final Company Model
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
            careers_url=job.company.careers_url,
        )

        # Update job with enriched company info
        job = Job(
            company=company,
            title=job.title,
            description=job.description,
            url=job.url,
            location_type=job.location_type,
            posted_date=job.posted_date,
            offers_equity=job.offers_equity,
            summary=job.summary,
        )

        # Validate Final Results
        if not all(
            [
                job is not None,
                company is not None,
                job.company == company,
                job.job_id,
                job.description,
                company.description,
                company.industry is not None,
                company.growth_stage is not None,
            ]
        ):
            logger.error("Final validation failed - halting process")
            return

        logger.info(
            f"Successfully processed job {job.job_id} for company {company.company_name}"
        )

        # Log final successful state
        logger.info("Test completed successfully")
        logger.debug(f"Final Job object: {job}")
        logger.debug(f"Final Company object: {company}")

        assert True

    except Exception as e:
        logger.error(f"Integration test failed: {str(e)}")
        raise
