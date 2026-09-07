from pydantic import BaseModel,Field
import httpx
import asyncio
from typing import Literal
from pydantic import ValidationError

class SearchInput(BaseModel):
    query: str=Field(
        min_length=1,
    )

class ToolResult(BaseModel):
    success: bool
    source: str
    data:dict|list|str|None= None
    error: str|None=None

async def search_web(client: httpx.AsyncClient,query:str)->ToolResult:
    try:
        response=await client.get(url="http://httpbin.org/get",
                                  params={"query":query,
                                          "source":"web"},
                                  timeout=10)
        response.raise_for_status()
        return ToolResult(success=True,
                          source="web",
                          data=response.json(),
                          error=None)
    except httpx.HTTPError as e:
        return ToolResult(success=False,
                          source="web",
                          data=None,
                          error=str(e))


async def search_rag(client: httpx.AsyncClient,query:str)->ToolResult:
    try:
        response=await client.get(url="http://httpbin.org/get",
                            params={"query":query,
                                    "source":"rag"},
                            timeout=10)
        response.raise_for_status()
        return ToolResult(success=True,
                          source="rag",
                          data=response.json(),
                          error=None)
    except httpx.HTTPError as e:
        return ToolResult(success=False,
                          source="rag",
                          data=None,
                          error=str(e))


TOOL_REGISTRY={
    "search_web":{
        "function":search_web,
        "input_model":SearchInput,
    },
    "search_rag":{
        "function":search_rag,
        "input_model":SearchInput,
    }
}


class ToolCall(BaseModel):
    tool:Literal["search_web","search_rag"]
    arguments:dict

async def execute_tool(client: httpx.AsyncClient,raw_tool_call: dict)->ToolResult:
    try:
        tool_call = ToolCall.model_validate(raw_tool_call)
        tool_info = TOOL_REGISTRY[tool_call.tool]
        tool_func = tool_info["function"]
        input_model = tool_info["input_model"]
        args = input_model.model_validate(tool_call.arguments)
        result = await tool_func(client=client,
                                 **args.model_dump())
        return result
    except ValidationError as e:
        return ToolResult(success=False,
                          source="validation_error",
                          data=None,
                          error=str(e))
    except Exception as e:
        return ToolResult(success=False,
                          source="executor_error",
                          data=None,
                          error=str(e))


tool_calls = [
    {
        "tool": "search_web",
        "arguments": {
            "query": "Agent"
        }
    },

    {
        "tool": "search_rag",
        "arguments": {
            "query": "RAG"
        }
    }
]

async def main():

    async with httpx.AsyncClient() as client:

        results = await asyncio.gather(
            *[
                execute_tool(
                    client,
                    tool_call
                )
                for tool_call in tool_calls
            ]
        )

        for result in results:
            print(result)


asyncio.run(main())
