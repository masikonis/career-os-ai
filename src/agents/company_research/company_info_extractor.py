from langchain_core.messages import HumanMessage

from src.logger import get_logger
from src.models.company.company_info import CompanyInfo
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
