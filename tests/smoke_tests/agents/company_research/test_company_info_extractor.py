import json

import pytest

from src.agents.company_research.company_info_extractor import CompanyInfoExtractor
from src.agents.copywriting.brand_voice_text_editor import BrandVoiceTextEditor
from src.logger import get_logger
from src.models.company.company import Company
from src.models.company.company_description import CompanyDescription
from src.models.company.company_founders import CompanyFounders, Founder
from src.models.company.company_funding import CompanyFunding
from src.models.company.company_growth_stage import CompanyGrowthStage, GrowthStage
from src.models.company.company_industry import CompanyIndustry
from src.models.company.company_location import CompanyLocation

logger = get_logger(__name__)


@pytest.mark.smoke
def test_company_info_extractor_smoke():
    extractor = CompanyInfoExtractor()

    # Sample source text containing company name and website
    source_text = """
    Generation Genius is an innovative educational technology company. For more information, visit https://www.generationgenius.com.
    """

    try:
        result = extractor.extract_info(source_text)

        assert result is not None, "Extractor returned None."
        assert isinstance(result, dict), "Result should be a dictionary."

        # Validate against CompanyInfo model
        company = Company(**result)

        assert company.company_name, "'company_name' is empty."
        assert company.website_url, "'website_url' is empty."
        logger.info("CompanyInfoExtractor smoke test passed.")
    except Exception as e:
        logger.error(f"CompanyInfoExtractor smoke test failed: {e}")
        raise


@pytest.mark.smoke
def test_extract_growth_stage_smoke():
    """Test the extraction of company growth stage from research output."""
    extractor = CompanyInfoExtractor()

    # Sample research output (now just a string, as returned by CompanyWebResearcher)
    comprehensive_summary = """
    Generation Genius is an innovative educational technology company founded in 2017 by scientist Jeff Vinokur and TV executive Eric Rollman, based in Los Angeles, California. The platform specializes in creating engaging and interactive video lessons in science and math for K-8 students, aiming to make these subjects enjoyable and accessible. With a library of animated and live-action videos, hands-on activities, and comprehensive lesson plans aligned with the Next Generation Science Standards (NGSS), Generation Genius serves approximately 30% of elementary schools in the U.S. The company has received notable recognition, including being named one of TIME's 100 Most Influential Companies in 2023 and ranking on the Inc. 5000 list of fastest-growing companies. Generation Genius has raised a total of $1.6 million in funding, including a $1 million grant from the Howard Hughes Medical Institute and $1.07 million through crowdfunding. The team, led by Vinokur, is committed to transforming science education, and customer feedback highlights the platform's effectiveness in enhancing student engagement and learning outcomes, despite some concerns regarding subscription costs and the need for parental involvement.
    """

    try:
        # Pass the string directly as research_output
        result = extractor.extract_growth_stage(
            {"comprehensive_summary": comprehensive_summary}
        )

        assert result is not None, "Growth stage extraction returned None"
        assert isinstance(
            result, CompanyGrowthStage
        ), "Result should be a CompanyGrowthStage object"

        # Validate the growth stage is one of the valid enum values
        assert isinstance(
            result.growth_stage, GrowthStage
        ), "Growth stage should be a valid GrowthStage enum"

        # Validate confidence score
        assert (
            0.0 <= result.confidence <= 1.0
        ), "Confidence should be between 0.0 and 1.0"

        # Validate reasoning
        assert result.reasoning, "Reasoning should not be empty"
        assert isinstance(result.reasoning, str), "Reasoning should be a string"

        logger.info(
            f"Extracted growth stage: {result.growth_stage} with confidence {result.confidence}"
        )
        logger.info(f"Reasoning: {result.reasoning}")

    except Exception as e:
        logger.error(f"Growth stage extraction test failed: {e}")
        raise


