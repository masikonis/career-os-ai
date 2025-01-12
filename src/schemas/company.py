from pydantic import BaseModel, Field, HttpUrl


class Company(BaseModel):
    """Basic schema for a company."""

    name: str = Field(description="The name of the company")
    website: HttpUrl = Field(description="The company's website URL")
    description: str = Field(description="A brief description of the company")
