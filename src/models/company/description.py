from pydantic import BaseModel, Field


class CompanyDescription(BaseModel):
    description: str = Field(
        description="Brief company description targeted at technical job seekers"
    )
