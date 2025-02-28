import json

import pytest

from src.logger import get_logger
from src.services.web_search.providers.perplexity import PerplexityProvider

logger = get_logger(__name__)


@pytest.mark.smoke
def test_perplexity_provider_basic_search_smoke():
    """Smoke test for the Perplexity provider basic search."""
    try:
        provider = PerplexityProvider()
        query = "What is Python programming language?"
        logger.info(f"Executing basic search with query: '{query}'")

        results = provider.basic_search(query)

        # Log the results for inspection
        logger.info(f"Basic search returned {len(results)} results")
        for i, result in enumerate(results):
            logger.info(f"Result {i+1}:")
            logger.info(
                f"  Content: {result.get('content', '')[:100]}..."
            )  # First 100 chars
            logger.info(f"  Source: {result.get('source', '')}")

        # Log the full results as JSON for detailed inspection
        logger.info(f"Full results: {json.dumps(results, indent=2)}")

        assert isinstance(results, list)
        if results:
            assert isinstance(results[0], dict)
            assert "content" in results[0]
            assert "source" in results[0]

        logger.info("Perplexity provider basic search executed successfully.")
    except Exception as e:
        logger.error(
            "Failed to execute basic search with Perplexity provider.", exc_info=True
        )
        pytest.fail(f"Perplexity provider basic search test failed: {e}")


@pytest.mark.smoke
def test_perplexity_provider_advanced_search_smoke():
    """Smoke test for the Perplexity provider advanced search."""
    try:
        provider = PerplexityProvider()
        query = "What are the latest developments in AI?"
        logger.info(f"Executing advanced search with query: '{query}'")

        results = provider.advanced_search(query)

        # Log the results for inspection
        logger.info(f"Advanced search returned {len(results)} results")
        for i, result in enumerate(results):
            logger.info(f"Result {i+1}:")
            logger.info(
                f"  Content: {result.get('content', '')[:100]}..."
            )  # First 100 chars
            logger.info(f"  Source: {result.get('source', '')}")

        # Log the full results as JSON for detailed inspection
        logger.info(f"Full results: {json.dumps(results, indent=2)}")

        assert isinstance(results, list)
        if results:
            assert isinstance(results[0], dict)
            assert "content" in results[0]
            assert "source" in results[0]

        logger.info("Perplexity provider advanced search executed successfully.")
    except Exception as e:
        logger.error(
            "Failed to execute advanced search with Perplexity provider.", exc_info=True
        )
        pytest.fail(f"Perplexity provider advanced search test failed: {e}")


@pytest.mark.smoke
def test_perplexity_provider_research_search_smoke():
    """Smoke test for the Perplexity provider research search."""
    try:
        provider = PerplexityProvider()
        query = "Explain the impact of quantum computing on cryptography"
        logger.info(f"Executing research search with query: '{query}'")

        result = provider.research_search(query)

        # Log the result for inspection
        logger.info("Research search returned result:")
        logger.info(
            f"  Content: {result.get('content', '')[:100]}..."
        )  # First 100 chars
        logger.info(f"  Sources: {result.get('sources', [])}")

        # Log the full result as JSON for detailed inspection
        logger.info(f"Full result: {json.dumps(result, indent=2)}")

        assert isinstance(result, dict)
        assert "content" in result
        assert "sources" in result
        assert isinstance(result["sources"], list)

        logger.info("Perplexity provider research search executed successfully.")
    except Exception as e:
        logger.error(
            "Failed to execute research search with Perplexity provider.", exc_info=True
        )
        pytest.fail(f"Perplexity provider research search test failed: {e}")
