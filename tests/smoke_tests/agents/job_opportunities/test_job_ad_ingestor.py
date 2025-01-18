import pytest

from src.agents.job_opportunities.job_ad_ingestor import JobAdIngestor
from src.logger import get_logger

logger = get_logger(__name__)


def test_ingest_content_valid_url():
    """Smoke test for JobAdIngestor.ingest_content with a valid URL."""
    ingestor = JobAdIngestor()
    sample_url = "https://weworkremotely.com/remote-jobs/bluegamma-full-stack-developer"
    content = ingestor.ingest_content(sample_url)
    assert isinstance(content, str), "Content should be a string."
    assert content, "Content should not be empty."
    logger.info(f"Extracted content: {content}")
