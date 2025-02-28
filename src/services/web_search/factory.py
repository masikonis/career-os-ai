from src.logger import get_logger
from src.services.web_search.interface import WebSearchInterface
from src.services.web_search.providers import ProviderType
from src.services.web_search.providers.tavily import TavilyProvider

logger = get_logger(__name__)


class WebSearchFactory:
    @staticmethod
    def get_provider(
        provider_type: ProviderType = ProviderType.TAVILY,
    ) -> WebSearchInterface:
        providers = {ProviderType.TAVILY: TavilyProvider()}

        if provider_type not in providers:
            logger.error(f"WebSearch provider type '{provider_type}' not found")
            raise ValueError(f"Provider '{provider_type}' is not supported.")

        logger.info(f"Initializing WebSearch provider: {provider_type.name}")
        return providers[provider_type]