@pytest.mark.smoke
def test_extract_founding_year_smoke():
    """Test the extraction of company founding year from research output."""
    extractor = CompanyInfoExtractor()

    # Sample research output
    comprehensive_summary = """
    Generation Genius is an innovative educational technology company founded in 2017 by scientist Jeff Vinokur and TV executive Eric Rollman, based in Los Angeles, California...
    """

    try:
        result = extractor.extract_founding_year(
            {"comprehensive_summary": comprehensive_summary}
        )

        assert result is not None, "Founding year extraction returned None"
        assert isinstance(result, int), "Result should be an integer"
        assert 1800 <= result <= 2024, "Founding year should be within reasonable range"

        logger.info(f"Extracted founding year: {result}")
        assert result == 2017, "Expected founding year is 2017"

    except Exception as e:
        logger.error(f"Founding year extraction test failed: {e}")
        raise


@pytest.mark.smoke
def test_extract_founders_smoke():
    """Test the extraction of company founders from research output."""
    extractor = CompanyInfoExtractor()

    # Sample research output
    comprehensive_summary = """
    Generation Genius is an innovative educational technology company founded in 2017 by scientist Jeff Vinokur and TV executive Eric Rollman, based in Los Angeles, California...
    """

    try:
        result = extractor.extract_founders(
            {"comprehensive_summary": comprehensive_summary}
        )

        assert result is not None, "Founders extraction returned None"
        assert isinstance(
            result, CompanyFounders
        ), "Result should be a CompanyFounders object"
        assert len(result.founders) > 0, "Should have found at least one founder"

        # Check specific founders
        founder_names = {founder.name for founder in result.founders}
        expected_names = {"Jeff Vinokur", "Eric Rollman"}
        assert (
            founder_names == expected_names
        ), f"Expected founders {expected_names}, got {founder_names}"

        # Check titles if available (case-insensitive comparison)
        for founder in result.founders:
            if founder.name == "Jeff Vinokur":
                assert (
                    founder.title.lower() == "scientist"
                ), "Jeff Vinokur should be identified as a scientist"
            elif founder.name == "Eric Rollman":
                assert (
                    founder.title.lower() == "tv executive"
                ), "Eric Rollman should be identified as a TV executive"

        # Update the logging to show more details
        founders_info = [f"{f.name} ({f.title})" for f in result.founders]
        logger.info(f"Extracted founders: {founders_info}")

    except Exception as e:
        logger.error(f"Founders extraction test failed: {e}")
        raise


@pytest.mark.smoke
def test_extract_location_smoke():
    """Test the extraction of company location from research output."""
    extractor = CompanyInfoExtractor()

    # Sample research output
    comprehensive_summary = """
    Generation Genius is an innovative educational technology company founded in 2017 by scientist Jeff Vinokur and TV executive Eric Rollman, based in Los Angeles, California. The platform specializes in creating engaging and interactive video lessons...
    """

    try:
        result = extractor.extract_location(
            {"comprehensive_summary": comprehensive_summary}
        )

        assert result is not None, "Location extraction returned None"
        assert isinstance(
            result, CompanyLocation
        ), "Result should be a CompanyLocation object"

        # Check specific location details
        assert result.city == "Los Angeles", "City should be Los Angeles"
        assert result.state == "California", "State should be California"
        assert result.country == "United States", "Country should be United States"

        # Log the extracted location
        logger.info(
            f"Extracted location: {result.city}, {result.state}, {result.country}"
        )

    except Exception as e:
        logger.error(f"Location extraction test failed: {e}")
        raise


