from typing import Literal

from pydantic import BaseModel, ValidationError
from day5.demo1.agent_config import LLMConfig
from day5.demo1.llm_client import LLMClient
import json

class ToolDecision(BaseModel):
    tool: Literal[
        "search",
        "calculator"
    ]

    arguments: dict
async def get_tool_decision(
    client: LLMClient,
    user_input: str
) -> ToolDecision | None:

    schema = (
        ToolDecision.model_json_schema()
    )

    schema_text = json.dumps(
        schema,
        ensure_ascii=False,
        indent=2
    )

    messages = [
        {
            "role": "system",
            "content": f"""
你负责选择合适的工具。

只能返回 JSON。
不要添加任何解释文字。
不要使用 Markdown 代码块。

输出必须符合下面的 Schema：

{schema_text}
"""
        },
        {
            "role": "user",
            "content": user_input
        }
    ]

    answer = await client.chat(
        messages
    )

    if answer is None:
        return None

    try:
        return ToolDecision.model_validate_json(
            answer
        )

    except ValidationError as e:
        print(
            "结构化输出验证失败："
        )
        print(e)

        return None