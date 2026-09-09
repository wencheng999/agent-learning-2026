这 5 题你已经掌握得比较稳了，尤其是你现在已经真正理解了：

旧消息不等于无用，最近消息也不等于最重要\boxed{\text{旧消息不等于无用，最近消息也不等于最重要}}

我们先把几个表述稍微修正一下，然后按刚才说的，做今天最后一个**小型 Python ContextManager 实战**。

## 练习检查

练习 1 正确。直接：

```python
messages = messages[-10:]
```

的问题主要有两个：

```text
① 可能把 system prompt、长期约束等重要早期信息删掉

② 可能把仍然与当前任务相关的旧信息删掉
```

比如 50 轮之前用户说：

```text
后面所有实验的 top_k 都不能超过 20
```

即使它很旧，也依然重要。

练习 2 完全正确。保留所有历史可能：

```text
超过 Context Window
增加 Token Cost
增加 Latency
引入 Context Noise
```

所以常见设计才会变成：

```text
System Prompt
+
Old History Summary
+
Recent Messages
+
Current Query
```

练习 3 正确。可以最终记成：

```text
conversation_summary
→ 旧历史的压缩版关键信息

recent_messages
→ 最近几轮需要保留细节的原始对话
```

练习 4 完全正确。LLM Summary 本身仍然是模型生成结果，可能：

```text
遗漏
误解
压缩过度
生成错误
```

所以像：

```text
max_top_k = 20
```

这种程序必须严格遵守的规则，更适合：

```python
state.constraints
```

结构化保存。

练习 5 也正确，不过注意你写的是：

```text
stata
```

应该是：

```text
state
```

最终可以记：

Context=Structured State+Summary+Recent Relevant Messages+Current Input\boxed{ Context = Structured\ State + Summary + Recent\ Relevant\ Messages + Current\ Input }

这里不是说每次必须四部分全部都用，而是表示它们都是重要 Context 来源。

------

# 今天最后一个实战：自己做一个 ContextManager

这次我们不接真实 LLM，目的只有一个：

> **亲眼看到 State 很多，但最后 Context 只挑一部分。**

------

## 第一步：定义 AgentState

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

    evidence: list[str] = Field(
        default_factory=list
    )
```

现在 State 有四块：

```text
messages
→ 原始历史消息

conversation_summary
→ 老历史摘要

constraints
→ 必须精确保留的规则

evidence
→ 当前任务得到的证据
```

------

# 第二步：手动创建一些历史

```python
state = AgentState()
```

先加一个规则：

```python
state.constraints = {
    "max_top_k": 20,
    "language": "Chinese"
}
```

然后模拟旧历史摘要：

```python
state.conversation_summary = (
    "用户正在学习AI Agent开发，"
    "已经掌握HTTP、Pydantic、async/await、"
    "LLM API、Streaming和Structured Output，"
    "当前正在学习Context Engineering。"
)
```

再加入最近消息：

```python
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
```

------

# 第三步：定义 ContextManager

```python
class ContextManager:

    def build_context(
        self,
        state: AgentState,
        current_query: str,
        recent_n: int = 4
    ) -> list[dict]:
```

这里输入：

```text
state
→ 所有当前状态

current_query
→ 这一轮最新问题