@pytest.mark.smoke
def test_extract_funding_smoke():
    """Test the extraction of company funding information from research output."""
    extractor = CompanyInfoExtractor()

    # Sample research output
    comprehensive_summary = """
    Generation Genius is an innovative educational technology company founded in 2017 by scientist Jeff Vinokur and TV executive Eric Rollman, based in Los Angeles, California. The platform specializes in creating engaging and interactive video lessons in science and math for K-8 students, aiming to make these subjects enjoyable and accessible. With a library of animated and live-action videos, hands-on activities, and comprehensive lesson plans aligned with the Next Generation Science Standards (NGSS), Generation Genius serves approximately 30% of elementary schools in the U.S. The company has received notable recognition, including being named one of TIME's 100 Most Influential Companies in 2023 and ranking on the Inc. 5000 list of fastest-growing companies. Generation Genius has raised a total of $1.6 million in funding, including a $1 million grant from the Howard Hughes Medical Institute and $1.07 million through crowdfunding. The team, led by Vinokur, is committed to transforming science education, and customer feedback highlights the platform's effectiveness in enhancing student engagement and learning outcomes, despite some concerns regarding subscription costs and the need for parental involvement.
    """

    try:
        result = extractor.extract_funding(
            {"comprehensive_summary": comprehensive_summary}
        )

        assert result is not None, "Funding extraction returned None"
        assert isinstance(
            result, CompanyFunding
        ), "Result should be a CompanyFunding object"

        # Check total funding
        assert (
            result.total_amount == 1.6
        ), f"Total funding should be 1.6M, got {result.total_amount}M"
        assert result.currency == "USD", "Currency should be USD"

        # Check funding sources
        assert len(result.funding_sources) == 2, "Should have found 2 funding sources"

        # Create a map of sources to amounts for easier checking
        funding_map = {
            source.source: source.amount for source in result.funding_sources
        }

        assert "Howard Hughes Medical Institute" in funding_map, "Missing HHMI funding"
        assert (
            funding_map["Howard Hughes Medical Institute"] == 1.0
        ), "HHMI amount should be 1.0M"

        # Check crowdfunding
        crowdfunding = next(
            (s for s in result.funding_sources if s.type.lower() == "crowdfunding"),
            None,
        )
        assert crowdfunding is not None, "Missing crowdfunding source"
        assert crowdfunding.amount == 1.07, "Crowdfunding amount should be 1.07M"

        # Log the details
        logger.info(f"Total funding: ${result.total_amount}M {result.currency}")
        for source in result.funding_sources:
            logger.info(
                f"Source: {source.source}, Amount: ${source.amount}M, Type: {source.type}"
            )

    except Exception as e:
        logger.error(f"Funding extraction test failed: {e}")
        raise


@pytest.mark.smoke
def test_extract_industry_smoke():
    """Test the extraction of company industry information from research output."""
    extractor = CompanyInfoExtractor()

    # Sample research output
    comprehensive_summary = """
    Generation Genius is an innovative educational technology company founded in 2017 by scientist Jeff Vinokur and TV executive Eric Rollman, based in Los Angeles, California. The platform specializes in creating engaging and interactive video lessons in science and math for K-8 students, aiming to make these subjects enjoyable and accessible...
    """

    try:
        result = extractor.extract_industry(
            {"comprehensive_summary": comprehensive_summary}
        )

        assert result is not None, "Industry extraction returned None"
        assert isinstance(
            result, CompanyIndustry
        ), "Result should be a CompanyIndustry object"

        # Check primary industry
        assert result.primary_industry.lower() in [
            "edtech",
            "educational technology",
        ], "Primary industry should be EdTech or Educational Technology"

        # Check verticals - allow common education verticals
        verticals_lower = [v.lower() for v in result.verticals]
        assert any(
            v in verticals_lower
            for v in [
                "k-8 education",
                "k-12 education",
                "science education",
                "math education",
            ]
        ), "Should include education-related vertical"

        # Log the details
        logger.info(f"Primary Industry: {result.primary_industry}")
        logger.info(f"Verticals: {', '.join(result.verticals)}")

    except Exception as e:
        logger.error(f"Industry extraction test failed: {e}")
        raise


