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
        fits our target company criteria.

        IMPORTANT: We are looking for early-stage product companies that create:
        A. Software products (SaaS, etc.)
        B. Tech-enabled content products (e.g. educational video content platforms that CREATE and DISTRIBUTE content)
        C. Digital products with clear value proposition

        You MUST respond 'UNFIT' if the company primarily does ANY of these:
        1. Education/Training Services:
           - Offers bootcamps or courses as main product
           - Provides training/certification programs
           - Focuses on teaching/training delivery
           - Offers job placement or career services
        
        2. Developer Services:
           - Developer hiring/talent matching
           - Developer vetting/testing
           - Freelance developer marketplace
           - Developer recruitment platform
        
        3. Company Stage/Type:
           - Series A or beyond funding
           - Public companies
           - Unicorns or well-established tech companies
           - Pure consulting/services businesses
           - Traditional/legacy businesses
           - Pure marketplace without own product

        IMPORTANT DISTINCTION:
        - A company that CREATES educational content/products = FIT
        - A company that DELIVERS education/training = UNFIT

        Response (FIT/UNFIT):"""

        try:
            response = self.llm.generate_response(
                prompt, model_type="reasoning", temperature=1
            )
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

        We are looking for early-stage product companies. The product can be:
        - Software products (SaaS, etc.)
        - Tech-enabled content/media products
        - Digital products with clear value proposition

        Respond 'UNFIT' if ANY of these are true:
        1. Education/Training Business:
           - Offers bootcamps
           - Provides job guarantees
           - Offers training programs
           - Delivers courses
           - Focuses on student outcomes
        
        2. Developer Services:
           - Developer hiring/talent matching
           - Developer vetting/testing
           - Freelance developer marketplace
        
        3. Company Stage/Type:
           - Series A or beyond funding
           - Public companies
           - Unicorns or well-established tech companies
           - Pure consulting/services businesses
           - Traditional/legacy businesses
           - Pure marketplace without own product

        Response (FIT/UNFIT):"""

        try:
            response = self.llm.generate_response(prompt, model_type="advanced")
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
