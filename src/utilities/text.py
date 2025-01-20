def sanitize_text(text: str) -> str:
    """Clean and normalize text content."""
    if not text:
        return ""
    return " ".join(text.split())


def preserve_paragraphs(text: str) -> str:
    """Preserve paragraph breaks while normalizing text."""
    if not text:
        return ""
    paragraphs = [sanitize_text(p) for p in text.split("\n\n")]
    return "\n\n".join(p for p in paragraphs if p)
