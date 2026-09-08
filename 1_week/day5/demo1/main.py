import asyncio
import json

from pydantic import ValidationError

from agent_config import LLMConfig
from llm_client import LLMClient
from schemas import ToolDecision
from tools import TOOL_REGISTRY


async def main():
    config = LLMConfig()
    client=LLMClient(api_key=config.api_key,
                     base_url=config.base_url,
                     model=config.model)
    decision_schema=(ToolDecision.model_json_schema())
    print(type(decision_schema))
    schema_text=json.dumps(decision_schema)
    print(type(schema_text))
    calculator_schema=(TOOL_REGISTRY["calculator"]["input_model"].model_json_schema())

    system_prompt = f"""
    你是一个简单的Agent决策器。

    用户提出问题以后，
    你需要判断应该调用哪个工具。

    当前只有一个工具：

    calculator：
    用于加减乘除计算。

    calculator的参数Schema如下：

    {json.dumps(
        calculator_schema,
        ensure_ascii=False,
        indent=2
    )}

    你的最终输出必须符合下面的ToolDecision Schema：

    {schema_text}

    要求：
    1. 只输出JSON。
    2. 不要输出Markdown代码块。
    3. 不要输出任何解释文字。
    """

    user_input=(
        "帮我计算12.5乘以8，"
        "并简单解释结果。"
    )
    decision_messages = [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": user_input
        }
    ]
    decision_text=await client.chat(messages=decision_messages)
    try:
        decision=(ToolDecision.model_validate_json(decision_text))
        print(decision)
    except ValidationError as e:
        print("LLM输出格式错误")
        print(e)
        return
    print(decision.tool)
    print(decision.arguments)
    tool_info=TOOL_REGISTRY[decision.tool]
    tool_func=tool_info["function"]
    input_model=tool_info["input_model"]
    try:
        tool_args = input_model.model_validate(decision.arguments)
    except ValidationError as e:
        print("Tool参数验证失败")
        print(e)
        return
    try:
        tool_result = tool_func(**tool_args.model_dump())
    except ValidationError as e:
        print(f"Tool执行失败{e}")
        return
    print(f"Tool执行结果{tool_result}")
    print()

    final_messages = [
        {
            "role": "system",
            "content": (
                "你是一名AI助手。"
                "请根据工具执行结果回答用户，"
                "不要编造工具没有提供的信息。"
            )
        },
        {
            "role": "user",
            "content": user_input
        },
        {
            "role": "assistant",
            "content": (
                f"我决定调用工具："
                f"{decision.tool}"
            )
        },
        {
            "role": "user",
            "content": (
                f"工具执行结果："
                f"{tool_result}"
            )
        }
    ]
    print("最终回答：")
    final_answer = await client.stream_chat(
        final_messages
    )
    # print(final_answer)


asyncio.run(main())
