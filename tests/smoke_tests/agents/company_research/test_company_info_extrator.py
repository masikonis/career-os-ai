import pytest

from src.agents.company_research.company_info_extractor import CompanyInfoExtractor
from src.logger import get_logger
from src.models.company.company_info import CompanyInfo

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
