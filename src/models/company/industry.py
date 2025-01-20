from typing import List

from pydantic import BaseModel, Field


class CompanyIndustry(BaseModel):
    primary_industry: str = Field(description="Main industry sector of the company")
    verticals: List[str] = Field(
        default_factory=list,
        description="Specific market segments or verticals the company operates in",
    )
