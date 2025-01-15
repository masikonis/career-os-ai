from tavily import TavilyClient

from src.cache import CacheManager
from src.config import config
from src.logger import get_logger
from src.services.web_search.interface import WebSearchInterface

logger = get_logger(__name__)


class TavilyProvider(WebSearchInterface):
    def __init__(self):
        self.client = TavilyClient(api_key=config["TAVILY_API_KEY"])
        self.cache = CacheManager()

    def search(self, query: str) -> list:
        cached_results = self.cache.get(query)
        if cached_results is not None:
            return cached_results
        try:
            response = self.client.search(query)
            results = response.get("results", [])
            self.cache.set(query, results)
            return results
        except Exception as e:
            logger.error(f"An error occurred during search: {e}")
            return []
