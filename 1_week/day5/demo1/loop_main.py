import asyncio

from day5.demo1.agent_config import LLMConfig
from day5.demo1.llm_client import LLMClient

async def main():

    config = LLMConfig()

    client = LLMClient(
        api_key=config.api_key,
        base_url=config.base_url,
        model=config.model
    )

    messages = [
        {
            "role": "system",
            "content": "你是一名AI助手。"
        }
    ]

    while True:

        user_input = input("User: ")

        if user_input == "exit":
            break

        messages.append(
            {
                "role": "user",
                "content": user_input
            }
        )

        answer = await client.chat(
            messages
        )

        if answer is None:
            print("Assistant: 请求失败")
            continue

        print(
            f"Assistant: {answer}"
        )

        messages.append(
            {
                "role": "assistant",
                "content": answer
            }
        )


asyncio.run(main())



