from src.agents.job_opportunities.job_ad_extractor import JobAdExtractor
from src.logger import get_logger

logger = get_logger(__name__)


def test_extract_details_valid_url():
    """Smoke test for JobAdExtractor.extract_details with a valid URL."""
    extractor = JobAdExtractor()
    sample_url = "https://weworkremotely.com/remote-jobs/bluegamma-full-stack-developer"
    content = extractor.extract_details(sample_url)
    assert isinstance(content, dict), "Content should be a dictionary."
    assert "company_name" in content, "Content should include 'company_name'."
    assert "website_url" in content, "Content should include 'website_url'."
    assert content["company_name"], "Company name should not be empty."
    assert content["website_url"], "Website URL should not be empty."
    logger.info(f"Extracted content: {content}")
