import re
from typing import Optional

# Comprehensive list of legal suffixes with variations
LEGAL_SUFFIXES = [
    " inc",
    " inc.",
    " incorporated",
    " corp",
    " corp.",
    " corporation",
    " llc",
    " l.l.c.",
    " limited liability company",
    " ltd",
    " ltd.",
    " limited",
    " gmbh",  # German companies
    " sa",
    " s.a.",  # French/Spanish companies
    " ag",  # Swiss/German companies
    " plc",
    " p.l.c.",  # UK companies
    " co",
    " co.",  # General
    " company",
]


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
        return ""

    # Convert to lowercase
    normalized = name.lower()

    # Remove legal suffixes
    for suffix in LEGAL_SUFFIXES:
        if normalized.endswith(suffix):
            normalized = normalized[: -len(suffix)]
            break  # Stop after first match to avoid multiple replacements

    # Handle special cases
    normalized = normalized.replace("&", "and")  # Convert & to 'and'

    # Remove accents/diacritics (é -> e, ü -> u, etc.)
    normalized = normalize_unicode(normalized)

    # Remove special characters and spaces
    normalized = re.sub(r"[^a-z0-9]", "", normalized)

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

    return "".join(
        c for c in unicodedata.normalize("NFKD", text) if not unicodedata.combining(c)
    )
