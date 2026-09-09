这 4 个问题你这次已经基本说顺了，说明前面最抽象的地方开始落地了。尤其第 2、3 题很准确：Writer 真正关心的是 `user_query + evidence`，而不是把 50 篇原始 `tool_results` 全塞进去。

有一个小地方再校准一下。你第 4 题说 ContextManager “从 State 选取合适的信息加上 Memory 其他信息”，方向对，但 **Memory 不是每次都必须加入**。更准确的定义是：

ContextManager = 根据当前任务，从可用信息中动态构造本次 LLM Context\boxed{\text{ContextManager = 根据当前任务，从可用信息中动态构造本次 LLM Context}}

这些“可用信息”可能来自：

```text
State
Memory
Tool Definitions
固定 Instructions
Retrieved Evidence
```

但具体放哪些，要看当前 Node 的任务。

所以你现在可以最终记成：

```text
State
→ Agent程序当前任务拥有的全部运行状态

Context
→ 这一次LLM调用真正看到的信息

ContextManager
→ 根据当前任务，从State等来源选择、压缩、组织出Context
```

这部分可以通过了。

------

# 下一节：Context Window + History 管理

现在来看一个非常现实的问题。

我们之前写聊天程序时：

```python
messages = [
    system,
    user,
    assistant,
    user,
    assistant,
    ...
]
```

每轮对话之后都：

```python
messages.append(...)
```

于是：

```text
第1轮
messages很短

第10轮
messages变长

第100轮
messages非常长
```

那是不是可以永远这样往里面加？

答案是：

不可以\boxed{\text{不可以}}

因为模型一次能处理的信息是有限的。

------

## 一、Context Window 到底是什么？

你可以把模型的 Context Window 想象成一张有限大小的桌子。

每次调用 LLM 时，桌子上可能要放：

```text
System Prompt
Conversation History
User Query
Tool Definitions
Tool Results
RAG Documents
Evidence
Few-shot Examples
```

模型还需要留一部分空间：

```text
生成最终回答
```

所以：

Context Window = 一次模型调用可以处理的上下文容量\boxed{\text{Context Window = 一次模型调用可以处理的上下文容量}}

通常使用 Token 衡量。

------

# 二、为什么不能把所有东西全部塞进去？

除了可能超过 Context Window，还有一个更重要的问题：

> **能放得下，不代表应该放进去。**

例如用户当前问：

```text
解释一下asyncio.gather()
```

结果 Context 中还有：

```text
两个月前关于Java自增运算符的对话
几十篇推荐系统论文
旧的错误日志
之前的天气查询
20个无关Tool定义
```

这些东西虽然模型理论上“看得到”，但会产生：

Context Noise\boxed{\text{Context Noise}}

也就是我们上一节讲的上下文噪声。

真正重要的信息容易被淹没。

------

# 三、最简单的方法：History Truncation

初学者第一种办法：

```python
messages = messages[-10:]
```

你应该能看懂。

假设：

```python
messages
```

有 100 条消息。

那么：

```python
messages[-10:]
```

表示：

> 只留下最后 10 条。

于是：

```text
旧的90条
→ 丢弃

最近10条
→ 保留
```

这叫：

History Truncation\boxed{\text{History Truncation}}

历史截断。

------

# 四、但是直接 `messages[-10:]` 有问题

这是一个很重要的坑。

假设：

```python
messages = [
    {"role": "system", ...},       # 第0条
    ...
    100条历史
]
```

你：

```python
messages = messages[-10:]
```

很可能把最前面的：

```python
system
```

直接删掉了。

然后模型不知道：

```text
自己是什么角色
有什么规则
输出应该是什么格式
```

所以不能简单地认为：

```python
最后N条
```

就是最好的 Context。

------

# 五、还有第二个问题：重要信息可能很早

比如第一轮用户说：

```text
我正在研究LLM4CDSR，
后续所有讨论都以这个模型为基础。
```

聊了 50 轮以后。

如果直接：

```python
messages[-10:]
```

这一条可能没了。

但它对当前问题仍然非常重要。

所以：

\boxed{\text{旧 ≠ 不重要}}

反过来：

\boxed{\text{新 ≠ 一定重要}}

这就是为什么成熟的 Context 管理不能只看时间。

------

# 六、更合理的方法：Summary + Recent Messages

一种非常经典的做法：

```text
System Prompt
+
Old History Summary
+
Recent Messages
+
Current User Query
```

