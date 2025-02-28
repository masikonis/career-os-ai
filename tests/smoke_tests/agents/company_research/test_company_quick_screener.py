import pytest

from src.agents.company_research.company_quick_screener import CompanyQuickScreener
from src.logger import get_logger
from src.models.company.company import Company

logger = get_logger(__name__)


@pytest.mark.smoke
def test_stripe_screening():
    """
    Smoke test for the CompanyQuickScreener using Stripe.
    This test verifies that the screener correctly identifies companies that don't fit our ICP.
    Stripe is a large, established company, so we expect it to be rejected.
    """
    logger.info("Starting smoke test for Stripe screening (expected to fail)")

    # Initialize the screener
    screener = CompanyQuickScreener()

    # Create the Stripe company
    company = Company.from_basic_info(
        company_name="Stripe", website_url="https://stripe.com"
    )

    logger.info(
        f"Created company object for {company.company_name} with URL {company.website_url}"
    )

    # Run the screening process
    result = screener.screen(company)

    # Log the result
    if result:
        logger.info(
            f"UNEXPECTED: {company.company_name} passed screening despite being a large, established company"
        )
    else:
        logger.info(
            f"EXPECTED: {company.company_name} was correctly rejected as it doesn't fit our ICP (large, established company)"
        )

    # We expect Stripe to be rejected since it's a large, established company
    assert (
        not result
    ), f"{company.company_name} should be rejected as it doesn't fit our ICP"

    logger.info("Completed smoke test for Stripe screening")


@pytest.mark.smoke
def test_generation_genius_screening():
    """
    Smoke test for the CompanyQuickScreener using Generation Genius.
    This test verifies that the screener correctly identifies companies that don't fit our ICP.
    Generation Genius was recently acquired, so we expect it to be rejected.
    """
    logger.info(
        "Starting smoke test for Generation Genius screening (expected to fail)"
    )

    # Initialize the screener
    screener = CompanyQuickScreener()

    # Create the Generation Genius company
    company = Company.from_basic_info(
        company_name="Generation Genius", website_url="https://www.generationgenius.com"
    )

    logger.info(
        f"Created company object for {company.company_name} with URL {company.website_url}"
    )

    # Run the screening process
    result = screener.screen(company)

    # Log the result
    if result:
        logger.info(
            f"UNEXPECTED: {company.company_name} passed screening despite being acquired"
        )
    else:
        logger.info(
            f"EXPECTED: {company.company_name} was correctly rejected as it doesn't fit our ICP (recently acquired)"
        )

    # We expect Generation Genius to be rejected since it was recently acquired
    assert (
        not result
    ), f"{company.company_name} should be rejected as it doesn't fit our ICP"

    logger.info("Completed smoke test for Generation Genius screening")


@pytest.mark.smoke
def test_known_ignored_domain_screening():
    """
    Smoke test for the CompanyQuickScreener using a known ignored domain (lemon.io).
    This test verifies that the screener correctly identifies and rejects companies with ignored domains.
    """
    logger.info("Starting smoke test for known ignored domain screening")

    # Initialize the screener
    screener = CompanyQuickScreener()

    # Create a company with a known ignored domain
    company = Company.from_basic_info(
        company_name="Lemon", website_url="https://lemon.io"
    )

    logger.info(
        f"Created company object for {company.company_name} with URL {company.website_url}"
    )

    # Run the screening process
    result = screener.screen(company)

    # Log the result
    if result:
        logger.info(
            f"UNEXPECTED: {company.company_name} passed screening despite having an ignored domain"
        )
    else:
        logger.info(
            f"EXPECTED: {company.company_name} was correctly rejected due to ignored domain"
        )

    # We expect companies with ignored domains to be rejected
    assert (
        not result
    ), f"{company.company_name} should be rejected due to ignored domain"

    logger.info("Completed smoke test for known ignored domain screening")
