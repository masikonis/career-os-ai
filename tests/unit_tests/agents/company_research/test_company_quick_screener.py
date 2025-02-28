from unittest.mock import MagicMock, patch

import pytest
import requests

from src.agents.company_research.company_quick_screener import CompanyQuickScreener
from src.logger import get_logger
from src.models.company.company import Company

logger = get_logger(__name__)


def test_company_quick_screener_basic_functionality(mocker):
    """Test the basic technical validation functionality of the CompanyQuickScreener."""
    # Mock web search and ICP validator to focus on technical validation
    mocker.patch("src.services.web_search.factory.WebSearchFactory.get_provider")
    mocker.patch(
        "src.agents.company_research.company_icp_fit_validator.CompanyICPFitValidator"
    )

    # Mock the _perform_basic_search_validation and _perform_advanced_search_validation methods
    # to always return True so we can focus on testing the technical validation
    mocker.patch.object(
        CompanyQuickScreener, "_perform_basic_search_validation", return_value=True
    )
    mocker.patch.object(
        CompanyQuickScreener, "_perform_advanced_search_validation", return_value=True
    )

    # Initialize the screener
    screener = CompanyQuickScreener()

    # Mock URL resolution for all test cases
    url_resolution_mock = mocker.patch.object(
        CompanyQuickScreener,
        "resolve_final_url",
        side_effect=lambda url: url,  # Default behavior
    )

    # Test case 1: Company with ignored domain (lemon.io)
    company_ignored = Company.from_basic_info(
        company_name="Lemon", website_url="https://lemon.io"
    )
    assert not screener.screen(
        company_ignored
    ), "Company with ignored domain should be skipped"

    # Test case 2: Valid domain (mock resolution success)
    url_resolution_mock.return_value = "https://startupxyz.com"
    company_valid = Company.from_basic_info(
        company_name="StartupXYZ", website_url="https://startupxyz.com"
    )
    assert screener.screen(company_valid), "Valid domain should proceed"

    # Test case 3: Missing website URL
    company_no_website = Company.from_basic_info(
        company_name="NoWebsiteCo", website_url=None
    )
    assert not screener.screen(
        company_no_website
    ), "Company with missing website URL should be skipped"

    # Test case 4: Unreachable website (simulate failed resolution)
    url_resolution_mock.return_value = None
    company_invalid_url = Company.from_basic_info(
        company_name="InvalidURLCo",
        website_url="https://bad-url.com",
    )
    assert not screener.screen(company_invalid_url), "Unresolvable URL should skip"

    # Test case 5: URL shortener to ignored domain
    url_resolution_mock.return_value = "https://contra.com"
    company_shortened_url = Company.from_basic_info(
        company_name="ContraShortened", website_url="http://bit.ly/3kLhMdk"
    )
    assert not screener.screen(
        company_shortened_url
    ), "Resolved ignored domain should skip"

    logger.info("All basic functionality tests passed")


def test_ignores_contra_via_shortener(mocker):
    """Test that the screener correctly resolves URL shorteners and ignores blacklisted domains."""
    # Mock web search and ICP validator
    mocker.patch("src.services.web_search.factory.WebSearchFactory.get_provider")
    mocker.patch(
        "src.agents.company_research.company_icp_fit_validator.CompanyICPFitValidator"
    )

    screener = CompanyQuickScreener()

    # Mock the URL resolution
    mock_response = mocker.MagicMock()
    mock_response.url = "https://contra.com"
    mocker.patch.object(requests, "head", return_value=mock_response)

    company = Company.from_basic_info(
        company_name="TestCo", website_url="http://bit.ly/3kLhMdk"
    )

    assert not screener.screen(company)
    logger.info("Verified URL shortener resolution and contra.com blocking")


