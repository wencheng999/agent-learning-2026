from pydantic import BaseModel
from pydantic import Field

class SearchInput(BaseModel):
    query:str=Field(
        min_length=1,
    )
    top_k:int=Field(
        default=5,
        ge=1,
        le=10,
    )
    language:str|None=Field(
        default=None,
    )