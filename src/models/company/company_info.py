from typing import List, Optional

from pydantic import BaseModel, HttpUrl

from .founders import CompanyFounders
from .growth_stage import CompanyGrowthStage


class CompanyInfo(BaseModel):
    company_name: str
    website_url: Optional[HttpUrl] = None
    growth_stage: Optional[CompanyGrowthStage] = None
    founding_year: Optional[int] = None
    founders: Optional[CompanyFounders] = None
