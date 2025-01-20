from typing import Optional
from urllib.parse import urlparse


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
