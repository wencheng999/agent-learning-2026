
import asyncio

from agent_config import LLMConfig
from llm_client import LLMClient
from state import AgentState
from prompt_builder import PromptBuilder
from task_analyzer import TaskAnalyzer

async def main():

    config = LLMConfig()

    client = LLMClient(
        api_key=config.api_key,
        base_url=config.base_url,
        model=config.model
    )

    state = AgentState(
        constraints={
            "language": "Chinese"
        }
    )

    prompt_builder = PromptBuilder()

    analyzer = TaskAnalyzer(
        client=client,
        prompt_builder=prompt_builder
    )
    current_query = input(
        "User: "
    )
    analysis = await analyzer.analyze(
        current_query=current_query,
        max_retries=2
    )
    if analysis is None:

        print(
            "任务分析失败"
        )

        return
    state.task_analysis = analysis
    print(
        state.task_analysis
    )
    if analysis.need_planning:
        print(
            "下一步：先执行任务规划"
        )

    if analysis.need_search:
        print(
            "下一步：需要调用搜索工具"
        )
    if (
            not analysis.need_search
            and not analysis.need_planning
    ):
        print(
            "下一步：可以直接回答用户"
        )

asyncio.run(main())

