import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse

from langchain.schema import HumanMessage, SystemMessage
from langchain_community.document_loaders import WebBaseLoader

from src.logger import get_logger
from src.models.company.company import Company
from src.services.llm.factory import LLMFactory
from src.services.web_search.factory import WebSearchFactory

logger = get_logger(__name__)


class CompanyWebResearcher:
    """Agent that researches a company by scraping related web pages and summarizing the content."""

    def __init__(
        self,
        model_type: str = "basic",
        temperature: float = 0.0,
        num_urls: int = 3,
        max_retries: int = 2,
        concurrency: int = 5,
    ):
        self.llm = LLMFactory.get_provider()
        self.web_search = WebSearchFactory.get_provider()
        self.model_type = model_type
        self.temperature = temperature
        self.num_urls = num_urls
        self.max_retries = max_retries
        self.concurrency = concurrency
        logger.info(
            "CompanyWebResearcher initialized with LLM, and WebSearch providers"
        )

    def research_company(self, company: Company) -> dict:
        """Research the company by performing multiple targeted searches and consolidate the information."""
        try:
            company_name = company.company_name
            website_url = str(company.website_url)
            logger.info(f"Starting research for company: {company_name}")

            # Step 1: Scrape the Home Page
            home_page_doc = self.scrape_urls_concurrently([website_url])
            home_page_summary = ""
            if home_page_doc:
                home_page_doc = home_page_doc[0]
                relevant_text = self.extract_relevant_info(
                    company_name, home_page_doc.page_content
                )
                home_page_summary = self.summarize_text(company_name, relevant_text)

            # Step 2: Multi-purpose search queries
            # "startup" search - covers stage, funding, founding year, founders
            startup_query = f"{company_name} startup"
            startup_search_results = self.web_search.search(startup_query)[
                : self.num_urls
            ]
            startup_related_urls = [
                result["url"] for result in startup_search_results if "url" in result
            ]

            # "product" search - covers business model, revenue model, industry
            product_query = f"{company_name} product"
            product_search_results = self.web_search.search(product_query)[
                : self.num_urls
            ]
            product_related_urls = [
                result["url"] for result in product_search_results if "url" in result
            ]

            # "team" search - covers team size, founders, location
            team_query = f"{company_name} team"
            team_search_results = self.web_search.search(team_query)[: self.num_urls]
            team_related_urls = [
                result["url"] for result in team_search_results if "url" in result
            ]

            # "about" search - covers company description, location, founding info
            about_query = f"{company_name} about"
            about_search_results = self.web_search.search(about_query)[: self.num_urls]
            about_related_urls = [
                result["url"] for result in about_search_results if "url" in result
            ]

            # Aggregate all URLs
            all_related_urls = (
                startup_related_urls
                + product_related_urls
                + team_related_urls
                + about_related_urls
            )

            # Deduplicate URLs
            unique_urls = list(set(all_related_urls))
            logger.info(f"Found {len(unique_urls)} unique URLs to scrape.")

            # Validate URLs
            valid_urls = self.validate_urls(unique_urls)
            logger.info(f"{len(valid_urls)} URLs are valid for scraping.")

            # Scrape documents concurrently with retries
            documents = self.scrape_urls_concurrently(valid_urls)
            logger.info(f"Scraped {len(documents)} documents.")

            if not documents and not home_page_summary:
                logger.warning(
                    "No documents were scraped and no home page summary available. Returning empty summary."
                )
                return {}

            # Summarize each scraped document concurrently
            doc_summaries = self.summarize_documents_concurrently(
                documents, company_name
            )

            # Include home page summary if available
            if home_page_summary:
                doc_summaries.append(home_page_summary)

            # Create initial summaries
            summaries = {
                "home_page_summary": home_page_summary,
                "comprehensive_summary": self.create_comprehensive_summary(
                    company_name, doc_summaries
                ),
                "company_summary": self.create_company_summary(
                    company_name, doc_summaries
                ),
                "funding_summary": self.create_funding_summary(
                    company_name, doc_summaries
                ),
                "team_summary": self.create_team_summary(company_name, doc_summaries),
            }

            # Add ICP research data after other summaries are created
            summaries["icp_research_data"] = self.generate_icp_research_data(
                company_name, summaries
            )

            logger.info("Completed research and summarization.")
            logger.debug(summaries)

            return summaries
        except Exception as e:
            logger.error(f"Error in research_company: {str(e)}")
            raise

    def scrape_urls_concurrently(self, urls: list) -> list:
        """Scrape multiple URLs concurrently with retry mechanisms."""
        documents = []
        with ThreadPoolExecutor(max_workers=self.concurrency) as executor:
            future_to_url = {
                executor.submit(self.scrape_with_retries, url): url for url in urls
            }
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    doc = future.result()
                    if doc:
                        documents.append(doc)
                        logger.debug(f"Successfully scraped URL: {url}")
                except Exception as e:
                    logger.error(f"Failed to scrape URL {url}: {str(e)}")
        return documents

    def scrape_with_retries(self, url: str):
        """Attempt to scrape a URL with a defined number of retries."""
        attempt = 0
        while attempt < self.max_retries:
            try:
                loader = WebBaseLoader(
                    web_paths=[url],
                    requests_kwargs={"timeout": 10},
                    continue_on_failure=True,
                )
                document = next(loader.lazy_load())
                return document
            except Exception as e:
                attempt += 1
                logger.warning(
                    f"Retry {attempt}/{self.max_retries} for URL {url} due to error: {str(e)}"
                )
                time.sleep(2)  # Backoff before retrying
        logger.error(f"Exceeded maximum retries for URL: {url}")
        return None

    def summarize_documents_concurrently(
        self, documents: list, company_name: str
    ) -> list:
        """
        Summarize multiple documents in parallel. Extract relevant info for each
        document, then produce a concise summary.
        """
        summaries = []
        with ThreadPoolExecutor(max_workers=self.concurrency) as executor:
            future_to_doc = {
                executor.submit(self.process_document, doc, company_name): doc
                for doc in documents
            }
            for future in as_completed(future_to_doc):
                doc = future_to_doc[future]
                try:
                    summary = future.result()
                    if summary:
                        summaries.append(summary)
                except Exception as e:
                    logger.error(
                        f"Error summarizing document from {doc.metadata.get('source')}: {str(e)}"
                    )
        return summaries

    def process_document(self, doc, company_name: str) -> str:
        """
        Extract relevant info from the document and then summarize that info.
        """
        relevant_text = self.extract_relevant_info(company_name, doc.page_content)
        return self.summarize_text(company_name, relevant_text)

    def extract_relevant_info(self, company_name: str, text: str) -> str:
        """
        Extract relevant information about the company from the scraped text.
        """
        try:
            prompt = (
                f"Extract relevant information about {company_name} and provide a summary of no more than 500 words.\n\n"
                + text
            )
            messages = [
                SystemMessage(
                    content=(
                        f"You are a helpful assistant that extracts comprehensive content about a company named {company_name}."
                    )
                ),
                HumanMessage(content=prompt),
            ]
            extracted_info = self.llm.generate_response(
                messages, model_type=self.model_type, temperature=self.temperature
            )
            return extracted_info
        except Exception as e:
            logger.error(f"Error extracting relevant information: {str(e)}")
            raise

    def validate_urls(self, urls: list) -> list:
        """Validate the list of URLs to ensure they are properly formatted."""
        valid_urls = []
        for url in urls:
            parsed = urlparse(url)
            if all([parsed.scheme, parsed.netloc]):
                valid_urls.append(url)
            else:
                logger.warning(f"Invalid URL skipped: {url}")
        return valid_urls

    def summarize_text(self, company_name: str, text: str) -> str:
        """
        Summarize the given text using the language model.
        """
        try:
            logger.debug(f"Summarizing text excerpt")

            prompt = (
                f"Provide a summary of the following information about a company named {company_name}.\n\n{text}"
                f"{text}"
            )
            messages = [
                SystemMessage(
                    content=(
                        f"You are a helpful assistant that summarizes content about a company named {company_name}."
                    )
                ),
                HumanMessage(content=prompt),
            ]
            summary = self.llm.generate_response(
                messages, model_type=self.model_type, temperature=self.temperature
            )
            return summary
        except Exception as e:
            logger.error(f"Error summarizing text: {str(e)}")
            raise

    def create_comprehensive_summary(self, company_name: str, summaries: list) -> str:
        """
        Create a concise, single-paragraph summary (no more than 250 words) from all individual summaries.
        """
        try:
            combined_text = "\n".join(summaries)
            prompt = (
                f"Review all relevant details from the following summaries about a company named '{company_name}'. "
                "If there are mentions of multiple entities with the same name, focus on whichever references "
                "are most clearly about the actual company. Then, synthesize a single-paragraph description covering key points: "
                "up to 50% on a general overview (who they are and what they offer), and the remaining 50% on funding information, "
                "team details, and customer sentiment. Keep your language clear, factual, and cohesive, ensuring other "
                "unrelated entities with the same name do not confuse the final summary.\n\n"
                f"{combined_text}"
            )
            messages = [
                SystemMessage(
                    content=(
                        "You are an expert at synthesizing information about a specific company. "
                        "You will create a concise overview that stays focused on the correct company."
                    )
                ),
                HumanMessage(content=prompt),
            ]
            comprehensive_summary = self.llm.generate_response(
                messages, model_type=self.model_type, temperature=self.temperature
            )
            logger.debug("Generated concise comprehensive summary.")
            return comprehensive_summary
        except Exception as e:
            logger.error(f"Error creating comprehensive summary: {str(e)}")
            raise

    def create_company_summary(self, company_name: str, summaries: list) -> str:
        """Create a summary focused on company overview, products, and services."""
        try:
            combined_text = "\n".join(summaries)
            prompt = (
                f"From the following summaries about {company_name}, create a focused summary "
                "about the company's core business, products, and services. Include their main "
                "value proposition and target market. Keep it factual and concise.\n\n"
                f"{combined_text}"
            )
            messages = [
                SystemMessage(
                    content="You are an expert at summarizing company business models and offerings."
                ),
                HumanMessage(content=prompt),
            ]
            return self.llm.generate_response(
                messages, model_type=self.model_type, temperature=self.temperature
            )
        except Exception as e:
            logger.error(f"Error creating company summary: {str(e)}")
            raise

    def create_funding_summary(self, company_name: str, summaries: list) -> str:
        """Create a summary focused on funding and financial information."""
        try:
            combined_text = "\n".join(summaries)
            prompt = (
                f"From the following summaries about {company_name}, create a focused summary "
                "about the company's funding history, including total funding amount, funding rounds, "
                "key investors, and any relevant financial metrics. Keep it factual and concise.\n\n"
                f"{combined_text}"
            )
            messages = [
                SystemMessage(
                    content="You are an expert at summarizing company funding and financial information."
                ),
                HumanMessage(content=prompt),
            ]
            return self.llm.generate_response(
                messages, model_type=self.model_type, temperature=self.temperature
            )
        except Exception as e:
            logger.error(f"Error creating funding summary: {str(e)}")
            raise

    def create_team_summary(self, company_name: str, summaries: list) -> str:
        """Create a summary focused on team and leadership information."""
        try:
            combined_text = "\n".join(summaries)
            prompt = (
                f"From the following summaries about {company_name}, create a focused summary "
                "about the company's team, including founders, key executives, and any relevant "
                "background information about the leadership. Keep it factual and concise.\n\n"
                f"{combined_text}"
            )
            messages = [
                SystemMessage(
                    content="You are an expert at summarizing company team and leadership information."
                ),
                HumanMessage(content=prompt),
            ]
            return self.llm.generate_response(
                messages, model_type=self.model_type, temperature=self.temperature
            )
        except Exception as e:
            logger.error(f"Error creating team summary: {str(e)}")
            raise

    def generate_icp_research_data(self, company_name: str, summaries: dict) -> str:
        """Generate ICP-focused research data from existing summaries."""
        try:
            combined_text = (
                f"Comprehensive: {summaries['comprehensive_summary']}\n"
                f"Company: {summaries['company_summary']}\n"
                f"Funding: {summaries['funding_summary']}\n"
                f"Team: {summaries['team_summary']}"
            )

            prompt = (
                f"Based on the following information about {company_name}, create a focused research summary "
                "that MUST follow this EXACT format:\n\n"
                f"{company_name} business details:\n"
                "- [Stage] stage, [Verified Funding Status]\n"
                "- [Product Type] (e.g., SaaS platform, software product)\n"
                "- Revenue split: [e.g., '100% SaaS product (no services)', '80% product, 20% services']\n"
                "- Team size: [Size Range or Specific Number]\n"
                "- Product status: [Development Stage/Launch Date/Traction]\n"
                "- Additional metrics: [Verified Users/Customers/Growth]\n\n"
                "Example 1:\n"
                "DataFlow business details:\n"
                "- Pre-seed stage, no verified external funding data\n"
                "- Pure SaaS data integration platform\n"
                "- 100% SaaS product revenue (no services or marketplace fees)\n"
                "- Team size: 5-10 employees (based on LinkedIn)\n"
                "- Product launched Q3 2023\n"
                "- Additional metrics: Early user adoption (specific numbers unverified)\n\n"
                "Example 2:\n"
                "CloudStack business details:\n"
                "- Seed stage, $2M funding announced on TechCrunch (Jan 2022)\n"
                "- B2B infrastructure automation platform\n"
                "- 90% SaaS product, 10% professional services\n"
                "- Team size: 15-20 people (company careers page)\n"
                "- Product in market since 2022\n"
                "- Additional metrics: 100+ enterprise clients (verified on case studies)\n\n"
                f"Now, create a similar summary for {company_name} using this information:\n\n"
                f"{combined_text}\n\n"
                "IMPORTANT:\n"
                "1. You MUST start with exactly '{company_name} business details:'\n"
                "2. You MUST use bullet points (-) for each line\n"
                "3. For ALL metrics and claims:\n"
                "   - Label source type: (verified: [source]), (reported by: [source]), or (company claimed)\n"
                "   - Include date of claim when available\n"
                "   - If multiple sources conflict, list all versions\n"
                "4. For funding data:\n"
                "   - Only mark as verified if from TechCrunch, Crunchbase, or official announcements\n"
                "   - Otherwise state as 'reported funding'\n"
                "5. For location and team size:\n"
                "   - List all reported locations with sources\n"
                "   - Include date for team size claims\n"
                "6. Do NOT include a separate confidence levels section\n"
                "7. Include source attribution directly in each bullet point\n"
            )

            messages = [
                SystemMessage(
                    content=(
                        "You are an expert at analyzing early-stage companies and extracting key business model "
                        "information. You carefully evaluate source reliability and clearly distinguish "
                        "between verified facts and marketing claims in your analysis."
                    )
                ),
                HumanMessage(content=prompt),
            ]

            icp_research_data = self.llm.generate_response(
                messages,
                model_type="advanced",  # Force advanced model here
                temperature=self.temperature,
            )

            logger.info(f"Generated ICP research data for {company_name}:")
            logger.info(icp_research_data)

            return icp_research_data

        except Exception as e:
            logger.error(f"Error generating ICP research data: {str(e)}")
            raise
