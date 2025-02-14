import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse

from langchain.schema import HumanMessage
from langchain_community.document_loaders import WebBaseLoader

from src.logger import get_logger
from src.models.company.company import Company
from src.services.llm.factory import LLMFactory
from src.services.web_search.factory import WebSearchFactory
from src.utilities.url import get_domain

logger = get_logger(__name__)


class CompanyWebResearcher:
    """Agent that researches a company by scraping related web pages and summarizing the content."""

    def __init__(
        self,
        num_urls: int = 3,
        max_retries: int = 2,
        concurrency: int = 5,
    ):
        self.llm = LLMFactory.get_provider()
        self.web_search = WebSearchFactory.get_provider()
        self.num_urls = num_urls
        self.max_retries = max_retries
        self.concurrency = concurrency

        # Define model configurations for different tasks
        self.model_config = {
            "summarization": {"model_type": "basic", "temperature": 0.0},
            "validation": {"model_type": "basic", "temperature": 0.0},
            "extraction": {"model_type": "basic", "temperature": 0.0},
            "analysis": {"model_type": "reasoning", "temperature": 1.0},
        }
        logger.info(
            "CompanyWebResearcher initialized with LLM, WebSearch providers and model configurations"
        )

    def research_company(self, company: Company) -> dict:
        """Research the company by performing multiple targeted searches and consolidate the information."""
        try:
            company_name = company.company_name
            website_url = str(company.website_url)
            domain = get_domain(website_url)
            logger.info(f"Starting research for company: {company_name}, {domain}")

            # Step 1: Scrape the Home Page - Essential step
            home_page_doc = self.scrape_urls_concurrently([website_url])
            if not home_page_doc:
                logger.error(
                    f"Failed to scrape home page for {company_name}. Halting research process."
                )
                raise ValueError(f"Failed to scrape home page for {company_name}")

            home_page_doc = home_page_doc[0]
            relevant_text = self.extract_relevant_info(
                company, home_page_doc.page_content
            )
            home_page_summary = self.summarize_text(company, relevant_text)

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
                documents, company, home_page_summary
            )

            # Include home page summary if available
            if home_page_summary:
                doc_summaries.append(home_page_summary)

            # Create initial summaries
            summaries = {
                "home_page_summary": home_page_summary,
                "comprehensive_summary": self.create_comprehensive_summary(
                    company, doc_summaries
                ),
                "company_summary": self.create_company_summary(company, doc_summaries),
                "funding_summary": self.create_funding_summary(company, doc_summaries),
                "team_summary": self.create_team_summary(company, doc_summaries),
            }

            # Add ICP research data after other summaries are created
            summaries["icp_research_data"] = self.generate_icp_research_data(
                company, summaries
            )

            logger.info("Completed research and summarization.")

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
        self, documents: list, company: Company, home_page_summary: str
    ) -> list:
        """
        Summarize multiple documents in parallel. Extract relevant info for each
        document, then produce a concise summary.
        """
        summaries = []
        with ThreadPoolExecutor(max_workers=self.concurrency) as executor:
            future_to_doc = {
                executor.submit(
                    self.process_document, doc, company, home_page_summary
                ): doc
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

    def process_document(self, doc, company: Company, home_page_summary: str) -> str:
        """
        Extract relevant info from the document and then summarize that info.
        """
        if not self.validate_document_relevance(doc, company, home_page_summary):
            logger.debug(
                f"Skipping irrelevant document from {doc.metadata.get('source')}"
            )
            return None

        relevant_text = self.extract_relevant_info(company, doc.page_content)
        return self.summarize_text(company, relevant_text)

    def validate_document_relevance(
        self, doc, company: Company, home_page_summary: str
    ) -> bool:
        """Validate document relevance using multiple criteria."""
        content = doc.page_content.lower()
        company_domain = get_domain(str(company.website_url)).lower()
        company_name = company.company_name.lower()

        # 1. Direct domain match in content
        if company_domain in content:
            return True

        # 2. Check for linked domain in metadata
        if "source" in doc.metadata:
            doc_domain = get_domain(doc.metadata["source"]).lower()
            if doc_domain == company_domain:
                return True

        # 3. LLM-powered contextual validation with home page context
        validation_prompt = f"""
        Does the following content refer to the same company described in the official home page summary?

        Company name: {company.company_name}
        Official domain: {str(company.website_url)}

        Home page summary: {home_page_summary}

        Content to verify: {content[:2000]}...

        Answer YES if the content clearly describes the same company (using details like products, leadership, location, or funding); otherwise, answer NO. Please respond only with YES or NO.
        """

        response = self.llm.generate_response(
            [HumanMessage(content=validation_prompt)],
            model_type=self.model_config["validation"]["model_type"],
            temperature=self.model_config["validation"]["temperature"],
        )

        # Add confidence threshold
        if response.strip().upper() not in ["YES", "NO"]:
            logger.warning(f"Unexpected LLM validation response: {response}")
            return False  # Fail closed

        # Add validation logging
        logger.debug(
            f"Validation result for {doc.metadata.get('source')}: {response.strip()}"
        )

        return response.strip().upper() == "YES"

    def extract_relevant_info(self, company: Company, text: str) -> str:
        """
        Extract relevant information about the company from the scraped text.
        """
        try:
            prompt = (
                f"Extract relevant information about {company.company_name} (website: {str(company.website_url)}) "
                f"and provide a summary of no more than 500 words.\n\n" + text
            )
            messages = [
                HumanMessage(
                    content=(
                        f"You are a helpful assistant that extracts comprehensive content about {company.company_name} "
                        f"(website: {str(company.website_url)}). Be sure to distinguish this company from others with similar names "
                        f"by using the website URL as a key identifier."
                    )
                ),
                HumanMessage(content=prompt),
            ]
            extracted_info = self.llm.generate_response(
                messages,
                model_type=self.model_config["extraction"]["model_type"],
                temperature=self.model_config["extraction"]["temperature"],
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

    def summarize_text(self, company: Company, text: str) -> str:
        """
        Summarize the given text using the language model.
        """
        try:
            logger.debug(f"Summarizing text excerpt")

            prompt = (
                f"Provide a summary of the following information about a company named {company.company_name} "
                f"(website: {str(company.website_url)}).\n\n{text}"
            )
            messages = [
                HumanMessage(
                    content=(
                        f"You are a helpful assistant that summarizes content about a company named {company.company_name} "
                        f"(website: {str(company.website_url)}). Always verify company identity using the website URL when "
                        "summarizing information."
                    )
                ),
                HumanMessage(content=prompt),
            ]
            summary = self.llm.generate_response(
                messages,
                model_type=self.model_config["summarization"]["model_type"],
                temperature=self.model_config["summarization"]["temperature"],
            )
            return summary
        except Exception as e:
            logger.error(f"Error summarizing text: {str(e)}")
            raise

    def create_comprehensive_summary(self, company: Company, summaries: list) -> str:
        """
        Create a concise, single-paragraph summary (no more than 250 words) from all individual summaries.
        """
        try:
            combined_text = "\n".join(summaries)
            prompt = (
                f"Review all relevant details from the following summaries about a company named '{company.company_name}' "
                f"(website: {str(company.website_url)}). If there are mentions of multiple entities with the same name, focus on "
                "whichever references are most clearly about the actual company using the website URL as verification."
            )
            messages = [
                HumanMessage(
                    content=(
                        "You are an expert at synthesizing information about a specific company. "
                        "You will create a concise overview that stays focused on the correct company."
                    )
                ),
                HumanMessage(content=prompt),
            ]
            comprehensive_summary = self.llm.generate_response(
                messages,
                model_type=self.model_config["summarization"]["model_type"],
                temperature=self.model_config["summarization"]["temperature"],
            )
            logger.debug("Generated concise comprehensive summary.")
            return comprehensive_summary
        except Exception as e:
            logger.error(f"Error creating comprehensive summary: {str(e)}")
            raise

    def create_company_summary(self, company: Company, summaries: list) -> str:
        """Create a summary focused on company overview, products, and services."""
        try:
            combined_text = "\n".join(summaries)
            prompt = (
                f"From the following summaries about {company.company_name} (website: {str(company.website_url)}), create a "
                "focused summary about the company's core business, products, and services. Include their main value proposition "
                "and target market. Keep it factual and concise.\n\n"
                f"{combined_text}"
            )
            messages = [
                HumanMessage(
                    content="You are an expert at summarizing company business models and offerings."
                ),
                HumanMessage(content=prompt),
            ]
            return self.llm.generate_response(
                messages,
                model_type=self.model_config["summarization"]["model_type"],
                temperature=self.model_config["summarization"]["temperature"],
            )
        except Exception as e:
            logger.error(f"Error creating company summary: {str(e)}")
            raise

    def create_funding_summary(self, company: Company, summaries: list) -> str:
        """Create a summary focused on funding and financial information."""
        try:
            combined_text = "\n".join(summaries)
            prompt = (
                f"From the following summaries about {company.company_name} (website: {str(company.website_url)}), create a "
                "focused summary about the company's funding history, including total funding amount, funding rounds, key investors, "
                "and any relevant financial metrics. Keep it factual and concise.\n\n"
                f"{combined_text}"
            )
            messages = [
                HumanMessage(
                    content="You are an expert at summarizing company funding and financial information."
                ),
                HumanMessage(content=prompt),
            ]
            return self.llm.generate_response(
                messages,
                model_type=self.model_config["extraction"]["model_type"],
                temperature=self.model_config["extraction"]["temperature"],
            )
        except Exception as e:
            logger.error(f"Error creating funding summary: {str(e)}")
            raise

    def create_team_summary(self, company: Company, summaries: list) -> str:
        """Create a summary focused on team and leadership information."""
        try:
            combined_text = "\n".join(summaries)
            prompt = (
                f"From the following summaries about {company.company_name} (website: {str(company.website_url)}), create a "
                "focused summary about the company's team, including founders, key executives, and any relevant background "
                "information about the leadership. Keep it factual and concise.\n\n"
                f"{combined_text}"
            )
            messages = [
                HumanMessage(
                    content="You are an expert at summarizing company team and leadership information."
                ),
                HumanMessage(content=prompt),
            ]
            return self.llm.generate_response(
                messages,
                model_type=self.model_config["extraction"]["model_type"],
                temperature=self.model_config["extraction"]["temperature"],
            )
        except Exception as e:
            logger.error(f"Error creating team summary: {str(e)}")
            raise

    def generate_icp_research_data(self, company: Company, summaries: dict) -> str:
        """Generate ICP-focused research data from existing summaries."""
        try:
            combined_text = (
                f"Comprehensive: {summaries['comprehensive_summary']}\n"
                f"Company: {summaries['company_summary']}\n"
                f"Funding: {summaries['funding_summary']}\n"
                f"Team: {summaries['team_summary']}"
            )

            prompt = (
                f"Based on the following information about {company.company_name} (website: {str(company.website_url)}), create a focused research summary "
                "that MUST follow this EXACT format:\n\n"
                f"{company.company_name} business details:\n"
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
                f"Now, create a similar summary for {company.company_name} using this information:\n\n"
                f"{combined_text}\n\n"
                "IMPORTANT:\n"
                "1. You MUST start with exactly '{company.company_name} business details:'\n"
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
                HumanMessage(
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
                model_type=self.model_config["analysis"]["model_type"],
                temperature=self.model_config["analysis"]["temperature"],
            )

            logger.info(f"Generated ICP research data for {company.company_name}:")
            logger.info(icp_research_data)

            return icp_research_data

        except Exception as e:
            logger.error(f"Error generating ICP research data: {str(e)}")
            raise
