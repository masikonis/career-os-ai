import pytest

from src.agents.job_opportunities.job_ad_ingestor import JobAdIngestor
from src.logger import get_logger

logger = get_logger(__name__)


def test_ingest_content_valid_url():
    """Smoke test for JobAdIngestor.ingest_content with a valid URL."""
    ingestor = JobAdIngestor()
    sample_url = "https://weworkremotely.com/remote-jobs/bluegamma-full-stack-developer"
    content = ingestor.ingest_content(sample_url)
    assert isinstance(content, dict), "Content should be a dictionary."
    assert "company_name" in content, "Content should include 'company_name'."
    assert "website_url" in content, "Content should include 'website_url'."
    assert content["company_name"], "Company name should not be empty."
    assert content["website_url"], "Website URL should not be empty."
    logger.info(f"Extracted content: {content}")
