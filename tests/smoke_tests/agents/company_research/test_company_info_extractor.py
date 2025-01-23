import pytest

from src.agents.company_research.company_info_extractor import CompanyInfoExtractor
from src.logger import get_logger
from src.models.company.company import Company
from src.models.company.company_description import CompanyDescription
from src.models.company.company_founders import CompanyFounders, Founder
from src.models.company.company_funding import CompanyFunding
from src.models.company.company_growth_stage import CompanyGrowthStage, GrowthStage
from src.models.company.company_industry import CompanyIndustry
from src.models.company.company_location import CompanyLocation

logger = get_logger(__name__)


@pytest.mark.smoke
def test_company_info_extractor_smoke():
    extractor = CompanyInfoExtractor()

    # Sample source text containing company name and website
    source_text = """
    Generation Genius is an innovative educational technology company. For more information, visit https://www.generationgenius.com.
    """

    try:
        result = extractor.extract_info(source_text)

        assert result is not None, "Extractor returned None."
        assert isinstance(result, dict), "Result should be a dictionary."

        # Validate against CompanyInfo model
        company = Company(**result)

        assert company.company_name, "'company_name' is empty."
        assert company.website_url, "'website_url' is empty."
        logger.info("CompanyInfoExtractor smoke test passed.")
    except Exception as e:
        logger.error(f"CompanyInfoExtractor smoke test failed: {e}")
        raise


@pytest.mark.smoke
def test_extract_growth_stage_smoke():
    """Test the extraction of company growth stage from research output."""
    extractor = CompanyInfoExtractor()

    # Sample research output (now just a string, as returned by CompanyWebResearcher)
    comprehensive_summary = """
    Generation Genius is an innovative educational technology company founded in 2017 by scientist Jeff Vinokur and TV executive Eric Rollman, based in Los Angeles, California. The platform specializes in creating engaging and interactive video lessons in science and math for K-8 students, aiming to make these subjects enjoyable and accessible. With a library of animated and live-action videos, hands-on activities, and comprehensive lesson plans aligned with the Next Generation Science Standards (NGSS), Generation Genius serves approximately 30% of elementary schools in the U.S. The company has received notable recognition, including being named one of TIME's 100 Most Influential Companies in 2023 and ranking on the Inc. 5000 list of fastest-growing companies. Generation Genius has raised a total of $1.6 million in funding, including a $1 million grant from the Howard Hughes Medical Institute and $1.07 million through crowdfunding. The team, led by Vinokur, is committed to transforming science education, and customer feedback highlights the platform's effectiveness in enhancing student engagement and learning outcomes, despite some concerns regarding subscription costs and the need for parental involvement.
    """

    try:
        # Pass the string directly as research_output
        result = extractor.extract_growth_stage(
            {"comprehensive_summary": comprehensive_summary}
        )

        assert result is not None, "Growth stage extraction returned None"
        assert isinstance(
            result, CompanyGrowthStage
        ), "Result should be a CompanyGrowthStage object"

        # Validate the growth stage is one of the valid enum values
        assert isinstance(
            result.growth_stage, GrowthStage
        ), "Growth stage should be a valid GrowthStage enum"

        # Validate confidence score
        assert (
            0.0 <= result.confidence <= 1.0
        ), "Confidence should be between 0.0 and 1.0"

        # Validate reasoning
        assert result.reasoning, "Reasoning should not be empty"
        assert isinstance(result.reasoning, str), "Reasoning should be a string"

        logger.info(
            f"Extracted growth stage: {result.growth_stage} with confidence {result.confidence}"
        )
        logger.info(f"Reasoning: {result.reasoning}")

    except Exception as e:
        logger.error(f"Growth stage extraction test failed: {e}")
        raise


@pytest.mark.smoke
def test_extract_founding_year_smoke():
    """Test the extraction of company founding year from research output."""
    extractor = CompanyInfoExtractor()

    # Sample research output
    comprehensive_summary = """
    Generation Genius is an innovative educational technology company founded in 2017 by scientist Jeff Vinokur and TV executive Eric Rollman, based in Los Angeles, California...
    """

    try:
        result = extractor.extract_founding_year(
            {"comprehensive_summary": comprehensive_summary}
        )

        assert result is not None, "Founding year extraction returned None"
        assert isinstance(result, int), "Result should be an integer"
        assert 1800 <= result <= 2024, "Founding year should be within reasonable range"

        logger.info(f"Extracted founding year: {result}")
        assert result == 2017, "Expected founding year is 2017"

    except Exception as e:
        logger.error(f"Founding year extraction test failed: {e}")
        raise


