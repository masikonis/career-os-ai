from pydantic import BaseModel, Field


class BasicResponse(BaseModel):
    """Basic schema for structured responses used in testing."""

    response: str = Field(description="The answer to the user's question")
    follow_up_question: str = Field(description="A follow-up question for the user")
