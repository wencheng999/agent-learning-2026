from state import AgentState
from llm_client import LLMClient
from agent_config import LLMConfig
from context_manager import ContextManager
import asyncio

async def main():
    config = LLMConfig()
    client = LLMClient(api_key=config.api_key,
                       base_url=config.base_url,
                       model=config.model
                       )
    state =AgentState(
        constraints={
            "language": "Chinese",
            "style": "beginner-friendly"
        }
    )
    manager = ContextManager()
    while True:
        current_query=input(
            "User: "
        )
        if current_query == "exit":
            break
        context=manager.build_context(
            state=state,
            current_query=current_query,
            recent_n=6
        )
        answer=await client.chat(context)
        if answer is None:
            print("Assistant:请求失败")
            continue
        print(
            f"Assistant: {answer}"
        )
        state.message.append({
            "role":"user",
            "content":current_query
        })
        state.message.append({
            "role":"assistant",
            "content":answer
        })
        await manager.summarize_history(client=client,
                                        state=state,
                                        recent_n=6,
                                        max_messages=10)

asyncio.run(main())