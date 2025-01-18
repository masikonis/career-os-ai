from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from src.config import load_config
from src.flows.research_company import CompanyResearchFlow
from src.logger import get_logger
from src.models.company.company_info import CompanyInfo

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
def run_research_flow(company_name: str, website_url: str):
    """Function to run the Prefect flow."""
    try:
        logger.info(
            f"Starting research flow for company: {company_name}, website: {website_url}"
        )
        research_flow = CompanyResearchFlow(
            company_name=company_name, website_url=website_url
        )
        result = research_flow.research_company()
        logger.info(f"Flow completed: {result}")
    except Exception as e:
        logger.error(f"Error running research flow: {e}")


@app.post("/flows/research-company")
def trigger_research_company_flow(
    company_info: CompanyInfo, background_tasks: BackgroundTasks
):
    try:
        background_tasks.add_task(
            run_research_flow, company_info.company_name, company_info.website_url
        )
        logger.info(f"Research task initiated for company: {company_info.company_name}")
        return {"message": "Research has been initiated."}
    except Exception as e:
        logger.error(f"Failed to initiate research task: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting FastAPI server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
