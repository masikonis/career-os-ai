import os
from typing import Dict

from dotenv import load_dotenv
from pydantic import BaseModel

from src.logger import get_logger
from src.services.llm.providers import ProviderType

logger = get_logger(__name__)


class LLMSettings(BaseModel):
    provider: ProviderType = ProviderType.OPENAI
    basic_model: str = "gpt-4o-mini"
    advanced_model: str = "gpt-4o"
    reasoning_model: str = "o1-mini"
    embedding_model: str = "text-embedding-3-small"


def load_config() -> Dict[str, str]:
    """Load configuration, prioritizing .env file over environment variables"""
    # First, store any existing env vars we want to override
    existing_vars = {}
    for key in ["OPENAI_API_KEY", "LANGCHAIN_API_KEY", "TAVILY_API_KEY", "USER_AGENT"]:
        if key in os.environ:
            existing_vars[key] = os.environ[key]
            del os.environ[key]

    load_dotenv(override=True)

    # Create config dictionary with added models
    config = {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "LANGCHAIN_API_KEY": os.getenv("LANGCHAIN_API_KEY"),
        "TAVILY_API_KEY": os.getenv("TAVILY_API_KEY"),
        "USER_AGENT": os.getenv("USER_AGENT"),
    }

    # Load LLM settings
    config["llm"] = LLMSettings()

    # Restore original env vars if needed
    for key, value in existing_vars.items():
        os.environ[key] = value

    return config


# Create a global config object
config = load_config()
