这 5 道题整体已经掌握得比较稳了，尤其是第 2、4、5 题，说明你已经理解了 **Context Window 管理不是简单截断，而是在“保留关键信息”和“控制上下文规模”之间做平衡**。

有一个地方需要修正：你在练习 3 里说“这样能够让 LLM 持久保存理解这些重要信息”。更准确应该是：

Structured State 是 Agent 程序持久、精确地保存信息，不是 LLM 自己保存\boxed{\text{Structured State 是 Agent 程序持久、精确地保存信息，不是 LLM 自己保存}}

例如：

```python
state.constraints = {
    "max_top_k": 20
}
```

真正记住 `20` 的是 Python 程序。下一次调用 LLM 时，`ContextManager` 再把这个信息提供给模型。LLM 本身并不会因为上一轮看到过它，就自动永久记住。

所以可以记成：

```text
Summary
→ 适合保存“语义性的历史概要”

Structured State
→ 适合保存“必须精确、不允许丢失的数据”
```

到这里第二节通过。

------

# Week 1 · Day 2 第三节

# Mini Context Agent 实战

今天最后我们把：

```text
AgentState
+
ContextManager
+
LLMClient
+
main.py
```

真正串成一个能运行的小项目。

这次我们的目标非常明确：

> 做一个能够多轮对话，并且历史过长时自动压缩旧历史的 LLM Chatbot。

最终流程：

```text
用户输入
   ↓
ContextManager
   ↓
System + Constraints
+ Summary
+ Recent Messages
+ Current Query
   ↓
LLMClient
   ↓
LLM Answer
   ↓
更新 state.messages
   ↓
历史过长？
   ↓
是
   ↓
LLM总结旧历史
   ↓
更新 conversation_summary
   ↓
只保留最近消息
```

------

# 一、项目结构

我们先按照最简单的工程结构：

```text
mini_context_agent/
│
├── .env
├── agent_config.py
├── llm_client.py
├── state.py
├── context_manager.py
└── main.py
```

你之前的：

```text
agent_config.py
llm_client.py
```

可以继续用。

所以今天主要新增：

```text
state.py
context_manager.py
```

然后修改：

```text
main.py
```

------

# 二、第一步：`state.py`

写：

```python
from pydantic import BaseModel, Field


class AgentState(BaseModel):

    messages: list[dict] = Field(
        default_factory=list
    )

    conversation_summary: str = ""

    constraints: dict = Field(
        default_factory=dict
    )
```

现在：

```python
state = AgentState()
```

相当于：

```python
{
    "messages": [],
    "conversation_summary": "",
    "constraints": {}
}
```

------

# 三、这三个字段的职责

`messages`：

```python
state.messages
```

保存最近的真实对话，例如：

```python
[
    {
        "role": "user",
        "content": "什么是Agent？"
    },
    {
        "role": "assistant",
        "content": "Agent是一种..."
    }
]
```

`conversation_summary`：

```python
state.conversation_summary
```

保存更旧历史的压缩版本。

例如：

```text
用户正在学习Agent开发，
目前已经学习HTTP、Pydantic、async和LLM API。
```

`constraints`：

```python
state.constraints
```

保存不希望被 Summary 弄丢的精确规则。

例如：

```python
{
    "language": "Chinese",
    "answer_style": "beginner-friendly"
}
```

------

# 四、第二步：创建 `context_manager.py`

先写导入：

```python
from state import AgentState
from llm_client import LLMClient
```

然后：

```python
class ContextManager:
```

我们今天让它有两个核心能力：

```text
build_context()
→ 给当前 LLM 构造上下文

summarize_history()
→ 历史太长时压缩
```

------

# 五、先写 `build_context()`

```python
def build_context(
    self,
    state: AgentState,
    current_query: str,
    recent_n: int = 6
) -> list[dict]:

    context = [
        {
            "role": "system",
            "content": (
                "你是一名AI Agent课程老师。"
                "请使用准确、通俗的中文回答用户问题。"
            )
        }
    ]
```

第一步永远放 System Prompt。

------

# 六、加入 Constraints

