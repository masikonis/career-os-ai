import pytest
from pydantic import HttpUrl

from src.agents.company_research.company_icp_fit_validator import CompanyICPFitValidator
from src.logger import get_logger
from src.models.company.company import Company

logger = get_logger(__name__)


@pytest.fixture
def validator():
    return CompanyICPFitValidator()


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
    their own educational content. Company details:
    - Pre-seed stage, founded 2023
    - Raised $1.5M initial funding
    - Pure technology platform play
    - Content authoring tools
    - Distribution infrastructure
    - Analytics dashboard
    - No content creation or delivery services
    - 100% revenue from platform subscriptions
    - They don't create or deliver educational content themselves, only provide the technology
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
    Key details:
    - Creates and produces high-quality science video content
    - Digital platform for K-12 science education
    - Content creation and distribution platform
    - $1.6M in total funding ($1M grant + crowdfunding)
    - Serves 30% of US elementary schools
    - Pure content product company, not a service provider
    - Early-stage with seed funding
    - Focus on content creation and platform development
    """

    try:
        result = validator.validate(company, research_data)
        assert (
            result is True
        ), "Generation Genius should be identified as fitting ICP based on research data"
        logger.info("Research-based validation test passed")
    except Exception as e:
        logger.error(f"Research-based validation test failed: {str(e)}")
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


@pytest.mark.smoke
def test_validate_pivot_company(validator):
    """Test validation of companies that recently pivoted from services to product"""
    company = Company.from_basic_info(
        company_name="PivotCo",
        website_url=HttpUrl("https://example.com"),
    )

    research_data = """
    PivotCo history:
    - Founded 2022 as consulting firm
    - Pivoted to SaaS product in 2023
    - Currently 90% revenue from product
    - Pre-seed stage
    - No longer accepting consulting clients
    - Focused on product development
    - Building developer productivity tools
    """

    try:
        result = validator.validate(company, research_data)
        assert (
            result is True
        ), "Recently pivoted company should be FIT if now product-focused"
        logger.info("Pivot company validation test passed")
    except Exception as e:
        logger.error(f"Pivot company validation test failed: {e}")
        raise


@pytest.mark.smoke
def test_validate_hardware_software_company(validator):
    """Test validation of companies with both hardware and software products"""
    company = Company.from_basic_info(
        company_name="HardSoft",
        website_url=HttpUrl("https://example.com"),
    )

    research_data = """
    HardSoft product mix:
    - IoT hardware devices
    - SaaS platform for device management
    - Pre-seed stage
    - Revenue: 70% software, 30% hardware
    - Software can be used independently of hardware
    - Platform includes analytics, device management, and automation tools
    """

    try:
        result = validator.validate(company, research_data)
        assert (
            result is True
        ), "Software-first hardware company should be FIT if primarily selling software"
        logger.info("Hardware-software company validation test passed")
    except Exception as e:
        logger.error(f"Hardware-software company validation test failed: {e}")
        raise


@pytest.mark.smoke
def test_validate_ai_startups(validator):
    """Test validation of different types of AI startups"""
    companies = [
        Company.from_basic_info(
            company_name="AIWorkflowPro",
            website_url=HttpUrl("https://example.com"),
        ),
        Company.from_basic_info(
            company_name="LegalAI",
            website_url=HttpUrl("https://example.com"),
        ),
        Company.from_basic_info(
            company_name="AIConsulting",
            website_url=HttpUrl("https://example.com"),
        ),
    ]

    research_data = """
    Information about AI companies:
    
    AIWorkflowPro:
    - Pre-seed startup building AI workflow automation platform
    - SaaS product that helps companies build and deploy AI workflows
    - Founded 2023, raised $2M seed
    - Pure product company, no consulting services
    
    LegalAI:
    - Seed-stage vertical AI company for legal industry
    - AI-powered contract analysis and management platform
    - Founded 2022, raised $3.5M seed
    - 100% product revenue from SaaS subscriptions
    
    AIConsulting:
    - AI implementation consulting firm
    - Helps enterprises deploy AI solutions
    - Founded 2021, bootstrapped
    - 90% revenue from consulting, 10% from tools
    """

    # Test AIWorkflowPro (should be FIT - horizontal AI platform)
    try:
        result = validator.validate(companies[0], research_data)
        assert (
            result is True
        ), "AI workflow platform should be FIT (early-stage product company)"
        logger.info("AI workflow platform validation test passed")
    except Exception as e:
        logger.error(f"AI workflow platform validation test failed: {e}")
        raise

    # Test LegalAI (should be FIT - vertical AI SaaS)
    try:
        result = validator.validate(companies[1], research_data)
        assert (
            result is True
        ), "Vertical AI SaaS should be FIT (early-stage product company)"
        logger.info("Vertical AI SaaS validation test passed")
    except Exception as e:
        logger.error(f"Vertical AI SaaS validation test failed: {e}")
        raise

    # Test AIConsulting (should be UNFIT - consulting focused)
    try:
        result = validator.validate(companies[2], research_data)
        assert (
            result is False
        ), "AI consulting company should be UNFIT (primarily services)"
        logger.info("AI consulting company validation test passed")
    except Exception as e:
        logger.error(f"AI consulting company validation test failed: {e}")
        raise


@pytest.mark.smoke
def test_validate_international_companies(validator):
    """Test validation of international companies in different markets"""
    companies = [
        Company.from_basic_info(
            company_name="EuroSaaS",
            website_url=HttpUrl("https://example.com"),
        ),
        Company.from_basic_info(
            company_name="LatAmTech",
            website_url=HttpUrl("https://example.com"),
        ),
    ]

    research_data = """
    Information about international companies:
    
    EuroSaaS:
    - German B2B SaaS startup
    - Pre-seed stage, €1.5M raised
    - Building collaboration tools for enterprises
    - Expanding from DACH to EU market
    - 100% product revenue
    
    LatAmTech:
    - Brazilian fintech platform
    - Series A, $12M raised
    - Already dominant in Brazil
    - 500+ enterprise customers
    - Expanding across Latin America
    - Mature operations and sales team
    """

    # Test EuroSaaS (should be FIT - early stage, product focus)
    try:
        result = validator.validate(companies[0], research_data)
        assert result is True, "Early-stage international SaaS should be FIT"
        logger.info("International early-stage validation test passed")
    except Exception as e:
        logger.error(f"International early-stage validation test failed: {e}")
        raise

    # Test LatAmTech (should be UNFIT - too mature/late stage)
    try:
        result = validator.validate(companies[1], research_data)
        assert result is False, "Later-stage international company should be UNFIT"
        logger.info("International later-stage validation test passed")
    except Exception as e:
        logger.error(f"International later-stage validation test failed: {e}")
        raise


@pytest.mark.smoke
def test_validate_open_source_companies(validator):
    """Test validation of open source companies with commercial products"""
    company = Company.from_basic_info(
        company_name="OpenCorpOS",
        website_url=HttpUrl("https://example.com"),
    )

    research_data = """
    OpenCorpOS business model:
    - Open source core product (50K+ GitHub stars)
    - Commercial cloud offering launched 2023
    - Pre-seed stage, $2M raised
    - 80% revenue from cloud product
    - 20% from enterprise support
    - Growing commercial customer base
    - Strong open source community
    """

    try:
        result = validator.validate(company, research_data)
        assert (
            result is True
        ), "Open source company with commercial product should be FIT"
        logger.info("Open source company validation test passed")
    except Exception as e:
        logger.error(f"Open source company validation test failed: {e}")
        raise


@pytest.mark.smoke
def test_validate_api_first_companies(validator):
    """Test validation of API-first businesses"""
    company = Company.from_basic_info(
        company_name="APIFirst",
        website_url=HttpUrl("https://example.com"),
    )

    research_data = """
    APIFirst platform details:
    - Developer-focused API platform
    - Pre-seed stage, founded 2023
    - Core product is API for data processing
    - Self-serve API marketplace
    - No consulting or implementation services
    - Pure product/platform play
    """

    try:
        result = validator.validate(company, research_data)
        assert result is True, "API-first product company should be FIT"
        logger.info("API-first company validation test passed")
    except Exception as e:
        logger.error(f"API-first company validation test failed: {e}")
        raise


@pytest.mark.smoke
def test_validate_marketplace_saas_hybrid(validator):
    """Test validation of marketplace + SaaS hybrid models"""
    companies = [
        Company.from_basic_info(
            company_name="HybridMarket",
            website_url=HttpUrl("https://example.com"),
        ),
        Company.from_basic_info(
            company_name="SaaSMarket",
            website_url=HttpUrl("https://example.com"),
        ),
    ]

    research_data = """
    Information about hybrid companies:
    
    HybridMarket:
    - Marketplace for digital assets
    - 70% revenue from marketplace fees
    - 30% from SaaS tools for sellers
    - Seed stage, $4M raised
    - Primarily a marketplace business
    
    SaaSMarket:
    - B2B software distribution platform
    - 80% revenue from SaaS platform
    - 20% from marketplace commissions
    - Pre-seed stage
    - Core product is the platform
    """

    # Test HybridMarket (should be UNFIT - primarily marketplace)
    try:
        result = validator.validate(companies[0], research_data)
        assert result is False, "Primarily marketplace hybrid should be UNFIT"
        logger.info("Marketplace-heavy hybrid validation test passed")
    except Exception as e:
        logger.error(f"Marketplace-heavy hybrid validation test failed: {e}")
        raise

    # Test SaaSMarket (should be FIT - primarily SaaS)
    try:
        result = validator.validate(companies[1], research_data)
        assert result is True, "Primarily SaaS hybrid should be FIT"
        logger.info("SaaS-heavy hybrid validation test passed")
    except Exception as e:
        logger.error(f"SaaS-heavy hybrid validation test failed: {e}")
        raise
