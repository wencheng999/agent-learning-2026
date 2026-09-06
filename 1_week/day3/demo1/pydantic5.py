
from pydantic import BaseModel

class Paper(BaseModel):
    title: str
    year: int

class SearchResult(BaseModel):
    query:str
    papers: list[Paper]
paper1=Paper(title="Agent Paper A",year=2026)
paper2=Paper(title="Agent Paper B",year=2025)
print(paper1.title)
print(paper1.year)
print(paper2.title)
print(paper2.year)
search1=SearchResult(query="打印论文",
                     papers=[
                         paper1,paper2
                     ])

print(search1.papers[0].title)
print(search1.papers[1].year)