from typing import List, Optional

from pydantic import BaseModel, HttpUrl

from .founders import CompanyFounders
from .funding import FundingInfo
from .growth_stage import CompanyGrowthStage
from .location import CompanyLocation


class CompanyInfo(BaseModel):
    company_name: str
    website_url: Optional[HttpUrl] = None
    growth_stage: Optional[CompanyGrowthStage] = None
    founding_year: Optional[int] = None
    founders: Optional[CompanyFounders] = None
    funding: Optional[FundingInfo] = None
    location: Optional[CompanyLocation] = None
