from pydantic import BaseModel, Field


class FoundingYear(BaseModel):
    year: int | None = Field(description="The year the company was founded")
