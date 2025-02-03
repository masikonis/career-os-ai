from pathlib import Path
from typing import Optional

from langchain_core.messages import HumanMessage, SystemMessage

from src.logger import get_logger
from src.services.llm.factory import LLMFactory

logger = get_logger(__name__)


class BrandVoiceTextEditor:
    """Agent that edits text to align with brand voice guidelines."""

    def __init__(self, model_type: str = "advanced", temperature: float = 0.3):
        self.llm = LLMFactory.get_provider()
        self.model_type = model_type
        self.temperature = temperature
        self.guidelines = self._load_guidelines()
        logger.info("BrandVoiceTextEditor initialized with LLM provider")

    def _load_guidelines(self) -> str:
        """Load brand voice guidelines from markdown file."""
        try:
            path = Path(__file__).parent / "brand_voice.md"
            return path.read_text(encoding="utf-8")
        except Exception as e:
            logger.error(f"Failed to load brand voice guidelines: {str(e)}")
            raise

    def edit_text(self, text: str, context: Optional[str] = None) -> str:
        """
        Edit text to align with brand voice guidelines.

        Args:
            text: The text to be edited
            context: Optional context about the text's purpose (e.g., "marketing email", "blog post")

        Returns:
            str: Edited text that follows brand voice guidelines
        """
        try:
            # Build the prompt
            prompt = f"""Edit the following text to align with our brand voice guidelines:
            
            Text to edit:
            {text}
            """

            # Add context if provided
            if context:
                prompt += f"\n\nContext: {context}"

            messages = [
                SystemMessage(
                    content=f"""You are a professional copy editor. Your task is to edit text to match our brand voice guidelines.
                    
                    Brand Voice Guidelines:
                    {self.guidelines}
                    """
                ),
                HumanMessage(content=prompt),
            ]

            # Generate the edited text
            edited_text = self.llm.generate_response(
                messages,
                model_type=self.model_type,
                temperature=self.temperature,
            )

            logger.info("Successfully edited text to align with brand voice")
            return edited_text

        except Exception as e:
            logger.error(f"Error editing text: {str(e)}")
            raise

    def batch_edit(self, texts: list[str], context: Optional[str] = None) -> list[str]:
        """
        Edit multiple texts to align with brand voice guidelines.

        Args:
            texts: List of texts to be edited
            context: Optional context about the texts' purpose

        Returns:
            list[str]: List of edited texts
        """
        try:
            edited_texts = []
            for text in texts:
                edited_text = self.edit_text(text, context)
                edited_texts.append(edited_text)
            logger.info(f"Successfully edited {len(texts)} texts")
            return edited_texts
        except Exception as e:
            logger.error(f"Error in batch editing: {str(e)}")
            raise
