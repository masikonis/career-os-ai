from src.workflows.company_research import CompanyResearchWorkflow


def test_company_research_workflow():
    # Initialize the workflow with test data
    company_name = "Generation Genius"
    website_url = "https://www.generationgenius.com/"

    # Create an instance of the workflow
    research_workflow = CompanyResearchWorkflow(
        company_name=company_name, website_url=website_url
    )

    # Run the workflow
    result = research_workflow.company_research()

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
    test_company_research_workflow()
