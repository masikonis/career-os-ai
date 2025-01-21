from typing import List

import requests
from bs4 import BeautifulSoup

from src.logger import get_logger

from .scraper_interface import ScraperInterface

logger = get_logger(__name__)


class WeWorkRemotelyScraper(ScraperInterface):
    """WeWorkRemotely job board scraper."""

    BASE_URL = "https://weworkremotely.com"
    TIMEOUT = 10

    # List of job category URLs to scrape
    CATEGORY_URLS = [
        "/categories/remote-full-stack-programming-jobs",
    ]

    def scrape_job_urls(self) -> List[str]:
        """Scrape job listing URLs from WeWorkRemotely."""
        urls = []

        for category_url in self.CATEGORY_URLS:
            try:
                full_url = f"{self.BASE_URL}{category_url}"
                response = requests.get(full_url, timeout=self.TIMEOUT)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, "html.parser")

                # Find the jobs section and get all job links
                if jobs_section := soup.find("section", class_="jobs"):
                    for job_link in jobs_section.find_all("a", href=True):
                        href = job_link.get("href")
                        # Skip non-job links like "View Company Profile" and "Back to all jobs"
                        if (
                            href.startswith("/remote-jobs/")
                            and "company" not in href
                            and "view-all" not in href
                        ):
                            urls.append(f"{self.BASE_URL}{href}")

                logger.info(f"Found {len(urls)} job URLs from {category_url}")

            except Exception as e:
                logger.error(f"Error scraping WWR category {category_url}: {str(e)}")
                continue

        return list(set(urls))  # Remove any duplicates
