from pydantic import BaseModel

class SearchInput(BaseModel):
    query: str
    top_k:int

search_input = SearchInput(query="agent", top_k=5)
print(search_input.query)
print(search_input.top_k)