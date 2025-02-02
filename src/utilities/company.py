import logging
import re
from typing import Optional

# Initialize logger
logger = logging.getLogger(__name__)

# Reordered legal suffixes by descending length to ensure longest matches first
LEGAL_SUFFIXES = (
    " limited liability company",
    " incorporated",
    " corporation",
    " l.l.c.",
    " gmbh",  # German companies
    " limited",
    " s.a.",  # French/Spanish companies
    " p.l.c.",  # UK companies
    " company",
    " corp.",
    " corp",
    " inc.",
    " inc",
    " llc",
    " ltd.",
    " ltd",
    " co.",
    " co",
    " ag",  # Swiss/German companies
    " plc",
    " lp",  # Limited partnership
    " llp",  # Limited liability partnership
    " sarl",  # French/Swiss LLC equivalent
    " bv",  # Dutch companies
    " nv",  # Dutch/Belgian companies
)

# Precompiled regex patterns
_SPECIAL_CHARS_PATTERN = re.compile(r"[^a-z0-9]")
_WHITESPACE_PATTERN = re.compile(r"\s+")


def normalize_company_name(name: Optional[str]) -> str:
    """Normalize company name to consistent format.

    Args:
        name: Company name to normalize

    Returns:
        Normalized name (e.g., 'paypal')

    Examples:
        >>> normalize_company_name('PayPal, Inc.')
        'paypal'
        >>> normalize_company_name('AT&T Corporation')
        'att'
        >>> normalize_company_name('Siemens AG')
        'siemens'
        >>> normalize_company_name('Société Générale S.A.')
        'societegenerale'
    """
    if not name:
        logger.debug("Received empty name in normalize_company_name")
        return ""

    if not isinstance(name, str):
        logger.warning(f"Non-string input to normalize_company_name: {type(name)}")
        return ""

    original_name = name
    normalized = name.lower()

    # Remove all legal suffixes
    while True:
        removed = False
        for suffix in LEGAL_SUFFIXES:
            if normalized.endswith(suffix):
                logger.debug(f"Removed legal suffix '{suffix}' from '{original_name}'")
                normalized = normalized[: -len(suffix)].rstrip()
                removed = True
                break
        if not removed:
            break

    # Normalize Unicode characters first
    normalized = normalize_unicode(normalized)

    # Remove special characters (including &) without replacement
    normalized = _SPECIAL_CHARS_PATTERN.sub("", normalized)

    # Final cleanup and validation
    normalized = _WHITESPACE_PATTERN.sub("", normalized)

    if not normalized:
        logger.warning(
            f"Company name became empty after normalization: '{original_name}'"
        )

    return normalized.strip()


def normalize_unicode(text: str) -> str:
    """Remove accents and diacritics from text while preserving base characters.

    Args:
        text: Text to normalize

    Returns:
        Text with accents/diacritics removed

    Examples:
        >>> normalize_unicode('Société')
        'Societe'
    """
    import unicodedata

    # Additional character mappings
    char_map = {
        "Æ": "AE",
        "æ": "ae",
        "Œ": "OE",
        "œ": "oe",
        "Ð": "D",
        "ð": "d",
        "Þ": "TH",
        "þ": "th",
        "ü": "u",
        "ö": "o",
        "ä": "a",
        "ß": "ss",
        "é": "e",
        "è": "e",
        "ê": "e",
        "ë": "e",
        "à": "a",
        "â": "a",
        "ç": "c",
        "î": "i",
        "ï": "i",
        "ô": "o",
        "ù": "u",
        "û": "u",
        "ÿ": "y",
    }

    # First apply custom mappings
    text = "".join(char_map.get(c, c) for c in text)

    # Then apply standard Unicode normalization
    return "".join(
        c for c in unicodedata.normalize("NFKD", text) if not unicodedata.combining(c)
    )
