from src.logger import get_logger

logger = get_logger(__name__)


def sanitize_text(text: str) -> str:
    """Clean and normalize text content by collapsing whitespace.

    Args:
        text: Input string to be sanitized

    Returns:
        Empty string if input is falsy, otherwise normalized string
    """
    if not text:
        logger.debug("Received empty text in sanitize_text")
        return ""

    if not isinstance(text, str):
        logger.warning(f"Non-string input to sanitize_text: {type(text)}")
        text = str(text)

    return " ".join(text.split())


def preserve_paragraphs(text: str) -> str:
    """Preserve paragraph breaks while normalizing text content.

    Args:
        text: Input string with potential paragraph breaks

    Returns:
        String with preserved paragraph structure and normalized whitespace
    """
    if not text:
        logger.debug("Received empty text in preserve_paragraphs")
        return ""

    if not isinstance(text, str):
        logger.warning(f"Non-string input to preserve_paragraphs: {type(text)}")
        text = str(text)

    # Split into paragraphs using double newlines
    paragraphs = text.split("\n\n")

    # Process and filter paragraphs
    processed_paragraphs = [sanitize_text(p) for p in paragraphs]
    filtered_paragraphs = [p for p in processed_paragraphs if p]

    logger.debug(
        f"Processed {len(paragraphs)} paragraphs, {len(filtered_paragraphs)} remaining after filtering"
    )
    return "\n\n".join(filtered_paragraphs)
