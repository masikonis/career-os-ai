import pytest
from langchain_community.document_loaders import WebBaseLoader
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


@pytest.mark.smoke
def test_validate_marketplace_companies(validator):
    """Test validation of marketplace companies which should not fit ICP"""
    companies = [
        Company.from_basic_info(
            company_name="Upwork",
            website_url=HttpUrl("https://www.upwork.com"),
        ),
        Company.from_basic_info(
            company_name="Fiverr",
            website_url=HttpUrl("https://www.fiverr.com"),
        ),
    ]

    for company in companies:
        try:
            result = validator.validate(company)
            assert (
                result is False
            ), f"{company.company_name} should be identified as not fitting ICP (marketplace)"
            logger.info(
                f"Non-ICP validation test passed for {company.company_name} (marketplace)"
            )
        except Exception as e:
            logger.error(
                f"Non-ICP validation test failed for {company.company_name}: {e}"
            )
            raise


@pytest.mark.smoke
def test_validate_consulting_companies(validator):
    """Test validation of consulting companies which should not fit ICP"""
    companies = [
        Company.from_basic_info(
            company_name="ThoughtWorks",
            website_url=HttpUrl("https://www.thoughtworks.com"),
        ),
        Company.from_basic_info(
            company_name="Slalom",
            website_url=HttpUrl("https://www.slalom.com"),
        ),
    ]

    for company in companies:
        try:
            result = validator.validate(company)
            assert (
                result is False
            ), f"{company.company_name} should be identified as not fitting ICP (consulting)"
            logger.info(
                f"Non-ICP validation test passed for {company.company_name} (consulting)"
            )
        except Exception as e:
            logger.error(
                f"Non-ICP validation test failed for {company.company_name}: {e}"
            )
            raise


@pytest.mark.smoke
def test_validate_with_homepage_content(validator):
    """Test validation using homepage content for context"""
    company = Company.from_basic_info(
        company_name="TestCompany",
        website_url=HttpUrl("https://example.com"),
    )

    homepage_content = """
    Welcome to TestCompany - Your Premier Tech Education Platform
    
    Our Offerings:
    - 12-week coding bootcamp
    - Job placement guarantee
    - Industry-leading curriculum
    - Expert instructors
    - Career services support
    
    Join thousands of successful graduates working at top tech companies!
    """

    try:
        result = validator.validate(company, homepage_content)
        assert (
            result is False
        ), "TestCompany should be identified as not fitting ICP based on homepage content"
        logger.info("Homepage-based validation test passed for TestCompany")
    except Exception as e:
        logger.error(f"Homepage-based validation test failed: {e}")
        raise


@pytest.mark.smoke
def test_validate_unicorn_companies(validator):
    """Test validation of well-known unicorn companies which should not fit ICP"""
    companies = [
        Company.from_basic_info(
            company_name="Databricks",
            website_url=HttpUrl("https://www.databricks.com"),
        ),
        Company.from_basic_info(
            company_name="Snowflake",
            website_url=HttpUrl("https://www.snowflake.com"),
        ),
    ]

    for company in companies:
        try:
            result = validator.validate(company)
            assert (
                result is False
            ), f"{company.company_name} should be identified as not fitting ICP (unicorn)"
            logger.info(
                f"Non-ICP validation test passed for {company.company_name} (unicorn)"
            )
        except Exception as e:
            logger.error(
                f"Non-ICP validation test failed for {company.company_name}: {e}"
            )
            raise


@pytest.mark.smoke
def test_validate_mixed_model_companies(validator):
    """Test validation of companies with mixed business models"""
    company = Company.from_basic_info(
        company_name="TestMixedCompany",
        website_url=HttpUrl("https://example.com"),
    )

    research_data = """
    TestMixedCompany operates in two main areas:
    1. Content Platform: Creates and sells educational video content for K-12
    2. Training Division: Offers 8-week bootcamps and certification programs
    
    The company started as a content creation platform but expanded into training.
    Revenue split: 60% from bootcamps, 40% from content platform.
    """

    try:
        result = validator.validate(company, research_data)
        assert (
            result is False
        ), "Mixed-model company with majority training revenue should be UNFIT"
        logger.info("Mixed-model validation test passed")
    except Exception as e:
        logger.error(f"Mixed-model validation test failed: {e}")
        raise


