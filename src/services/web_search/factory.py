from src.logger import get_logger
from src.services.web_search.interface import WebSearchInterface
from src.services.web_search.providers.tavily import Tavily

logger = get_logger(__name__)


class WebSearchFactory:
    @staticmethod
    def get_provider(provider_name: str = "tavily") -> WebSearchInterface:
        if provider_name.lower() == "tavily":
            logger.info("Initializing Tavily provider")
            return Tavily()
        else:
            logger.error(f"Provider '{provider_name}' not found")
            raise ValueError(f"Provider '{provider_name}' is not supported.")