@pytest.mark.smoke
def test_extract_founders_smoke():
    """Test the extraction of company founders from research output."""
    extractor = CompanyInfoExtractor()

    # Sample research output
    comprehensive_summary = """
    Generation Genius is an innovative educational technology company founded in 2017 by scientist Jeff Vinokur and TV executive Eric Rollman, based in Los Angeles, California...
    """

    try:
        result = extractor.extract_founders(
            {"comprehensive_summary": comprehensive_summary}
        )

        assert result is not None, "Founders extraction returned None"
        assert isinstance(
            result, CompanyFounders
        ), "Result should be a CompanyFounders object"
        assert len(result.founders) > 0, "Should have found at least one founder"

        # Check specific founders
        founder_names = {founder.name for founder in result.founders}
        expected_names = {"Jeff Vinokur", "Eric Rollman"}
        assert (
            founder_names == expected_names
        ), f"Expected founders {expected_names}, got {founder_names}"

        # Check titles if available (case-insensitive comparison)
        for founder in result.founders:
            if founder.name == "Jeff Vinokur":
                assert (
                    founder.title.lower() == "scientist"
                ), "Jeff Vinokur should be identified as a scientist"
            elif founder.name == "Eric Rollman":
                assert (
                    founder.title.lower() == "tv executive"
                ), "Eric Rollman should be identified as a TV executive"

        # Update the logging to show more details
        founders_info = [f"{f.name} ({f.title})" for f in result.founders]
        logger.info(f"Extracted founders: {founders_info}")

    except Exception as e:
        logger.error(f"Founders extraction test failed: {e}")
        raise


@pytest.mark.smoke
def test_extract_location_smoke():
    """Test the extraction of company location from research output."""
    extractor = CompanyInfoExtractor()

    # Sample research output
    comprehensive_summary = """
    Generation Genius is an innovative educational technology company founded in 2017 by scientist Jeff Vinokur and TV executive Eric Rollman, based in Los Angeles, California. The platform specializes in creating engaging and interactive video lessons...
    """

    try:
        result = extractor.extract_location(
            {"comprehensive_summary": comprehensive_summary}
        )

        assert result is not None, "Location extraction returned None"
        assert isinstance(
            result, CompanyLocation
        ), "Result should be a CompanyLocation object"

        # Check specific location details
        assert result.city == "Los Angeles", "City should be Los Angeles"
        assert result.state == "California", "State should be California"
        assert result.country == "United States", "Country should be United States"

        # Log the extracted location
        logger.info(
            f"Extracted location: {result.city}, {result.state}, {result.country}"
        )

    except Exception as e:
        logger.error(f"Location extraction test failed: {e}")
        raise


