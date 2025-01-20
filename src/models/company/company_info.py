from typing import Optional

from pydantic import BaseModel, HttpUrl


class CompanyInfo(BaseModel):
    company_name: str
    website_url: Optional[HttpUrl] = None
