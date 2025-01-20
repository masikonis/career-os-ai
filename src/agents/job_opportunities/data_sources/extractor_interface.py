from abc import ABC, abstractmethod
from typing import Dict, TypedDict


class JobDetailsDict(TypedDict):
    """Job details dictionary structure."""

    company_name: str
    website_url: str
    job_ad_title: str
    job_ad: str


class ExtractorInterface(ABC):
    """Base interface for job board extractors.

    Requirements:
    - Handle network errors gracefully
    - Return empty strings for missing fields
    - Sanitize text and preserve formatting
    - Implement logging
    """

    @abstractmethod
    def extract_details(self, job_ad_url: str) -> JobDetailsDict:
        """Extract job details from URL.

        Args:
            job_ad_url: Job advertisement URL

        Returns:
            Dict with company_name, website_url, job_ad_title, and job_ad
        """
        raise NotImplementedError
