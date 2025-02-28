from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from src.config import load_config
from src.logger import get_logger
from src.models.company.company import Company
from src.workflows.company_research import CompanyResearchWorkflow

app = FastAPI()
logger = get_logger(__name__)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return RedirectResponse(url="/static/favicon.ico")


@app.get("/")
async def read_root():
    return {"message": "Hello, world!"}


# Flow endpoints
def run_company_research_workflow(company_name: str, website_url: str):
    """Function to run the Prefect workflow."""
    try:
        logger.info(
            f"Starting company research workflow for company: {company_name}, website: {website_url}"
        )
        research_workflow = CompanyResearchWorkflow(
            company_name=company_name, website_url=website_url
        )
        result = research_workflow.company_research()
        logger.info(f"Workflow completed: {result}")
    except Exception as e:
        logger.error(f"Error running company research workflow: {e}")


@app.post("/workflows/company-research")
def trigger_company_research_workflow(
    company: Company, background_tasks: BackgroundTasks
):
    try:
        background_tasks.add_task(
            run_company_research_workflow, company.company_name, company.website_url
        )
        logger.info(f"Research task initiated for company: {company.company_name}")
        return {"message": "Research has been initiated."}
    except Exception as e:
        logger.error(f"Failed to initiate research task: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting FastAPI server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