recent_n
→ 最近保留多少条原始消息
```

------

# 第四步：先选最近消息

```python
recent_messages = (
    state.messages[-recent_n:]
)
```

如果：

```python
recent_n = 4
```

那么只取：

```text
最后4条
```

但是旧历史的重要信息并没有完全消失，因为还有：

```python
state.conversation_summary
```

------

# 第五步：创建 System Context

```python
context = [
    {
        "role": "system",
        "content": (
            "你是一名AI Agent课程老师，"
            "请使用准确但通俗的中文回答。"
        )
    }
]
```

这个永远保留。

所以不会因为：

```python
messages[-4:]
```

把 System Prompt 删掉。

------

# 第六步：加入 Summary

```python
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
```

如果有摘要，就加入。

此时：

```text
Context
├── System Prompt
└── Old History Summary
```

------

# 第七步：加入结构化规则

我们不能只依赖 Summary。

所以：

```python
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
```

比如最终模型能看到：

```text
[CONSTRAINTS]
{
    'max_top_k': 20,
    'language': 'Chinese'
}
```

------

# 第八步：加入最近消息

```python
context.extend(
    recent_messages
)
```

注意这里是：

```python
extend()
```

不是：

```python
append()
```

因为：

```python
recent_messages
```

本身是一个消息列表。

------

# 第九步：加入最新问题

```python
context.append(
    {
        "role": "user",
        "content": current_query
    }
)
```

于是：

```text
System
↓
Summary
↓
Constraints
↓
Recent Messages
↓
Current Query
```

完整 Context 出来了。

------

# 完整 ContextManager

```python
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
                        + str(state.constraints)
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
```

------

# 第十步：实际调用

```python
manager = ContextManager()

context = manager.build_context(
    state=state,
    current_query=(
        "请再简单解释一下Context Window。"
    ),
    recent_n=4
)
```

打印：

```python
for message in context:
    print(
        message["role"],
        ":",
        message["content"]
    )
    print("-" * 30)
```

------

# 最终大概输出

```text
system:
你是一名AI Agent课程老师，请使用准确但通俗的中文回答。
------------------------------

system:
[CONVERSATION SUMMARY]
用户正在学习AI Agent开发，已经掌握……
------------------------------

system:
[CONSTRAINTS]
{'max_top_k': 20, 'language': 'Chinese'}
------------------------------

assistant:
State保存当前任务全部运行状态……
------------------------------

user:
那ContextManager是做什么的？
------------------------------

assistant:
它根据当前任务……
------------------------------

user:
那历史越来越长怎么办？
------------------------------

user:
请再简单解释一下Context Window。
------------------------------
```

注意：

> State 里可能还有很多东西，但最终给 LLM 的只是经过设计后的 `context`。

这就是今天整节课最核心的工程落地。

------

# 一个你可能马上会发现的问题

你这里会看到：

```text
最后一条历史 user：
那历史越来越长怎么办？

然后 current_query 又是：
请再简单解释一下Context Window。
```

这是合理的，因为：

```text
state.messages
```

保存的是已经发生的历史，

而：

```text
current_query
```

表示刚刚到来的新输入。

等模型回答结束以后，我们再：

```python
state.messages.append(
    {
        "role": "user",
        "content": current_query
    }
)

state.messages.append(
    {
        "role": "assistant",
        "content": answer
    }
)
```

这样它们才正式成为历史。

完整循环就是：

```text
Current Query
↓
ContextManager
↓
LLM
↓
Answer
↓
把 Current Query + Answer
加入 State.messages
↓
下一轮
```

这个思想非常重要。

------

# 今天到这里，其实已经学得够多了

今天你完成了：

```text
Prompt Engineering
    ↓
Task Decomposition
    ↓
Context Engineering
    ↓
State / Context / Memory
    ↓
Per-Node Context
    ↓
Context Window
    ↓
History Truncation
    ↓
Conversation Summary
    ↓
Recent Messages
    ↓
Structured State
    ↓
ContextManager
```

这一天的信息量已经不小了。

最后给你 3 道非常小的实战检查题，不再开新章节：

1. 为什么 `ContextManager` 不是一个“保存所有 Context 的数据库”，而更像一个“Context 加工器”？
2. 在上面的代码中，为什么 `constraints` 不直接全部写进 `conversation_summary`？
3. 当前用户输入 `current_query` 应该在什么时候加入 `state.messages`：**发送给 LLM 之前，还是 LLM 回答完成以后？为什么？**

这三题答完，今天就可以正式收尾。