@pytest.mark.smoke
def test_extract_funding_smoke():
    """Test the extraction of company funding information from research output."""
    extractor = CompanyInfoExtractor()

    # Sample research output
    comprehensive_summary = """
    Generation Genius is an innovative educational technology company founded in 2017 by scientist Jeff Vinokur and TV executive Eric Rollman, based in Los Angeles, California. The platform specializes in creating engaging and interactive video lessons in science and math for K-8 students, aiming to make these subjects enjoyable and accessible. With a library of animated and live-action videos, hands-on activities, and comprehensive lesson plans aligned with the Next Generation Science Standards (NGSS), Generation Genius serves approximately 30% of elementary schools in the U.S. The company has received notable recognition, including being named one of TIME's 100 Most Influential Companies in 2023 and ranking on the Inc. 5000 list of fastest-growing companies. Generation Genius has raised a total of $1.6 million in funding, including a $1 million grant from the Howard Hughes Medical Institute and $1.07 million through crowdfunding. The team, led by Vinokur, is committed to transforming science education, and customer feedback highlights the platform's effectiveness in enhancing student engagement and learning outcomes, despite some concerns regarding subscription costs and the need for parental involvement.
    """

    try:
        result = extractor.extract_funding(
            {"comprehensive_summary": comprehensive_summary}
        )

        assert result is not None, "Funding extraction returned None"
        assert isinstance(
            result, CompanyFunding
        ), "Result should be a CompanyFunding object"

        # Check total funding
        assert (
            result.total_amount == 1.6
        ), f"Total funding should be 1.6M, got {result.total_amount}M"
        assert result.currency == "USD", "Currency should be USD"

        # Check funding sources
        assert len(result.funding_sources) == 2, "Should have found 2 funding sources"

        # Create a map of sources to amounts for easier checking
        funding_map = {
            source.source: source.amount for source in result.funding_sources
        }

        assert "Howard Hughes Medical Institute" in funding_map, "Missing HHMI funding"
        assert (
            funding_map["Howard Hughes Medical Institute"] == 1.0
        ), "HHMI amount should be 1.0M"

        # Check crowdfunding
        crowdfunding = next(
            (s for s in result.funding_sources if s.type.lower() == "crowdfunding"),
            None,
        )
        assert crowdfunding is not None, "Missing crowdfunding source"
        assert crowdfunding.amount == 1.07, "Crowdfunding amount should be 1.07M"

        # Log the details
        logger.info(f"Total funding: ${result.total_amount}M {result.currency}")
        for source in result.funding_sources:
            logger.info(
                f"Source: {source.source}, Amount: ${source.amount}M, Type: {source.type}"
            )

    except Exception as e:
        logger.error(f"Funding extraction test failed: {e}")
        raise


@pytest.mark.smoke
def test_extract_industry_smoke():
    """Test the extraction of company industry information from research output."""
    extractor = CompanyInfoExtractor()

    # Sample research output
    comprehensive_summary = """
    Generation Genius is an innovative educational technology company founded in 2017 by scientist Jeff Vinokur and TV executive Eric Rollman, based in Los Angeles, California. The platform specializes in creating engaging and interactive video lessons in science and math for K-8 students, aiming to make these subjects enjoyable and accessible...
    """

    try:
        result = extractor.extract_industry(
            {"comprehensive_summary": comprehensive_summary}
        )

        assert result is not None, "Industry extraction returned None"
        assert isinstance(
            result, CompanyIndustry
        ), "Result should be a CompanyIndustry object"

        # Check primary industry
        assert (
            result.primary_industry.lower() == "edtech"
        ), "Primary industry should be EdTech"

        # Check verticals - allow either K-8 or K-12 Education
        verticals_lower = [v.lower() for v in result.verticals]
        assert any(
            v in verticals_lower for v in ["k-8 education", "k-12 education"]
        ), "Should include K-8 or K-12 Education vertical"
        assert (
            "science education" in verticals_lower
        ), "Should include Science Education vertical"

        # Log the details
        logger.info(f"Primary Industry: {result.primary_industry}")
        logger.info(f"Verticals: {', '.join(result.verticals)}")

    except Exception as e:
        logger.error(f"Industry extraction test failed: {e}")
        raise


@pytest.mark.smoke
def test_create_description_smoke():
    """Test the creation of professional company summary."""
    extractor = CompanyInfoExtractor()

    comprehensive_summary = """
    Generation Genius is an innovative educational technology company founded in 2017 by scientist Jeff Vinokur and TV executive Eric Rollman, based in Los Angeles, California. The platform specializes in creating engaging and interactive video lessons in science and math for K-8 students, aiming to make these subjects enjoyable and accessible. With a library of animated and live-action videos, hands-on activities, and comprehensive lesson plans aligned with the Next Generation Science Standards (NGSS), Generation Genius serves approximately 30% of elementary schools in the U.S. The company has received notable recognition, including being named one of TIME's 100 Most Influential Companies in 2023 and ranking on the Inc. 5000 list of fastest-growing companies. Generation Genius has raised a total of $1.6 million in funding, including a $1 million grant from the Howard Hughes Medical Institute and $1.07 million through crowdfunding. The team, led by Vinokur, is committed to transforming science education, and customer feedback highlights the platform's effectiveness in enhancing student engagement and learning outcomes, despite some concerns regarding subscription costs and the need for parental involvement.
    """

    try:
        result = extractor.create_description(
            {"comprehensive_summary": comprehensive_summary}
        )

        assert result is not None, "Description creation returned None"
        assert isinstance(
            result, CompanyDescription
        ), "Result should be a CompanyDescription object"

        # Just check that we got a reasonable length description
        assert len(result.description) > 50, "Description too short"
        assert len(result.description) < 1000, "Description too long"

        # Log the description
        logger.info("Generated Summary:")
        logger.info(result.description)

    except Exception as e:
        logger.error(f"Description creation test failed: {e}")
        raise


