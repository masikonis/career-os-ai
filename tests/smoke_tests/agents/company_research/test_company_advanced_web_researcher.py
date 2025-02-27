import json

from openai import OpenAI

from src.config import config
from src.logger import get_logger

logger = get_logger(__name__)


def test_perplexity_deep_research():
    """
    A simple test to connect to Perplexity API and test the deep research capability.
    This is a temporary test to evaluate the API and response quality.
    """
    # Get API key from config
    api_key = config.get("PERPLEXITY_API_KEY")
    if not api_key:
        logger.error("PERPLEXITY_API_KEY not set in config or .env file")
        raise ValueError("PERPLEXITY_API_KEY not set in config or .env file")

    # Initialize the OpenAI client with Perplexity's base URL
    client = OpenAI(api_key=api_key, base_url="https://api.perplexity.ai")

    # Company to research
    company_name = "Generation Genius"

    # The simplified prompt that performed better in testing
    messages = [
        {
            "role": "user",
            "content": f"""
            Conduct comprehensive business research on {company_name}, the educational company. Please include:

            1. Company overview: founding, mission, core business and products
            2. Funding history and financial information
            3. Team details including founders, key executives and company size
            4. Market position and competitors

            Finally, provide a structured business summary with:
            - Company stage and funding status
            - Product type and revenue model
            - Team size and locations
            - Product status and traction metrics

            For all information, please cite sources and distinguish between verified facts and company claims.
            """,
        }
    ]

    # Make the API call
    try:
        logger.info(f"Making request to Perplexity API for company: {company_name}")
        response = client.chat.completions.create(
            model="sonar-deep-research",
            messages=messages,
            temperature=0.0,  # Lower temperature for more factual responses
        )

        # Print the response
        print(f"RESPONSE FROM PERPLEXITY DEEP RESEARCH:\n")
        print(response.choices[0].message.content)

        # Save the response to a file for detailed analysis
        with open("perplexity_response.json", "w") as f:
            # Need to convert the OpenAI response object to a dict
            response_dict = {
                "content": response.choices[0].message.content,
                "model": response.model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                },
            }
            json.dump(response_dict, f, indent=4)

        # Print token usage for cost estimation
        logger.info(
            f"Token usage - Prompt: {response.usage.prompt_tokens}, "
            + f"Completion: {response.usage.completion_tokens}, "
            + f"Total: {response.usage.total_tokens}"
        )

        return True

    except Exception as e:
        logger.error(f"Error calling Perplexity API: {str(e)}")
        return False


if __name__ == "__main__":
    # This allows running the test directly
    test_perplexity_deep_research()
