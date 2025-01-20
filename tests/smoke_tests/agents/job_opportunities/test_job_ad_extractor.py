from src.agents.job_opportunities.job_ad_extractor import JobAdExtractor
from src.logger import get_logger

logger = get_logger(__name__)


def test_extract_details_valid_url():
    """Smoke test for JobAdExtractor.extract_details with a valid URL."""
    extractor = JobAdExtractor()
    sample_url = "https://weworkremotely.com/remote-jobs/bluegamma-full-stack-developer"
    content = extractor.extract_details(sample_url)

    # Check dictionary structure
    assert isinstance(content, dict), "Content should be a dictionary."
    expected_keys = {"company_name", "website_url", "job_ad_title", "job_ad"}
    assert all(
        key in content for key in expected_keys
    ), f"Content should include all keys: {expected_keys}"

    # Check non-empty values for required fields
    assert content["company_name"], "Company name should not be empty"
    assert content["website_url"], "Website URL should not be empty"
    assert content["job_ad_title"], "Job ad title should not be empty"
    assert content["job_ad"], "Job ad content should not be empty"

    logger.info(f"Extracted content: {content}")
