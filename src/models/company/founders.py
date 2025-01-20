from typing import List

from pydantic import BaseModel, Field


class Founder(BaseModel):
    name: str
    title: str | None = None


class CompanyFounders(BaseModel):
    founders: List[Founder] = Field(
        default_factory=list,
        description="List of company founders with their names and optional titles",
    )
