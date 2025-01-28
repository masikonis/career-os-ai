from typing import Optional

from langchain_community.document_loaders import WebBaseLoader

from src.logger import get_logger
from src.models.company.company import Company
from src.services.llm.factory import LLMFactory

logger = get_logger(__name__)


class CompanyFitValidator:
    def __init__(self):
        self.llm = LLMFactory.get_provider()

    def validate(self, company: Company, research_data: str) -> bool:
        """
        Validates if a company fits our target ICP criteria based on research data.
        Returns True if company fits, False otherwise.
        """
        prompt = f"""Based on the following research about {company.company_name}, determine if it fits our target criteria.

        Research Data:
        {research_data}

        IMPORTANT: We are looking for early-stage product companies that create:
        A. Software products (SaaS, etc.)
        B. Tech-enabled content products
        C. Digital products with clear value proposition
        D. Technology platforms and tools (e.g. developer tools, content authoring tools)

        Company Stage Guidelines:
        - Pre-seed to Seed stage is FIT
        - Pre-Series A can be FIT if still operating like a seed-stage company
        - Early-stage companies with limited information but clear product focus are FIT
        - Consider operational scale and market position, not just funding amount

        You MUST respond 'UNFIT' if the company primarily does ANY of these:
        1. Education/Training Services:
           - Offers bootcamps or courses as main product
           - Provides training/certification programs
           - Focuses on teaching/training delivery
           - Offers job placement or career services
           NOTE: Companies that provide SOFTWARE TOOLS for education are FIT
        
        2. Developer Services:
           - Developer hiring/talent matching
           - Developer vetting/testing
           - Freelance developer marketplace
           - Developer recruitment platform
           NOTE: Companies that create TOOLS FOR developers are FIT
        
        3. Company Stage/Type:
           - Series A or beyond with mature operations
           - Public companies
           - Unicorns or well-established tech companies
           - Pure consulting/services businesses
           - Traditional/legacy businesses
           - Pure marketplace without own product

        IMPORTANT DISTINCTIONS:
        - A company that CREATES tools FOR developers = FIT
        - A company that provides developer SERVICES = UNFIT
        - A company that CREATES educational content/products = FIT
        - A company that DELIVERS education/training = UNFIT
        - A company that provides SOFTWARE TOOLS = FIT
        - A company that provides SERVICES = UNFIT
        - A pre-seed/seed company with limited info but clear product focus = FIT

        Response (FIT/UNFIT):"""

        try:
            response = self.llm.generate_response(prompt, model_type="basic")
            is_unfit = "UNFIT" in response.upper()

            fit_description = "does not fit ICP" if is_unfit else "fits ICP"
            logger.info(
                f"Company {company.company_name} validated as {fit_description} based on research data"
            )

            return not is_unfit

        except Exception as e:
            logger.error(
                f"Error validating company fit for {company.company_name}: {str(e)}"
            )
            return False
