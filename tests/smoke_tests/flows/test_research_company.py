from src.flows.research_company import CompanyResearchFlow


def test_research_company_flow():
    # Initialize the flow with test data
    company_name = "Generation Genius"
    website_url = "https://www.generationgenius.com/"

    # Create an instance of the flow
    research_flow = CompanyResearchFlow(
        company_name=company_name, website_url=website_url
    )

    # Run the flow
    result = research_flow.research_company()

    # Check the result structure
    assert "message" in result, "Result should contain a 'message' key"
    assert "summary" in result, "Result should contain a 'summary' key"
    assert (
        result["message"] == f"Research completed for {company_name}."
    ), "Message should indicate completion for the correct company"

    # Print the result for manual inspection
    print(result)


# Run the test
if __name__ == "__main__":
    test_research_company_flow()
