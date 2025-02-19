import pytest

from src.logger import get_logger
from src.utilities.url import (
    get_domain,
    is_domain_reachable,
    normalize_domain,
    normalize_url,
    resolve_redirects,
)

logger = get_logger(__name__)


@pytest.mark.unit
def test_get_domain():
    # Test basic domain extraction
    assert get_domain("https://www.example.com") == "www.example.com"
    assert get_domain("http://example.com/path") == "example.com"
    assert get_domain("https://sub.example.com:8080") == "sub.example.com:8080"
    assert get_domain("ftp://user:pass@example.com") == "user:pass@example.com"

    # Test case insensitivity
    assert get_domain("https://WWW.EXAMPLE.COM") == "www.example.com"

    # Test invalid URLs
    assert get_domain("not-a-url") == ""
    assert get_domain("") == ""

    # New test cases for redirect handling
    assert get_domain("https://contra.com/home") == "contra.com"
    assert get_domain("http://invalid-url") == "invalid-url"


@pytest.mark.unit
def test_normalize_url():
    # Test relative URLs with base URL
    assert normalize_url("/path", "https://example.com") == "https://example.com/path"
    assert normalize_url("/path", "https://example.com/") == "https://example.com/path"

    # Test absolute URLs
    assert normalize_url("https://example.com/path") == "https://example.com/path"
    assert normalize_url("http://example.com") == "http://example.com"

    # Test empty URLs
    assert normalize_url("") == ""
    assert normalize_url("/path", None) == "/path"


@pytest.mark.unit
def test_normalize_domain():
    # Test common prefixes
    assert normalize_domain("https://www.example.com") == "example.com"
    assert normalize_domain("http://app.example.com") == "example.com"
    assert normalize_domain("https://portal.example.co.uk") == "example.co.uk"

    # Test without scheme
    assert normalize_domain("example.com") == "example.com"
    assert normalize_domain("www.example.com") == "example.com"

    # Test invalid domains
    assert normalize_domain("not-a-domain") == ""
    assert normalize_domain("") == ""


@pytest.mark.unit
def test_is_domain_reachable():
    # Test reachable domains (assuming these domains exist)
    assert is_domain_reachable("google.com") is True
    assert is_domain_reachable("example.com") is True

    # Test unreachable domains
    assert is_domain_reachable("this-domain-does-not-exist.com") is False
    assert is_domain_reachable("invalid") is False

    # Test with timeout
    assert is_domain_reachable("google.com", timeout=0.1) is True


@pytest.mark.unit
def test_remove_common_prefixes():
    from src.utilities.url import _remove_common_prefixes

    # Test common prefixes
    assert _remove_common_prefixes("www.example.com") == "example.com"
    assert _remove_common_prefixes("app.example.com") == "example.com"
    assert _remove_common_prefixes("web.example.com") == "example.com"

    # Test without prefix
    assert _remove_common_prefixes("example.com") == "example.com"


@pytest.mark.unit
def test_simplify_domain_structure():
    from src.utilities.url import _simplify_domain_structure

    # Test non-essential subdomains
    assert _simplify_domain_structure("app.example.com") == "example.com"
    assert _simplify_domain_structure("web.example.co.uk") == "example.co.uk"

    # Test essential subdomains
    assert _simplify_domain_structure("sub.example.com") == "sub.example.com"
    assert _simplify_domain_structure("example.com") == "example.com"


@pytest.mark.integration
def test_get_domain_with_real_redirects():
    """Integration test with real URLs (might be flaky)"""
    assert get_domain("http://bit.ly/3kLhMdk") == "contra.com"
    assert get_domain("https://t.co/example") != "t.co"  # Most t.co links redirect
    assert get_domain("https://non-existent-domain.fake") == "non-existent-domain.fake"
