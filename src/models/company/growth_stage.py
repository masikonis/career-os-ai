from enum import Enum

from pydantic import BaseModel


class GrowthStage(str, Enum):
    IDEA = "IDEA"
    PRE_SEED = "PRE_SEED"
    MVP = "MVP"
    SEED = "SEED"
    EARLY = "EARLY"
    SERIES_A = "SERIES_A"
    LATER = "LATER"


class CompanyGrowthStage(BaseModel):
    growth_stage: GrowthStage
    confidence: float  # 0.0 to 1.0
    reasoning: str
