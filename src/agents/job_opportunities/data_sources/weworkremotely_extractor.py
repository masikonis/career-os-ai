import re
from dataclasses import dataclass
from typing import Dict, List, Optional

import requests
from bs4 import BeautifulSoup, Tag

from src.logger import get_logger

from .extractor_interface import ExtractorInterface

logger = get_logger(__name__)


@dataclass
class JobDetails:
    """Job details container."""

    company_name: str = ""
    website_url: str = ""
    job_ad_title: str = ""
    job_ad: str = ""

    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary."""
        return {
            "company_name": self.company_name,
            "website_url": self.website_url,
            "job_ad_title": self.job_ad_title,
            "job_ad": self.job_ad,
        }


class WeWorkRemotelyExtractor(ExtractorInterface):
    """WeWorkRemotely job board extractor."""

    BASE_URL = "https://weworkremotely.com"
    TIMEOUT = 10
    RELEVANT_TAGS = ["p", "ul", "h1", "h2", "h3", "h4", "h5", "h6"]

    def extract_details(self, job_ad_url: str) -> Dict[str, str]:
        """Extract job details from URL."""
        try:
            soup = self._fetch_and_parse(job_ad_url)
            if not soup:
                return JobDetails().to_dict()

            company_card = self._find_company_card(soup)
            if not company_card:
                return JobDetails().to_dict()

            details = JobDetails(
                company_name=self._extract_company_name(company_card),
                website_url=self._extract_website_url(company_card),
                job_ad_title=self._extract_job_title(soup),
                job_ad=self._extract_job_description(soup),
            )

            return details.to_dict()

        except Exception as e:
            logger.error(f"Error extracting job details: {e}")
            return JobDetails().to_dict()

    def _fetch_and_parse(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch and parse webpage."""
        try:
            response = requests.get(url, timeout=self.TIMEOUT)
            response.raise_for_status()
            return BeautifulSoup(response.text, "html.parser")
        except requests.RequestException as exc:
            logger.error(f"Error fetching URL: {exc}")
            return None

    def _find_company_card(self, soup: BeautifulSoup) -> Optional[Tag]:
        """Find company card in page."""
        company_card = soup.find("div", class_=re.compile(r"\bcompany-card\b"))
        if not company_card:
            logger.error("Company card not found")
            logger.debug(f"HTML snippet: {soup.prettify()[:1000]}")
        return company_card

    def _extract_company_name(self, company_card: Tag) -> str:
        """Get company name from card."""
        company_name_tag = company_card.find("h2")
        if company_name_tag and (name_link := company_name_tag.find("a")):
            company_name = name_link.get_text(strip=True)
            logger.debug(f"Found company name: {company_name}")
            return company_name
        logger.warning("Company name not found")
        return ""

    def _extract_website_url(self, company_card: Tag) -> str:
        """Get website URL from card."""
        for h3 in company_card.find_all("h3"):
            if a_tag := h3.find("a", href=True):
                if "Website" in a_tag.get_text(strip=True):
                    url = a_tag["href"]
                    if url.startswith("/"):
                        url = f"{self.BASE_URL}{url}"
                    logger.debug(f"Found website URL: {url}")
                    return url
        logger.warning("Website URL not found")
        return ""

    def _extract_job_title(self, soup: BeautifulSoup) -> str:
        """Get job title from page."""
        if title_tag := soup.find("h1"):
            return title_tag.get_text(strip=True)
        logger.warning("Job title not found")
        return ""

    def _extract_job_description(self, soup: BeautifulSoup) -> str:
        """Get job description from page."""
        if listing := soup.find("div", class_="listing-container"):
            sections = self._extract_content_sections(listing)
            if sections:
                return "\n\n".join(sections)
            logger.warning("No content sections found")
        else:
            logger.warning("Job listing not found")
        return ""

    def _extract_content_sections(self, container: Tag) -> List[str]:
        """Extract text sections from container."""
        sections = []
        for section in container.find_all(self.RELEVANT_TAGS):
            if text := section.get_text(strip=True):
                sections.append(text)
        return sections
