from typing import Optional

from langchain_core.messages import HumanMessage

from src.logger import get_logger
from src.models.company.company_info import CompanyInfo
from src.models.company.founding_year import FoundingYear
from src.models.company.growth_stage import CompanyGrowthStage
from src.services.llm.factory import LLMFactory

logger = get_logger(__name__)


class CompanyInfoExtractor:
    """Agent that extracts essential company information"""

    def __init__(self, model_type: str = "basic", temperature: float = 0.0):
        self.llm = LLMFactory.get_provider()
        self.model_type = model_type
        self.temperature = temperature
        logger.info("CompanyInfoExtractor initialized with LLM provider")

    def extract_info(self, source_text: str) -> dict:
        """Extract company information from a given source text"""
        try:
            messages = [
                HumanMessage(
                    content=f"""Extract the company information from the following text:
                    {source_text}

                    Format your response as:
                    COMPANY_NAME: <company_name>
                    WEBSITE_URL: <website_url>
                    """
                )
            ]
            response = self.llm.generate_structured_response(
                messages,
                CompanyInfo,
                model_type=self.model_type,
                temperature=self.temperature,
            )
            logger.debug("Generated structured response: %s", response)
            logger.info("Completed extraction of company information.")
            return response.model_dump()
        except Exception as e:
            logger.error(f"Error extracting company info: {str(e)}")
            raise

    def extract_growth_stage(self, research_output: dict) -> CompanyGrowthStage:
        """Extract company growth stage from research output"""
        try:
            comprehensive_summary = research_output.get("comprehensive_summary", "")
            source_summaries = research_output.get("source_summaries", [])

            # Combine all available information
            combined_text = f"""
            Comprehensive Summary: {comprehensive_summary}
            
            Detailed Sources:
            {' '.join(source_summaries)}
            """

            messages = [
                HumanMessage(
                    content=f"""Based on the following company research, determine the company's growth stage.
                    
                    {combined_text}
                    
                    Classify the growth stage into one of these categories:
                    - IDEA: Just an idea, no real product yet
                    - PRE_SEED: Early development, pre-product
                    - MVP: Has a minimum viable product
                    - SEED: Has product with some traction
                    - EARLY: Growing revenue and customer base
                    - SERIES_A: Significant traction, seeking scale
                    - LATER: Well-established, multiple funding rounds
                    
                    Provide:
                    1. The most appropriate growth stage
                    2. Your confidence level (0.0 to 1.0)
                    3. Brief reasoning for your classification
                    """
                )
            ]

            response = self.llm.generate_structured_response(
                messages,
                CompanyGrowthStage,
                model_type=self.model_type,
                temperature=self.temperature,
            )

            logger.info(
                f"Extracted growth stage: {response.growth_stage} with confidence {response.confidence}"
            )
            return response

        except Exception as e:
            logger.error(f"Error extracting growth stage: {str(e)}")
            raise

    def extract_founding_year(self, research_output: dict) -> Optional[int]:
        """Extract company founding year from research output"""
        try:
            comprehensive_summary = research_output.get("comprehensive_summary", "")

            messages = [
                HumanMessage(
                    content=f"""Extract the founding year from the following company description. 
                    Return the year as a number. If no founding year is mentioned, return null.
                    
                    Text: {comprehensive_summary}
                    """
                )
            ]

            response = self.llm.generate_structured_response(
                messages,
                FoundingYear,
                model_type=self.model_type,
                temperature=self.temperature,
            )

            logger.info(f"Extracted founding year: {response.year}")
            return response.year

        except Exception as e:
            logger.error(f"Error extracting founding year: {str(e)}")
            raise
