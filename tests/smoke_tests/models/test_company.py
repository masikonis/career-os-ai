import pytest
from pydantic import HttpUrl

from src.logger import get_logger
from src.models.company.company import Company

logger = get_logger(__name__)


def test_company_id_generation():
    """Test company ID generation with various inputs."""

    # Test with website URL
    company = Company(
        company_name="PayPal, Inc.", website_url=HttpUrl("https://www.paypal.com")
    )
    logger.info(f"Generated ID for PayPal: {company.company_id}")
    assert company.company_id.startswith("company_pay_")
    assert len(company.company_id) == 20  # company_XXX_8chars

    # Test without website URL
    company_no_web = Company(company_name="Local Business LLC")
    logger.info(
        f"Generated ID for company without website: {company_no_web.company_id}"
    )
    assert company_no_web.company_id.startswith("company_nwb_")
    assert len(company_no_web.company_id) == 20

    # Test consistency
    company1 = Company(
        company_name="PayPal Inc", website_url=HttpUrl("https://www.paypal.com")
    )
    company2 = Company(
        company_name="PAYPAL INC.", website_url=HttpUrl("http://paypal.com")
    )
    logger.info(f"Consistency test IDs:")
    logger.info(f"Company1 ID: {company1.company_id}")
    logger.info(f"Company2 ID: {company2.company_id}")
    assert (
        company1.company_id == company2.company_id
    ), "Same company should have same ID"


def test_company_id_edge_cases():
    """Test company ID generation with edge cases."""

    # Test with special characters
    company = Company(
        company_name="AT&T Corporation", website_url=HttpUrl("https://www.att.com")
    )
    logger.info(f"Generated ID for AT&T: {company.company_id}")
    assert company.company_id.startswith("company_att_")

    # Test with international characters
    company = Company(
        company_name="Société Générale",
        website_url=HttpUrl("https://www.societegenerale.fr"),
    )
    logger.info(f"Generated ID for Société Générale: {company.company_id}")
    assert company.company_id.startswith("company_soc_")

    # Test with subdomain
    company = Company(
        company_name="Company Name", website_url=HttpUrl("https://app.company.com")
    )
    logger.info(f"Generated ID for subdomain test: {company.company_id}")
    assert company.company_id.startswith("company_com_")
