from prefect import flow

from src.agents.company_research.company_web_researcher import CompanyWebResearcher
from src.models.company.company import Company


class CompanyResearchWorkflow:
    def __init__(self, company_name: str = "Generation Genius", website_url: str = ""):
        """
        Initialize the CompanyResearchWorkflow with the company name and website URL.
        """
        self.company_name = company_name
        self.website_url = website_url
        self.researcher = CompanyWebResearcher()

    @flow(log_prints=True)
    def company_research(self) -> dict:
        """
        Prefect workflow to research a company.
        """
        company = Company.from_basic_info(
            company_name=self.company_name, website_url=self.website_url
        )
        summary = self.researcher.research_company(company)
        return {
            "message": f"Research completed for {self.company_name}.",
            "summary": summary,
        }

    def serve(
        self, name: str = "company-research-deployment", tags=None, interval: int = 60
    ):
        """
        Deploy the workflow with the specified configuration.
        """
        if tags is None:
            tags = ["research"]

        self.company_research.serve(
            name=name,
            tags=tags,
            parameters={
                "company_name": self.company_name,
                "website_url": self.website_url,
            },
            interval=interval,
        )


if __name__ == "__main__":
    research_workflow = CompanyResearchWorkflow(
        company_name="Generation Genius",
        website_url="https://www.generationgenius.com/",
    )
    research_workflow.serve()
