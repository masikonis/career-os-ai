from prefect import flow

from src.agents.job_discovery.job_ads_scraper import JobAdsScraper
from src.logger import get_logger

logger = get_logger(__name__)


class JobDiscoveryWorkflow:
    def __init__(self):
        """
        Initialize the JobDiscoveryWorkflow.
        """
        self.scraper = JobAdsScraper()

    @flow(log_prints=True)
    def job_discovery(self) -> dict:
        """
        Prefect workflow to discover new job postings.
        """
        job_urls = self.scraper.scrape_job_urls()
        return {
            "message": f"Job discovery completed. Found {len(job_urls)} jobs.",
            "job_urls": job_urls,
        }

    def serve(
        self, name: str = "job-discovery-deployment", tags=None, interval: int = 86400
    ):
        """
        Deploy the workflow with the specified configuration.
        """
        if tags is None:
            tags = ["jobs"]

        self.job_discovery.serve(
            name=name,
            tags=tags,
            interval=interval,
        )


if __name__ == "__main__":
    discovery_workflow = JobDiscoveryWorkflow()
    discovery_workflow.serve()