```python
    if state.constraints:

        context.append({
            "role": "system",
            "content": (
                "[CONSTRAINTS]\n"
                + str(state.constraints)
            )
        })
```

例如 State：

```python
{
    "language": "Chinese",
    "style": "simple"
}
```

LLM 能看到：

```text
[CONSTRAINTS]
{'language': 'Chinese', 'style': 'simple'}
```

------

# 七、加入旧历史 Summary

```python
    if state.conversation_summary:

        context.append({
            "role": "system",
            "content": (
                "[CONVERSATION SUMMARY]\n"
                + state.conversation_summary
            )
        })
```

所以：

```text
以前聊过很多内容
↓
被压缩
↓
conversation_summary
↓
重新作为Context提供给LLM
```

------

# 八、加入最近消息

```python
    recent_messages = (
        state.messages[-recent_n:]
    )

    context.extend(
        recent_messages
    )
```

假设：

```python
recent_n = 6
```

那么最多保留：

```text
最近6条原始消息
```

这里注意是：

```text
6条Message
```

不一定是：

```text
6轮对话
```

因为一轮通常有：

```text
1条user
+
1条assistant
```

所以 6 条 message 大概等于 3 轮。

------

# 九、加入 Current Query

```python
    context.append({
        "role": "user",
        "content": current_query
    })
```

最后：

```python
    return context
```

于是完整函数：

```python
def build_context(
    self,
    state: AgentState,
    current_query: str,
    recent_n: int = 6
) -> list[dict]:

    context = [
        {
            "role": "system",
            "content": (
                "你是一名AI Agent课程老师。"
                "请使用准确、通俗的中文回答用户问题。"
            )
        }
    ]

    if state.constraints:
        context.append({
            "role": "system",
            "content": (
                "[CONSTRAINTS]\n"
                + str(state.constraints)
            )
        })

    if state.conversation_summary:
        context.append({
            "role": "system",
            "content": (
                "[CONVERSATION SUMMARY]\n"
                + state.conversation_summary
            )
        })

    recent_messages = (
        state.messages[-recent_n:]
    )

    context.extend(
        recent_messages
    )

    context.append({
        "role": "user",
        "content": current_query
    })

    return context
```

------

# 十、现在写最重要的 `summarize_history()`

定义：

```python
async def summarize_history(
    self,
    client: LLMClient,
    state: AgentState,
    recent_n: int = 6,
    max_messages: int = 10
) -> None:
```

这里两个参数要区分。

```python
recent_n = 6
```

表示：

> 压缩后还保留多少条最近原始消息。

而：

```python
max_messages = 10
```

表示：

> 历史超过多少条以后触发总结。

------

# 十一、先判断要不要 Summary

```python
    if len(state.messages) <= max_messages:
        return
```

假设：

```text
message数量 = 8
max_messages = 10
```

那么：

```text
不用总结
直接返回
```

如果：

```text
message数量 = 12
```

则继续。

------

# 十二、找出准备压缩的历史

```python
    old_messages = (
        state.messages[:-recent_n]
    )
```

假设：

```text
总共12条
recent_n = 6
```

那么：

```text
old_messages
→ 前6条

recent messages
→ 后6条
```

------

# 十三、把旧 Summary 也一起给 LLM

```python
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
```

这样：

```text
之前已经有的Summary
+
本次准备删除的旧历史
↓
LLM
↓
生成新的完整Summary
```

------

# 十四、调用 LLM

```python
    summary = await client.chat(
        summary_messages
    )
```

这就是为什么这个函数必须：

```python
async def
```

因为里面出现了：

```python
await
```

------

# 十五、如果 Summary 失败怎么办？

```python
    if summary is None:
        return
```

这个设计非常重要。

如果 Summary LLM API 挂了：

```text
不要删除旧消息
```

否则：

```text
Summary失败
+
你又把原始消息删掉
↓
历史信息永久丢失
```

所以正确顺序必须是：

```text
先成功生成Summary
↓
再删除旧Messages
```

这属于一个很重要的工程原则：

先确认新状态成功，再破坏旧状态\boxed{\text{先确认新状态成功，再破坏旧状态}}

------

# 十六、更新 Summary

```python
    state.conversation_summary = (
        summary
    )
```

