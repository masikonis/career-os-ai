from typing import Optional

from pydantic import BaseModel, HttpUrl

from .growth_stage import CompanyGrowthStage


class CompanyInfo(BaseModel):
    company_name: str
    website_url: Optional[HttpUrl] = None
    growth_stage: Optional[CompanyGrowthStage] = None
