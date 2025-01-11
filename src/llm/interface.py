from abc import ABC, abstractmethod

from langchain.chat_models.base import BaseChatModel
from langchain.embeddings.base import Embeddings


class LLMProvider(ABC):
    """Base interface for LLM providers using LangChain."""

    @abstractmethod
    def get_chat_model(self) -> BaseChatModel:
        """Returns configured chat model."""
        pass

    @abstractmethod
    def get_embeddings(self) -> Embeddings:
        """Returns configured embeddings model."""
        pass
