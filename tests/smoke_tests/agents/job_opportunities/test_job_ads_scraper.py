from src.agents.job_opportunities.job_ads_scraper import JobAdsScraper
from src.logger import get_logger

logger = get_logger(__name__)


def test_scrape_job_urls():
    """Smoke test for JobAdsScraper.scrape_job_urls."""
    scraper = JobAdsScraper()
    urls = scraper.scrape_job_urls()

    # Basic validation
    assert isinstance(urls, list), "Should return a list of URLs"
    assert len(urls) > 0, "Should find at least one job URL"

    # Validate URL format
    for url in urls:
        assert isinstance(url, str), "Each URL should be a string"
        assert url.startswith("https://"), "URLs should start with https://"
        assert (
            "weworkremotely.com/remote-jobs/" in url
        ), "URLs should be WWR job listings"

    # Log results for inspection
    logger.info("Job URLs scraping results:")
    logger.info("------------------------")
    logger.info(f"Total URLs found: {len(urls)}")
    logger.info("Sample URLs (up to 5):")
    for url in urls[:5]:
        logger.info(url)
    logger.info("------------------------")


def test_get_scraper():
    """Test scraper retrieval by domain."""
    scraper = JobAdsScraper()

    # Test valid domain
    wwr_scraper = scraper.get_scraper("weworkremotely.com")
    assert wwr_scraper is not None, "Should return WWR scraper"

    # Test invalid domain
    invalid_scraper = scraper.get_scraper("invalid-domain.com")
    assert invalid_scraper is None, "Should return None for invalid domain"
