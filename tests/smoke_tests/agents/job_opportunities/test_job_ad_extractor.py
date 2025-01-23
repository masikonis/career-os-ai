from datetime import datetime

from src.agents.job_opportunities.job_ad_extractor import JobAdExtractor
from src.logger import get_logger
from src.models.job.job import Job
from src.models.job.job_location import JobLocation

logger = get_logger(__name__)


def test_extract_details_valid_url():
    """Smoke test for JobAdExtractor.extract_details with a valid URL."""
    extractor = JobAdExtractor()
    sample_url = "https://weworkremotely.com/remote-jobs/bluegamma-full-stack-developer"
    content = extractor.extract_details(sample_url)

    # Check if it's a Job instance
    assert isinstance(content, Job), "Content should be a Job instance"

    # Convert to dict for easier testing
    content_dict = content.model_dump()

    # Check non-empty values for required fields
    assert content_dict["company"]["company_name"], "Company name should not be empty"
    # Website URL is now optional, so we don't assert it
    assert content_dict["title"], "Job title should not be empty"
    assert content_dict["description"], "Job description should not be empty"
    assert content_dict["url"], "URL should not be empty"

    # Check location type
    assert "location_type" in content_dict, "Location type should be present"
    assert isinstance(
        content.location_type, JobLocation
    ), "Location type should be a JobLocation model"
    assert content.location_type.type in [
        "Remote",
        "Hybrid",
        "Onsite",
    ], "Location type should be one of: Remote, Hybrid, Onsite"

    # Check posted date
    assert "posted_date" in content_dict, "Posted date should be present"
    if content.posted_date:
        assert isinstance(
            content.posted_date, datetime
        ), "Posted date should be a datetime object"

    # Check job_id format
    assert content.job_id, "Job ID should not be empty"
    assert content.job_id.startswith(
        "job_ad_wew_"
    ), "Job ID should start with job_ad_wew_"
    assert (
        len(content.job_id) == 19
    ), "Job ID should be 19 characters (job_ad_src_hash format)"
    assert (
        content.job_id.count("_") == 3
    ), "Job ID should contain three underscores (job_ad_src_hash)"

    # Print full model for inspection
    logger.info("Full extracted job details:")
    logger.info("------------------------")
    logger.info(f"Job ID: {content.job_id}")
    logger.info(f"Company Name: {content.company.company_name}")
    logger.info(f"Company Website: {content.company.website_url}")
    logger.info(f"Job Title: {content.title}")
    logger.info(f"Location Type: {content.location_type.type}")
    logger.info(f"Posted Date: {content.posted_date}")
    logger.info(f"URL: {content.url}")
    logger.info("Description:")
    logger.info(f"{content.description[:200]}...")  # First 200 chars of description
    logger.info("------------------------")


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
