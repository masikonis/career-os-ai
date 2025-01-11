import pytest
from langchain.schema import HumanMessage, SystemMessage

from src.llm.factory import create_provider
from src.llm.providers import ProviderType
from src.logger import get_logger

logger = get_logger(__name__)


@pytest.mark.smoke
def test_openai_provider_smoke():
    # Create an instance of the OpenAI provider
    provider = create_provider(ProviderType.OPENAI)

    # Define the messages
    messages = [
        SystemMessage(content="You are a helpful assistant."),
        HumanMessage(content="Hello, how can I help you today?"),
    ]

    # Generate a response using the chat model
    try:
        response = provider.generate_response(
            messages, model_type="basic", temperature=0.5
        )
        logger.debug(f"Chat model response: {response}")
        # Check if the response is not empty
        assert response is not None
        assert len(response) > 0
        logger.info("Chat model response generated successfully.")
    except Exception as e:
        logger.error(f"Failed to generate chat model response: {e}")
        raise

    # Generate embeddings using the embedding model
    try:
        text = "This is a sample text for embedding."
        embeddings = provider.generate_embeddings(text)
        logger.debug(f"Embeddings: {embeddings[:100]}")
        # Check if the embeddings are not empty
        assert embeddings is not None
        assert len(embeddings) > 0
        logger.info("Embeddings generated successfully.")
    except Exception as e:
        logger.error(f"Failed to generate embeddings: {e}")
        raise
