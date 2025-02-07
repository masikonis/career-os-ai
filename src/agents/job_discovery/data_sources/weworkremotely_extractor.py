import re
from datetime import datetime, timedelta
from typing import Optional

import pytz
import requests
from bs4 import BeautifulSoup, Tag

from src.logger import get_logger
from src.models.company.company import Company
from src.models.job.job import Job
from src.models.job.job_location import JobLocation
from src.utilities.text import preserve_paragraphs, sanitize_text
from src.utilities.url import normalize_url

from .extractor_interface import ExtractorInterface

logger = get_logger(__name__)


class WeWorkRemotelyExtractor(ExtractorInterface):
    """WeWorkRemotely job board extractor."""

    BASE_URL = "https://weworkremotely.com"
    TIMEOUT = 10
    RELEVANT_TAGS = ["p", "ul", "h1", "h2", "h3", "h4", "h5", "h6"]

    def extract_details(self, job_ad_url: str) -> Job:
        """Extract job details from URL."""
        try:
            response = requests.get(job_ad_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            # Validate markup before proceeding
            if not self._validate_markup(soup):
                logger.error(f"Markup validation failed for URL: {job_ad_url}")
                return self._empty_response(job_ad_url)

            return Job(
                company=Company.from_basic_info(
                    company_name=self._extract_company_name(soup),
                    website_url=self._extract_company_website(soup),
                ),
                title=self._extract_title(soup),
                description=self._extract_description(soup),
                url=normalize_url(job_ad_url),
                location_type=JobLocation(type="Remote"),
                posted_date=self._extract_posted_date(soup),
            )
        except Exception as e:
            logger.error(f"Error extracting job details: {str(e)}")
            raise

    def _empty_response(self, url: str) -> Job:
        """Return empty response."""
        return Job(
            company=Company.from_basic_info(
                company_name="",
                website_url=None,
            ),
            title="",
            description="",
            url=url,
            location_type=JobLocation(type="Remote"),
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
        try:
            company_details = soup.find(
                "div", class_="lis-container__job__sidebar__companyDetails"
            )
            if company_details:
                title_div = company_details.find(
                    "div",
                    class_="lis-container__job__sidebar__companyDetails__info__title",
                )
                if title_div and title_div.h3:
                    company_name = title_div.h3.get_text(strip=True)
                    logger.debug(f"Found company name: {company_name}")
                    return sanitize_text(company_name)
            logger.warning("Company name not found")
            return ""
        except Exception as e:
            logger.error(f"Error extracting company name: {str(e)}")
            return ""

    def _extract_company_website(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract company website URL from page."""
        try:
            # Find the company profile link
            if company_link := soup.find(
                "a",
                class_="lis-container__job__sidebar__companyDetails__info__link",
                href=True,
            ):
                company_profile_url = self.BASE_URL + company_link["href"]

                # Fetch the company profile page
                if company_profile_soup := self._fetch_and_parse(company_profile_url):
                    if company_card := company_profile_soup.find(
                        "div", class_="company-card"
                    ):
                        if website_link := company_card.find(
                            "a", href=True, target="_blank"
                        ):
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
        if title_tag := soup.find(
            "h2", class_="lis-container__header__hero__company-info__title"
        ):
            return sanitize_text(title_tag.get_text(strip=True))
        logger.warning("Job title not found")
        return ""

    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Get job description from page."""
        if description_div := soup.find(
            "div", class_="lis-container__job__content__description"
        ):
            return preserve_paragraphs(description_div.get_text(separator="\n").strip())
        logger.warning("Job description not found")
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
            if about_section := soup.find(
                "div", class_="lis-container__job__sidebar__job-about"
            ):
                if posted_tag := about_section.find(
                    "span", string=lambda x: x and "days ago" in x
                ):
                    days_ago = int(posted_tag.get_text(strip=True).split()[0])
                    return datetime.now(pytz.UTC) - timedelta(days=days_ago)
            logger.warning("Posted date not found")
            return None
        except Exception as e:
            logger.error(f"Error parsing posted date: {str(e)}")
            return None

    def needs_location_analysis(self) -> bool:
        """WWR is remote-only, no need for LLM analysis."""
        return False

    def _validate_markup(self, soup: BeautifulSoup) -> bool:
        """Validate that the page contains expected elements."""
        required_selectors = {
            "company_name": "div.lis-container__job__sidebar__companyDetails h3",
            "title": "h2.lis-container__header__hero__company-info__title",
            "description": "div.lis-container__job__content__description",
            "posted_date": "div.lis-container__job__sidebar__job-about span",
            "company_profile_link": "a.lis-container__job__sidebar__companyDetails__info__link",
        }

        for field, selector in required_selectors.items():
            if not soup.select_one(selector):
                logger.error(
                    f"Markup validation failed: Missing {field} element (selector: {selector})"
                )
                return False
        return True
