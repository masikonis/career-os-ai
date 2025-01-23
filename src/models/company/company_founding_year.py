from pydantic import BaseModel, Field


class CompanyFoundingYear(BaseModel):
    year: int | None = Field(description="The year the company was founded")
