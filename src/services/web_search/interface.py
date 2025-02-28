from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class WebSearchInterface(ABC):
    """Base interface for Web Search providers.

    This interface defines methods for different levels of search capabilities:
    - basic_search: Simple, fast, and cost-effective search
    - advanced_search: More comprehensive search with additional options
    - research_search: In-depth, multi-source research with synthesis
    """

    @abstractmethod
    def basic_search(self, query: str) -> List[Dict[str, str]]:
        """Performs a basic web search for the given query.

        This is the simplest and most cost-effective search option.

        Args:
            query: The search query string

        Returns:
            A list of search results, where each result is a dictionary
            containing at minimum 'content' and 'source' keys.
        """
        pass

    @abstractmethod
    def advanced_search(self, query: str) -> List[Dict[str, str]]:
        """Performs an advanced web search with more comprehensive results.

        This provides more detailed and higher-quality results than basic search.

        Args:
            query: The search query string

        Returns:
            A list of search results, where each result is a dictionary
            containing at minimum 'content' and 'source' keys.
        """
        pass

    @abstractmethod
    def research_search(self, query: str) -> Dict[str, Any]:
        """Performs an in-depth research search with synthesis.

        This conducts comprehensive research across multiple sources,
        synthesizing the information into a coherent response.

        Args:
            query: The research query or topic

        Returns:
            A dictionary containing the synthesized research results,
            including 'content' and 'sources' keys.
        """
        pass
