import pytest

from src.agents.company_research.company_web_researcher import CompanyWebResearcher
from src.logger import get_logger
from src.models.company.company import Company

logger = get_logger(__name__)


@pytest.mark.smoke
def test_company_web_researcher_smoke():
    """
    Smoke test for CompanyWebResearcher.
    Ensures that the researcher can process a basic company info and return summaries.
    """
    researcher = CompanyWebResearcher()

    # Sample company information
    company = Company.from_basic_info(
        company_name="SlideSpeak",
        website_url="https://slidespeak.co",
    )

    try:
        result = researcher.research_company(company)

        # Check basic structure
        assert result is not None, "Researcher returned None"
        assert isinstance(result, dict), "Result should be a dictionary"

        # Check for required summary types
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

        # Check for key ICP information components
        icp_data = result["icp_research_data"].lower()
        logger.info("ICP Research Data: %s", result["icp_research_data"])

        required_elements = [
            "stage",
            "product",
            "revenue",
            "team",
        ]
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
    Test CompanyWebResearcher with Intellisync (Italian company) to validate geographic consistency
    and proper handling of European companies.
    """
    researcher = CompanyWebResearcher()
    company = Company.from_basic_info(
        company_name="Intellisync",
        website_url="https://www.intellisync.it/",
    )

    try:
        result = researcher.research_company(company)

        # Basic structure validation
        assert result is not None, "Researcher returned None"
        assert isinstance(result, dict), "Result should be a dictionary"

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

        # Validate geographic consistency
        icp_data = result["icp_research_data"].lower()
        assert (
            "italy" in icp_data or "italian" in icp_data
        ), "Should mention Italy/Italian location"
        assert (
            "intellisync.it" in result.get("home_page_summary", "").lower()
        ), "Should recognize intellisync.it domain"

        # Validate funding information
        funding_summary = result["funding_summary"].lower()
        if "nasdaq" in funding_summary:
            assert (
                "us" in funding_summary or "american" in funding_summary
            ), "NASDAQ funding should be marked as US"

        # Validate company-specific details
        comp_summary = result["comprehensive_summary"].lower()
        assert "intellisync" in comp_summary, "Should mention company name"
        assert any(
            word in comp_summary for word in ["technology", "tech", "software"]
        ), "Should mention tech/software focus"

        logger.info("Intellisync research test passed successfully")

    except Exception as e:
        logger.error(f"Intellisync research test failed: {e}")
        raise
