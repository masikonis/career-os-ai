import pytest

from src.logger import get_logger
from src.services.web_search.factory import WebSearchFactory

logger = get_logger(__name__)


@pytest.mark.smoke
def test_tavily_provider_smoke():
    provider = WebSearchFactory.get_provider()
    query = "Generation Genius"

    try:
        results = provider.search(query)
        assert results is not None, "Search results are None."
        assert len(results) > 0, "Search results are empty."
        logger.info("Tavily provider search executed successfully.")
    except Exception as e:
        logger.error("Failed to execute search with Tavily provider.", exc_info=True)
        raise
