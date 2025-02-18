import pytest
from pydantic import HttpUrl

from src.agents.company_research.company_web_researcher import CompanyWebResearcher
from src.logger import get_logger
from src.models.company.company import Company

logger = get_logger(__name__)


@pytest.mark.smoke
def test_company_web_researcher_generation_genius():
    """
    Smoke test for CompanyWebResearcher.
    Ensures that the researcher can process a basic company info and return summaries.
    """
    researcher = CompanyWebResearcher()

    # Use from_basic_info to create Company instance
    company = Company.from_basic_info(
        company_name="Generation Genius",
        website_url=HttpUrl("https://www.generationgenius.com/"),
    )

    try:
        result = researcher.research_company(company)

        # Update assertion to check for source_summaries
        expected_summaries = [
            "comprehensive_summary",
            "company_summary",
            "funding_summary",
            "team_summary",
            "icp_research_data",
        ]

        # Update ICP data validation
        icp_data = result["icp_research_data"].lower()
        required_elements = ["stage", "platform", "revenue", "team size"]

        # Check basic structure
        assert result is not None, "Researcher returned None"
        assert isinstance(result, dict), "Result should be a dictionary"

        # Check for required summary types
        for summary_type in expected_summaries:
            assert summary_type in result, f"Missing {summary_type} in result"
            assert isinstance(
                result[summary_type], str
            ), f"{summary_type} should be a string"
            assert (
                len(result[summary_type].strip()) > 0
            ), f"{summary_type} should not be empty"

        # Check for key ICP information components
        logger.info("ICP Research Data: %s", result["icp_research_data"])
        logger.info("Comprehensive Summary: %s", result["comprehensive_summary"])

        for element in required_elements:
            assert (
                element in icp_data
            ), f"ICP research data should contain information about {element}"

        logger.info("CompanyWebResearcher smoke test passed")

    except Exception as e:
        logger.error(f"CompanyWebResearcher smoke test failed: {e}")
        raise


@pytest.mark.smoke
def test_company_web_researcher_intellisync():
    """
    Test CompanyWebResearcher with Intellisync (Italian company) to validate handling of European companies.
    """
    researcher = CompanyWebResearcher()

    # Use from_basic_info to create Company instance
    company = Company.from_basic_info(
        company_name="Intellisync", website_url=HttpUrl("https://www.intellisync.it/")
    )

    try:
        result = researcher.research_company(company)

        # Update funding validation
        funding_summary = result["funding_summary"].lower()
        if "european" in funding_summary:
            assert "eu" in funding_summary, "Should specify EU funding sources"

        # Validate summary types
        expected_summaries = [
            "comprehensive_summary",
            "company_summary",
            "funding_summary",
            "team_summary",
            "icp_research_data",
        ]

        for summary_type in expected_summaries:
            assert summary_type in result, f"Missing {summary_type} in result"
            assert isinstance(
                result[summary_type], str
            ), f"{summary_type} should be a string"
            assert (
                len(result[summary_type].strip()) > 0
            ), f"{summary_type} should not be empty"

        # Validate company-specific details
        comp_summary = result["comprehensive_summary"].lower()
        logger.info("Comprehensive Summary: %s", result["comprehensive_summary"])
        assert "intellisync" in comp_summary, "Should mention company name"
        assert any(
            word in comp_summary for word in ["technology", "tech", "software"]
        ), "Should mention tech/software focus"

        logger.info("Intellisync research test passed successfully")

    except Exception as e:
        logger.error(f"Intellisync research test failed: {e}")
        raise


