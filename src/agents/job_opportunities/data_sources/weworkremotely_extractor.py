import re
from datetime import datetime
from typing import Optional

import pytz
import requests
from bs4 import BeautifulSoup, Tag

from src.logger import get_logger
from src.models.company.company_info import CompanyInfo
from src.models.job.job_details import JobDetails
from src.models.job.job_location import LocationType
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
            response = requests.get(job_ad_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            return JobDetails(
                company=CompanyInfo(
                    company_name=self._extract_company_name(soup),
                    website_url=self._extract_company_website(soup),
                ),
                title=self._extract_title(soup),
                description=self._extract_description(soup),
                url=normalize_url(job_ad_url),
                location_type=LocationType(type="Remote"),
                posted_date=self._extract_posted_date(soup),
            )
        except Exception as e:
            logger.error(f"Error extracting job details: {str(e)}")
            raise

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

    def _extract_company_name(self, soup: BeautifulSoup) -> str:
        """Get company name from page."""
        if company_card := self._find_company_card(soup):
            company_name_tag = company_card.find("h2")
            if company_name_tag and (name_link := company_name_tag.find("a")):
                company_name = name_link.get_text(strip=True)
                logger.debug(f"Found company name: {company_name}")
                return sanitize_text(company_name)
        logger.warning("Company name not found")
        return ""

    def _extract_company_website(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract company website URL from page."""
        try:
            if company_card := self._find_company_card(soup):
                if website_link := company_card.find("a", href=True, target="_blank"):
                    if website_link.find("i", class_="fa-globe-americas"):
                        website_url = website_link.get("href")
                        logger.debug(f"Found company website: {website_url}")
                        return website_url
            logger.warning("Company website not found")
            return None
        except Exception as e:
            logger.error(f"Error extracting company website: {str(e)}")
            return None

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Get job title from page."""
        if title_tag := soup.find("h1"):
            return sanitize_text(title_tag.get_text(strip=True))
        logger.warning("Job title not found")
        return ""

    def _extract_description(self, soup: BeautifulSoup) -> str:
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

    def _extract_posted_date(self, soup: BeautifulSoup) -> Optional[datetime]:
        """Extract posted date from the job listing."""
        try:
            if header := soup.find("div", class_="listing-header-container"):
                if time_tag := header.find("time"):
                    datetime_str = time_tag.get("datetime")
                    if datetime_str:
                        return datetime.fromisoformat(
                            datetime_str.replace("Z", "+00:00")
                        )
            logger.warning("Posted date not found")
            return None
        except Exception as e:
            logger.error(f"Error parsing posted date: {str(e)}")
            return None

    def needs_location_analysis(self) -> bool:
        """WWR is remote-only, no need for LLM analysis."""
        return False
