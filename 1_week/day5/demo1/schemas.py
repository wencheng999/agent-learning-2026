from typing import Literal
from pydantic import BaseModel,Field

class CalculatorInput(BaseModel):
    a:float
    b:float
    operation:Literal[
        "add",
        "subtract",
        "multiply",
        "divide"
    ]

class ToolDecision(BaseModel):
    tool:Literal[
        "calculator"
    ]
    arguments:dict

