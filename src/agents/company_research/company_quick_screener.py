from typing import Optional

from src.logger import get_logger
from src.models.company.company import Company
from src.utilities.url import get_domain, is_domain_reachable

logger = get_logger(__name__)


class CompanyQuickScreener:
    def __init__(self):
        # Add domains to ignore (e.g., developer hiring platforms, irrelevant industries)
        self.ignored_domains = {
            "lemon.io",
            "lumenalta.com",
            "x-team.com",
            "contra.com",
            "toptal.com",
            "testgorilla.com",
            "remoteyear.com",
            "remotemore.com",
            "hireology.com",
            "xwp.co",
            "upwork.com",
            "fiverr.com",
            "freelancer.com",
            "guru.com",
            "peopleperhour.com",
            "turing.com",
            "arc.dev",
            "gun.io",
            "codementor.io",
            "hired.com",
            "weworkremotely.com",
            "remote.com",
            "outsourcely.com",
            "flexjobs.com",
            "triplebyte.com",
            "hackerrank.com",
            "codility.com",
            "coderpad.io",
        }

    def screen(self, company: Company) -> bool:
        """
        Quickly screen companies to determine if they should be researched.
        Returns True if the company should be researched, False if it should be skipped.
        """
        try:
            # Check if company has basic info
            if not company.company_name or not company.website_url:
                logger.info(
                    f"Skipping company due to missing basic info: {company.company_name}"
                )
                return False

            # Extract domain from website URL
            domain = get_domain(str(company.website_url))
            if not domain:
                logger.info(
                    f"Skipping company due to invalid website URL: {company.company_name}"
                )
                return False

            # Check if domain is in the ignore list
            if domain in self.ignored_domains:
                logger.info(f"Skipping company due to ignored domain: {domain}")
                return False

            # Check if domain is reachable
            if not is_domain_reachable(domain):
                logger.info(f"Skipping company due to unreachable domain: {domain}")
                return False

            # If domain is not ignored and is reachable, proceed with research
            logger.info(
                f"Domain {domain} is not ignored and is reachable. Proceeding with research for {company.company_name}"
            )
            return True

        except Exception as e:
            logger.error(f"Error screening company: {str(e)}")
            return False  # Default to False on error
