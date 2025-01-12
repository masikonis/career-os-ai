from abc import ABC, abstractmethod


class WebSearchInterface(ABC):
    @abstractmethod
    def search(self, query: str) -> list:
        pass
