from pydantic import BaseModel, Field


class CompanyLocation(BaseModel):
    city: str | None = Field(description="City where the company is based")
    state: str | None = Field(description="State or region where the company is based")
    country: str | None = Field(
        description="Country where the company is based", default="United States"
    )