然后：

```python
    state.messages = (
        state.messages[-recent_n:]
    )
```

所以：

```text
旧历史
→ Summary

最近历史
→ Raw Messages
```

------

# 十七、完整 `context_manager.py`

最终：

```python
from state import AgentState
from llm_client import LLMClient


class ContextManager:

    def build_context(
        self,
        state: AgentState,
        current_query: str,
        recent_n: int = 6
    ) -> list[dict]:

        context = [
            {
                "role": "system",
                "content": (
                    "你是一名AI Agent课程老师。"
                    "请使用准确、通俗的中文回答用户问题。"
                )
            }
        ]

        if state.constraints:
            context.append({
                "role": "system",
                "content": (
                    "[CONSTRAINTS]\n"
                    + str(state.constraints)
                )
            })

        if state.conversation_summary:
            context.append({
                {
                    "role": "system",
                    "content": (
                        "[CONVERSATION SUMMARY]\n"
                        + state.conversation_summary
                    )
                }
            })

        recent_messages = (
            state.messages[-recent_n:]
        )

        context.extend(
            recent_messages
        )

        context.append({
            "role": "user",
            "content": current_query
        })

        return context


    async def summarize_history(
        self,
        client: LLMClient,
        state: AgentState,
        recent_n: int = 6,
        max_messages: int = 10
    ) -> None:

        if len(state.messages) <= max_messages:
            return

        old_messages = (
            state.messages[:-recent_n]
        )

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

        summary = await client.chat(
            summary_messages
        )

        if summary is None:
            return

        state.conversation_summary = (
            summary
        )

        state.messages = (
            state.messages[-recent_n:]
        )
```

不过注意，我上面在 `conversation_summary` 那一小段故意保留了一个你很容易犯的括号错误，我们现在来找一下。

------

# 十八、这里有一个错误

这一段：

```python
context.append({
    {
        "role": "system",
        "content": (...)
    }
})
```

是错的。

因为变成了：

```text
{
    {
        dict
    }
}
```

外面那个 `{}` 会被 Python 理解成：

```text
set
```

而 dict 不能作为 set 元素。

正确应该是：

```python
context.append({
    "role": "system",
    "content": (
        "[CONVERSATION SUMMARY]\n"
        + state.conversation_summary
    )
})
```

也就是：

```text
append(
    一个dict
)
```

不是：

```text
append(
    一个装着dict的{}
)
```

我专门把这个坑放出来，是因为以后复制复杂 JSON / dict 时非常容易多打一层 `{}`。

------

# 十九、下面写 `main.py`

```python
import asyncio

from agent_config import LLMConfig
from llm_client import LLMClient
from state import AgentState
from context_manager import ContextManager
```

然后：

```python
async def main():

    config = LLMConfig()

    client = LLMClient(
        api_key=config.api_key,
        base_url=config.base_url,
        model=config.model
    )

    state = AgentState(
        constraints={
            "language": "Chinese",
            "style": "beginner-friendly"
        }
    )

    manager = ContextManager()
```

现在：

```text
LLMClient
→ 管 API

AgentState
→ 管状态

ContextManager
→ 管 Context

main
→ 管流程
```

------

# 二十、创建聊天循环

```python
    while True:

        current_query = input(
            "User: "
        )

        if current_query == "exit":
            break
```

然后：

```python
        context = manager.build_context(
            state=state,
            current_query=current_query,
            recent_n=6
        )
```

------

# 二十一、发送给 LLM

```python
        answer = await client.chat(
            context
        )
```

失败：

```python
        if answer is None:
            print(
                "Assistant: 请求失败"
            )
            continue
```

成功：

```python
        print(
            f"Assistant: {answer}"
        )
```

------

# 二十二、更新 State

```python
        state.messages.append({
            "role": "user",
            "content": current_query
        })

        state.messages.append({
            "role": "assistant",
            "content": answer
        })
```

现在本轮正式进入历史。

------

# 二十三、检查是否需要 Summary

```python
        await manager.summarize_history(
            client=client,
            state=state,
            recent_n=6,
            max_messages=10
        )
```

于是：

