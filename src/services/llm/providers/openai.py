from typing import Type

from langchain.schema import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from pydantic import BaseModel

from src.config import config
from src.logger import get_logger
from src.services.llm.interface import LLMInterface

logger = get_logger(__name__)


class OpenAIProvider(LLMInterface):
    def __init__(self, config):
        self.config = config
        self.chat_models = {}
        self.embedding_model = None

    def create_chat_model(
        self, model_type: str = "basic", temperature: float = None
    ) -> ChatOpenAI:
        model_name = getattr(
            self.config["llm"], f"{model_type}_model", self.config["llm"].basic_model
        )
        temperature = temperature if temperature is not None else 0.7
        key = (model_type, temperature)
        if key not in self.chat_models:
            try:
                self.chat_models[key] = ChatOpenAI(
                    model_name=model_name,
                    temperature=temperature,
                )
                logger.info(
                    f"Created chat model: {model_name} with temperature {temperature}"
                )
            except Exception as e:
                logger.error(f"Failed to create chat model: {e}")
                raise
        return self.chat_models[key]

    def create_embedding_model(self) -> OpenAIEmbeddings:
        if not self.embedding_model:
            try:
                self.embedding_model = OpenAIEmbeddings(
                    model=self.config["llm"].embedding_model
                )
                logger.info("Created embedding model.")
            except Exception as e:
                logger.error(f"Failed to create embedding model: {e}")
                raise
        return self.embedding_model

    def generate_response(
        self, messages: list, model_type: str = "basic", temperature: float = None
    ) -> str:
        chat_model = self.create_chat_model(
            model_type=model_type, temperature=temperature
        )
        try:
            response = chat_model.invoke(messages)
            logger.debug(f"Generated response: {response.content}")
            return response.content
        except Exception as e:
            logger.error(f"Failed to generate response: {e}")
            raise

    def generate_structured_response(
        self,
        messages: list,
        schema: Type[BaseModel],
        model_type: str = "basic",
        temperature: float = None,
    ) -> BaseModel:
        """Generates a structured response using the chat model."""
        chat_model = self.create_chat_model(
            model_type=model_type, temperature=temperature
        )
        model_with_structure = chat_model.with_structured_output(schema)
        try:
            structured_output = model_with_structure.invoke(messages)
            logger.debug(f"Generated structured response: {structured_output}")
            return schema.model_validate(structured_output)
        except Exception as e:
            logger.error(f"Error generating structured response: {e}")
            raise

    def generate_embeddings(self, text: str) -> list:
        embedding_model = self.create_embedding_model()
        try:
            embeddings = embedding_model.embed_query(text)
            logger.debug(f"Generated embeddings for text: {text}")
            return embeddings
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}")
            raise
