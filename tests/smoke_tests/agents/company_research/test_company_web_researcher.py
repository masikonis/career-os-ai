import pytest

from src.agents.company_research.company_web_researcher import CompanyWebResearcher
from src.logger import get_logger
from src.models.company.company_info import CompanyInfo

logger = get_logger(__name__)


@pytest.mark.smoke
def test_company_web_researcher_smoke():
    """
    Smoke test for CompanyWebResearcher.
    Ensures that the researcher can process a basic company info and return a summary.
    """
    researcher = CompanyWebResearcher()

    # Sample company information
    company_info = CompanyInfo(
        company_name="Single Grain",
        website_url="https://www.singlegrain.com/",
    )

    try:
        result = researcher.research_company(company_info)

        assert result is not None, "Researcher returned None."
        assert isinstance(result, dict), "Result should be a dictionary."
        assert "final_summary" in result, "Result should contain 'final_summary'."
        assert (
            "combined_summaries" in result
        ), "Result should contain 'combined_summaries'."

        assert isinstance(
            result["final_summary"], str
        ), "'final_summary' should be a string."
        assert isinstance(
            result["combined_summaries"], list
        ), "'combined_summaries' should be a list."
        assert (
            len(result["final_summary"].strip()) > 0
        ), "'final_summary' should not be empty."
        assert (
            len(result["combined_summaries"]) > 0
        ), "'combined_summaries' should not be empty."

        logger.info("CompanyWebResearcher smoke test passed.")

    except Exception as e:
        logger.error(f"CompanyWebResearcher smoke test failed: {e}")
        raise
