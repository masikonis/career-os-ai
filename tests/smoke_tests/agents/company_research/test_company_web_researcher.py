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
