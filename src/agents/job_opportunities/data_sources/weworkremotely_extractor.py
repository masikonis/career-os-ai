import re
from typing import Dict

import requests
from bs4 import BeautifulSoup

from src.logger import get_logger

from .extractor_interface import ExtractorInterface

logger = get_logger(__name__)


class WeWorkRemotelyExtractor(ExtractorInterface):
    """Extractor for We Work Remotely job ads."""

    def extract_details(self, job_ad_url: str) -> Dict[str, str]:
        """Extract company and website details from a We Work Remotely job ad.

        Args:
            job_ad_url (str): The URL of the job advertisement.

        Returns:
            Dict[str, str]: A dictionary with 'company_name' and 'website_url'.
        """
        try:
            response = requests.get(job_ad_url, timeout=10)
            response.raise_for_status()
            html_content = response.text
        except requests.RequestException as exc:
            logger.error(f"Error fetching job ad content: {exc}")
            return {"company_name": "", "website_url": ""}

        soup = BeautifulSoup(html_content, "html.parser")

        # Locate the company card div (flexible regex match for class names containing 'company-card')
        company_card = soup.find("div", class_=re.compile(r"\bcompany-card\b"))
        if not company_card:
            logger.error("Company card div not found.")
            # Optionally log a snippet of the HTML for debugging
            logger.debug(f"HTML snippet: {soup.prettify()[:1000]}")
            return {"company_name": "", "website_url": ""}

        # Extract company name
        company_name_tag = company_card.find("h2")
        if company_name_tag and company_name_tag.find("a"):
            company_name = company_name_tag.find("a").get_text(strip=True)
            logger.debug(f"Extracted company name: {company_name}")
        else:
            logger.warning("Company name not found.")
            company_name = ""

        # Extract website URL by searching through all <h3> tags
        website_url = ""
        h3_tags = company_card.find_all("h3")
        for h3 in h3_tags:
            a_tag = h3.find("a", href=True)
            if a_tag and "Website" in a_tag.get_text(strip=True):
                website_url = a_tag["href"]
                logger.debug(f"Extracted website URL: {website_url}")
                break

        if not website_url:
            logger.warning("Website URL not found.")
        else:
            # Ensure the URL is absolute
            if website_url.startswith("/"):
                website_url = f"https://weworkremotely.com{website_url}"

        return {"company_name": company_name, "website_url": website_url}