@pytest.mark.smoke
def test_company_web_researcher_single_grain():
    """
    Test CompanyWebResearcher with Single Grain to validate handling of marketing agencies.
    """
    researcher = CompanyWebResearcher()

    # Use from_basic_info to create Company instance
    company = Company.from_basic_info(
        company_name="Single Grain",
        website_url=HttpUrl("https://www.singlegrain.com/"),
    )

    try:
        result = researcher.research_company(company)

        # Validate summary types
        expected_summaries = [
            "comprehensive_summary",
            "company_summary",
            "funding_summary",
            "team_summary",
            "icp_research_data",
        ]

        for summary_type in expected_summaries:
            assert summary_type in result, f"Missing {summary_type} in result"
            assert isinstance(
                result[summary_type], str
            ), f"{summary_type} should be a string"
            assert (
                len(result[summary_type].strip()) > 0
            ), f"{summary_type} should not be empty"

        # Validate company-specific details
        comp_summary = result["comprehensive_summary"].lower()
        logger.info("Comprehensive Summary: %s", result["comprehensive_summary"])
        assert "single grain" in comp_summary, "Should mention company name"
        assert any(
            word in comp_summary for word in ["marketing", "agency", "digital"]
        ), "Should mention marketing/digital focus"

        # Validate ICP data
        icp_data = result["icp_research_data"].lower()
        required_elements = ["stage", "revenue", "team size"]
        optional_elements = ["marketing", "agency", "services"]

        # Check required elements
        for element in required_elements:
            assert (
                element in icp_data
            ), f"ICP research data should contain information about {element}"

        # Check if any optional elements are present
        assert any(
            element in icp_data for element in optional_elements
        ), f"ICP research data should contain at least one of: {', '.join(optional_elements)}"

        logger.info("Single Grain research test passed successfully")

    except Exception as e:
        logger.error(f"Single Grain research test failed: {e}")
        raise


@pytest.mark.smoke
def test_company_web_researcher_glacis():
    """
    Test CompanyWebResearcher with Glacis to validate handling of supply chain companies.
    """
    researcher = CompanyWebResearcher()

    # Use from_basic_info to create Company instance
    company = Company.from_basic_info(
        company_name="Glacis", website_url=HttpUrl("https://glacis.com/")
    )

    try:
        result = researcher.research_company(company)

        # Validate summary types
        expected_summaries = [
            "comprehensive_summary",
            "company_summary",
            "funding_summary",
            "team_summary",
            "icp_research_data",
        ]

        for summary_type in expected_summaries:
            assert summary_type in result, f"Missing {summary_type} in result"
            assert isinstance(
                result[summary_type], str
            ), f"{summary_type} should be a string"
            assert (
                len(result[summary_type].strip()) > 0
            ), f"{summary_type} should not be empty"

        # Validate company-specific details
        comp_summary = result["comprehensive_summary"].lower()
        logger.info("Comprehensive Summary: %s", result["comprehensive_summary"])
        assert "glacis" in comp_summary, "Should mention company name"
        assert any(
            word in comp_summary for word in ["supply chain", "logistics", "automation"]
        ), "Should mention supply chain/logistics focus"

        logger.info("Glacis research test passed successfully")

    except Exception as e:
        logger.error(f"Glacis research test failed: {e}")
        raise


@pytest.mark.smoke
def test_company_web_researcher_scope():
    """
    Test CompanyWebResearcher with Scope to validate handling of inspection software companies.
    """
    researcher = CompanyWebResearcher()

    # Use from_basic_info to create Company instance
    company = Company.from_basic_info(
        company_name="Scope", website_url=HttpUrl("https://www.getscope.ai/")
    )

    try:
        result = researcher.research_company(company)

        # Validate summary types
        expected_summaries = [
            "comprehensive_summary",
            "company_summary",
            "funding_summary",
            "team_summary",
            "icp_research_data",
        ]

        for summary_type in expected_summaries:
            assert summary_type in result, f"Missing {summary_type} in result"
            assert isinstance(
                result[summary_type], str
            ), f"{summary_type} should be a string"
            assert (
                len(result[summary_type].strip()) > 0
            ), f"{summary_type} should not be empty"

        # Validate company-specific details
        comp_summary = result["comprehensive_summary"].lower()
        logger.info("Comprehensive Summary: %s", result["comprehensive_summary"])
        assert "scope" in comp_summary, "Should mention company name"
        assert any(
            word in comp_summary
            for word in ["inspection", "software", "ai", "efficiency"]
        ), "Should mention inspection software and AI focus"

        logger.info("Scope research test passed successfully")

    except Exception as e:
        logger.error(f"Scope research test failed: {e}")
        raise
