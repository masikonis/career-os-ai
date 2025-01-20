from src.logger import get_logger
from src.models.company.company_info import CompanyInfo
from src.models.company.growth_stage import GrowthStage
from src.services.llm.factory import LLMFactory

logger = get_logger(__name__)


class EarlyStageValidator:
    def __init__(self):
        self.llm = LLMFactory.get_provider()

    def validate(self, company_info: CompanyInfo) -> bool:
        """
        Quickly validates if a company appears to be early-stage (pre-Series A)
        using LLM knowledge. Returns True if early-stage or uncertain, False if definitely later-stage.
        """
        prompt = f"""Based on your knowledge cutoff, analyze if {company_info.company_name} (website: {company_info.website_url}) 
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
                f"Company {company_info.company_name} validated as {stage_description}"
            )

            return not is_later_stage

        except Exception as e:
            logger.error(
                f"Error validating company stage for {company_info.company_name}: {str(e)}"
            )
            return True  # Default to True (early-stage) in case of errors
