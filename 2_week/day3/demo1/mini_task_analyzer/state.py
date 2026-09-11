from pydantic import BaseModel, Field

from schemas import TaskAnalysis


class AgentState(BaseModel):

    messages: list[dict] = Field(
        default_factory=list
    )

    conversation_summary: str = ""

    constraints: dict = Field(
        default_factory=dict
    )

    task_analysis: TaskAnalysis | None = None