from src.agents.job_opportunities.job_ad_extractor import JobAdExtractor
from src.logger import get_logger
from src.models.job.job_details import JobDetails

logger = get_logger(__name__)


def test_extract_details_valid_url():
    """Smoke test for JobAdExtractor.extract_details with a valid URL."""
    extractor = JobAdExtractor()
    sample_url = "https://weworkremotely.com/remote-jobs/bluegamma-full-stack-developer"
    content = extractor.extract_details(sample_url)

    # Check if it's a JobDetails instance
    assert isinstance(content, JobDetails), "Content should be a JobDetails instance"

    # Convert to dict for easier testing
    content_dict = content.model_dump()

    # Check non-empty values for required fields
    assert content_dict["company"]["company_name"], "Company name should not be empty"
    assert content_dict["company"]["website_url"], "Website URL should not be empty"
    assert content_dict["title"], "Job title should not be empty"
    assert content_dict["description"], "Job description should not be empty"
    assert content_dict["url"], "URL should not be empty"

    logger.info(f"Extracted content: {content_dict}")
