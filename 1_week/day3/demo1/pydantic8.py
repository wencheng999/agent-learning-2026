from typing import Literal

from pydantic import BaseModel, Field, ValidationError


class SearchInput(BaseModel):
    query: str = Field(
        min_length=1,
        description="Query string for searching"
    )

    top_k: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Number of results to return"
    )


class CalculatorInput(BaseModel):
    a: float
    b: float


class ToolDecision(BaseModel):
    tool: Literal[
        "search",
        "calculator",
        "multiply"
    ]

    arguments: dict


def search_paper(
    query: str,
    top_k: int
) -> list[str]:

    return [
        f"{query} Paper {i}"
        for i in range(1, top_k + 1)
    ]


def calculator(
    a: float,
    b: float
) -> float:

    return a + b

def multiply(a: float, b: float) -> float:
    return a * b

TOOL_REGISTRY ={
    "search":{
        "function":search_paper,
        "input_model":SearchInput,
    },
    "calculator":{
        "function":calculator,
        "input_model":CalculatorInput,
    },
    "multiply":{
        "function":multiply,
        "input_model":CalculatorInput,
    }
}

def execute_tool(
    llm_output: dict
):
    try:
        decision = ToolDecision.model_validate(
            llm_output
        )
        tool_info=TOOL_REGISTRY[decision.tool]
        tool_func=tool_info["function"]
        input_model=tool_info["input_model"]
        args=input_model.model_validate(
            decision.arguments
        )
        result=tool_func(**args.model_dump())
        return result
    except ValidationError as e:
        print("Tool参数验证失败")
        print(e)



llm_output1 = {
    "tool": "search",
    "arguments": {
        "query": "Agent",
        "top_k": 3
    }
}

llm_output2 = {
    "tool": "calculator",
    "arguments": {
        "a": 10,
        "b": 20
    }
}
llm_output3 = {
    "tool": "multiply",
    "arguments": {
        "a": 4,
        "b": 5
    }
}


result1 = execute_tool(llm_output1)
result2 = execute_tool(llm_output2)
result3 = execute_tool(llm_output3)

print(result1)
print(result2)
print(result3)