@pytest.mark.smoke
def test_find_careers_url_smoke():
    extractor = CompanyInfoExtractor()

    # Test with a known website
    website_url = "https://www.generationgenius.com"

    try:
        careers_url = extractor.find_careers_url(website_url)

        # We don't assert the exact URL since it might change
        # Instead, we verify the method works without errors
        logger.info(f"Found careers URL: {careers_url}")

        # Test with invalid URL
        invalid_result = extractor.find_careers_url(None)
        assert invalid_result is None, "Should return None for invalid URL"

        logger.info("find_careers_url smoke test passed.")
    except Exception as e:
        logger.error(f"find_careers_url smoke test failed: {e}")
        raise


@pytest.mark.smoke
def test_extract_all_info_smoke():
    """Test the comprehensive extraction of all company information."""
    extractor = CompanyInfoExtractor()

    # Using the full comprehensive summary as other tests
    comprehensive_summary = """
    Generation Genius is an innovative educational technology company founded in 2017 by scientist Jeff Vinokur and TV executive Eric Rollman, based in Los Angeles, California. The platform specializes in creating engaging and interactive video lessons in science and math for K-8 students, aiming to make these subjects enjoyable and accessible. With a library of animated and live-action videos, hands-on activities, and comprehensive lesson plans aligned with the Next Generation Science Standards (NGSS), Generation Genius serves approximately 30% of elementary schools in the U.S. The company has received notable recognition, including being named one of TIME's 100 Most Influential Companies in 2023 and ranking on the Inc. 5000 list of fastest-growing companies. Generation Genius has raised a total of $1.6 million in funding, including a $1 million grant from the Howard Hughes Medical Institute and $1.07 million through crowdfunding. The team, led by Vinokur, is committed to transforming science education, and customer feedback highlights the platform's effectiveness in enhancing student engagement and learning outcomes, despite some concerns regarding subscription costs and the need for parental involvement.
    """

    website_url = "https://www.generationgenius.com"

    try:
        result = extractor.extract_all_info(
            {"comprehensive_summary": comprehensive_summary}, company_url=website_url
        )

        # Check that all expected keys are present
        expected_keys = {
            "careers_url",  # Move to top to match implementation order
            "founding_year",
            "founders",
            "location",
            "industry",
            "growth_stage",
            "funding",
            "description",
        }

        # Validate URL-based fields first
        if result["careers_url"]:
            assert isinstance(
                result["careers_url"], str
            ), "Careers URL should be a string"
            assert result["careers_url"].startswith(
                "http"
            ), "Careers URL should be a valid URL"

        # Then validate LLM-based fields
        assert result["founding_year"] == 2017, "Incorrect founding year"
        assert isinstance(
            result["founders"], CompanyFounders
        ), "Founders should be CompanyFounders object"
        assert isinstance(
            result["location"], CompanyLocation
        ), "Location should be CompanyLocation object"
        assert isinstance(
            result["industry"], CompanyIndustry
        ), "Industry should be CompanyIndustry object"
        assert isinstance(
            result["growth_stage"], CompanyGrowthStage
        ), "Growth stage should be CompanyGrowthStage object"
        assert isinstance(
            result["funding"], CompanyFunding
        ), "Funding should be CompanyFunding object"
        assert isinstance(
            result["description"], CompanyDescription
        ), "Description should be CompanyDescription object"

        # Log successful extractions
        logger.info("Successfully extracted all company information:")
        for key, value in result.items():
            if value is not None:
                logger.info(f"{key}: {value}")

    except Exception as e:
        logger.error(f"Comprehensive extraction test failed: {e}")
        raise
