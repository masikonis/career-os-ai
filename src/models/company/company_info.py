from typing import List, Optional

from pydantic import BaseModel, HttpUrl

from .founders import CompanyFounders
from .funding import FundingInfo
from .growth_stage import CompanyGrowthStage
from .industry import CompanyIndustry
from .location import CompanyLocation


class CompanyInfo(BaseModel):
    company_name: str
    website_url: Optional[HttpUrl] = None
    founding_year: Optional[int] = None
    founders: Optional[CompanyFounders] = None
    location: Optional[CompanyLocation] = None
    industry: Optional[CompanyIndustry] = None
    growth_stage: Optional[CompanyGrowthStage] = None
    funding: Optional[FundingInfo] = None
