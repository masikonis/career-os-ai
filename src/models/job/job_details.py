from datetime import datetime
from hashlib import sha256
from typing import Optional
from urllib.parse import urlparse

from pydantic import BaseModel, HttpUrl, computed_field

from src.models.company.company_info import CompanyInfo
from src.models.job.job_location import LocationType


class JobDetails(BaseModel):
    """Job posting details."""

    company: CompanyInfo
    title: str
    description: str
    url: HttpUrl
    location_type: LocationType
    posted_date: Optional[datetime] = None

    @computed_field
    def job_id(self) -> str:
        """Generate unique job ID combining prefix, source and content hash.

        Returns:
            str: Unique job ID in format 'job_ad_src_hash' (e.g. 'job_ad_wwr_8f4b2c9e')
        """
        parsed = urlparse(str(self.url))
        source = parsed.netloc.split(".")[0][:3]  # First 3 chars of domain
        content_hash = sha256(str(self.url).encode()).hexdigest()[
            :8
        ]  # First 8 chars of hash
        return f"job_ad_{source}_{content_hash}"
