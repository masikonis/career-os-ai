from langchain_community.document_loaders import WebBaseLoader

from src.logger import get_logger

logger = get_logger(__name__)


class JobAdIngestor:
    """Agent that ingests raw content from a job advertisement."""

    def __init__(self):
        logger.info("JobAdIngestor initialized.")

    def ingest_content(self, job_ad_url: str) -> str:
        """Ingest the raw content from a job advertisement URL."""
        try:
            logger.info(f"Ingesting job ad from URL: {job_ad_url}")
            loader = WebBaseLoader(
                web_paths=[job_ad_url], requests_kwargs={"timeout": 10}
            )
            documents = loader.load()
            if documents:
                job_content = documents[0].page_content.strip()
                logger.info("Completed ingestion of job advertisement content.")
                return job_content
            else:
                logger.warning("No content found at the provided URL.")
                return ""
        except Exception as e:
            logger.error(f"Error ingesting job ad content: {str(e)}")
            raise
