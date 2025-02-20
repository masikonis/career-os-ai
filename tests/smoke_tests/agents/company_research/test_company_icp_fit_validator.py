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
    SlideSpeak business details:
    - Seed stage, $5 million funding (verified: TechCrunch, Series A round, 2023)
    - AI-powered SaaS platform for presentation creation and management
    - 100% SaaS product revenue (no services) (company claimed)
    - Team size: 2-10 employees (reported by: LinkedIn, October 2023)
    - Product launched in 2023 (company claimed)
    - Additional metrics: Over 4 million files uploaded (company claimed, October 2023)
    - Locations: San Antonio, Texas, and London (reported by: company website, October 2023)

    Yooli: Seed stage customer feedback platform, founded 2022
    Subscript: Early-stage contract management software, founded 2021
    All companies are focused on building software products, not services.
    """

    for company in companies:
        try:
            result = validator.validate(company, research_data)
            assert (
                result is True
            ), f"{company.company_name} should be identified as fitting ICP (early SaaS)"
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


@pytest.mark.smoke
def test_validate_intellisync_company(validator):
    """Test validation of Intellisync company based on provided data"""
    company = Company.from_basic_info(
        company_name="Intellisync",
        website_url=HttpUrl("https://example.com"),
    )

    research_data = """
    Intellisync business details:
    - Early stage, reported funding (company claimed)
    - AI-powered software solutions (company claimed)
    - Revenue split: Not publicly disclosed (company claimed)
    - Team size: Not publicly disclosed (company claimed)
    - Product available in the market (company claimed)
    - Additional metrics: No verified user or customer metrics available (company claimed)
    """

    try:
        result = validator.validate(company, research_data)
        assert (
            result is True
        ), "Intellisync should be identified as fitting ICP based on provided data"
        logger.info("Intellisync validation test passed")
    except Exception as e:
        logger.error(f"Intellisync validation test failed: {e}")
        raise


@pytest.mark.smoke
def test_validate_glacis_company(validator):
    """Test validation of Glacis company based on provided data"""
    company = Company.from_basic_info(
        company_name="Glacis",
        website_url=HttpUrl("https://glacis.com/"),
    )

    research_data = """
    Glacis business details:
    - Series A stage, reported funding of $10 million across seed and Series A rounds (company claimed)
    - AI-driven supply chain management SaaS platform (company claimed)
    - 100% SaaS product revenue (no services) (company claimed)
    - Team size: information not available (company claimed)
    - Product launched and in use (company claimed)
    - Additional metrics: specific user or customer numbers unverified (company claimed)
    """

    try:
        result = validator.validate(company, research_data)
        assert (
            result is True
        ), "Glacis should be identified as fitting ICP based on provided data"
        logger.info("Glacis validation test passed")
    except Exception as e:
        logger.error(f"Glacis validation test failed: {e}")
        raise


@pytest.mark.smoke
def test_validate_scope_company(validator):
    """Test validation of Scope company based on provided data"""
    company = Company.from_basic_info(
        company_name="Scope",
        website_url=HttpUrl("https://www.getscope.ai/"),
    )

    research_data = """
    Scope business details:
    - Early-stage, reported funding (company claimed) (2024)
    - AI-native SaaS inspection software platform
    - Revenue split: Not publicly disclosed
    - Team size: Not publicly disclosed
    - Product launched in 2024 (company claimed)
    - Additional metrics: Clients reduce end-to-end inspection time by an average of 2.2 times and inspectors improve productivity by 40% through system integrations (company claimed, 2024)
    """

    try:
        result = validator.validate(company, research_data)
        assert (
            result is True
        ), "Scope should be identified as fitting ICP based on provided data"
        logger.info("Scope validation test passed")
    except Exception as e:
        logger.error(f"Scope validation test failed: {e}")
        raise


@pytest.mark.smoke
def test_validate_generation_genius_post_acquisition(validator):
    """Test validation of Generation Genius company based on latest data post-acquisition"""
    company = Company.from_basic_info(
        company_name="Generation Genius",
        website_url=HttpUrl("https://www.generationgenius.com"),
    )

    research_data = """
    Generation Genius business details:
    - Seed stage, reported funding of $1.1 million through equity crowdfunding in June 2019 (reported funding, company claimed)
    - Educational subscription platform
    - Revenue split: 100% SaaS product revenue (subscription model) (company claimed)
    - Team size: 11-50 employees (company website, 2023)
    - Product launched in 2017, utilized in approximately 30% of elementary schools across the United States (company claimed, 2023)
    - Additional metrics:
      - Over 100 educational episodes produced (company claimed, 2023)
      - 92% of students find videos helpful for learning (research data, company claimed, 2023)
      - Recognized as #1 education company on the Inc. 500 list in 2022 (verified: Inc. 500)
      - Included in Time Magazine's TIME100 list of influential companies in 2023 (verified: Time Magazine)
      - Acquired by Newsela for $100 million in February 2025, primarily in cash and performance-based payments (company claimed)
    """

    try:
        result = validator.validate(company, research_data)
        assert (
            result is False
        ), "Acquired company should no longer be considered early-stage and FIT"
        logger.info(
            "Post-acquisition validation test passed - correctly identified as UNFIT"
        )
    except Exception as e:
        logger.error(f"Post-acquisition validation test failed: {e}")
        raise
