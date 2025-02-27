from prefect import flow

from src.agents.company_research.company_surface_researcher import (
    CompanySurfaceResearcher,
)
from src.models.company.company import Company


class CompanyResearchFlow:
    def __init__(self, company_name: str = "Generation Genius", website_url: str = ""):
        """
        Initialize the CompanyResearchFlow with the company name and website URL.
        """
        self.company_name = company_name
        self.website_url = website_url
        self.surface_researcher = CompanySurfaceResearcher()

    @flow(log_prints=True)
    def research_company(self) -> dict:
        """
        Prefect flow to research a company.
        """
        company = Company.from_basic_info(
            company_name=self.company_name, website_url=self.website_url
        )
        summary = self.surface_researcher.research_company(company)
        return {
            "message": f"Research completed for {self.company_name}.",
            "summary": summary,
        }

    def serve(
        self, name: str = "company-research-deployment", tags=None, interval: int = 60
    ):
        """
        Deploy the flow with the specified configuration.
        """
        if tags is None:
            tags = ["research"]

        self.research_company.serve(
            name=name,
            tags=tags,
            parameters={
                "company_name": self.company_name,
                "website_url": self.website_url,
            },
            interval=interval,
        )


if __name__ == "__main__":
    research_flow = CompanyResearchFlow(
        company_name="Generation Genius",
        website_url="https://www.generationgenius.com/",
    )
    research_flow.serve()