```text
每次回答完成
↓
检查历史长度
↓
短
→ 什么都不做

长
→ 总结
→ 更新Summary
→ 删除部分旧History
```

------

# 二十四、完整 `main.py`

```python
import asyncio

from agent_config import LLMConfig
from llm_client import LLMClient
from state import AgentState
from context_manager import ContextManager


async def main():

    config = LLMConfig()

    client = LLMClient(
        api_key=config.api_key,
        base_url=config.base_url,
        model=config.model
    )

    state = AgentState(
        constraints={
            "language": "Chinese",
            "style": "beginner-friendly"
        }
    )

    manager = ContextManager()

    while True:

        current_query = input(
            "User: "
        )

        if current_query == "exit":
            break

        context = manager.build_context(
            state=state,
            current_query=current_query,
            recent_n=6
        )

        answer = await client.chat(
            context
        )

        if answer is None:
            print(
                "Assistant: 请求失败"
            )
            continue

        print(
            f"Assistant: {answer}"
        )

        state.messages.append({
            "role": "user",
            "content": current_query
        })

        state.messages.append({
            "role": "assistant",
            "content": answer
        })

        await manager.summarize_history(
            client=client,
            state=state,
            recent_n=6,
            max_messages=10
        )


asyncio.run(main())
```

------

# 二十五、我们模拟运行一下

第一轮：

```text
User:
我叫Tom
```

State：

```text
messages:
user: 我叫Tom
assistant: 你好Tom

summary:
""
```

第二轮：

```text
User:
我正在学习Agent
```

继续保存。

等到超过：

```text
10条messages
```

比如现在：

```text
12条
```

程序自动：

```text
前6条
↓
交给LLM

+
旧Summary
↓
生成新Summary
```

例如：

```text
用户叫Tom，
正在学习AI Agent，
之前讨论过HTTP和Pydantic。
```

然后：

```text
state.messages
```

只留下：

```text
最近6条
```

于是 State：

```text
conversation_summary:
用户叫Tom，正在学习AI Agent...

messages:
最近6条原始历史
```

下一轮 Context：

```text
System Prompt
↓
Constraints
↓
Conversation Summary
↓
最近6条
↓
Current Query
```

这就是一个真正可以工作的：

Mini Context Agent\boxed{\text{Mini Context Agent}}

------

# 二十六、但是这个版本还不算成熟

因为现在还有三个明显问题。

第一，我们按：

```python
len(messages)
```

控制上下文。

但真正应该更关心：

```text
Token数量
```

第二，Summary 仍然可能：

```text
Summary Drift
```

第三，目前只有：

```text
Conversation Context
```

还没有：

```text
RAG Evidence
Tool Result
Memory Retrieval
```

不过这些恰恰就是我们后面逐步升级的方向。

------

# 今天这一节最重要的不是把代码背下来

你真正要理解的是这个循环：

```text
                ┌────────────────┐
                │   AgentState   │
                └───────┬────────┘
                        │
                        ↓
                ContextManager
                        │
                        ↓
                    Context
                        │
                        ↓
                       LLM
                        │
                        ↓
                     Answer
                        │
                        ↓
                Update Messages
                        │
                        ↓
                History太长？
                   /        \
                 否          是
                 │           ↓
                 │       Summarize
                 │           ↓
                 └────→ Update State
                              │
                              ↓
                           下一轮
```

这张逻辑图比所有代码都重要。

------

# 今天第三节最后只做 4 道实战检查

1. 为什么一定要先：

```python
summary = await client.chat(...)
```

确认 `summary` 成功以后，才能：

```python
state.messages = state.messages[-recent_n:]
```

？

1. `recent_n=6` 和 `max_messages=10` 分别是什么意思？它们有什么区别？
2. 假设现在：

```text
state.messages = 12条
conversation_summary = "旧Summary"
recent_n = 6
max_messages = 10
```

调用 `summarize_history()` 后，程序大概会经历什么过程？

1. 用自己的话解释整个 Mini Context Agent：

```text
User
→ ContextManager
→ Context
→ LLM
→ Answer
→ Update State
→ Summarize History
→ 下一轮
```

这 4 道做完，**Week 1 · Day 2 今天的内容就可以正式收尾**。