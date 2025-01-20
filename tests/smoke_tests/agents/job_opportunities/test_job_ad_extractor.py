from src.agents.job_opportunities.job_ad_extractor import JobAdExtractor
from src.logger import get_logger
from src.models.job.job_details import JobDetails
from src.models.job.job_location import LocationType

logger = get_logger(__name__)


def test_extract_details_valid_url():
    """Smoke test for JobAdExtractor.extract_details with a valid URL."""
    extractor = JobAdExtractor()
    sample_url = "https://weworkremotely.com/remote-jobs/bluegamma-full-stack-developer"
    content = extractor.extract_details(sample_url)

    # Check if it's a JobDetails instance
    assert isinstance(content, JobDetails), "Content should be a JobDetails instance"

    # Convert to dict for easier testing
    content_dict = content.model_dump()

    # Check non-empty values for required fields
    assert content_dict["company"]["company_name"], "Company name should not be empty"
    assert content_dict["company"]["website_url"], "Website URL should not be empty"
    assert content_dict["title"], "Job title should not be empty"
    assert content_dict["description"], "Job description should not be empty"
    assert content_dict["url"], "URL should not be empty"

    # Check location type
    assert "location_type" in content_dict, "Location type should be present"
    assert isinstance(
        content.location_type, LocationType
    ), "Location type should be a LocationType model"
    assert content.location_type.type in [
        "Remote",
        "Hybrid",
        "Onsite",
    ], "Location type should be one of: Remote, Hybrid, Onsite"

    logger.info("Extracted job details:")
    logger.info(f"Company: {content.company.company_name}")
    logger.info(f"Title: {content.title}")
    logger.info(f"Location Type: {content.location_type.type}")
    logger.info(f"Description excerpt: {content.description[:200]}...")


def test_determine_location_type():
    """Test location type determination with sample descriptions."""
    extractor = JobAdExtractor()

    # Test remote job description
    remote_description = """
    This is a fully remote position. Work from anywhere in the world.
    You'll be able to work from home and collaborate with our distributed team.
    """
    remote_type = extractor._determine_location_type(remote_description)
    logger.info("\nTesting REMOTE description:")
    logger.info(f"Input: {remote_description.strip()}")
    logger.info(f"Output: {remote_type.type}")
    assert remote_type.type == "Remote", "Should detect remote work"

    # Test hybrid job description
    hybrid_description = """
    We offer a flexible hybrid work arrangement.
    You'll need to be in the office 2 days per week and can work remotely the rest.
    """
    hybrid_type = extractor._determine_location_type(hybrid_description)
    logger.info("\nTesting HYBRID description:")
    logger.info(f"Input: {hybrid_description.strip()}")
    logger.info(f"Output: {hybrid_type.type}")
    assert hybrid_type.type == "Hybrid", "Should detect hybrid work"

    # Test onsite job description
    onsite_description = """
    This position is based in our New York office.
    You'll be working from our state-of-the-art facility in Manhattan.
    """
    onsite_type = extractor._determine_location_type(onsite_description)
    logger.info("\nTesting ONSITE description:")
    logger.info(f"Input: {onsite_description.strip()}")
    logger.info(f"Output: {onsite_type.type}")
    assert onsite_type.type == "Onsite", "Should detect onsite work"