@pytest.mark.smoke
def test_create_description_smoke():
    """Test the creation of professional company summary."""
    extractor = CompanyInfoExtractor()

    comprehensive_summary = """
    Generation Genius is an innovative educational technology company founded in 2017 by scientist Jeff Vinokur and TV executive Eric Rollman, based in Los Angeles, California. The platform specializes in creating engaging and interactive video lessons in science and math for K-8 students, aiming to make these subjects enjoyable and accessible. With a library of animated and live-action videos, hands-on activities, and comprehensive lesson plans aligned with the Next Generation Science Standards (NGSS), Generation Genius serves approximately 30% of elementary schools in the U.S. The company has received notable recognition, including being named one of TIME's 100 Most Influential Companies in 2023 and ranking on the Inc. 5000 list of fastest-growing companies. Generation Genius has raised a total of $1.6 million in funding, including a $1 million grant from the Howard Hughes Medical Institute and $1.07 million through crowdfunding. The team, led by Vinokur, is committed to transforming science education, and customer feedback highlights the platform's effectiveness in enhancing student engagement and learning outcomes, despite some concerns regarding subscription costs and the need for parental involvement.
    """

    try:
        result = extractor.create_description(
            {"comprehensive_summary": comprehensive_summary}
        )

        assert result is not None, "Description creation returned None"
        assert isinstance(
            result, CompanyDescription
        ), "Result should be a CompanyDescription object"

        # Just check that we got a reasonable length description
        assert len(result.description) > 50, "Description too short"
        assert len(result.description) < 1000, "Description too long"

        # Log the description
        logger.info("Generated Summary:")
        logger.info(result.description)

    except Exception as e:
        logger.error(f"Description creation test failed: {e}")
        raise


@pytest.mark.smoke
def test_find_careers_url_smoke():
    extractor = CompanyInfoExtractor()

    # Test with a known website
    website_url = "https://www.generationgenius.com"

    try:
        careers_url = extractor.find_careers_url(website_url)

        # We don't assert the exact URL since it might change
        # Instead, we verify the method works without errors
        logger.info(f"Found careers URL: {careers_url}")

        # Test with invalid URL
        invalid_result = extractor.find_careers_url(None)
        assert invalid_result is None, "Should return None for invalid URL"

        logger.info("find_careers_url smoke test passed.")
    except Exception as e:
        logger.error(f"find_careers_url smoke test failed: {e}")
        raise


@pytest.mark.smoke
def test_extract_all_info_smoke():
    """Test the comprehensive extraction of all company information."""
    extractor = CompanyInfoExtractor()

    # Using the full comprehensive summary as other tests
    comprehensive_summary = """
    Generation Genius is an innovative educational technology company founded in 2017 by scientist Jeff Vinokur and TV executive Eric Rollman, based in Los Angeles, California. The platform specializes in creating engaging and interactive video lessons in science and math for K-8 students, aiming to make these subjects enjoyable and accessible. With a library of animated and live-action videos, hands-on activities, and comprehensive lesson plans aligned with the Next Generation Science Standards (NGSS), Generation Genius serves approximately 30% of elementary schools in the U.S. The company has received notable recognition, including being named one of TIME's 100 Most Influential Companies in 2023 and ranking on the Inc. 5000 list of fastest-growing companies. Generation Genius has raised a total of $1.6 million in funding, including a $1 million grant from the Howard Hughes Medical Institute and $1.07 million through crowdfunding. The team, led by Vinokur, is committed to transforming science education, and customer feedback highlights the platform's effectiveness in enhancing student engagement and learning outcomes, despite some concerns regarding subscription costs and the need for parental involvement.
    """

    website_url = "https://www.generationgenius.com"

    try:
        result = extractor.extract_all_info(
            {"comprehensive_summary": comprehensive_summary}, company_url=website_url
        )

        # Check that all expected keys are present
        expected_keys = {
            "careers_url",  # Move to top to match implementation order
            "founding_year",
            "founders",
            "location",
            "industry",
            "growth_stage",
            "funding",
            "description",
        }

        # Validate URL-based fields first
        if result["careers_url"]:
            assert isinstance(
                result["careers_url"], str
            ), "Careers URL should be a string"
            assert result["careers_url"].startswith(
                "http"
            ), "Careers URL should be a valid URL"

        # Then validate LLM-based fields
        assert result["founding_year"] == 2017, "Incorrect founding year"
        assert isinstance(
            result["founders"], CompanyFounders
        ), "Founders should be CompanyFounders object"
        assert isinstance(
            result["location"], CompanyLocation
        ), "Location should be CompanyLocation object"
        assert isinstance(
            result["industry"], CompanyIndustry
        ), "Industry should be CompanyIndustry object"
        assert isinstance(
            result["growth_stage"], CompanyGrowthStage
        ), "Growth stage should be CompanyGrowthStage object"
        assert isinstance(
            result["funding"], CompanyFunding
        ), "Funding should be CompanyFunding object"
        assert isinstance(
            result["description"], CompanyDescription
        ), "Description should be CompanyDescription object"

        # Log successful extractions
        logger.info("Successfully extracted all company information:")
        for key, value in result.items():
            if value is not None:
                logger.info(f"{key}: {value}")

    except Exception as e:
        logger.error(f"Comprehensive extraction test failed: {e}")
        raise


