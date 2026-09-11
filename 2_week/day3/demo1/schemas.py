from typing import Literal
from pydantic import BaseModel

class TaskAnalysis(BaseModel):
    intent:str
    difficulty:Literal[
        'easy',
        'medium',
        'hard'
    ]
    need_search:bool
    need_planning:bool

