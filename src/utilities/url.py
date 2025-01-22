from typing import Optional
from urllib.parse import urlparse, urlunparse


def get_domain(url: str) -> str:
    """Extract domain from URL."""
    return urlparse(url).netloc.lower()


def normalize_url(url: str, base_url: Optional[str] = None) -> str:
    """Normalize URL by adding base URL if needed."""
    if not url:
        return ""
    if url.startswith("/") and base_url:
        return f"{base_url.rstrip('/')}{url}"
    return url


def normalize_domain(url: Optional[str]) -> str:
    """Normalize URL to consistent format for ID generation.

    Args:
        url: URL string to normalize

    Returns:
        Normalized domain (e.g., 'company.com')

    Examples:
        >>> normalize_domain('https://www.company.co.uk/')
        'company.co.uk'
        >>> normalize_domain('http://app.company.com')
        'company.com'
    """
    if not url:
        return ""

    try:
        # Parse URL
        parsed = urlparse(url if "://" in url else f"https://{url}")

        # Get domain without www and common subdomains
        domain = parsed.netloc.lower()
        if domain.startswith("www."):
            domain = domain[4:]

        # Handle common subdomains
        parts = domain.split(".")
        if len(parts) > 2 and parts[0] in ["app", "web", "portal", "dashboard"]:
            domain = ".".join(parts[1:])

        return domain
    except Exception:
        return ""
