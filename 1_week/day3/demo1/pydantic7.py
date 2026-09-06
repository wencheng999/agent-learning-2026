import json

from pydantic import BaseModel
from pydantic import Field
from pydantic import field_validator

class SearchInput(BaseModel):
    query: str
    top_k: int=5

schema=SearchInput.model_json_schema()
print(schema)
print(type(schema))
json_schema=json.dumps(schema,
                       ensure_ascii=False,
                       indent=2)
print(json_schema)
print(type(json_schema))