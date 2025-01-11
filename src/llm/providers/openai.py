import logging

from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from src.config import config
from src.llm.interface import LLMProvider

logger = logging.getLogger(__name__)


class OpenAIProvider(LLMProvider):
    def __init__(self, config):
        self.config = config

    def get_chat_model(self, temperature: float = None) -> ChatOpenAI:
        temperature = temperature or self.config["llm"].temperature
        try:
            return ChatOpenAI(
                model_name=self.config["llm"].default_model,
                temperature=temperature,
            )
        except Exception as e:
            logger.error(f"Failed to get chat model: {e}")
            raise

    def get_embeddings(self) -> OpenAIEmbeddings:
        try:
            return OpenAIEmbeddings(model=self.config["llm"].embedding_model)
        except Exception as e:
            logger.error(f"Failed to get embeddings: {e}")
            raise
