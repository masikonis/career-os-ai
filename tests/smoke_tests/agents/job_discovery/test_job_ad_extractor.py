from datetime import datetime

from src.agents.job_discovery.job_ad_extractor import JobAdExtractor
from src.logger import get_logger
from src.models.company.company import Company
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
    assert content_dict["title"], "Job title should not be empty"
    assert content_dict["description"], "Job description should not be empty"
    assert content_dict["url"], "URL should not be empty"

    # Check equity offering field
    assert "offers_equity" in content_dict, "Equity offering field should be present"
    assert isinstance(
        content.offers_equity, bool
    ), "Equity offering should be a boolean"
    logger.info(f"Job offers equity: {content.offers_equity}")

    # Check summary
    assert "summary" in content_dict, "Summary field should be present"
    if content.summary:
        assert isinstance(content.summary, str), "Summary should be a string"
        assert len(content.summary) > 0, "Summary should not be empty"
        logger.info("Job Summary:")
        logger.info(content.summary)

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


def test_summary_generation():
    """Test job summary generation."""
    extractor = JobAdExtractor()

    # Create a sample job
    job = Job(
        company=Company.from_basic_info(company_name="Test Company"),
        title="Software Engineer",
        description="""We are looking for a skilled software engineer to join our team. 
        Responsibilities include developing web applications, writing clean code, and collaborating with cross-functional teams. 
        Required skills: Python, JavaScript, and experience with React.""",
        url="https://example.com/job",
        location_type=JobLocation(type="Remote"),
    )

    # Generate summary
    summary = extractor._generate_summary(job)

    # Basic validation
    assert summary is None or isinstance(
        summary, str
    ), "Summary should be a string or None"
    if summary:
        assert len(summary) > 0, "Summary should not be empty"
        assert (
            "developing web applications" in summary
        ), "Summary should include key responsibilities"
        assert "Python" in summary, "Summary should include Python"
        assert "JavaScript" in summary, "Summary should include JavaScript"
        assert "Test Company" not in summary, "Summary should exclude company name"
        assert "Remote" not in summary, "Summary should exclude location type"
        assert "Software Engineer" not in summary, "Summary should exclude job title"

    logger.info("Summary generation test passed")


def test_equity_detection():
    """Test equity offering detection with sample descriptions."""
    extractor = JobAdExtractor()

    # Test job with equity
    equity_description = """
    We offer competitive compensation including:
    - Salary range: $120k-$150k
    - Equity package
    - 401(k) matching
    """
    job_with_equity = Job(
        company=Company.from_basic_info(company_name="Test Company"),
        title="Software Engineer",
        description=equity_description,
        url="https://example.com/job",
        location_type=JobLocation(type="Remote"),
    )
    assert extractor._determine_equity_offering(
        equity_description
    ), "Should detect equity offering"

    # Test job without equity
    no_equity_description = """
    We offer:
    - Competitive salary
    - Health insurance
    - 401(k) matching
    """
    job_without_equity = Job(
        company=Company.from_basic_info(company_name="Test Company"),
        title="Software Engineer",
        description=no_equity_description,
        url="https://example.com/job",
        location_type=JobLocation(type="Remote"),
    )
    assert not extractor._determine_equity_offering(
        no_equity_description
    ), "Should not detect equity offering"

    logger.info("Equity detection tests passed")
