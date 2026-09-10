好，今天第一节我们正式把昨天的理论接到你前面已经写过的 `LLMClient` 上。

这一节的目标不是一下子做“很聪明的 Agent”，而是先做出一个最小但完整的：

Context-aware Chatbot\boxed{\text{Context-aware Chatbot}}

也就是它不再由 `main.py` 手工维护一大坨 `messages`，而是形成：

```text
用户输入
   ↓
AgentState
   ↓
ContextManager
   ↓
本轮 messages
   ↓
LLMClient
   ↓
LLM
   ↓
answer
   ↓
Update AgentState
   ↓
下一轮
```

这条链如果你今天真正理解了，后面学 LangGraph 的 State 会轻松很多。

------

# 一、先回忆你以前的 Chatbot

你之前大概是这样写：

```python
messages = [
    {
        "role": "system",
        "content": "你是一名AI助手"
    }
]

while True:
    user_input = input("User: ")

    messages.append({
        "role": "user",
        "content": user_input
    })

    answer = await client.chat(messages)

    messages.append({
        "role": "assistant",
        "content": answer
    })
```

这个版本能运行。

但问题是：

```text
所有东西
↓
都塞进 messages
```

以后 Agent 再有：

```text
plan
evidence
constraints
tool_results
current_step
conversation_summary
```

就会越来越乱。

所以今天我们把：

```python
messages = [...]
```

升级成：

```python
state = AgentState(...)
```

------

# 二、今天先创建 `state.py`

我们先定义一个非常简单的状态模型：

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

现在只有三个字段。

为什么今天暂时不加：

```text
plan
tool_results
evidence
```

因为我们第一节只解决：

> **多轮聊天 + Context 管理。**

先把最小系统跑通，再一点一点加。

------

# 三、这个 AgentState 到底保存什么？

假设：

```python
state = AgentState()
```

刚创建时相当于：

```python
{
    "messages": [],
    "conversation_summary": "",
    "constraints": {}
}
```

然后我们设置：

```python
state.constraints = {
    "language": "Chinese",
    "style": "simple"
}
```

此时：

```text
AgentState
│
├── messages
│   └── 当前已经发生的对话历史
│
├── conversation_summary
│   └── 更早历史的压缩摘要
│
└── constraints
    └── 必须稳定保留的规则
```

这就是：

Structured State\boxed{\text{Structured State}}

注意：

> 这只是 Python 程序中的状态，并不是 LLM 自己在“脑子里保存”。

------

# 四、为什么 `constraints` 不直接写进 messages？

当然可以写，但我们希望程序逻辑更清楚。

比如：

```python
state.constraints = {
    "language": "Chinese",
    "answer_style": "beginner-friendly"
}
```

这是：

```text
程序当前明确知道的规则
```

我们之后让 `ContextManager` 决定：

> 什么时候、以什么格式把它交给 LLM。

所以：

```text
State
→ 保存

ContextManager
→ 使用
```

不要混在一起。

------

# 五、接下来创建 `context_manager.py`

先写最简单的：

```python
from state import AgentState


class ContextManager:

    def build_context(
        self,
        state: AgentState,
        current_query: str
    ) -> list[dict]:

        context = []

        return context
```

现在这个函数什么都没干。

它接收两个东西：

```python
state
```

表示：

> 当前 Agent 已经拥有的信息。

以及：

```python
current_query
```

表示：

> 用户这一轮刚刚提出的问题。

最后返回：

```python
list[dict]
```

为什么？

因为我们的：

```python
LLMClient.chat(messages)
```

需要的就是：

```python
list[dict]
```

所以 ContextManager 是中间桥梁：

```text
AgentState
       ↓
ContextManager
       ↓
list[dict]
       ↓
LLMClient
```

------

# 六、先加入 System Prompt

修改：

```python
class ContextManager:

    def build_context(
        self,
        state: AgentState,
        current_query: str
    ) -> list[dict]:

        context = [
            {
                "role": "system",
                "content": (
                    "你是一名AI Agent课程老师，"
                    "请使用准确但通俗的方式回答。"
                )
            }
        ]

        return context
```

现在如果：

```python
context = manager.build_context(
    state,
    "什么是Agent？"
)
```

暂时只得到：

```python
[
    {
        "role": "system",
        "content": "你是一名AI Agent课程老师..."
    }
]
```

