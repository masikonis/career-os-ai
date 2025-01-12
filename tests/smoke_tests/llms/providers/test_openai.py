import pytest
from langchain.schema import HumanMessage, SystemMessage

from src.llms.factory import create_provider
from src.llms.providers import ProviderType
from src.logger import get_logger

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
        logger.debug(f"Chat model response: {response}")
        assert response is not None, "Chat response is None."
        assert len(response) > 0, "Chat response is empty."
        logger.info("Chat model response generated successfully.")
    except Exception as e:
        logger.error(f"Failed to generate chat model response: {e}")
        raise

    # Structured response test
    try:
        schema = {
            "title": "ResponseFormatter",
            "type": "object",
            "properties": {
                "answer": {
                    "type": "string",
                    "description": "The answer to the user's question",
                },
                "followup_question": {
                    "type": "string",
                    "description": "A followup question the user could ask",
                },
            },
            "required": ["answer", "followup_question"],
        }
        structured_response = provider.generate_structured_response(
            messages, schema, model_type="basic", temperature=0.5
        )
        logger.debug(f"Structured response: {structured_response}")
        assert isinstance(
            structured_response, dict
        ), "Structured response is not a dictionary."
        assert "answer" in structured_response and isinstance(
            structured_response["answer"], str
        ), "Structured response missing 'answer' or it is not a string."
        assert "followup_question" in structured_response and isinstance(
            structured_response["followup_question"], str
        ), "Structured response missing 'followup_question' or it is not a string."
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
