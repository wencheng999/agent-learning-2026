from demo1.llm_client import LLMClient
from state import AgentState

class ContextManager:
    def build_context(self,
                      state: AgentState,
                      current_query:str,
                      recent_n: int = 6
                      )->list[dict]:
        context = [{
            "role": "system",
            "content": (
                "你是一名AI Agent课程老师，"
                "请使用准确但通俗的方式回答。"
            )
        }]
        if state.constraints:
            context.append({
                "role":"system",
                "content":(
                    "[CONSTRAINTS]\n"
                     +str(state.constraints)
                )
            })
        if state.conversation_summary:
            context.append({
                "role":"system",
                "content":(
                    "[CONVERSATION SUMMARY]\n"
                    +str(state.conversation_summary)
                )
            })
        recent_messages = (
            state.messages[-recent_n:]
        )

        context.extend(
            recent_messages
        )
        context.append({
            "role":"user",
            "content":current_query
        })
        return context

    async def summarize_history(self,
                                client:LLMClient,
                                state:AgentState,
                                recent_n:int=6)->None:
        if len(state.messages) <= recent_n:
            return
        old_messages = state.messages[:-recent_n]
        if not old_messages:
            return
        summary_messages = [
            {
                "role": "system",
                "content": (
                    "请更新历史对话摘要。"
                    "保留用户长期目标、"
                    "重要事实、关键决定和未完成任务。"
                    "删除寒暄和重复内容。"
                )
            },
            {
                "role": "user",
                "content": f"""
        [OLD SUMMARY]
        {state.conversation_summary}

        [NEW OLD MESSAGES]
        {old_messages}
        """
            }
        ]
        summary=await client.chat(summary_messages)
        if summary is None:
            return
        state.conversation_summary = (summary)
        state.messages=(state.messages[-recent_n:])