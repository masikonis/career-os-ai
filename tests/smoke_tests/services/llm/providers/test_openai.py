import pytest
from langchain.schema import HumanMessage, SystemMessage

from src.logger import get_logger
from src.models.company.company import Company
from src.services.llm.factory import LLMFactory
from src.services.llm.interface import LLMInterface
from src.services.llm.providers import ProviderType

logger = get_logger(__name__)


@pytest.mark.smoke
def test_openai_provider_smoke():
    provider: LLMInterface = LLMFactory.get_provider(ProviderType.OPENAI)

    messages = [
        SystemMessage(content="You are a helpful assistant."),
        HumanMessage(content="Hello, how can I help you today?"),
    ]

    # Response test
    try:
        response = provider.generate_response(
            messages, model_type="basic", temperature=0.5
        )
        assert response is not None, "Chat response is None."
        assert len(response) > 0, "Chat response is empty."
        logger.info("Chat model response generated successfully.")
    except Exception:
        logger.error("Failed to generate chat model response.", exc_info=True)
        raise

    # Company structured response test
    try:
        structured_response = provider.generate_structured_response(
            messages, Company, model_type="basic", temperature=0.5
        )

        assert isinstance(
            structured_response, Company
        ), "Structured response is not an instance of Company."

        assert structured_response.info.company_name, "Company 'company_name' is empty."
        assert structured_response.info.website_url, "Company 'website_url' is empty."

        logger.info("Company structured response generated successfully.")
    except Exception:
        logger.error("Failed to generate company structured response.", exc_info=True)
        raise

    # Embedding test
    try:
        text = "This is a sample text for embedding."
        embeddings = provider.generate_embeddings(text)
        assert embeddings is not None, "Embeddings are None."
        assert len(embeddings) > 0, "Embeddings are empty."
        logger.info("Embeddings generated successfully.")
    except Exception:
        logger.error("Failed to generate embeddings.", exc_info=True)
        raise
