import pytest
from langchain.schema import HumanMessage, SystemMessage

from src.llms.factory import create_provider
from src.llms.providers import ProviderType
from src.logger import get_logger
from src.schemas.basic_response import BasicResponse

logger = get_logger(__name__)


@pytest.mark.smoke
def test_openai_provider_smoke():
    provider = create_provider(ProviderType.OPENAI)

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
    except Exception as e:
        logger.error(f"Failed to generate chat model response: {e}")
        raise

    # Structured response test
    try:
        structured_response = provider.generate_structured_response(
            messages, BasicResponse, model_type="basic", temperature=0.5
        )

        assert isinstance(
            structured_response, BasicResponse
        ), "Structured response is not an instance of BasicResponse."

        assert structured_response.response, "Structured response 'response' is empty."
        assert (
            structured_response.follow_up_question
        ), "Structured response 'follow_up_question' is empty."

        logger.info("Structured response generated successfully.")
    except Exception as e:
        logger.error(f"Failed to generate structured response: {e}")
        raise

    # Embedding test
    try:
        text = "This is a sample text for embedding."
        embeddings = provider.generate_embeddings(text)
        logger.debug(f"Embeddings: {embeddings[:100]}")
        assert embeddings is not None, "Embeddings are None."
        assert len(embeddings) > 0, "Embeddings are empty."
        logger.info("Embeddings generated successfully.")
    except Exception as e:
        logger.error(f"Failed to generate embeddings: {e}")
        raise
