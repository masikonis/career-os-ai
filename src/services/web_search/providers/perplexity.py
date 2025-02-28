import httpx
from openai import OpenAI

from src.cache import CacheManager
from src.config import config
from src.logger import get_logger
from src.services.web_search.interface import WebSearchInterface

logger = get_logger(__name__)


class PerplexityProvider(WebSearchInterface):
    """Perplexity AI provider for web search."""

    def __init__(self):
        self.api_key = config["PERPLEXITY_API_KEY"]
        self.base_url = "https://api.perplexity.ai"
        self.cache = CacheManager()

        if not self.api_key:
            logger.error("Perplexity API key not found in configuration")
            raise ValueError("Perplexity API key is required")

        # Initialize OpenAI client with Perplexity base URL
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)

    def basic_search(self, query: str) -> list[dict[str, str]]:
        """Performs a basic web search using Perplexity's standard model."""
        cache_key = f"perplexity_basic_{query}"
        cached_results = self.cache.get(cache_key)
        if cached_results is not None:
            return cached_results

        try:
            # Use a 60-second timeout for basic search
            response = self._make_api_request(query, "sonar", timeout=60.0)
            results = self._process_search_results(response)
            self.cache.set(cache_key, results)
            return results
        except Exception as e:
            logger.error(f"Error during basic search: {e}")
            return []

    def advanced_search(self, query: str) -> list[dict[str, str]]:
        """Performs an advanced web search using Perplexity's pro model."""
        cache_key = f"perplexity_advanced_{query}"
        cached_results = self.cache.get(cache_key)
        if cached_results is not None:
            return cached_results

        try:
            # Use a 120-second timeout for advanced search
            response = self._make_api_request(query, "sonar-pro", timeout=120.0)
            results = self._process_search_results(response)
            self.cache.set(cache_key, results)
            return results
        except Exception as e:
            logger.error(f"Error during advanced search: {e}")
            return []

    def research_search(self, query: str) -> dict[str, any]:
        """Performs an in-depth research search using Perplexity's deep research model."""
        cache_key = f"perplexity_research_{query}"
        cached_results = self.cache.get(cache_key)
        if cached_results is not None:
            return cached_results

        try:
            # Use a much longer timeout for research search (15 minutes)
            response = self._make_api_request(
                query, "sonar-deep-research", timeout=900.0
            )
            result = self._process_research_results(response)
            self.cache.set(cache_key, result)
            return result
        except Exception as e:
            logger.error(f"Error during research search: {e}")
            return {"content": "", "sources": []}

    def _make_api_request(self, query: str, model: str, timeout: float = 60.0) -> dict:
        """Makes an API request to Perplexity using the OpenAI client.

        Args:
            query: The search query
            model: The model to use
            timeout: The timeout in seconds (default: 60.0)
        """
        logger.info(
            f"Making API request to Perplexity with model: {model}, timeout: {timeout}s"
        )

        try:
            # Create messages for the API request
            messages = [{"role": "user", "content": query}]

            # Set request timeout
            self.client.timeout = timeout

            # Make the API call
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.0,  # Lower temperature for more factual responses
            )

            # Log token usage for cost estimation
            if hasattr(response, "usage") and response.usage:
                logger.info(
                    f"Token usage - Prompt: {response.usage.prompt_tokens}, "
                    + f"Completion: {response.usage.completion_tokens}, "
                    + f"Total: {response.usage.total_tokens}"
                )

            # Convert OpenAI response to dict format expected by processing methods
            return {
                "choices": [
                    {
                        "message": {"content": response.choices[0].message.content},
                        "citations": getattr(
                            response.choices[0].message, "citations", []
                        ),
                    }
                ]
            }

        except Exception as e:
            logger.error(f"Error calling Perplexity API: {str(e)}")
            raise

    def _process_search_results(self, response: dict) -> list[dict[str, str]]:
        """Processes the search results from the API response."""
        try:
            results = []

            # Extract the main content
            if "choices" in response and response["choices"]:
                content = response["choices"][0]["message"]["content"]

                # Extract citations if available
                citations = []
                if "citations" in response["choices"][0]:
                    citations = response["choices"][0]["citations"]

                # If we have citations, create a result for each one
                if citations:
                    for citation in citations:
                        results.append(
                            {
                                "content": citation.get("text", ""),
                                "source": citation.get("url", ""),
                            }
                        )
                # If no citations, use the main content as a single result
                else:
                    results.append({"content": content, "source": "Perplexity AI"})

            return results
        except Exception as e:
            logger.error(f"Error processing search results: {e}")
            return []

    def _process_research_results(self, response: dict) -> dict[str, any]:
        """Processes the research results from the API response."""
        try:
            # Extract the main content
            content = ""
            sources = []

            if "choices" in response and response["choices"]:
                content = response["choices"][0]["message"]["content"]

                # Extract citations if available
                if "citations" in response["choices"][0]:
                    for citation in response["choices"][0]["citations"]:
                        if "url" in citation:
                            sources.append(citation["url"])

            return {"content": content, "sources": sources}
        except Exception as e:
            logger.error(f"Error processing research results: {e}")
            return {"content": "", "sources": []}
