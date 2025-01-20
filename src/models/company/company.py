from typing import List, Optional

from pydantic import BaseModel, HttpUrl

from src.logger import get_logger

from .description import CompanyDescription
from .founders import CompanyFounders, Founder
from .funding import FundingInfo, FundingSource
from .growth_stage import CompanyGrowthStage, GrowthStage
from .industry import CompanyIndustry
from .location import CompanyLocation

logger = get_logger(__name__)


class Company(BaseModel):
    """Master schema for a company, including all company-related information."""

    # Basic Info
    company_name: str
    website_url: Optional[HttpUrl] = None
    description: Optional[CompanyDescription] = None

    # Detailed Information
    founding_year: Optional[int] = None
    founders: Optional[CompanyFounders] = None
    location: Optional[CompanyLocation] = None
    industry: Optional[CompanyIndustry] = None
    growth_stage: Optional[CompanyGrowthStage] = None
    funding: Optional[FundingInfo] = None

    def flatten(self) -> dict:
        """
        Converts the company model into a flat dictionary structure
        suitable for database storage.
        """
        flattened = {
            "company_name": self.company_name,
            "website_url": str(self.website_url) if self.website_url else None,
            "description": self.description.description if self.description else None,
            "founding_year": self.founding_year,
            # Location
            "city": self.location.city if self.location else None,
            "state": self.location.state if self.location else None,
            "country": self.location.country if self.location else None,
            # Industry
            "primary_industry": (
                self.industry.primary_industry if self.industry else None
            ),
            "verticals": self.industry.verticals if self.industry else [],
            # Growth Stage
            "growth_stage": (
                self.growth_stage.growth_stage.value if self.growth_stage else None
            ),
            "growth_stage_confidence": (
                self.growth_stage.confidence if self.growth_stage else None
            ),
            # Funding
            "total_funding": self.funding.total_amount if self.funding else None,
            "funding_currency": self.funding.currency if self.funding else "USD",
        }

        # Add founders as a list
        if self.founders:
            flattened["founders"] = [
                {"name": f.name, "title": f.title} for f in self.founders.founders
            ]
        else:
            flattened["founders"] = []

        # Add funding sources as a list
        if self.funding:
            flattened["funding_sources"] = [
                {"source": fs.source, "amount": fs.amount, "type": fs.type}
                for fs in self.funding.funding_sources
            ]
        else:
            flattened["funding_sources"] = []

        logger.debug("Flattened company data: %s", flattened)
        return flattened
