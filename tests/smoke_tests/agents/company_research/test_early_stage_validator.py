import pytest
from pydantic import HttpUrl

from src.agents.company_research.early_stage_validator import EarlyStageValidator
from src.models.company.company_info import CompanyInfo


@pytest.fixture
def validator():
    return EarlyStageValidator()


def test_validate_early_stage_company(validator):
    """Test validation of an early-stage company"""
    company_info = CompanyInfo(
        company_name="Generation Genius",
        website_url=HttpUrl("https://www.generationgenius.com"),
    )

    result = validator.validate(company_info)
    assert result is True


def test_validate_later_stage_company(validator):
    """Test validation of a well-known later-stage company"""
    company_info = CompanyInfo(
        company_name="Stripe", website_url=HttpUrl("https://stripe.com")
    )

    result = validator.validate(company_info)
    assert result is False
