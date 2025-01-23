from typing import Optional
from urllib.parse import urljoin

import requests
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import HttpUrl

from src.logger import get_logger
from src.models.company.company import Company
from src.models.company.company_description import CompanyDescription
from src.models.company.company_founders import CompanyFounders
from src.models.company.company_founding_year import CompanyFoundingYear
from src.models.company.company_funding import CompanyFunding
from src.models.company.company_growth_stage import CompanyGrowthStage
from src.models.company.company_industry import CompanyIndustry
from src.models.company.company_location import CompanyLocation
from src.services.llm.factory import LLMFactory

logger = get_logger(__name__)


class CompanyInfoExtractor:
    """Agent that extracts essential company information"""

    COMMON_CAREER_PATHS = [
        "/careers",
        "/jobs",
        "/work-with-us",
        "/join-us",
        "/join",
        "/career",
        "/opportunities",
        "/work-at",
        "/employment",
        "/hiring",
    ]

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
                Company,
                model_type=self.model_type,
                temperature=self.temperature,
            )
            logger.debug("Generated structured response: %s", response)
            logger.info("Completed extraction of company information.")
            return response.model_dump()
        except Exception as e:
            logger.error(f"Error extracting company info: {str(e)}")
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
                CompanyFoundingYear,
                model_type=self.model_type,
                temperature=self.temperature,
            )
            logger.info(f"Extracted founding year: {response.year}")
            return response.year
        except Exception as e:
            logger.error(f"Error extracting founding year: {str(e)}")
            raise

    def extract_founders(self, research_output: dict) -> Optional[CompanyFounders]:
        """Extract company founders from research output"""
        try:
            comprehensive_summary = research_output.get("comprehensive_summary", "")
            messages = [
                HumanMessage(
                    content=f"""Extract the founders' information from the following company description.
                    For each founder, provide their name and title/role if mentioned.
                    If no founders are mentioned, return an empty list.
                    
                    Text: {comprehensive_summary}
                    """
                )
            ]
            response = self.llm.generate_structured_response(
                messages,
                CompanyFounders,
                model_type=self.model_type,
                temperature=self.temperature,
            )
            if not response.founders:
                logger.info("No founders found in the text")
                return None
            logger.info(f"Extracted {len(response.founders)} founders")
            return response
        except Exception as e:
            logger.error(f"Error extracting founders: {str(e)}")
            raise

    def extract_location(self, research_output: dict) -> Optional[CompanyLocation]:
        """Extract company location from research output"""
        try:
            comprehensive_summary = research_output.get("comprehensive_summary", "")
            messages = [
                HumanMessage(
                    content=f"""Extract the company's location information from the following text.
                    Return the city, state, and country if mentioned. If a field is not mentioned,
                    return null for that field. For US companies, if only city and state are mentioned,
                    assume country is United States.
                    
                    Text: {comprehensive_summary}
                    """
                )
            ]
            response = self.llm.generate_structured_response(
                messages,
                CompanyLocation,
                model_type=self.model_type,
                temperature=self.temperature,
            )
            if not (response.city or response.state or response.country):
                logger.info("No location information found in the text")
                return None
            logger.info(
                f"Extracted location: {response.city}, {response.state}, {response.country}"
            )
            return response
        except Exception as e:
            logger.error(f"Error extracting location: {str(e)}")
            raise

    def extract_industry(self, research_output: dict) -> Optional[CompanyIndustry]:
        """Extract company industry and verticals from research output"""
        try:
            comprehensive_summary = research_output.get("comprehensive_summary", "")
            messages = [
                HumanMessage(
                    content=f"""Extract the company's industry information from the following text.
                    Identify:
                    1. The primary industry (e.g., EdTech, FinTech, HealthTech)
                    2. List of specific verticals or market segments (e.g., K-12 Education, Science Education)
                    Be specific but concise with the classifications.
                    
                    Text: {comprehensive_summary}
                    """
                )
            ]
            response = self.llm.generate_structured_response(
                messages,
                CompanyIndustry,
                model_type=self.model_type,
                temperature=self.temperature,
            )
            if not response.primary_industry:
                logger.info("No industry information found in the text")
                return None
            logger.info(f"Extracted primary industry: {response.primary_industry}")
            logger.info(f"Verticals: {', '.join(response.verticals)}")
            return response
        except Exception as e:
            logger.error(f"Error extracting industry: {str(e)}")
            raise

    def extract_growth_stage(self, research_output: dict) -> CompanyGrowthStage:
        """Extract company growth stage from research output"""
        try:
            comprehensive_summary = research_output.get("comprehensive_summary", "")
            source_summaries = research_output.get("source_summaries", [])
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
                    - LATER: Series A or beyond
                    
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

    def extract_funding(self, research_output: dict) -> Optional[CompanyFunding]:
        """Extract company funding information from research output"""
        try:
            comprehensive_summary = research_output.get("comprehensive_summary", "")
            messages = [
                HumanMessage(
                    content=f"""Extract funding information from the following text.
                    Include total funding amount (in millions), and list each funding source with its amount and type.
                    For amounts, convert to millions (e.g., $1,000,000 = 1.0).
                    If an amount is not specified for a source, return null for that amount.
                    
                    Text: {comprehensive_summary}
                    """
                )
            ]
            response = self.llm.generate_structured_response(
                messages,
                CompanyFunding,
                model_type=self.model_type,
                temperature=self.temperature,
            )
            if not response.funding_sources and not response.total_amount:
                logger.info("No funding information found in the text")
                return None
            logger.info(
                f"Extracted total funding: ${response.total_amount}M {response.currency}"
            )
            logger.info(f"Number of funding sources: {len(response.funding_sources)}")
            return response
        except Exception as e:
            logger.error(f"Error extracting funding: {str(e)}")
            raise

    def create_description(self, research_output: dict) -> Optional[CompanyDescription]:
        """Create a concise, professional summary of the research"""
        try:
            comprehensive_summary = research_output.get("comprehensive_summary", "")
            messages = [
                SystemMessage(
                    content="""Create a brief, professional summary of this company research in 2-3 
                    concise sentences. Focus on the most relevant facts while maintaining 
                    a clear, objective tone."""
                ),
                HumanMessage(content=f"Text: {comprehensive_summary}"),
            ]
            response = self.llm.generate_structured_response(
                messages,
                CompanyDescription,
                model_type=self.model_type,
                temperature=0.5,
            )
            logger.info(f"Generated summary: {response.description}")
            return response
        except Exception as e:
            logger.error(f"Error creating summary: {str(e)}")
            raise

    def find_careers_url(self, base_url: HttpUrl) -> Optional[str]:
        """
        Find careers page URL using common patterns.

        Args:
            base_url: Base company URL

        Returns:
            str: Valid careers page URL if found and accessible, None otherwise
        """
        if not base_url:
            logger.debug("No base URL provided")
            return None

        base = str(base_url).rstrip("/")

        for path in self.COMMON_CAREER_PATHS:
            try:
                potential_url = urljoin(base, path)
                logger.debug(f"Checking potential careers URL: {potential_url}")

                # Validate URL by making a HEAD request
                response = requests.head(potential_url, timeout=5, allow_redirects=True)
                if response.status_code == 200:
                    logger.info(f"Found valid careers URL: {potential_url}")
                    return potential_url

            except requests.RequestException as e:
                logger.debug(f"URL {potential_url} not accessible: {str(e)}")
                continue
            except Exception as e:
                logger.error(f"Error checking URL {potential_url}: {str(e)}")
                continue

        logger.info("No valid careers URL found using common patterns")
        return None
