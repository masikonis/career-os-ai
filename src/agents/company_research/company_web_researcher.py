import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse

from langchain.schema import HumanMessage, SystemMessage
from langchain_community.document_loaders import WebBaseLoader

from src.logger import get_logger
from src.models.company.company_info import CompanyInfo
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
        concurrency: int = 3,
    ):
        self.llm = LLMFactory.get_provider()
        self.web_search = WebSearchFactory.get_provider()
        self.model_type = model_type
        self.temperature = temperature
        self.num_urls = num_urls
        self.max_retries = max_retries
        self.concurrency = concurrency
        logger.info("CompanyWebResearcher initialized with LLM and WebSearch providers")

    def research_company(self, company_info: CompanyInfo) -> str:
        """Research the company by performing multiple targeted searches and consolidate the information."""
        try:
            company_name = company_info.company_name
            website_url = str(company_info.website_url)
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

            # Step 2: Search for Company Name
            company_search_results = self.web_search.search(company_name)[
                : self.num_urls
            ]
            company_related_urls = [
                result["url"] for result in company_search_results if "url" in result
            ]

            # Step 3: Search for Funding Information
            funding_query = f"{company_name} funding"
            funding_search_results = self.web_search.search(funding_query)[
                : self.num_urls
            ]
            funding_related_urls = [
                result["url"] for result in funding_search_results if "url" in result
            ]

            # Step 4: Search for Team Information
            team_query = f"{company_name} team"
            team_search_results = self.web_search.search(team_query)[: self.num_urls]
            team_related_urls = [
                result["url"] for result in team_search_results if "url" in result
            ]

            # Step 5: Search for Sentiment Analysis
            sentiment_query = f"{company_name} reviews"
            sentiment_search_results = self.web_search.search(sentiment_query)[
                : self.num_urls
            ]
            sentiment_related_urls = [
                result["url"] for result in sentiment_search_results if "url" in result
            ]

            # Aggregate all URLs
            all_related_urls = (
                company_related_urls
                + funding_related_urls
                + team_related_urls
                + sentiment_related_urls
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
                return ""

            # Summarize each document
            summaries = []
            for doc in documents:
                try:
                    relevant_text = self.extract_relevant_info(
                        company_name, doc.page_content
                    )
                    summary = self.summarize_text(company_name, relevant_text)
                    summaries.append(summary)
                except Exception as e:
                    logger.error(
                        f"Error summarizing document from {doc.metadata.get('source')}: {str(e)}"
                    )

            # Include home page summary if available
            if home_page_summary:
                summaries.append(home_page_summary)

            # Consolidate all summaries into a final comprehensive summary
            final_summary = self.create_final_summary(company_name, summaries)
            logger.info("Completed research and summarization.")
            logger.debug(final_summary)

            return final_summary

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

    def extract_relevant_info(self, company_name: str, text: str) -> str:
        """Extract relevant information about the company from the scraped text."""
        try:
            prompt = (
                f"Extract relevant information about {company_name} and provide a summary of no more than 500 words.\n\n"
                + text
            )
            messages = [
                SystemMessage(
                    content=f"You are a helpful assistant that extracts comprehensive content about {company_name}."
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
        """Summarize the given text using the language model."""
        try:
            prompt = f"Provide a summary of the following information about {company_name}.\n\n{text}"
            messages = [
                SystemMessage(
                    content=f"You are a helpful assistant that summarizes content about {company_name}."
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

    def create_final_summary(self, company_name: str, summaries: list) -> str:
        """Create a concise, single-paragraph summary (no more than 250 words) from all individual summaries."""
        try:
            combined_text = "\n".join(summaries)
            prompt = (
                f"Critically evaluate the following summaries and synthesize a single-paragraph description of {company_name}, "
                "no more than 250 words. Present an overall portrayal that captures the company’s focus, offerings, and "
                "key attributes in a concise, balanced manner.\n\n"
                f"{combined_text}"
            )
            messages = [
                SystemMessage(
                    content="You are an expert in synthesizing information to create concise company overviews."
                ),
                HumanMessage(content=prompt),
            ]
            final_summary = self.llm.generate_response(
                messages, model_type=self.model_type, temperature=self.temperature
            )
            logger.debug("Generated concise final summary.")
            return final_summary
        except Exception as e:
            logger.error(f"Error creating final summary: {str(e)}")
            raise
