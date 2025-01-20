import pytest

from src.agents.company_research.company_info_extractor import CompanyInfoExtractor
from src.logger import get_logger
from src.models.company.company_info import CompanyInfo
from src.models.company.growth_stage import CompanyGrowthStage, GrowthStage

logger = get_logger(__name__)


@pytest.mark.smoke
def test_company_info_extractor_smoke():
    extractor = CompanyInfoExtractor()

    # Sample source text containing company name and website
    source_text = """
    We are thrilled to welcome you to Acme Corp. For more details, visit our website at https://www.acmecorp.com.
    """

    try:
        result = extractor.extract_info(source_text)

        assert result is not None, "Extractor returned None."
        assert isinstance(result, dict), "Result should be a dictionary."

        # Validate against CompanyInfo model
        company_info = CompanyInfo(**result)

        assert company_info.company_name, "'company_name' is empty."
        assert company_info.website_url, "'website_url' is empty."
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
