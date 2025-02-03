from src.agents.copywriting.brand_voice_text_editor import BrandVoiceTextEditor
from src.logger import get_logger

logger = get_logger(__name__)


def test_brand_voice_text_editor_basic_functionality():
    """Smoke test to verify basic functionality of BrandVoiceTextEditor."""
    try:
        # Initialize the editor
        editor = BrandVoiceTextEditor()
        logger.info("Successfully initialized BrandVoiceTextEditor")

        # Test text to edit - shortened Generation Genius description
        test_text = """Generation Genius is an edtech company founded in 2017 by Jeff Vinokur and Eric Rollman. 
        Based in Los Angeles, it creates engaging video lessons in science and math for K-8 students. 
        The platform serves 30% of U.S. elementary schools and has raised $1.6M in funding."""

        context = "company overview"

        # Edit the text
        edited_text = editor.edit_text(test_text, context)
        logger.info(f"Original text: {test_text}")
        logger.info(f"Edited text: {edited_text}")

        # Basic assertions
        assert isinstance(edited_text, str), "Edited text should be a string"
        assert len(edited_text) > 0, "Edited text should not be empty"
        assert test_text != edited_text, "Edited text should be different from original"

        # Verify key information is preserved
        assert "Generation Genius" in edited_text, "Company name should be preserved"
        assert "2017" in edited_text, "Founding year should be preserved"
        assert "Los Angeles" in edited_text, "Location should be preserved"

        logger.info("Smoke test passed successfully")

    except Exception as e:
        logger.error(f"Smoke test failed: {str(e)}")
        raise


if __name__ == "__main__":
    test_brand_voice_text_editor_basic_functionality()
