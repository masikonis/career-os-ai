import pytest
from pydantic import HttpUrl

from src.agents.company_research.company_early_stage_validator import (
    CompanyEarlyStageValidator,
)
from src.logger import get_logger
from src.models.company.company import Company

logger = get_logger(__name__)


@pytest.fixture
def validator():
    return CompanyEarlyStageValidator()


@pytest.mark.smoke
def test_validate_early_stage_company(validator):
    """Test validation of an early-stage company using LLM knowledge"""
    company = Company.from_basic_info(
        company_name="Generation Genius",
        website_url=HttpUrl("https://www.generationgenius.com"),
    )

    try:
        result = validator.validate(company)
        assert result is True, "Generation Genius should be identified as early-stage"
        logger.info("Early-stage validation test passed for Generation Genius")
    except Exception as e:
        logger.error(f"Early-stage validation test failed: {e}")
        raise


@pytest.mark.smoke
def test_validate_later_stage_company(validator):
    """Test validation of a well-known later-stage company using LLM knowledge"""
    company = Company.from_basic_info(
        company_name="Stripe", website_url=HttpUrl("https://stripe.com")
    )

    try:
        result = validator.validate(company)
        assert result is False, "Stripe should be identified as later-stage"
        logger.info("Later-stage validation test passed for Stripe")
    except Exception as e:
        logger.error(f"Later-stage validation test failed: {e}")
        raise


@pytest.mark.smoke
def test_validate_with_research_data(validator):
    """Test validation using research data"""
    company = Company.from_basic_info(
        company_name="Generation Genius",
        website_url=HttpUrl("https://www.generationgenius.com"),
    )

    research_data = """
    Generation Genius is an innovative educational technology company founded in 2017. 
    The company has raised a total of $1.6 million in funding, including a $1 million 
    grant from the Howard Hughes Medical Institute and $1.07 million through crowdfunding. 
    The platform serves approximately 30% of elementary schools in the U.S.
    """

    try:
        result = validator.validate(company, research_data)
        assert (
            result is True
        ), "Generation Genius should be identified as early-stage based on research data"
        logger.info("Research-based validation test passed for Generation Genius")
    except Exception as e:
        logger.error(f"Research-based validation test failed: {e}")
        raise
