from pydantic import BaseModel,Field

class AgentState(BaseModel):
    message:list[dict]=Field(
        default_factory=list
    )
    conversation_summary:str=""
    constraints:dict=Field(
        default_factory=dict
    )
