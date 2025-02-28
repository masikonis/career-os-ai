from abc import ABC

import pytest

from src.services.web_search.interface import WebSearchInterface


class TestWebSearchInterface:
    """Unit tests for the WebSearchInterface class."""

    def test_interface_is_abstract(self):
        """Test that WebSearchInterface is an abstract base class."""
        assert issubclass(WebSearchInterface, ABC)

    def test_basic_search_is_abstract(self):
        """Test that basic_search is an abstract method."""
        assert WebSearchInterface.basic_search.__isabstractmethod__

    def test_advanced_search_is_abstract(self):
        """Test that advanced_search is an abstract method."""
        assert WebSearchInterface.advanced_search.__isabstractmethod__

    def test_research_search_is_abstract(self):
        """Test that research_search is an abstract method."""
        assert WebSearchInterface.research_search.__isabstractmethod__

    def test_cannot_instantiate_interface(self):
        """Test that WebSearchInterface cannot be instantiated directly."""
        with pytest.raises(TypeError) as excinfo:
            WebSearchInterface()
        assert "Can't instantiate abstract class" in str(excinfo.value)

    def test_concrete_implementation_required(self):
        """Test that concrete implementations must implement all abstract methods."""

        # Define a class that inherits from WebSearchInterface but doesn't implement all methods
        class IncompleteProvider(WebSearchInterface):
            def basic_search(self, query):
                return []

            # Missing advanced_search and research_search implementations

        # Attempting to instantiate should fail
        with pytest.raises(TypeError) as excinfo:
            IncompleteProvider()
        assert "Can't instantiate abstract class" in str(excinfo.value)

    def test_complete_implementation_allowed(self):
        """Test that complete implementations can be instantiated."""

        # Define a class that implements all required methods
        class CompleteProvider(WebSearchInterface):
            def basic_search(self, query):
                return []

            def advanced_search(self, query):
                return []

            def research_search(self, query):
                return {"content": "", "sources": []}

        # Should be able to instantiate
        provider = CompleteProvider()
        assert isinstance(provider, WebSearchInterface)
