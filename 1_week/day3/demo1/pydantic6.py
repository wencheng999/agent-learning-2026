from pydantic import BaseModel
from pydantic import field_validator
from pydantic import Field
class SearchInput(BaseModel):
    query:str=Field(
        min_length=1,
    )
    @field_validator('query')
    @classmethod
    def valid_query(cls, value:str)->str:
        value=value.strip()
        if not value:
            raise ValueError("query 不能为空")
        return value


search_input = SearchInput.model_json_schema()
print(search_input)