from src.config import config
from src.logger import get_logger
from src.services.llm.interface import LLMInterface
from src.services.llm.providers import ProviderType
from src.services.llm.providers.openai import OpenAIProvider

logger = get_logger(__name__)


class LLMFactory:
    @staticmethod
    def get_provider(provider_type: ProviderType = ProviderType.OPENAI) -> LLMInterface:
        providers = {ProviderType.OPENAI: OpenAIProvider(config)}

        if provider_type not in providers:
            logger.error(f"LLM Provider type '{provider_type}' is unsupported")
            raise ValueError(f"Unsupported provider type: {provider_type}")

        logger.info(f"Initializing LLM provider: {provider_type.name}")
        return providers[provider_type]
