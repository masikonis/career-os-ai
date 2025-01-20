from abc import ABC, abstractmethod

from src.models.job.job_details import JobDetails


class ExtractorInterface(ABC):
    """Base interface for job board extractors.

    Requirements:
    - Handle network errors gracefully
    - Return empty strings for missing fields
    - Sanitize text and preserve formatting
    - Implement logging
    """

    @abstractmethod
    def extract_details(self, job_ad_url: str) -> JobDetails:
        """Extract job details from URL.

        Args:
            job_ad_url: Job advertisement URL

        Returns:
            JobDetails object
        """
        raise NotImplementedError
