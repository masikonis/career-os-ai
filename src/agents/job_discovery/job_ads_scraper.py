from typing import Dict, List

from src.logger import get_logger
from src.utilities.url import get_domain

from .data_sources.scraper_interface import ScraperInterface
from .data_sources.weworkremotely_scraper import WeWorkRemotelyScraper

logger = get_logger(__name__)


class JobAdsScraper:
    """Delegates job ad URL scraping to specific scrapers based on source."""

    def __init__(self):
        self.scrapers: Dict[str, ScraperInterface] = {
            "weworkremotely.com": WeWorkRemotelyScraper(),
        }
        logger.info("JobAdsScraper initialized with scrapers")

    def scrape_job_urls(self) -> List[str]:
        """Scrape job URLs from all configured sources."""
        all_urls = []

        for domain, scraper in self.scrapers.items():
            try:
                logger.info(f"Scraping job URLs from {domain}")
                urls = scraper.scrape_job_urls()
                all_urls.extend(urls)
                logger.info(f"Found {len(urls)} URLs from {domain}")
            except Exception as e:
                logger.error(f"Error scraping {domain}: {str(e)}")
                continue

        # Remove duplicates while preserving order
        unique_urls = list(dict.fromkeys(all_urls))
        logger.info(f"Total unique job URLs found: {len(unique_urls)}")
        return unique_urls

    def get_scraper(self, domain: str) -> ScraperInterface | None:
        """Get scraper for domain."""
        return self.scrapers.get(domain)
