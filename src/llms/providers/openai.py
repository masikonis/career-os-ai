from langchain.schema import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from src.config import config
from src.llms.interface import LLMProvider
from src.logger import get_logger

logger = get_logger(__name__)


class OpenAIProvider(LLMProvider):
    def __init__(self, config):
        self.config = config

    def create_chat_model(
        self, model_type: str = "basic", temperature: float = None
    ) -> ChatOpenAI:
        model_name = getattr(
            self.config["llm"], f"{model_type}_model", self.config["llm"].basic_model
        )
        temperature = (
            temperature if temperature is not None else 0.7
        )  # Set a default temperature
        try:
            return ChatOpenAI(
                model_name=model_name,
                temperature=temperature,
            )
        except Exception as e:
            logger.error(f"Failed to create chat model: {e}")
            raise

    def create_embedding_model(self) -> OpenAIEmbeddings:
        try:
            return OpenAIEmbeddings(model=self.config["llm"].embedding_model)
        except Exception as e:
            logger.error(f"Failed to create embedding model: {e}")
            raise

    def generate_response(
        self, messages: list, model_type: str = "basic", temperature: float = None
    ) -> str:
        chat_model = self.create_chat_model(
            model_type=model_type, temperature=temperature
        )
        try:
            response = chat_model.invoke(messages)
            return response.content
        except Exception as e:
            logger.error(f"Failed to generate response: {e}")
            raise

    def generate_embeddings(self, text: str) -> list:
        embedding_model = self.create_embedding_model()
        try:
            embeddings = embedding_model.embed_query(text)
            return embeddings
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}")
            raise
