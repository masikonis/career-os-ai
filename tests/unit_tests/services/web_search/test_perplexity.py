from unittest.mock import MagicMock, call, patch

import pytest

from src.services.web_search.providers.perplexity import PerplexityProvider


class TestPerplexityProvider:
    """Unit tests for the PerplexityProvider class."""

    @pytest.fixture
    def mock_config(self):
        """Fixture to mock the config with a valid API key."""
        with patch(
            "src.services.web_search.providers.perplexity.config",
            {"PERPLEXITY_API_KEY": "test-api-key"},
        ):
            yield

    @pytest.fixture
    def mock_openai(self):
        """Fixture to mock the OpenAI class."""
        with patch(
            "src.services.web_search.providers.perplexity.OpenAI"
        ) as mock_openai_cls:
            mock_client = MagicMock()
            mock_openai_cls.return_value = mock_client
            yield mock_openai_cls

    @pytest.fixture
    def mock_cache(self):
        """Fixture to mock the cache manager."""
        with patch(
            "src.services.web_search.providers.perplexity.CacheManager"
        ) as mock_cache_cls:
            mock_cache_instance = MagicMock()
            mock_cache_cls.return_value = mock_cache_instance
            yield mock_cache_instance

    @pytest.fixture
    def provider(self, mock_config, mock_openai, mock_cache):
        """Fixture to create a PerplexityProvider instance with mocked dependencies."""
        return PerplexityProvider()

    def test_init_with_valid_api_key(self, mock_config, mock_openai):
        """Test initialization with a valid API key."""
        provider = PerplexityProvider()
        assert provider.api_key == "test-api-key"
        assert provider.base_url == "https://api.perplexity.ai"
        mock_openai.assert_called_once_with(
            api_key="test-api-key", base_url="https://api.perplexity.ai"
        )

    def test_init_with_missing_api_key(self):
        """Test initialization with a missing API key raises ValueError."""
        with patch(
            "src.services.web_search.providers.perplexity.config",
            {"PERPLEXITY_API_KEY": None},
        ):
            with pytest.raises(ValueError) as excinfo:
                PerplexityProvider()
            assert "API key is required" in str(excinfo.value)

    def test_basic_search_cached(self, provider, mock_cache):
        """Test basic_search returns cached results if available."""
        mock_cache.get.return_value = [
            {"content": "cached content", "source": "cached source"}
        ]

        results = provider.basic_search("test query")

        mock_cache.get.assert_called_once_with("perplexity_basic_test query")
        assert results == [{"content": "cached content", "source": "cached source"}]

    def test_basic_search_api_call(self, provider, mock_cache, mock_openai):
        """Test basic_search makes API call if no cached results."""
        # Set up cache miss
        mock_cache.get.return_value = None

        # Set up mock API response
        mock_client = mock_openai.return_value
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content="test content", citations=[]))
        ]
        mock_response.usage = MagicMock(
            prompt_tokens=10, completion_tokens=20, total_tokens=30
        )
        mock_client.chat.completions.create.return_value = mock_response

        results = provider.basic_search("test query")

        # Verify cache check
        mock_cache.get.assert_called_once_with("perplexity_basic_test query")

        # Verify API call
        mock_client.chat.completions.create.assert_called_once_with(
            model="sonar",
            messages=[{"role": "user", "content": "test query"}],
            temperature=0.0,
        )

        # Verify results
        assert results == [{"content": "test content", "source": "Perplexity AI"}]

        # Verify cache set
        mock_cache.set.assert_called_once_with("perplexity_basic_test query", results)

    def test_advanced_search_cached(self, provider, mock_cache):
        """Test advanced_search returns cached results if available."""
        mock_cache.get.return_value = [
            {"content": "cached content", "source": "cached source"}
        ]

        results = provider.advanced_search("test query")

        mock_cache.get.assert_called_once_with("perplexity_advanced_test query")
        assert results == [{"content": "cached content", "source": "cached source"}]

    def test_advanced_search_api_call(self, provider, mock_cache, mock_openai):
        """Test advanced_search makes API call if no cached results."""
        # Set up cache miss
        mock_cache.get.return_value = None

        # Set up mock API response
        mock_client = mock_openai.return_value
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content="test content", citations=[]))
        ]
        mock_response.usage = MagicMock(
            prompt_tokens=10, completion_tokens=20, total_tokens=30
        )
        mock_client.chat.completions.create.return_value = mock_response

        results = provider.advanced_search("test query")

        # Verify cache check
        mock_cache.get.assert_called_once_with("perplexity_advanced_test query")

        # Verify API call
        mock_client.chat.completions.create.assert_called_once_with(
            model="sonar-pro",
            messages=[{"role": "user", "content": "test query"}],
            temperature=0.0,
        )

        # Verify results
        assert results == [{"content": "test content", "source": "Perplexity AI"}]

        # Verify cache set
        mock_cache.set.assert_called_once_with(
            "perplexity_advanced_test query", results
        )

    def test_research_search_cached(self, provider, mock_cache):
        """Test research_search returns cached results if available."""
        mock_cache.get.return_value = {
            "content": "cached content",
            "sources": ["source1", "source2"],
        }

        results = provider.research_search("test query")

        mock_cache.get.assert_called_once_with("perplexity_research_test query")
        assert results == {
            "content": "cached content",
            "sources": ["source1", "source2"],
        }

    def test_research_search_api_call(self, provider, mock_cache, mock_openai):
        """Test research_search makes API call if no cached results."""
        # Set up cache miss
        mock_cache.get.return_value = None

        # Set up mock API response
        mock_client = mock_openai.return_value
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(
                    content="test content",
                    citations=[{"url": "source1"}, {"url": "source2"}],
                )
            )
        ]
        mock_response.usage = MagicMock(
            prompt_tokens=10, completion_tokens=20, total_tokens=30
        )
        mock_client.chat.completions.create.return_value = mock_response

        results = provider.research_search("test query")

        # Verify cache check
        mock_cache.get.assert_called_once_with("perplexity_research_test query")

        # Verify API call
        mock_client.chat.completions.create.assert_called_once_with(
            model="sonar-deep-research",
            messages=[{"role": "user", "content": "test query"}],
            temperature=0.0,
        )

        # Verify results
        assert results == {"content": "test content", "sources": ["source1", "source2"]}

        # Verify cache set
        mock_cache.set.assert_called_once_with(
            "perplexity_research_test query", results
        )

    def test_basic_search_error_handling(self, provider, mock_cache, mock_openai):
        """Test basic_search handles errors gracefully."""
        # Set up cache miss
        mock_cache.get.return_value = None

        # Set up API error
        mock_client = mock_openai.return_value
        mock_client.chat.completions.create.side_effect = Exception("API error")

        results = provider.basic_search("test query")

        # Verify empty results on error
        assert results == []

        # Verify no cache set on error
        mock_cache.set.assert_not_called()

    def test_advanced_search_error_handling(self, provider, mock_cache, mock_openai):
        """Test advanced_search handles errors gracefully."""
        # Set up cache miss
        mock_cache.get.return_value = None

        # Set up API error
        mock_client = mock_openai.return_value
        mock_client.chat.completions.create.side_effect = Exception("API error")

        results = provider.advanced_search("test query")

        # Verify empty results on error
        assert results == []

        # Verify no cache set on error
        mock_cache.set.assert_not_called()

    def test_research_search_error_handling(self, provider, mock_cache, mock_openai):
        """Test research_search handles errors gracefully."""
        # Set up cache miss
        mock_cache.get.return_value = None

        # Set up API error
        mock_client = mock_openai.return_value
        mock_client.chat.completions.create.side_effect = Exception("API error")

        results = provider.research_search("test query")

        # Verify empty results on error
        assert results == {"content": "", "sources": []}

        # Verify no cache set on error
        mock_cache.set.assert_not_called()

    def test_process_search_results_with_citations(self, provider):
        """Test _process_search_results with citations."""
        response = {
            "choices": [
                {
                    "message": {"content": "main content"},
                    "citations": [
                        {"text": "citation 1", "url": "url1"},
                        {"text": "citation 2", "url": "url2"},
                    ],
                }
            ]
        }

        results = provider._process_search_results(response)

        assert results == [
            {"content": "citation 1", "source": "url1"},
            {"content": "citation 2", "source": "url2"},
        ]

    def test_process_search_results_without_citations(self, provider):
        """Test _process_search_results without citations."""
        response = {
            "choices": [{"message": {"content": "main content"}, "citations": []}]
        }

        results = provider._process_search_results(response)

        assert results == [{"content": "main content", "source": "Perplexity AI"}]

    def test_process_search_results_error_handling(self, provider):
        """Test _process_search_results handles errors gracefully."""
        # Invalid response format
        response = {"invalid": "format"}

        results = provider._process_search_results(response)

        assert results == []

    def test_process_research_results(self, provider):
        """Test _process_research_results."""
        response = {
            "choices": [
                {
                    "message": {"content": "research content"},
                    "citations": [{"url": "url1"}, {"url": "url2"}],
                }
            ]
        }

        results = provider._process_research_results(response)

        assert results == {"content": "research content", "sources": ["url1", "url2"]}

    def test_process_research_results_error_handling(self, provider):
        """Test _process_research_results handles errors gracefully."""
        # Invalid response format
        response = {"invalid": "format"}

        results = provider._process_research_results(response)

        assert results == {"content": "", "sources": []}
