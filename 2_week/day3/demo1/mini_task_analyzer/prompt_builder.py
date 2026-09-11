import json
from schemas import TaskAnalysis

class PromptBuilder:
    def build_task_analyzer_messages(self,
                                     current_query:str)->list[dict]:
        schema = (TaskAnalysis.model_json_schema())
        schema_text=json.dumps(schema,ensure_ascii=False,indent=2)
        system_prompt = f"""
        [ROLE]
        你是一个任务分析器。

        [TASK]
        分析用户提出的请求。
        不要直接回答用户问题本身。

        [DECISION RULES]
        1. intent表示用户的主要任务意图。
        2. difficulty只能是easy、medium、hard。
        3. need_search表示完成任务是否需要外部最新信息。
        4. need_planning表示任务是否需要拆成多个子任务。

        [CONSTRAINTS]
        1. 必须严格符合给定Schema。
        2. 只输出JSON。
        3. 不要输出Markdown代码块。
        4. 不要输出额外解释。

        [OUTPUT SCHEMA]
        {schema_text}
        """
        return [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": current_query
            }
        ]
    def build_repair_messages(self,
                              raw_output:str,
                              error_message:str)->list[dict]:
        schema=(TaskAnalysis.model_json_schema())
        schema_text=json.dumps(schema,ensure_ascii=False,indent=2)
        repair_prompt = f"""
        [OUTPUT SCHEMA]
        {schema_text}

        [INVALID OUTPUT]
        {raw_output}

        [VALIDATION ERROR]
        {error_message}

        [TASK]
        请修复上面的错误输出。

        [CONSTRAINTS]
        1. 必须严格符合Schema。
        2. 只输出修复后的JSON。
        3. 不要解释。
        4. 不要使用Markdown代码块。
        """

        return [
            {
                "role": "system",
                "content": (
                    "你负责修复无效的结构化输出。"
                )
            },
            {
                "role": "user",
                "content": repair_prompt
            }
        ]
