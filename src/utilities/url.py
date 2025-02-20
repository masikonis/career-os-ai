import socket
from typing import Optional, Union
from urllib.parse import urlparse, urlunparse

import requests

from src.logger import get_logger

logger = get_logger(__name__)


def resolve_redirects(url: str, timeout: float = 2.0) -> str:
    """Resolve URL redirects and return final URL."""
    try:
        if not url.startswith(("http://", "https://")):
            logger.debug(f"Skipping redirect resolution for non-HTTP(S) URL: {url}")
            return url

        logger.debug(f"Resolving redirects for: {url}")
        response = requests.get(url, allow_redirects=True, timeout=timeout)
        final_url = response.url
        if final_url != url:
            logger.debug(f"Resolved {url} → {final_url}")
        return final_url
    except requests.RequestException as e:
        logger.debug(f"Error resolving redirects for {url}: {str(e)}")
        return url


def get_domain(url: str) -> str:
    """Extract and lowercase domain from URL after resolving redirects."""
    resolved_url = resolve_redirects(url)
    parsed = urlparse(resolved_url)
    return parsed.netloc.lower()


def normalize_url(url: str, base_url: Optional[str] = None) -> str:
    """Normalize URL by combining with base URL if relative."""
    if not url:
        return ""

    if url.startswith("/") and base_url:
        return f"{base_url.rstrip('/')}{url}"

    return url


def normalize_domain(url: Optional[str]) -> str:
    """
    Normalize domain to consistent format (e.g., 'company.com').

    Examples:
        >>> normalize_domain('https://www.company.co.uk/')
        'company.co.uk'
    """
    if not url:
        return ""

    try:
        # Ensure URL has scheme for proper parsing
        url_to_parse = url if "://" in url else f"https://{url}"
        parsed = urlparse(url_to_parse)
        domain = parsed.netloc.lower()

        # If the domain is empty or doesn't contain a dot, it's invalid
        if not domain or "." not in domain:
            return ""

        # Clean domain parts
        domain = _remove_common_prefixes(domain)
        return _simplify_domain_structure(domain)
    except (ValueError, AttributeError) as e:
        logger.debug(f"Error normalizing domain {url}: {str(e)}")
        return ""


def is_domain_reachable(domain: str, timeout: float = 2.0) -> bool:
    """Check if a domain is resolvable with DNS lookup."""
    try:
        clean_domain = domain.replace("www.", "").split(":")[0]
        socket.gethostbyname(clean_domain)
        return True
    except socket.gaierror:
        return False
    except socket.timeout:
        logger.debug(f"Domain resolution timed out: {domain}")
        return False


def _remove_common_prefixes(domain: str) -> str:
    """Remove common subdomain prefixes like www, app, etc."""
    prefixes = {"www.", "app.", "web.", "portal.", "dashboard."}
    return (
        domain[len(prefix) :]
        if (prefix := next((p for p in prefixes if domain.startswith(p)), None))
        else domain
    )


def _simplify_domain_structure(domain: str) -> str:
    """Simplify domain by removing non-essential subdomains."""
    parts = domain.split(".")
    if len(parts) > 2 and parts[0] in {"app", "web", "portal", "dashboard"}:
        return ".".join(parts[1:])
    return domain
