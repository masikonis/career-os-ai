import pytest

from src.agents.company_research.company_quick_screener import CompanyQuickScreener
from src.logger import get_logger
from src.models.company.company import Company

logger = get_logger(__name__)


@pytest.mark.smoke
def test_company_quick_screener_basic_functionality():
    # Initialize the screener
    screener = CompanyQuickScreener()

    # Test case 1: Company with ignored domain (lemon.io)
    company_ignored = Company.from_basic_info(
        company_name="Lemon", website_url="https://lemon.io"
    )
    assert not screener.screen(
        company_ignored
    ), "Company with ignored domain should be skipped"

    # Test case 2: Company with valid domain
    company_valid = Company.from_basic_info(
        company_name="StartupXYZ", website_url="https://startupxyz.com"
    )
    assert screener.screen(company_valid), "Company with valid domain should proceed"

    # Test case 3: Company with missing website URL
    company_no_website = Company.from_basic_info(
        company_name="NoWebsiteCo", website_url=None
    )
    assert not screener.screen(
        company_no_website
    ), "Company with missing website URL should be skipped"

    # Test case 4: Company with invalid website URL (use a valid URL format but non-existent domain)
    company_invalid_url = Company.from_basic_info(
        company_name="InvalidURLCo",
        website_url="https://this-domain-does-not-exist.com",
    )
    assert not screener.screen(
        company_invalid_url
    ), "Company with invalid website URL should be skipped"

    logger.info("All basic functionality tests for CompanyQuickScreener passed")
