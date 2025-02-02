import pytest

from src.logger import get_logger
from src.utilities.company import (
    LEGAL_SUFFIXES,
    normalize_company_name,
    normalize_unicode,
)

logger = get_logger(__name__)


@pytest.mark.parametrize(
    "input_name,expected_output",
    [
        # Basic cases
        ("PayPal, Inc.", "paypal"),
        ("AT&T Corporation", "att"),
        ("Siemens AG", "siemens"),
        ("Société Générale S.A.", "societegenerale"),
        # Edge cases
        ("", ""),
        ("   ", ""),
        (None, ""),
        # International cases
        ("Müller GmbH", "muller"),
        ("Österreichische Post AG", "osterreichischepost"),
        ("株式会社サンプル", ""),
        # Special characters
        ("Company & Co.", "company"),
        ("Example-Company", "examplecompany"),
        ("Test_Company", "testcompany"),
        # Multiple suffixes
        ("Example Corp. Ltd.", "example"),
        # Numbers
        ("3M Company", "3m"),
        ("Company 123", "company123"),
    ],
)
def test_normalize_company_name(input_name, expected_output):
    """Test company name normalization with various inputs."""
    result = normalize_company_name(input_name)
    logger.debug(f"Normalized '{input_name}' to '{result}'")
    assert result == expected_output


@pytest.mark.parametrize(
    "suffix",
    LEGAL_SUFFIXES,
)
def test_legal_suffix_removal(suffix):
    """Test that all legal suffixes are properly removed."""
    test_name = f"TestCompany{suffix}"
    result = normalize_company_name(test_name)
    assert result == "testcompany"


@pytest.mark.parametrize(
    "input_text,expected_output",
    [
        ("Société", "Societe"),
        ("naïve", "naive"),
        ("Müller", "Muller"),
        ("Æther", "AEther"),
        ("café", "cafe"),
        ("", ""),
        ("normal text", "normal text"),
    ],
)
def test_normalize_unicode(input_text, expected_output):
    """Test Unicode normalization with various inputs."""
    result = normalize_unicode(input_text)
    logger.debug(f"Normalized Unicode '{input_text}' to '{result}'")
    assert result == expected_output


def test_normalize_company_name_logging(caplog):
    """Test that appropriate logging occurs during normalization."""
    test_name = "Test Company, Inc."
    with caplog.at_level("DEBUG"):
        _ = normalize_company_name(test_name)

    # Verify debug logs
    assert "Received empty name" not in caplog.text
    assert any("Removed legal suffix" in message for message in caplog.messages)


def test_empty_input_logging(caplog):
    """Test logging behavior with empty input."""
    with caplog.at_level("DEBUG"):
        _ = normalize_company_name("")
    assert any("Received empty name" in message for message in caplog.messages)


def test_invalid_input_logging(caplog):
    """Test logging behavior with invalid input."""
    _ = normalize_company_name(123)  # type: ignore
    assert "Non-string input to normalize_company_name" in caplog.text