@pytest.mark.smoke
def test_extract_all_info_with_real_data():
    """Test all extraction methods with real research data from SlideSpeak."""
    extractor = CompanyInfoExtractor()

    # Real research data from web researcher
    research_data = {
        "comprehensive_summary": """SlideSpeak is an innovative AI-powered platform designed to enhance the creation, summarization, and interaction with presentations and documents, particularly focusing on PowerPoint files. Launched in August 2023, it leverages advanced ChatGPT technology to automate the generation of professional-quality slides from various document formats, including Word and PDFs, while also providing features for summarizing content and engaging in interactive Q&A sessions. The company, headquartered in London and Austin, operates with a small, fully remote team that emphasizes collaboration and creativity, fostering a supportive work culture. Despite its rapid growth, evidenced by over 4 million files uploaded, user feedback has been mixed, with an average rating of 3 out of 5 stars, highlighting both its efficiency and some technical issues. SlideSpeak is actively hiring to expand its team and improve its offerings, while also maintaining a commitment to data security and user privacy. Overall, SlideSpeak positions itself as a valuable tool for professionals, educators, and students seeking efficient solutions for presentation management.""",
        "company_summary": """**SlideSpeak Company Summary**

SlideSpeak is an AI-powered platform that enhances the creation, summarization, and interaction with presentations and documents, primarily targeting professionals, educators, and students. The company offers a robust API that streamlines the presentation workflow by enabling users to generate, update, and redesign PowerPoint presentations efficiently.

**Core Offerings:**
- **AI Presentation Generation**: Automatically creates visually appealing slides from various document formats, including PowerPoint, Word, and PDFs.
- **Document Summarization**: Extracts key insights and generates concise summaries from lengthy documents.
- **Interactive Q&A**: Users can engage with their presentations through a chat interface, asking questions and receiving real-time responses.
- **Custom Templates and Multi-Format Support**: Allows for personalized branding and compatibility with multiple document types.

**Value Proposition**: SlideSpeak's main value lies in its ability to save time and enhance productivity by automating the presentation creation process, allowing users to focus on content delivery rather than design mechanics. Its user-friendly interface makes it accessible to individuals with varying technical skills.

**Target Market**: The platform primarily serves business professionals, educators, researchers, marketers, and students who require efficient and effective presentation solutions.

In summary, SlideSpeak is positioned as a significant player in the presentation technology sector, leveraging AI to transform how users create and manage presentations while fostering a collaborative and innovative company culture.""",
        "funding_summary": """**SlideSpeak Funding Summary**

SlideSpeak is an AI-driven technology company focused on enhancing the presentation creation process. As of October 2023, the company has successfully raised a total of **$5 million** in funding through **two rounds**. The funding rounds include a **Seed round** and a **Series A round**, with participation from notable investors such as **Techstars**, **Y Combinator**, and **Sequoia Capital**.

The company has demonstrated significant user engagement, with over **4 million files uploaded** to its platform, indicating strong demand for its innovative solutions. SlideSpeak operates with a small team and has a growing presence in the market, positioning itself as a key player in the presentation technology sector.

Overall, SlideSpeak's funding history reflects a solid foundation for future growth and product development, leveraging its AI capabilities to transform how users create and manage presentations.""",
        "team_summary": """**SlideSpeak Team Summary**

SlideSpeak is an AI-driven technology company founded in 2022, headquartered in San Antonio, Texas, with additional operations in London and Austin, Texas. The company specializes in enhancing the presentation creation process through innovative software solutions, particularly focusing on AI-powered tools that streamline the development and management of presentations.

The leadership team consists of a small, fully remote group of 2-10 employees, fostering a collaborative and friendly work culture. The team emphasizes teamwork and creativity, holding in-person meetups every three months to strengthen connections and enhance productivity. Currently, SlideSpeak is looking to expand its team by hiring a Full Stack Software Engineer with expertise in backend development.

SlideSpeak's commitment to community engagement is evident through its active participation in developer forums and social media, where it shares insights on AI applications in presentations and gathers user feedback for product improvements. The company values innovation and aims to refine its AI tools to meet the evolving needs of its users in both business and academic settings.

Overall, SlideSpeak's leadership is focused on creating a supportive work environment while driving the development of cutting-edge presentation technology, positioning the company for continued growth and success in the industry.""",
    }

    try:
        # Test growth stage extraction
        growth_stage = extractor.extract_growth_stage(research_data)
        assert isinstance(growth_stage, CompanyGrowthStage)
        assert growth_stage.growth_stage == GrowthStage.SEED
        logger.info(
            f"Growth Stage: {growth_stage.growth_stage} (Confidence: {growth_stage.confidence})"
        )
        logger.info(f"Growth Stage Reasoning: {growth_stage.reasoning}")

        # Test founding year extraction
        founding_year = extractor.extract_founding_year(research_data)
        assert founding_year == 2022  # Updated based on team summary
        logger.info(f"Founding Year: {founding_year}")

        # Test location extraction
        location = extractor.extract_location(research_data)
        assert isinstance(location, CompanyLocation)
        logger.info(f"Location: {location.city}, {location.state}, {location.country}")
        assert (
            "San Antonio" in location.city
            or "London" in location.city
            or "Austin" in location.city
        )

        # Test funding extraction
        funding = extractor.extract_funding(research_data)
        assert isinstance(funding, CompanyFunding)
        assert funding.total_amount == 5.0
        assert any(source.source == "Techstars" for source in funding.funding_sources)
        assert any(
            source.source == "Y Combinator" for source in funding.funding_sources
        )
        assert any(
            source.source == "Sequoia Capital" for source in funding.funding_sources
        )
        logger.info(f"Funding: ${funding.total_amount}M")
        logger.info(
            f"Investors: {', '.join(source.source for source in funding.funding_sources)}"
        )

        # Test industry extraction
        industry = extractor.extract_industry(research_data)
        assert isinstance(industry, CompanyIndustry)
        logger.info(f"Industry: {industry.primary_industry}")
        logger.info(f"Verticals: {', '.join(industry.verticals)}")

        # Test description creation
        description = extractor.create_description(research_data)
        assert isinstance(description, CompanyDescription)
        logger.info(f"Description: {description.description}")

        # Test all info extraction
        all_info = extractor.extract_all_info(
            research_data, company_url="https://slidespeak.co"
        )

        assert all_info is not None
        assert isinstance(all_info, dict)
        logger.info("Successfully extracted all company information")

        # Create and log full company model
        company = Company(
            company_name="SlideSpeak", website_url="https://slidespeak.co", **all_info
        )
        logger.info("Full Company Model:")
        # Format the flattened data as pretty JSON
        flattened_data = company.flatten()
        formatted_json = json.dumps(flattened_data, indent=2)
        logger.info("\n" + formatted_json)

    except Exception as e:
        logger.error(f"Real data extraction test failed: {e}")
        raise


@pytest.mark.smoke
def test_brand_voice_integration():
    """Test that brand voice editor is properly integrated."""
    extractor = CompanyInfoExtractor()

    # Verify brand voice editor is initialized
    assert hasattr(
        extractor, "brand_voice_editor"
    ), "Brand voice editor not initialized"
    assert isinstance(
        extractor.brand_voice_editor, BrandVoiceTextEditor
    ), "Brand voice editor is not of correct type"

    logger.info("Brand voice editor integration test passed")
