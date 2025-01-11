from abc import ABC, abstractmethod

from langchain.chat_models.base import BaseChatModel
from langchain.embeddings.base import Embeddings


class LLMProvider(ABC):
    """Base interface for LLM providers using LangChain."""

    @abstractmethod
    def create_chat_model(
        self, model_type: str = "basic", temperature: float = None
    ) -> BaseChatModel:
        """Creates and returns a configured chat model instance."""
        pass

    @abstractmethod
    def create_embedding_model(self) -> Embeddings:
        """Creates and returns a configured embedding model instance."""
        pass

    @abstractmethod
    def generate_response(
        self, messages: list, model_type: str = "basic", temperature: float = None
    ) -> str:
        """Generates a response using the chat model."""
        pass

    @abstractmethod
    def generate_embeddings(self, text: str) -> list:
        """Generates embeddings for the given text."""
        pass
