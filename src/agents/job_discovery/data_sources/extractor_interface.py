from abc import ABC, abstractmethod

from src.models.job.job import Job


class ExtractorInterface(ABC):
    """Base interface for job board extractors.

    Requirements:
    - Handle network errors gracefully
    - Return empty strings for missing fields
    - Sanitize text and preserve formatting
    - Implement logging
    """

    @abstractmethod
    def extract_details(self, job_ad_url: str) -> Job:
        """Extract job details from URL.

        Args:
            job_ad_url: Job advertisement URL

        Returns:
            Job: Extracted job details
        """
        raise NotImplementedError

    def needs_location_analysis(self) -> bool:
        """Indicate if this extractor needs LLM location analysis.

        Returns:
            bool: True if LLM should analyze location type, False if extractor knows the type
        """
        return True  # Default to True for backward compatibility