这显然还不够。

------

# 七、把 `constraints` 加进去

继续：

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

假设：

```python
state.constraints = {
    "language": "Chinese",
    "style": "simple"
}
```

那么 Context 中多了一条：

```text
[CONSTRAINTS]
{'language': 'Chinese', 'style': 'simple'}
```

于是：

```text
State中的结构化规则
↓
ContextManager
↓
转换成LLM能够看到的信息
```

看到区别了吗？

`constraints` 原来是：

```python
dict
```

最后为了给 LLM 看，被组织成：

```text
文本 message
```

------

# 八、再加入 Conversation Summary

继续：

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

如果：

```python
state.conversation_summary = (
    "用户正在学习Agent开发，"
    "目前正在学习Context Engineering。"
)
```

LLM 就会看到：

```text
[CONVERSATION SUMMARY]
用户正在学习Agent开发，目前正在学习Context Engineering。
```

------

# 九、加入历史 messages

暂时我们先全部加入：

```python
context.extend(
    state.messages
)
```

注意：

```python
extend()
```

是把：

```python
[
    message1,
    message2,
    message3
]
```

逐条放进 `context`。

假设：

```python
state.messages = [
    {
        "role": "user",
        "content": "什么是State？"
    },
    {
        "role": "assistant",
        "content": "State是Agent当前运行状态..."
    }
]
```

那么：

```python
context.extend(state.messages)
```

以后：

```text
context
├── system
├── constraints
├── summary
├── old user
└── old assistant
```

------

# 十、最后加入本轮 `current_query`

```python
context.append({
    "role": "user",
    "content": current_query
})
```

于是完整方法变成：

```python
from state import AgentState


class ContextManager:

    def build_context(
        self,
        state: AgentState,
        current_query: str
    ) -> list[dict]:

        context = [
            {
                "role": "system",
                "content": (
                    "你是一名AI Agent课程老师，"
                    "请使用准确但通俗的方式回答。"
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

        context.extend(
            state.messages
        )

        context.append({
            "role": "user",
            "content": current_query
        })

        return context
```

------

# 十一、这段代码实际上干了什么？

假设当前：

```python
state = AgentState(
    messages=[
        {
            "role": "user",
            "content": "什么是State？"
        },
        {
            "role": "assistant",
            "content": "State是Agent当前运行状态。"
        }
    ],
    conversation_summary=(
        "用户正在学习Agent开发。"
    ),
    constraints={
        "language": "Chinese"
    }
)
```

用户新问题：

```python
current_query = "那Context又是什么？"
```

调用：

```python
context = manager.build_context(
    state,
    current_query
)
```

最终 Context：

```text
system:
你是一名AI Agent课程老师...

system:
[CONSTRAINTS]
{'language': 'Chinese'}

system:
[CONVERSATION SUMMARY]
用户正在学习Agent开发。

user:
什么是State？

assistant:
State是Agent当前运行状态。

user:
那Context又是什么？
```

然后这整个：

```python
context
```

才会真正发给 LLM。

所以现在你应该更加明确：

State 不等于 messages\boxed{\text{State 不等于 messages}}

也：

State 不等于 Context\boxed{\text{State 不等于 Context}}

而是：

```text
State
↓
ContextManager处理
↓
Context
↓
LLM
```

------

# 十二、现在把它和你的 `LLMClient` 接起来

你的 `LLMClient` 已经有：

```python
answer = await client.chat(messages)
```

所以现在 `main.py` 可以这样：

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
            current_query=current_query
        )

        answer = await client.chat(
            context
        )

        if answer is None:
            print("Assistant: 请求失败")
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


asyncio.run(main())
```

现在开始真正重要了。

------

# 十三、第一轮发生什么？

用户：

```text
User:
我叫Tom。
```

此时：

```python
state.messages
```

还是：

```python
[]
```

ContextManager 构造：

```text
system
constraints
current_query = 我叫Tom
```

发送：

```python
answer = await client.chat(context)
```

模型回答：

```text
你好Tom！
```

然后：

```python
state.messages.append(...)
```

最终：

```python
state.messages
```

变成：

```python
[
    {
        "role": "user",
        "content": "我叫Tom。"
    },
    {
        "role": "assistant",
        "content": "你好Tom！"
    }
]
```

------

# 十四、第二轮就不一样了

用户：

```text
User:
我叫什么？
```

此时 ContextManager 读取 State。

构造：

```text
system