比如原来有 50 轮历史。

我们不是全部保留，而是把旧历史总结成：

```text
[CONVERSATION SUMMARY]

用户正在学习Agent开发。

已经掌握：
Python基础、HTTP、Pydantic、async/await、
LLM API、Streaming、Structured Output。

当前正在学习：
Context Engineering。

用户已经理解：
State是当前任务运行状态；
Context是某次LLM调用看到的信息。
```

然后只保留最近几轮原始消息：

```text
[RECENT MESSAGES]

User:
State和Context有什么区别？

Assistant:
...

User:
我还是感觉有点抽象。
```

于是：

```text
旧历史
→ 压缩成 Summary

最近历史
→ 保留原文
```

这就同时做了：

Compress + Select\boxed{\text{Compress + Select}}

------

# 七、为什么最近消息通常保留原文？

因为越靠近当前问题的内容，通常越需要细节。

比如：

```text
User：
Writer应该看到哪些Context？

Assistant：
user_query + evidence

User：
那tool_results呢？
```

如果把最近几轮也压缩得特别狠，模型可能不知道：

```text
“那”到底指什么
```

所以常见设计：

```text
较旧内容
→ Summary

最近几轮
→ Raw Messages
```

------

# 八、最终 Context 可能长这样

以后你的 Agent 真正调用 LLM 时，可能构造：

```python
messages = [
    {
        "role": "system",
        "content": "你是一名Agent课程老师。"
    },
    {
        "role": "system",
        "content": f"""
[CONVERSATION SUMMARY]
{summary}
"""
    },

    # 最近几轮真实消息
    *recent_messages,

    {
        "role": "user",
        "content": current_query
    }
]
```

这里的思想比代码更重要：

```text
固定规则
↓
System

旧历史精华
↓
Summary

最近上下文细节
↓
Recent Messages

当前问题
↓
Current Query
```

------

# 九、这时候 State 可以怎么设计？

例如：

```python
from pydantic import BaseModel, Field


class AgentState(BaseModel):
    user_query: str

    messages: list[dict] = Field(
        default_factory=list
    )

    conversation_summary: str = ""

    evidence: list[str] = Field(
        default_factory=list
    )
```

这里：

```python
messages
```

保存最近原始对话。

而：

```python
conversation_summary
```

保存被压缩掉的旧对话摘要。

于是：

```text
AgentState
│
├── messages
│   └── 最近历史
│
└── conversation_summary
    └── 老历史摘要
```

------

# 十、ContextManager 可以开始真正干活了

例如：

```python
class ContextManager:

    def build_chat_context(
        self,
        state: AgentState,
        recent_n: int = 6
    ) -> list[dict]:

        recent_messages = (
            state.messages[-recent_n:]
        )

        context = [
            {
                "role": "system",
                "content": (
                    "你是一名AI Agent课程老师。"
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

        context.extend(
            recent_messages
        )

        return context
```

这时候 ContextManager 干的事情已经非常具体了。

------

# 十一、一步一步看

假设：

```python
state.messages
```

有：

```text
20条消息
```

调用：

```python
manager.build_chat_context(
    state,
    recent_n=6
)
```

先：

```python
recent_messages = state.messages[-6:]
```

得到最近 6 条。

然后创建：

```python
context = [
    system_message
]
```

如果存在旧历史摘要：

```python
state.conversation_summary
```

就：

```python
context.append(summary_message)
```

最后：

```python
context.extend(recent_messages)
```

把最近消息加入。

------

# 十二、`append()` 和 `extend()` 再区分一下

这个你以后很容易遇到。

假设：

```python
a = [1, 2]
```

执行：

```python
a.append([3, 4])
```

得到：

```python
[1, 2, [3, 4]]
```

整个 `[3,4]` 被当成一个元素。

而：

```python
a.extend([3, 4])
```

得到：

```python
[1, 2, 3, 4]
```

也就是把里面的元素逐个加入。

所以：

```python
context.extend(recent_messages)
```

就是：

> 把多条 message 分别加入 context。

------

# 十三、那 Summary 谁生成？

这里又出现一个非常有意思的问题。

旧消息太长：

```text
↓
需要Summary
```

谁来总结？

最简单：

让 LLM 自己总结\boxed{\text{让 LLM 自己总结}}

比如：

