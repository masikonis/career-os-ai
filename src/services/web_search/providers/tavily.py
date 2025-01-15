from tavily import TavilyClient

from src.config import config
from src.logger import get_logger
from src.services.web_search.interface import WebSearchInterface

logger = get_logger(__name__)


class TavilyProvider(WebSearchInterface):
    def __init__(self):
        self.client = TavilyClient(api_key=config["TAVILY_API_KEY"])

    def search(self, query: str) -> list:
        try:
            response = self.client.search(query)
            results = response.get("results", [])
            return results
        except Exception as e:
            logger.error(f"An error occurred during search: {e}")
            return []
