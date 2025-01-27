from typing import Optional

from src.logger import get_logger
from src.models.company.company import Company
from src.services.llm.factory import LLMFactory

logger = get_logger(__name__)


class CompanyFitValidator:
    def __init__(self):
        self.llm = LLMFactory.get_provider()

    def validate(self, company: Company, research_data: Optional[str] = None) -> bool:
        """
        Validates if a company fits our target ICP criteria:
        - Is a product-focused company
        - Not a developer vetting/hiring platform
        - Digital/tech business (not legacy)
        - Pre-Series A stage
        - Other ICP criteria

        Args:
            company: Basic company information
            research_data: Optional research summary about the company

        Returns:
            bool: True if company fits ICP criteria or uncertain, False if definitely doesn't fit
        """
        if research_data:
            return self._validate_with_research(company, research_data)
        return self._validate_with_llm_knowledge(company)

    def _validate_with_llm_knowledge(self, company: Company) -> bool:
        """Quick validation using only LLM's existing knowledge."""
        prompt = f"""Based on your knowledge cutoff, analyze if {company.company_name} (website: {company.website_url}) 
        fits these criteria:

        1. Is it a product-focused company? (can be tech-enabled products like educational content, but NOT pure services/consulting)
        2. Is it NOT a developer hiring/vetting platform?
        3. Is it a modern digital business? (not a traditional/legacy business)
        4. Is it pre-Series A stage? Consider these stages:
           - IDEA stage
           - PRE_SEED stage
           - MVP stage
           - SEED stage
           - EARLY stage (but pre-Series A)
           - LATER stage (Series A or beyond - AUTOMATIC DISQUALIFICATION)

        Respond 'UNFIT' if ANY of these are true:
        - Company has raised Series A or beyond funding
        - Company is publicly traded
        - Company is a unicorn or well-established tech company
        - Company is a dev hiring/vetting platform
        - Company is primarily a services business
        - Company is a legacy/non-digital business

        Otherwise, respond 'FIT'.
        
        Response (FIT/UNFIT):"""

        try:
            response = self.llm.generate_response(prompt)
            is_unfit = "UNFIT" in response.upper()

            fit_description = "does not fit ICP" if is_unfit else "fits ICP"
            logger.info(
                f"Company {company.company_name} validated as {fit_description} based on LLM knowledge"
            )

            return not is_unfit

        except Exception as e:
            logger.error(
                f"Error validating company fit with LLM knowledge for {company.company_name}: {str(e)}"
            )
            return True  # Default to True (fits ICP) in case of errors

    def _validate_with_research(self, company: Company, research_data: str) -> bool:
        """Detailed validation using web research data."""
        prompt = f"""Based on the following research about {company.company_name}, determine if it fits our target criteria.

        Research summary:
        {research_data}

        Analyze if the company meets ALL these criteria:
        1. Product Focus:
           - Offers a clear product or tech-enabled solution (can be content, educational materials, etc.)
           - Not primarily services/consulting
           - Not a developer hiring/vetting platform

        2. Business Type:
           - Modern digital or tech-enabled business
           - Not a traditional/legacy business
           - Not a pure marketplace/platform

        3. Company Stage:
           - Pre-Series A stage
           - Could be: IDEA, PRE-SEED, MVP, SEED, or EARLY
           - Not at Series A or beyond

        4. Other Indicators:
           - Funding rounds and amounts
           - Employee count
           - Market presence
           - Product maturity
           - Revenue/growth stage
        
        Only respond 'UNFIT' if the research clearly shows the company doesn't meet our criteria.
        If uncertain or company appears to fit, respond 'FIT'.
        
        Response (FIT/UNFIT):"""

        try:
            response = self.llm.generate_response(prompt)
            is_unfit = "UNFIT" in response.upper()

            fit_description = "does not fit ICP" if is_unfit else "fits ICP"
            logger.info(
                f"Company {company.company_name} validated as {fit_description} based on research data"
            )

            return not is_unfit

        except Exception as e:
            logger.error(
                f"Error validating company fit with research data for {company.company_name}: {str(e)}"
            )
            return True  # Default to True (fits ICP) in case of errors