constraints

user:
我叫Tom。

assistant:
你好Tom！

user:
我叫什么？
```

然后发给 LLM。

所以它能回答：

```text
你叫Tom。
```

整个程序真正形成：

```text
第一轮
User Query
↓
Context
↓
LLM
↓
Answer
↓
Update State

第二轮
新的User Query
↓
读取已经更新的State
↓
重新构造新的Context
↓
LLM
↓
Answer
↓
再次Update State
```

这就是：

Agent State Loop\boxed{\text{Agent State Loop}}

------

# 十五、注意 Context 不是一直存着不变的

这是今天非常重要的一点。

第一轮：

```text
Context₁
=
System
+
Constraints
+
Query₁
```

执行以后更新 State。

第二轮：

```text
Context₂
=
System
+
Constraints
+
History₁
+
Query₂
```

第三轮：

```text
Context₃
=
System
+
Constraints
+
History₁
+
History₂
+
Query₃
```

所以：

Context 是动态构造的\boxed{\text{Context 是动态构造的}}

不是提前创建一份然后永远使用。

------

# 十六、那 ContextManager 和以前手写 messages 有什么区别？

你可能觉得：

> 我以前直接 `messages.append()` 不是也能做到吗？

对。

如果只是一个简单 Chatbot：

```python
messages.append(...)
```

完全可以。

我们现在多加：

```text
AgentState
+
ContextManager
```

是为了将来容易加入：

```text
Summary
Constraints
Evidence
Plan
Tool Results
Memory
不同Node的Context
```

例如以后 Writer：

```python
manager.build_writer_context(state)
```

Searcher：

```python
manager.build_searcher_context(state)
```

Planner：

```python
manager.build_planner_context(state)
```

而不用让一个：

```python
messages
```

承担所有职责。

------

# 十七、把它类比成 MVC 一类的“职责分离”

你现在不用记设计模式，只理解思想。

以前：

```text
main.py
│
├── 保存历史
├── 管Context
├── 调LLM
├── 拼Prompt
├── 管规则
└── 打印结果
```

什么都让 `main.py` 干。

现在：

```text
AgentState
→ 专门保存状态

ContextManager
→ 专门构造上下文

LLMClient
→ 专门和LLM服务器通信

main.py
→ 专门组织流程
```

这就叫：

Separation of Concerns\boxed{\text{Separation of Concerns}}

即：

> **职责分离。**

这个词以后面试、工程开发都经常遇到。

------

# 十八、目前还有一个明显问题

现在：

```python
context.extend(
    state.messages
)
```

会把所有历史全部加入。

所以：

```text
第10轮
→ 20条message

第100轮
→ 200条message

第1000轮
→ 2000条message
```

还是会越来越长。

也就是说：

> 今天第一节我们只完成了“State + ContextManager + LLMClient”的连接，但还没有解决 Context Window。

下一节才会把这里：

```python
context.extend(
    state.messages
)
```

升级成：

```text
旧历史
→ Summary

最近消息
→ 保留

重要规则
→ Structured State
```

这就是今天第二节的重点。

------

# 第一节先做 5 道练习

1. 为什么：

```python
state.messages
```

和：

```python
context
```

不是同一个东西？分别负责什么？

1. 解释：

```python
context = manager.build_context(
    state=state,
    current_query=current_query
)
```

这行代码到底完成了什么。

1. 为什么：

```python
state.messages.append({
    "role": "user",
    "content": current_query
})
```

是在 LLM 返回答案以后执行，而不是 ContextManager 里已经加入一次 `current_query` 后就不再保存？

1. 为什么要拆成：

```text
AgentState
ContextManager
LLMClient
main.py
```

四部分，而不是所有逻辑全部写进 `main.py`？

1. 假设第一轮：

```text
User:
我叫Tom
```

模型回答：

```text
Assistant:
你好Tom
```

第二轮：

```text
User:
我叫什么？
```

请你自己按照顺序写出**第二轮真正发给 LLM 的 Context 大概包含哪些内容**。

这 5 题答完，我们马上进入今天第二节：把现在的 `ContextManager` 升级成真正能够进行 **Recent History + Summary + Context Window 管理** 的版本。