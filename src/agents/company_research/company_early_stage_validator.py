from typing import Optional

from src.logger import get_logger
from src.models.company.company import Company
from src.models.company.company_growth_stage import GrowthStage
from src.services.llm.factory import LLMFactory

logger = get_logger(__name__)


class CompanyEarlyStageValidator:
    def __init__(self):
        self.llm = LLMFactory.get_provider()

    def validate(self, company: Company, research_data: Optional[str] = None) -> bool:
        """
        Validates if a company appears to be early-stage (pre-Series A).

        Args:
            company: Basic company information
            research_data: Optional research summary about the company

        Returns:
            bool: True if early-stage or uncertain, False if definitely later-stage
        """
        if research_data:
            return self._validate_with_research(company, research_data)
        return self._validate_with_llm_knowledge(company)

    def _validate_with_llm_knowledge(self, company: Company) -> bool:
        """Quick validation using only LLM's existing knowledge."""
        prompt = f"""Based on your knowledge cutoff, analyze if {company.company_name} (website: {company.website_url}) 
        is at any of these stages:
        - IDEA stage
        - PRE_SEED stage
        - MVP stage
        - SEED stage
        - EARLY stage
        - LATER stage (Series A or beyond)

        Only respond 'LATER' if you are very confident the company is at Series A or beyond.
        If you're unsure or know it's pre-Series A, respond 'EARLY'.
        
        Response (EARLY/LATER):"""

        try:
            response = self.llm.generate_response(prompt)
            is_later_stage = "LATER" in response.upper()

            stage_description = (
                "later-stage (Series A or beyond)"
                if is_later_stage
                else "early-stage (pre-Series A)"
            )
            logger.info(
                f"Company {company.company_name} validated as {stage_description} based on LLM knowledge"
            )

            return not is_later_stage

        except Exception as e:
            logger.error(
                f"Error validating company stage with LLM knowledge for {company.company_name}: {str(e)}"
            )
            return True  # Default to True (early-stage) in case of errors

    def _validate_with_research(self, company: Company, research_data: str) -> bool:
        """Detailed validation using web research data."""
        prompt = f"""Based on the following research about {company.company_name}, determine if it's a later-stage company.

        Research summary:
        {research_data}

        Analyze the research for indicators of company stage, such as:
        - Funding rounds and amounts
        - Employee count
        - Market presence and traction
        - Product maturity
        - Revenue or growth metrics
        
        Consider these stages:
        - IDEA/PRE_SEED/MVP: Very early, limited product/traction
        - SEED: Has product, early traction
        - EARLY: Growing revenue and customers
        - LATER: Series A or beyond, significant scale
        
        Only respond 'LATER' if the research clearly indicates Series A or later funding, or equivalent scale.
        If uncertain or pre-Series A indicators, respond 'EARLY'.
        
        Response (EARLY/LATER):"""

        try:
            response = self.llm.generate_response(prompt)
            is_later_stage = "LATER" in response.upper()

            stage_description = (
                "later-stage (Series A or beyond)"
                if is_later_stage
                else "early-stage (pre-Series A)"
            )
            logger.info(
                f"Company {company.company_name} validated as {stage_description} based on research data"
            )

            return not is_later_stage

        except Exception as e:
            logger.error(
                f"Error validating company stage with research data for {company.company_name}: {str(e)}"
            )
            return True  # Default to True (early-stage) in case of errors
