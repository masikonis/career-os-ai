from prefect import flow


@flow(log_prints=False)
def research_company(company_name: str = "Generation Genius") -> str:
    return f"Research completed for {company_name}."


if __name__ == "__main__":
    research_company.serve(
        name="company-research-deployment",
        tags=["research"],
        parameters={},
        interval=60,
    )
