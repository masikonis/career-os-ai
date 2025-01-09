import os
from typing import Dict

from dotenv import load_dotenv

# Add model configurations
LLM_MODELS = {
    "basic": "gpt-4o-mini",
    "advanced": "gpt-4o",
    "reasoning": "o1-preview",
    "embeddings": "text-embedding-3-small",
}


def load_config() -> Dict[str, str]:
    """Load configuration, prioritizing .env file over environment variables"""
    # First, store any existing env vars we want to override
    existing_vars = {}
    for key in [
        "OPENAI_API_KEY",
        "LANGCHAIN_API_KEY",
    ]:
        if key in os.environ:
            existing_vars[key] = os.environ[key]
            del os.environ[key]

    # Now load .env file
    load_dotenv(override=True)

    # Create config dictionary with added models
    config = {
        "LLM_MODELS": LLM_MODELS,
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "LANGCHAIN_API_KEY": os.getenv("LANGCHAIN_API_KEY"),
    }

    # Restore original env vars if needed
    for key, value in existing_vars.items():
        os.environ[key] = value

    return config


# Create a global config object
config = load_config()
