from src.config import config
from src.llm.interface import LLMProvider
from src.llm.providers import ProviderType
from src.llm.providers.openai import OpenAIProvider


def create_provider(provider_type: ProviderType, config=config) -> LLMProvider:
    """Create LLM provider instance based on provider type."""
    providers = {ProviderType.OPENAI: OpenAIProvider(config)}

    if provider_type not in providers:
        raise ValueError(f"Unsupported provider type: {provider_type}")

    return providers[provider_type]
