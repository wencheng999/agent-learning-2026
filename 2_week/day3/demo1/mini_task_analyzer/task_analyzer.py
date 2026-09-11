from pydantic import ValidationError

from schemas import TaskAnalysis
from prompt_builder import PromptBuilder
from llm_client import LLMClient

class TaskAnalyzer:

    def __init__(
        self,
        client: LLMClient,
        prompt_builder: PromptBuilder
    ):
        self.client = client
        self.prompt_builder = prompt_builder

    async def analyze(self,
                      current_query:str,
                      max_retries:int=2)->TaskAnalysis|None:
        messages=(
            self.prompt_builder.build_task_analyzer_messages(
                current_query))
        raw_output=await self.client.chat(messages)
        if raw_output is None:
            return None
        for attempt in range(max_retries+1):
            try:
                analysis = (TaskAnalysis
                            .model_validate_json(
                    raw_output
                ))
                return analysis
            except ValidationError as e:
                print(f"第{attempt+1}次验证失败")
                if attempt == max_retries:
                    return None
                repair_messages=(self.prompt_builder
                                 .build_repair_messages(
                    raw_output=raw_output,
                    error_msg=str(e)
                ))
                raw_output=(
                    await self.client.chat(repair_messages)
                )
                if raw_output is None:
                    return None