def test_web_search_and_icp_validation(mocker):
    """Test the web search and ICP validation functionality."""
    # Mock the technical validation to always pass
    mocker.patch.object(
        CompanyQuickScreener, "_perform_technical_validation", return_value=True
    )

    # Mock web search provider
    mock_web_search = MagicMock()
    mocker.patch(
        "src.services.web_search.factory.WebSearchFactory.get_provider",
        return_value=mock_web_search,
    )

    # Mock ICP validator
    mock_icp_validator = MagicMock()
    mocker.patch(
        "src.agents.company_research.company_icp_fit_validator.CompanyICPFitValidator",
        return_value=mock_icp_validator,
    )

    # Create test company
    company = Company.from_basic_info(
        company_name="TechStartup", website_url="https://techstartup.com"
    )

    # Initialize screener
    screener = CompanyQuickScreener()

    # Test case 1: Company passes basic search but fails ICP validation
    mock_web_search.basic_search.return_value = [
        {"content": "TechStartup is a Series B company", "source": "example.com"}
    ]
    mock_icp_validator.validate.return_value = False

    assert not screener.screen(
        company
    ), "Company should be rejected after basic search ICP validation"

    # Test case 2: Company passes basic search and ICP validation but fails advanced search ICP validation
    mock_web_search.basic_search.return_value = [
        {"content": "TechStartup is a seed-stage company", "source": "example.com"}
    ]
    mock_web_search.advanced_search.return_value = [
        {
            "content": "TechStartup offers developer recruitment services",
            "source": "example.com",
        }
    ]

    # First validation passes, second fails
    mock_icp_validator.validate.side_effect = [True, False]

    assert not screener.screen(
        company
    ), "Company should be rejected after advanced search ICP validation"

    # Test case 3: Company passes all validations
    mock_web_search.basic_search.return_value = [
        {"content": "TechStartup is a seed-stage company", "source": "example.com"}
    ]
    mock_web_search.advanced_search.return_value = [
        {
            "content": "TechStartup offers a SaaS platform for businesses",
            "source": "example.com",
        }
    ]

    # Both validations pass
    mock_icp_validator.validate.side_effect = [True, True]

    assert screener.screen(
        company
    ), "Company should proceed after passing all validations"

    # Test case 4: No search results found, should proceed
    mock_web_search.basic_search.return_value = []
    mock_web_search.advanced_search.return_value = []

    assert screener.screen(company), "Company should proceed if no search results found"

    logger.info("All web search and ICP validation tests passed")


def test_error_handling(mocker):
    """Test error handling in the screening process."""
    # Mock the technical validation to always pass
    mocker.patch.object(
        CompanyQuickScreener, "_perform_technical_validation", return_value=True
    )

    # Create test company
    company = Company.from_basic_info(
        company_name="ErrorCo", website_url="https://errorco.com"
    )

    # Initialize screener with mocked dependencies
    screener = CompanyQuickScreener()

    # Test case 1: Error in basic search
    # Mock web search provider to raise an exception for basic search
    mock_web_search = MagicMock()
    mock_web_search.basic_search.side_effect = Exception("API error")
    mock_web_search.advanced_search.return_value = [
        {"content": "ErrorCo is a SaaS platform", "source": "example.com"}
    ]

    # Mock ICP validator to return True
    mock_icp_validator = MagicMock()
    mock_icp_validator.validate.return_value = True

    # Apply mocks
    screener.web_search = mock_web_search
    screener.icp_validator = mock_icp_validator

    assert screener.screen(company), "Should handle errors in basic search and proceed"

    # Test case 2: Error in advanced search
    mock_web_search.advanced_search.side_effect = Exception("API error")
    screener.web_search = mock_web_search

    assert screener.screen(
        company
    ), "Should handle errors in advanced search and proceed"

    # Test case 3: Error in ICP validation
    mock_web_search = MagicMock()
    mock_web_search.basic_search.return_value = [
        {"content": "Some content", "source": "example.com"}
    ]
    mock_web_search.advanced_search.return_value = [
        {"content": "More content", "source": "example.com"}
    ]

    mock_icp_validator = MagicMock()
    mock_icp_validator.validate.side_effect = Exception("LLM error")

    screener.web_search = mock_web_search
    screener.icp_validator = mock_icp_validator

    assert screener.screen(
        company
    ), "Should handle errors in ICP validation and proceed"

    logger.info("All error handling tests passed")
