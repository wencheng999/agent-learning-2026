from pydantic import BaseModel, Field


class AgentState(BaseModel):
    messages: list[dict] = Field(
        default_factory=list
    )

    conversation_summary: str = ""

    constraints: dict = Field(
        default_factory=dict
    )

    evidence: list[str] = Field(
        default_factory=list
    )

state = AgentState()

state.constraints = {
    "max_top_k": 20,
    "language": "Chinese"
}

state.conversation_summary = (
    "用户正在学习AI Agent开发，"
    "已经掌握HTTP、Pydantic、async/await、"
    "LLM API、Streaming和Structured Output，"
    "当前正在学习Context Engineering。"
)
state.messages = [
    {
        "role": "user",
        "content": "State和Context有什么区别？"
    },
    {
        "role": "assistant",
        "content": "State保存当前任务全部运行状态，Context是当前LLM真正看到的信息。"
    },
    {
        "role": "user",
        "content": "那ContextManager是做什么的？"
    },
    {
        "role": "assistant",
        "content": "它根据当前任务，从State等来源构造合适的Context。"
    },
    {
        "role": "user",
        "content": "那历史越来越长怎么办？"
    }
]

class ContextManager:

    def build_context(
        self,
        state: AgentState,
        current_query: str,
        recent_n: int = 4
    ) -> list[dict]:
        recent_messages = (
            state.messages[-recent_n:]
        )
        context = [
            {
                "role": "system",
                "content": (
                    "你是一名AI Agent课程老师，"
                    "请使用准确但通俗的中文回答。"
                )
            }
        ]
        if state.conversation_summary:
            context.append(
                {
                    "role": "system",
                    "content": (
                            "[CONVERSATION SUMMARY]\n"
                            + state.conversation_summary
                    )
                }
            )
        if state.constraints:
            context.append(
                {
                    "role": "system",
                    "content": (
                        "[CONSTRAINTS]\n"
                        f"{state.constraints}"
                    )
                }
            )
        context.extend(
            recent_messages
        )
        context.append(
            {
                "role": "user",
                "content": current_query
            }
        )
        return context

manager = ContextManager()

context = manager.build_context(
    state=state,
    current_query=(
        "请再简单解释一下Context Window。"
    ),
    recent_n=4
)
for message in context:
    print(
        message["role"],
        ":",
        message["content"]
    )
    print("-" * 30)
