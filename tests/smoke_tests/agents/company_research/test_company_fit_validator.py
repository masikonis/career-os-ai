import pytest
from pydantic import HttpUrl

from src.agents.company_research.company_fit_validator import CompanyFitValidator
from src.logger import get_logger
from src.models.company.company import Company

logger = get_logger(__name__)


@pytest.fixture
def validator():
    return CompanyFitValidator()


@pytest.mark.smoke
def test_validate_early_stage_company(validator):
    """Test validation of an early-stage company using LLM knowledge"""
    company = Company.from_basic_info(
        company_name="Generation Genius",
        website_url=HttpUrl("https://www.generationgenius.com"),
    )

    try:
        result = validator.validate(company)
        assert result is True, "Generation Genius should be identified as fitting ICP"
        logger.info("ICP validation test passed for Generation Genius")
    except Exception as e:
        logger.error(f"ICP validation test failed: {e}")
        raise


@pytest.mark.smoke
def test_validate_later_stage_company(validator):
    """Test validation of a well-known later-stage company using LLM knowledge"""
    company = Company.from_basic_info(
        company_name="Stripe", website_url=HttpUrl("https://stripe.com")
    )

    try:
        result = validator.validate(company)
        assert result is False, "Stripe should be identified as not fitting ICP"
        logger.info("Non-ICP validation test passed for Stripe")
    except Exception as e:
        logger.error(f"Non-ICP validation test failed: {e}")
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
        ), "Generation Genius should be identified as fitting ICP based on research data"
        logger.info("Research-based validation test passed for Generation Genius")
    except Exception as e:
        logger.error(f"Research-based validation test failed: {e}")
        raise


@pytest.mark.smoke
def test_validate_dev_platform_companies(validator):
    """Test validation of developer hiring/vetting platforms which should not fit ICP"""
    companies = [
        Company.from_basic_info(
            company_name="Contra",
            website_url=HttpUrl("https://contra.com"),
        ),
        Company.from_basic_info(
            company_name="Lemon.io",
            website_url=HttpUrl("https://lemon.io"),
        ),
    ]

    for company in companies:
        try:
            result = validator.validate(company)
            assert (
                result is False
            ), f"{company.company_name} should be identified as not fitting ICP (dev platform)"
            logger.info(
                f"Non-ICP validation test passed for {company.company_name} (dev platform)"
            )
        except Exception as e:
            logger.error(
                f"Non-ICP validation test failed for {company.company_name}: {e}"
            )
            raise


@pytest.mark.smoke
def test_validate_education_platform(validator):
    """Test validation of education platforms which should not fit ICP"""
    company = Company.from_basic_info(
        company_name="Metana",
        website_url=HttpUrl("https://metana.io"),
    )

    research_data = """
    Metana is a tech education platform offering bootcamps in Web3, Solidity, and other tech skills.
    The company provides job guarantees and has trained thousands of students. They offer various
    bootcamps including Web3 Solidity Bootcamp, Full Stack Software Engineering Bootcamp, and more.
    """

    try:
        result = validator.validate(company, research_data)
        assert (
            result is False
        ), "Metana should be identified as not fitting ICP (education platform)"
        logger.info("Non-ICP validation test passed for Metana (education platform)")
    except Exception as e:
        logger.error(f"Non-ICP validation test failed for Metana: {e}")
        raise


@pytest.mark.smoke
def test_validate_early_saas_companies(validator):
    """Test validation of early-stage SaaS companies that should fit ICP"""
    companies = [
        Company.from_basic_info(
            company_name="SlideSpeak",
            website_url=HttpUrl("https://slidespeak.co"),
        ),
        Company.from_basic_info(
            company_name="Yooli",
            website_url=HttpUrl("https://www.yooli.co"),
        ),
        Company.from_basic_info(
            company_name="Subscript",
            website_url=HttpUrl("https://www.subscript.com"),
        ),
    ]

    for company in companies:
        try:
            result = validator.validate(company)
            assert (
                result is True
            ), f"{company.company_name} should be identified as fitting ICP (early SaaS)"
            logger.info(
                f"ICP validation test passed for {company.company_name} (early SaaS)"
            )
        except Exception as e:
            logger.error(f"ICP validation test failed for {company.company_name}: {e}")
            raise
