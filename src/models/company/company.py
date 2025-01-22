from hashlib import sha256
from typing import List, Optional

from pydantic import BaseModel, HttpUrl, computed_field

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

    @computed_field
    def company_id(self) -> str:
        """Generate unique company ID combining domain prefix and content hash.

        Returns:
            str: Unique company ID in format 'company_prefix_hash' where:
                - prefix is first 3 chars of normalized domain (or 'nwb' if no website)
                - hash is based on full domain and company name

        Examples:
            >>> company_id
            'company_pay_8f4b2c9e'  # PayPal (from paypal.com)
            >>> company_id
            'company_nwb_a7d8e9f3'  # Company without website
        """
        from src.utilities.company import normalize_company_name
        from src.utilities.url import normalize_domain

        # Get normalized components
        norm_domain = normalize_domain(
            str(self.website_url) if self.website_url else None
        )
        norm_name = normalize_company_name(self.company_name)

        # Determine source
        source = norm_domain[:3] if norm_domain else "nwb"

        # Generate hash from normalized data
        content = f"{norm_domain}:{norm_name}" if norm_domain else norm_name
        content_hash = sha256(content.encode()).hexdigest()[:8]

        return f"company_{source}_{content_hash}"

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
