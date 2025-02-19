from unittest.mock import patch

import pytest
import requests

from src.agents.company_research.company_quick_screener import CompanyQuickScreener
from src.logger import get_logger
from src.models.company.company import Company

logger = get_logger(__name__)


@pytest.mark.smoke
def test_company_quick_screener_basic_functionality(mocker):
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