@pytest.mark.smoke
def test_validate_pivoted_company(validator):
    """Test validation of companies that have pivoted their business model"""
    company = Company.from_basic_info(
        company_name="PivotedCo",
        website_url=HttpUrl("https://example.com"),
    )

    research_data = """
    PivotedCo was founded in 2020 as a coding bootcamp. In 2023, they pivoted to become
    a SaaS platform that helps companies manage their technical documentation.
    They no longer offer any educational services or bootcamps.
    The platform is used by over 100 early-stage startups.
    """

    try:
        result = validator.validate(company, research_data)
        assert result is True, "Pivoted company (now pure SaaS) should be FIT"
        logger.info("Pivoted company validation test passed")
    except Exception as e:
        logger.error(f"Pivoted company validation test failed: {e}")
        raise


@pytest.mark.smoke
def test_validate_ambiguous_stage_company(validator):
    """Test validation of companies with ambiguous funding stages"""
    company = Company.from_basic_info(
        company_name="GrowthCo",
        website_url=HttpUrl("https://example.com"),
    )

    research_data = """
    GrowthCo is a pre-Series A company:
    - $3M Seed (2021)
    - $15M Seed Extension (2023)
    - Still operating at seed stage
    - No Series A round planned yet
    - Product launched in 2022
    - 45 employees
    - $4M ARR
    - Focused on product development
    - Bootstrapped first year before seed
    """

    try:
        result = validator.validate(company, research_data)
        assert (
            result is True
        ), "Pre-Series A company should still be FIT despite large seed funding"
        logger.info("Ambiguous stage validation test passed")
    except Exception as e:
        logger.error(f"Ambiguous stage validation test failed: {e}")
        raise


@pytest.mark.smoke
def test_validate_b2b2c_education_company(validator):
    """Test validation of B2B2C educational product companies"""
    company = Company.from_basic_info(
        company_name="EduTechOS",
        website_url=HttpUrl("https://example.com"),
    )

    research_data = """
    EduTechOS provides a white-label platform for schools to create and distribute
    their own educational content. The platform includes:
    - Content authoring tools
    - Distribution infrastructure
    - Analytics dashboard
    
    They don't create or deliver educational content themselves, only provide the technology.
    """

    try:
        result = validator.validate(company, research_data)
        assert (
            result is True
        ), "B2B2C education platform should be FIT (they provide tools, not education)"
        logger.info("B2B2C education platform validation test passed")
    except Exception as e:
        logger.error(f"B2B2C education platform validation test failed: {e}")
        raise


@pytest.mark.smoke
def test_validate_with_scraping_failure(validator, monkeypatch):
    """Test validation when web scraping fails"""

    def mock_scrape(*args, **kwargs):
        raise Exception("Simulated scraping failure")

    monkeypatch.setattr(WebBaseLoader, "lazy_load", mock_scrape)

    company = Company.from_basic_info(
        company_name="ScrapeFail",
        website_url=HttpUrl("https://example.com"),
    )

    try:
        result = validator.validate(company)
        # Should fall back to LLM knowledge and make a decision
        assert isinstance(
            result, bool
        ), "Should return a boolean despite scraping failure"
        logger.info("Scraping failure fallback test passed")
    except Exception as e:
        logger.error(f"Scraping failure fallback test failed: {e}")
        raise


@pytest.mark.smoke
def test_validate_minimal_presence_company(validator):
    """Test validation of companies with minimal online presence"""
    company = Company.from_basic_info(
        company_name="StealthStartup",
        website_url=HttpUrl("https://example.com"),
    )

    research_data = """
    Limited information available about StealthStartup.
    - Founded in 2023
    - Building developer tools
    - Pre-seed stage
    - Website only contains a waitlist signup form
    """

    try:
        result = validator.validate(company, research_data)
        assert (
            result is True
        ), "Early-stage company should be FIT despite limited information"
        logger.info("Minimal presence validation test passed")
    except Exception as e:
        logger.error(f"Minimal presence validation test failed: {e}")
        raise
