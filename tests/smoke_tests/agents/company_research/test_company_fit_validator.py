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
    """Test validation of an early-stage company"""
    company = Company.from_basic_info(
        company_name="Generation Genius",
        website_url=HttpUrl("https://www.generationgenius.com"),
    )

    research_data = """
    Generation Genius is an innovative educational technology company founded in 2017. 
    The company has raised a total of $1.6 million in funding, including a $1 million 
    grant from the Howard Hughes Medical Institute. They create and distribute high-quality
    educational video content for K-12 students. The platform serves approximately 30% 
    of elementary schools in the U.S.
    """

    result = validator.validate(company, research_data)
    assert result is True, "Generation Genius should be identified as fitting ICP"


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

    result = validator.validate(company, research_data)
    assert result is False, "Metana should be identified as not fitting ICP"


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

    result = validator.validate(company, research_data)
    assert (
        result is False
    ), "Mixed-model company with majority training revenue should be UNFIT"


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

    result = validator.validate(company, research_data)
    assert (
        result is True
    ), "B2B2C education platform should be FIT (they provide tools, not education)"


@pytest.mark.smoke
def test_validate_later_stage_company(validator):
    """Test validation of a well-known later-stage company"""
    company = Company.from_basic_info(
        company_name="Stripe",
        website_url=HttpUrl("https://stripe.com"),
    )

    research_data = """
    Stripe is a well-established financial technology company founded in 2010.
    The company has raised over $2.2 billion in funding and is valued at $95 billion.
    They are one of the largest payment processors globally, serving millions of businesses.
    """

    result = validator.validate(company, research_data)
    assert result is False, "Stripe should be identified as not fitting ICP"


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

    research_data = """
    Both companies operate in the developer hiring and vetting space:
    - Contra is a platform for hiring and managing freelance developers
    - Lemon.io is a marketplace for pre-vetted developers
    Both focus on talent matching and recruitment services.
    """

    for company in companies:
        try:
            result = validator.validate(company, research_data)
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

    research_data = """
    All three companies are early-stage SaaS startups:
    - SlideSpeak: Pre-seed stage presentation software, founded 2023
    - Yooli: Seed stage customer feedback platform, founded 2022
    - Subscript: Early-stage contract management software, founded 2021
    All companies are focused on building software products, not services.
    """

    for company in companies:
        try:
            result = validator.validate(company, research_data)
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

    research_data = """
    Both are established freelance marketplaces:
    - Upwork: Public company, pure marketplace model
    - Fiverr: Public company, pure marketplace model
    Both focus on connecting freelancers with clients without their own product.
    """

    for company in companies:
        try:
            result = validator.validate(company, research_data)
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

    research_data = """
    Both are established consulting companies:
    - ThoughtWorks: Global technology consultancy
    - Slalom: Business and technology consulting firm
    Both primarily offer consulting and professional services.
    """

    for company in companies:
        try:
            result = validator.validate(company, research_data)
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

    research_data = """
    Both are well-established data companies:
    - Databricks: Valued at $43B, late-stage
    - Snowflake: Public company, mature stage
    Both are well beyond early-stage.
    """

    for company in companies:
        try:
            result = validator.validate(company, research_data)
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
def test_validate_minimal_presence_company(validator):
    """Test validation of companies with minimal online presence"""
    company = Company.from_basic_info(
        company_name="StealthStartup",
        website_url=HttpUrl("https://example.com"),
    )

    research_data = """
    Limited information available about StealthStartup:
    - Founded in 2023
    - Building software tools and infrastructure for developers
    - Pre-seed stage
    - Product in private beta
    - Website only contains a waitlist signup form
    - Not a recruitment or hiring platform
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
