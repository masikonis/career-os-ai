from src.logger import get_logger
from src.services.scraper.interface import ScraperInterface
from src.services.scraper.providers import ProviderType
from src.services.scraper.providers.requests import RequestsProvider

logger = get_logger(__name__)


class ScraperFactory:
    @staticmethod
    def get_provider(
        provider_type: ProviderType = ProviderType.REQUESTS,
    ) -> ScraperInterface:
        providers = {ProviderType.REQUESTS: RequestsProvider()}

        if provider_type not in providers:
            logger.error(f"Scraper provider type '{provider_type}' not found")
            raise ValueError(f"Provider '{provider_type}' is not supported.")

        logger.info(f"Initializing Scraper provider: {provider_type.name}")
        return providers[provider_type]
