from abc import ABC, abstractmethod
from typing import List


class WebSearchInterface(ABC):
    """Base interface for Web Search providers."""

    @abstractmethod
    def search(self, query: str) -> List[str]:
        """Performs a web search for the given query and returns a list of results."""
        pass