```python
summary_prompt = """
请总结下面的历史对话。

要求：
1. 保留用户长期目标；
2. 保留已经做出的关键决定；
3. 保留尚未完成的任务；
4. 删除寒暄和重复信息；
5. 尽量简洁。
"""
```

然后把旧消息交给 LLM。

得到：

```text
用户正在学习Agent开发，
已完成Python、HTTP、Pydantic和async基础，
当前学习Context Engineering。
用户已理解State和Context的基本区别。
```

这个摘要再写回：

```python
state.conversation_summary = summary
```

这就是：

Summarization Memory\boxed{\text{Summarization Memory}}

的一种最简单实现。

------

# 十四、什么时候做 Summary？

不能每说一句都总结一次。

那会导致：

```text
每轮对话
↓
额外调用一次LLM
↓
成本翻倍
```

所以通常设置一个条件。

例如：

```python
if len(state.messages) > 20:
    ...
```

达到一定长度：

```text
旧消息
↓
Summary
↓
只留下最近几轮
```

可以理解为：

```text
messages越来越长
        ↓
超过阈值？
   /          \
 否            是
 ↓             ↓
继续       总结旧消息
               ↓
          更新summary
               ↓
          删除部分旧消息
```

------

# 十五、但是 Summary 也有风险

LLM 总结不是完美的。

比如原始历史：

```text
用户明确说：
top_k最大必须为20。
```

Summary 可能漏掉。

后来 Agent：

```text
top_k = 100
```

就出问题。

所以重要的结构化事实，不应该全部只依赖自然语言 Summary。

例如：

```python
state.constraints = {
    "max_top_k": 20
}
```

这种关键规则最好单独结构化保存。

这也是为什么：

State 不能全部变成一段 Summary\boxed{\text{State 不能全部变成一段 Summary}}

------

# 十六、所以成熟一点的设计是

```text
AgentState
│
├── Structured State
│   ├── user_query
│   ├── plan
│   ├── constraints
│   ├── current_step
│   └── tool_results
│
├── Conversation Summary
│
├── Recent Messages
│
└── Evidence
```

然后 ContextManager：

```text
当前是谁？
↓
Planner / Searcher / Writer
↓
决定选哪些Structured State
+
哪些Summary
+
哪些Recent Messages
+
哪些Evidence
↓
构造Context
```

这已经很接近真实 Agent 的 Context Engineering 了。

------

# 十七、你现在可以把 Context 管理理解成“三层”

第一层：

```text
必须长期精确保留的信息
→ Structured State
```

比如：

```text
任务计划
限制条件
Tool Result
任务状态
```

第二层：

```text
过去大量聊天的精华
→ Summary
```

第三层：

```text
当前附近的细节
→ Recent Messages
```

最终：

Context=StructuredState+Summary+RecentRelevantMessages+CurrentInput\boxed{ Context = Structured State + Summary + Recent Relevant Messages + Current Input }

具体每次不一定全部使用，但这个模型非常好理解。

------

# 十八、结合你的 Research Agent

未来你做 Deep Research Agent 时：

```text
State
│
├── query
├── plan
├── search_results
├── selected_papers
├── evidence
├── draft
└── errors
```

如果 Writer 工作：

```text
Writer Context
=
query
+
relevant plan
+
selected evidence
+
report requirements
```

而不是：

```text
完整State全部复制过去
```

如果 Critic 工作：

```text
Critic Context
=
query
+
draft
+
evidence
+
evaluation criteria
```

这就是：

Context Engineering = 为每一步准备恰到好处的信息\boxed{\text{Context Engineering = 为每一步准备恰到好处的信息}}

------

# 这一节你先做 5 个小练习

1. 为什么直接：

```python
messages = messages[-10:]
```

虽然简单，但可能有问题？至少说出两个原因。

1. 为什么比较合理的 Conversation Context 经常采用：

```text
System Prompt
+
Old History Summary
+
Recent Messages
+
Current Query
```

而不是全部历史？

1. `conversation_summary` 和 `recent_messages` 各自主要负责保存什么？
2. 为什么：

```text
top_k最大值=20
```

这种重要规则最好保存成结构化 State，而不是完全依赖 LLM Summary？

1. 用自己的话解释：

Context=StructuredState+Summary+RecentRelevantMessages+CurrentInput\boxed{ Context = Structured State + Summary + Recent Relevant Messages + Current Input }

这一轮做完，我们今天最后再做一个**非常小的 Python ContextManager 实战**，把 `State → History截断 → Summary → Context` 真正跑一遍。