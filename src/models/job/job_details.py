from pydantic import BaseModel, HttpUrl

from src.models.company.company_info import CompanyInfo


class JobDetails(BaseModel):
    """Job posting details."""

    company: CompanyInfo
    title: str
    description: str
    url: HttpUrl
