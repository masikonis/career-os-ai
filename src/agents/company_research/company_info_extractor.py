from typing import Optional
from urllib.parse import urljoin

import requests
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import HttpUrl

from src.agents.copywriting.brand_voice_text_editor import BrandVoiceTextEditor
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
    ]

    def __init__(self, model_type: str = "basic", temperature: float = 0.0):
        self.llm = LLMFactory.get_provider()
        self.model_type = model_type
        self.temperature = temperature
        self.brand_voice_editor = BrandVoiceTextEditor()
        logger.info(
            "CompanyInfoExtractor initialized with LLM provider and brand voice editor"
        )

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
            # Combine all relevant summaries
            all_text = f"""
            Comprehensive Summary: {research_output.get('comprehensive_summary', '')}
            Team Summary: {research_output.get('team_summary', '')}
            Company Summary: {research_output.get('company_summary', '')}
            """

            messages = [
                HumanMessage(
                    content=f"""Extract the company's founding year (not launch year) from the following text. 
                    Look for explicit mentions of 'founded in' or 'established in'.
                    Return the year as a number. If no founding year is mentioned, return null.
                    
                    Text: {all_text}
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
                SystemMessage(
                    content="""When classifying company industries, follow these principles:
                    1. Primary Industry:
                       - For software companies, be specific: 'AI Software', 'SaaS', 'Enterprise Software'
                       - Combine core technologies if both are fundamental (e.g., 'AI Software/SaaS')
                       - For non-software companies, use their operational industry
                    
                    2. Verticals:
                       - List core product capabilities using simple, clear terms
                       - Capitalize each vertical (e.g., 'Presentation Software')
                       - Focus on main functionalities, not technical details
                       - Use natural language with proper capitalization
                       - Only include key capabilities proven in the source text
                       - Limit to 2-3 most important verticals"""
                ),
                HumanMessage(
                    content=f"""Based on this text, identify:
                    1. The company's primary industry
                    2. List of specific verticals based on proven capabilities
                    
                    Text: {comprehensive_summary}
                    """
                ),
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
            all_text = f"""
            Funding Summary: {research_output.get('funding_summary', '')}
            Comprehensive Summary: {research_output.get('comprehensive_summary', '')}
            Company Summary: {research_output.get('company_summary', '')}
            """

            messages = [
                SystemMessage(
                    content="""When extracting funding information:
                    1. Only include information from verifiable sources (press releases, SEC filings, reliable news outlets)
                    2. Distinguish between announced/confirmed funding and reported/rumored funding
                    3. If source reliability is unclear, exclude the information"""
                ),
                HumanMessage(
                    content=f"""Extract the verified funding information from this text. Include:
                    1. Total funding amount (in millions)
                    2. Individual funding rounds with sources
                    3. Only include information that appears to be from reliable sources
                    
                    Text: {all_text}
                    """
                ),
            ]
            response = self.llm.generate_structured_response(
                messages,
                CompanyFunding,
                model_type=self.model_type,
                temperature=self.temperature,
            )

            if response.total_amount is None and not response.funding_sources:
                logger.info("No funding information found in the text")
                return CompanyFunding(
                    total_amount=None, currency="USD", funding_sources=[]
                )

            funding_str = str(response)
            logger.info(f"Extracted funding info: {funding_str}")
            return response

        except Exception as e:
            logger.error(f"Error extracting funding: {str(e)}")
            return CompanyFunding(total_amount=None, currency="USD", funding_sources=[])

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

            # Use class-wide brand voice editor
            edited_description = self.brand_voice_editor.edit_text(
                response.description, context="company profile"
            )

            logger.info(f"Generated and edited summary: {edited_description}")
            return CompanyDescription(description=edited_description)
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

    def extract_all_info(
        self, research_output: dict, company_url: Optional[HttpUrl] = None
    ) -> dict:
        """Extract all available company information from research output."""
        logger.info("Starting comprehensive information extraction")

        try:
            extracted_info = {
                "careers_url": None,
                "founding_year": None,
                "founders": None,
                "location": None,
                "industry": None,
                "growth_stage": None,
                "funding": None,
                "description": None,
            }

            # Do URL-based extraction first
            if company_url:
                try:
                    extracted_info["careers_url"] = self.find_careers_url(company_url)
                except Exception as e:
                    logger.error(f"Failed to find careers URL: {e}")

            # Then do LLM-based extractions
            try:
                extracted_info["founding_year"] = self.extract_founding_year(
                    research_output
                )
            except Exception as e:
                logger.error(f"Failed to extract founding year: {e}")

            try:
                extracted_info["founders"] = self.extract_founders(research_output)
            except Exception as e:
                logger.error(f"Failed to extract founders: {e}")

            try:
                extracted_info["location"] = self.extract_location(research_output)
            except Exception as e:
                logger.error(f"Failed to extract location: {e}")

            try:
                extracted_info["industry"] = self.extract_industry(research_output)
            except Exception as e:
                logger.error(f"Failed to extract industry: {e}")

            try:
                extracted_info["growth_stage"] = self.extract_growth_stage(
                    research_output
                )
            except Exception as e:
                logger.error(f"Failed to extract growth stage: {e}")

            try:
                extracted_info["funding"] = self.extract_funding(research_output)
            except Exception as e:
                logger.error(f"Failed to extract funding: {e}")

            try:
                extracted_info["description"] = self.create_description(research_output)
            except Exception as e:
                logger.error(f"Failed to create description: {e}")

            # Log successful extractions
            successful = [k for k, v in extracted_info.items() if v is not None]
            logger.info(f"Successfully extracted: {', '.join(successful)}")

            return extracted_info

        except Exception as e:
            logger.error(f"Error in comprehensive extraction: {e}")
            raise
