from typing import Dict, List, Optional

import requests

from src.agents.company_research.company_icp_fit_validator import CompanyICPFitValidator
from src.logger import get_logger
from src.models.company.company import Company
from src.services.web_search.factory import WebSearchFactory
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
            "clouddevs.com",
        }

        # Initialize web search provider and ICP validator
        self.web_search = WebSearchFactory.get_provider()
        self.icp_validator = CompanyICPFitValidator()

    def screen(self, company: Company) -> bool:
        """
        Quickly screen companies to determine if they should be researched.
        Returns True if the company should be researched, False if it should be skipped.

        Enhanced with two-tier web search and ICP validation.
        """
        try:
            # Step 1: Perform technical validation (existing checks)
            if not self._perform_technical_validation(company):
                return False

            # Step 2: Basic web search + first ICP validation
            if not self._perform_basic_search_validation(company):
                return False

            # Step 3: Advanced web search + second ICP validation
            if not self._perform_advanced_search_validation(company):
                return False

            # If company passes all checks, proceed with research
            logger.info(
                f"Company {company.company_name} passed all screening checks and is ready for deep research"
            )
            return True
        except Exception as e:
            logger.error(f"Unexpected error in screening process: {str(e)}")
            # For unexpected errors, we'll proceed with the company
            return True

    def _perform_technical_validation(self, company: Company) -> bool:
        """Perform the technical validation checks (existing functionality)."""
        try:
            # Check if company has basic info
            if not company.company_name or not company.website_url:
                logger.info(
                    f"Skipping company due to missing basic info: {company.company_name}"
                )
                return False

            # Resolve final URL first
            resolved_url = self.resolve_final_url(str(company.website_url))
            if not resolved_url:
                logger.info(
                    f"Skipping company due to unresolvable URL: {company.website_url}"
                )
                return False

            # Extract domain from RESOLVED URL, not original
            domain = get_domain(resolved_url)
            if not domain:
                logger.info(
                    f"Skipping company due to invalid resolved URL: {resolved_url}"
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
                f"Domain {domain} is not ignored and is reachable. Proceeding with web search for {company.company_name}"
            )
            return True

        except Exception as e:
            logger.error(f"Error in technical validation: {str(e)}")
            return False

    def _perform_basic_search_validation(self, company: Company) -> bool:
        """
        Perform basic search validation for the company.

        Args:
            company: The company to validate.

        Returns:
            bool: True if the company passes basic search validation, False otherwise.
        """
        try:
            logger.info(
                f"Performing basic search for {company.company_name}: '{company.company_name} company type funding stage acquired'"
            )
            search_results = self.web_search.basic_search(
                f"{company.company_name} company type funding stage acquired"
            )

            if not search_results:
                logger.info(f"No basic search results found for {company.company_name}")
                return True

            research_data = self._prepare_research_data(search_results)

            try:
                is_fit = self.icp_validator.validate(company, research_data)

                if not is_fit:
                    logger.info(
                        f"Company {company.company_name} disqualified after basic search and ICP validation"
                    )
                    return False

                logger.info(
                    f"Company {company.company_name} passed basic search validation"
                )
                return True
            except Exception as e:
                logger.error(f"Error in ICP validation after basic search: {str(e)}")
                # Continue with screening even if ICP validation fails
                return True

        except Exception as e:
            logger.error(f"Error in basic search validation: {str(e)}")
            return True

    def _perform_advanced_search_validation(self, company: Company) -> bool:
        """
        Perform advanced search validation for the company.

        Args:
            company: The company to validate.

        Returns:
            bool: True if the company passes advanced search validation, False otherwise.
        """
        try:
            logger.info(
                f"Performing advanced search for {company.company_name}: '{company.company_name} business model product offering team size revenue marketplace SaaS'"
            )
            search_results = self.web_search.advanced_search(
                f"{company.company_name} business model product offering team size revenue marketplace SaaS"
            )

            if not search_results:
                logger.info(
                    f"No advanced search results found for {company.company_name}"
                )
                return True

            research_data = self._prepare_research_data(search_results)

            try:
                is_fit = self.icp_validator.validate(company, research_data)

                if not is_fit:
                    logger.info(
                        f"Company {company.company_name} disqualified after advanced search and ICP validation"
                    )
                    return False

                logger.info(
                    f"Company {company.company_name} passed advanced search validation"
                )
                return True
            except Exception as e:
                logger.error(f"Error in ICP validation after advanced search: {str(e)}")
                # Continue with screening even if ICP validation fails
                return True

        except Exception as e:
            logger.error(f"Error in advanced search validation: {str(e)}")
            return True

    def _prepare_research_data(self, search_results: List[Dict[str, str]]) -> str:
        """Convert web search results into a format suitable for the ICP validator."""
        research_text = ""

        for i, result in enumerate(search_results, 1):
            research_text += f"Source {i}: {result.get('source', 'Unknown')}\n"
            research_text += f"{result.get('content', '')}\n\n"

        return research_text

    def resolve_final_url(self, url: str) -> Optional[str]:
        """Resolve URL redirects to get final destination URL"""
        try:
            response = requests.head(url, allow_redirects=True, timeout=5)
            return response.url
        except Exception as e:
            logger.warning(f"Failed to resolve URL {url}: {str(e)}")
            return None
