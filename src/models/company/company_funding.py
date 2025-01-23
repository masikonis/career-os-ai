from typing import List

from pydantic import BaseModel, Field


class FundingSource(BaseModel):
    source: str = Field(
        description="Name of the funding source (e.g., VC firm, grant provider)"
    )
    amount: float | None = Field(description="Amount in millions", default=None)
    type: str = Field(
        description="Type of funding (e.g., Grant, Crowdfunding, Venture Capital)"
    )


class CompanyFunding(BaseModel):
    total_amount: float | None = Field(description="Total funding amount in millions")
    currency: str = Field(description="Currency of the funding amounts", default="USD")
    funding_sources: List[FundingSource] = Field(
        default_factory=list,
        description="List of individual funding sources and their details",
    )
