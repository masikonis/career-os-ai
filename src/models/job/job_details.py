from datetime import datetime
from typing import Optional

from pydantic import BaseModel, HttpUrl

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
