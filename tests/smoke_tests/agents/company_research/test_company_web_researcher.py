import pytest

from src.agents.company_research.company_web_researcher import CompanyWebResearcher
from src.logger import get_logger
from src.models.company.company import Company

logger = get_logger(__name__)


@pytest.mark.smoke
def test_company_web_researcher_smoke():
    """
    Smoke test for CompanyWebResearcher.
    Ensures that the researcher can process a basic company info and return a summary.
    """
    researcher = CompanyWebResearcher()

    # Sample company information
    company = Company.from_basic_info(
        company_name="Generation Genius",
        website_url="https://www.generationgenius.com/",
    )

    try:
        result = researcher.research_company(company)

        assert result is not None, "Researcher returned None."
        assert isinstance(result, str), "Result should be a string."
        assert len(result.strip()) > 0, "Result should not be empty."

        logger.info("CompanyWebResearcher smoke test passed.")

    except Exception as e:
        logger.error(f"CompanyWebResearcher smoke test failed: {e}")
        raise
