from state import AgentState
from llm_client import LLMClient

class ContextManager:
    def build_context(self,
                      state: AgentState,
                      current_query:str,
                      recent_n:int=6)->list[dict]:
        context = [{
            "role": "system",
            "content": (
                "你是一名AI Agent课程老师。"
                "请使用准确、通俗的中文回答用户问题。"
            )
        }]
        if state.constraints:
            context.append({
                "role": "system",
                "content": (
                    "[CONSTRAINTS]\n"
                    +str(state.constraints)
                )
            })
        if state.conversation_summary:
            context.append({
                "role": "system",
                "content": (
                    "[CONVERSATION SUMMARY]\n"
                    +state.conversation_summary
                )
            })
        recent_messages=(
            state.message[-recent_n:]
        )
        context.extend(recent_messages)
        context.append({
            "role": "user",
            "content": current_query
        })
        return context

    async def summarize_history(self,
                          client: LLMClient,
                          state: AgentState,
                          recent_n:int=6,
                          max_messages:int=10)->None:
        if len(state.message)>max_messages:
            return
        old_messages=state.message[:-recent_n]
        summary_messages = [
            {
                "role": "system",
                "content": (
                    "你负责维护一份简洁准确的对话摘要。"
                    "请保留用户长期目标、重要事实、"
                    "关键决定和未完成任务。"
                    "删除寒暄、重复信息和无关细节。"
                )
            },
            {
                "role": "user",
                "content": f"""
        [OLD SUMMARY]
        {state.conversation_summary}

        [NEW HISTORY]
        {old_messages}
        """
            }
        ]
        summary=await client.chat(summary_messages)
        if summary is None:
            return
        state.conversation_summary=(summary)
        state.message=(state.message[-recent_n:])

