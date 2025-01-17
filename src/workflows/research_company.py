from prefect import flow


class CompanyResearchFlow:
    def __init__(self, company_name: str = "Generation Genius"):
        """
        Initialize the CompanyResearchFlow with the company name.
        """
        self.company_name = company_name

    @flow(log_prints=False)
    def research_company(self) -> str:
        """
        Prefect flow to research a company.
        """
        return f"Research completed for {self.company_name}."

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
            parameters={"company_name": self.company_name},
            interval=interval,
        )


if __name__ == "__main__":
    research_flow = CompanyResearchFlow(company_name="Generation Genius")
    research_flow.serve()
