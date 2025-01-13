from pydantic import BaseModel

from src.logger import get_logger

from .company_info import CompanyInfo

logger = get_logger(__name__)


class Company(BaseModel):
    """Master schema for a company, composed of atomic submodels."""

    info: CompanyInfo

    def flatten(self):
        flattened = {
            "company_name": self.info.company_name,
            "website_url": self.info.website_url,
        }
        logger.debug("Flattened company data: %s", flattened)
        return flattened
