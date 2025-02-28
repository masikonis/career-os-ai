from unittest.mock import MagicMock, patch

import pytest

from src.services.web_search.factory import WebSearchFactory
from src.services.web_search.providers import ProviderType
from src.services.web_search.providers.perplexity import PerplexityProvider


class TestWebSearchFactory:
    """Unit tests for the WebSearchFactory class."""

    def test_get_provider_perplexity(self):
        """Test that the factory returns a PerplexityProvider when requested."""
        provider = WebSearchFactory.get_provider(ProviderType.PERPLEXITY)
        assert isinstance(provider, PerplexityProvider)

    def test_get_provider_default(self):
        """Test that the factory returns the default provider (Perplexity) when no type is specified."""
        provider = WebSearchFactory.get_provider()
        assert isinstance(provider, PerplexityProvider)

    def test_get_provider_invalid(self):
        """Test that the factory raises a ValueError for an invalid provider type."""

        # Create a mock provider type that doesn't exist in the factory
        class MockProviderType:
            name = "MOCK"

        with pytest.raises(ValueError) as excinfo:
            WebSearchFactory.get_provider(MockProviderType())

        assert "is not supported" in str(excinfo.value)

    @patch("src.services.web_search.factory.logger")
    def test_get_provider_logs_initialization(self, mock_logger):
        """Test that the factory logs the provider initialization."""
        WebSearchFactory.get_provider(ProviderType.PERPLEXITY)
        mock_logger.info.assert_called_once_with(
            f"Initializing WebSearch provider: {ProviderType.PERPLEXITY.name}"
        )
