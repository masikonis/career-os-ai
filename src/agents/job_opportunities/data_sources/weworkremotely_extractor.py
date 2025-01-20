import re
from typing import Optional

import requests
from bs4 import BeautifulSoup, Tag

from src.logger import get_logger
from src.models.company.company_info import CompanyInfo
from src.models.job.job_details import JobDetails
from src.utilities.text import preserve_paragraphs, sanitize_text
from src.utilities.url import normalize_url

from .extractor_interface import ExtractorInterface

logger = get_logger(__name__)


class WeWorkRemotelyExtractor(ExtractorInterface):
    """WeWorkRemotely job board extractor."""

    BASE_URL = "https://weworkremotely.com"
    TIMEOUT = 10
    RELEVANT_TAGS = ["p", "ul", "h1", "h2", "h3", "h4", "h5", "h6"]

    def extract_details(self, job_ad_url: str) -> JobDetails:
        """Extract job details from URL."""
        try:
            soup = self._fetch_and_parse(job_ad_url)
            if not soup:
                return self._empty_response(job_ad_url)

            company_card = self._find_company_card(soup)
            if not company_card:
                return self._empty_response(job_ad_url)

            company_info = CompanyInfo(
                company_name=self._extract_company_name(company_card),
                website_url=self._extract_website_url(company_card),
            )

            return JobDetails(
                company=company_info,
                title=self._extract_job_title(soup),
                description=self._extract_job_description(soup),
                url=job_ad_url,
            )

        except Exception as e:
            logger.error(f"Error extracting job details: {e}")
            return self._empty_response(job_ad_url)

    def _empty_response(self, url: str) -> JobDetails:
        """Return empty response."""
        return JobDetails(
            company=CompanyInfo(company_name="", website_url=""),
            title="",
            description="",
            url=url,
        )

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
            return sanitize_text(company_name)
        logger.warning("Company name not found")
        return ""

    def _extract_website_url(self, company_card: Tag) -> str:
        """Get website URL from card."""
        for h3 in company_card.find_all("h3"):
            if a_tag := h3.find("a", href=True):
                if "Website" in a_tag.get_text(strip=True):
                    return normalize_url(a_tag["href"], self.BASE_URL)
        logger.warning("Website URL not found")
        return ""

    def _extract_job_title(self, soup: BeautifulSoup) -> str:
        """Get job title from page."""
        if title_tag := soup.find("h1"):
            return sanitize_text(title_tag.get_text(strip=True))
        logger.warning("Job title not found")
        return ""

    def _extract_job_description(self, soup: BeautifulSoup) -> str:
        """Get job description from page."""
        if listing := soup.find("div", class_="listing-container"):
            sections = self._extract_content_sections(listing)
            if sections:
                return preserve_paragraphs("\n\n".join(sections))
            logger.warning("No content sections found")
        else:
            logger.warning("Job listing not found")
        return ""

    def _extract_content_sections(self, container: Tag) -> list[str]:
        """Extract text sections from container."""
        sections = []
        for section in container.find_all(self.RELEVANT_TAGS):
            if text := section.get_text(strip=True):
                sections.append(sanitize_text(text))
        return sections
