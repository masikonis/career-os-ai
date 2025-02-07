from src.agents.job_discovery.data_sources.weworkremotely_extractor import (
    WeWorkRemotelyExtractor,
)
from src.logger import get_logger

logger = get_logger(__name__)


def test_weworkremotely_extractor():
    """Smoke test for WeWorkRemotelyExtractor."""
    extractor = WeWorkRemotelyExtractor()
    sample_url = "https://weworkremotely.com/remote-jobs/bluegamma-full-stack-developer"

    try:
        # Fetch and log raw HTML
        response = extractor._fetch_and_parse(sample_url)
        if response:
            logger.info("Successfully fetched HTML content")
            logger.debug(
                f"HTML content:\n{response.prettify()[:2000]}..."
            )  # First 2000 chars
        else:
            logger.error("Failed to fetch HTML content")
            return

        # Test individual extraction methods
        company_name = extractor._extract_company_name(response)
        logger.info(f"Extracted company name: {company_name}")

        company_website = extractor._extract_company_website(response)
        logger.info(f"Extracted company website: {company_website}")

        title = extractor._extract_title(response)
        logger.info(f"Extracted title: {title}")

        description = extractor._extract_description(response)
        logger.info(f"Extracted description (first 200 chars): {description[:200]}...")

        posted_date = extractor._extract_posted_date(response)
        logger.info(f"Extracted posted date: {posted_date}")

    except Exception as e:
        logger.error(f"Error during extraction: {str(e)}")
        raise
