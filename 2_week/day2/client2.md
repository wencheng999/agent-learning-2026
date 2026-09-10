这 5 道题整体答得不错，说明你已经真正理解了这一节最核心的数据流：

State→ContextManager→Context→LLM→Update State\boxed{\text{State} \rightarrow \text{ContextManager} \rightarrow \text{Context} \rightarrow \text{LLM} \rightarrow \text{Update State}}

不过第 3、5 题有两个地方需要稍微校准一下，然后我们直接进入今天第二节。

## 练习 1：正确 ✅

你说：

> `state.messages` 保存用户和 LLM 的历史交互信息；`context` 是本次真正发给 LLM 的全部信息。

这个区分已经很准确了。

可以最终记成：

```text
state.messages
→ 只是 State 中“历史对话”这一部分

context
→ 当前这次 LLM 调用真正看到的全部消息
```

所以：

state.messages 是 Context 的一个可能来源，而不是 Context 本身\boxed{\text{state.messages 是 Context 的一个可能来源，而不是 Context 本身}}

例如 Context 还可能包含：

```text
System Prompt
Constraints
Conversation Summary
Recent Messages
Current Query
Evidence
Tool Results
```

------

## 练习 2：完全正确 ✅

这句：

```python
context = manager.build_context(
    state=state,
    current_query=current_query
)
```

就是：

> 把当前 Agent 已经拥有的状态 `state` 和新问题 `current_query` 交给 `ContextManager`，让它挑选、组织成本轮真正要发送给 LLM 的 `context`。

可以理解：

```text
一大堆已有状态
        +
当前新问题
        ↓
ContextManager
        ↓
本轮 LLM 输入
```

------

## 练习 3：方向正确，但别把它理解成 LLM 自己“获得了记忆”

你说：

> 保存以后能让 LLM 后面根据历史提问回答，让 LLM 具有更好的记忆功能。

从使用效果上这样理解没问题，但工程上要再准确一点：

不是 LLM 自己把这段历史永久记住了\boxed{\text{不是 LLM 自己把这段历史永久记住了}}

而是：

```text
应用程序
↓
把 current_query + answer
保存进 state.messages
↓
下一轮 ContextManager 再把相关历史
重新提供给 LLM
↓
模型看起来“记得”
```

所以这里真正有“记忆管理能力”的主要是：

```text
Agent应用层
```

而不是一次无状态的 LLM API 调用本身。

------

## 练习 4：完全正确 ✅

这就是：

Separation of Concerns，职责分离\boxed{\text{Separation of Concerns，职责分离}}

现在：

```text
AgentState
→ 保存状态

ContextManager
→ 构造上下文

LLMClient
→ 负责和 LLM API 通信

main.py
→ 控制整个执行流程
```

以后再加：

```text
ToolManager
MemoryManager
Planner
Evaluator
```

也不会全部堆进一个 `main.py`。

------

# 练习 5：思路对，但数据结构需要纠正一下

你写成了：

```python
{
    messages: [...],
    constraints: "...",
    summary: "...",
    current_query: {...}
}
```

这个更像：

> “Context 中包含哪些逻辑部分”的示意图。

但按照我们现在 `LLMClient.chat()` 接收的格式，真正发给模型的是：

list[dict]\boxed{\text{list[dict]}}

也就是 `messages` 风格。

假设：

```python
state.constraints = {
    "language": "Chinese"
}

state.conversation_summary = (
    "用户正在学习Agent。"
)
```

那么第二轮实际 Context 更接近：

```python
[
    {
        "role": "system",
        "content": "你是一名AI Agent课程老师..."
    },

    {
        "role": "system",
        "content": "[CONSTRAINTS]\n{'language': 'Chinese'}"
    },

    {
        "role": "system",
        "content": "[CONVERSATION SUMMARY]\n用户正在学习Agent。"
    },

    {
        "role": "user",
        "content": "我叫Tom"
    },

    {
        "role": "assistant",
        "content": "你好Tom"
    },

    {
        "role": "user",
        "content": "我叫什么？"
    }
]
```

注意这里：

```text
State
→ 是结构化 Python 对象

Context
→ 最终通常转换成模型 API 能理解的 messages
```

这点很重要。

第一节正式通过 ✅。

------

# Week 1 · Day 2 第二节

# Recent History + Summary + Context Window 管理

现在我们解决第一节留下的问题：

```python
context.extend(
    state.messages
)
```

这句话目前意味着：

> 不管有多少历史，我全部塞给 LLM。

如果用户聊了 1000 轮：

```text
2000条左右的 user / assistant messages
```

Context 就会越来越大。

所以今天我们把它升级成：

```text
老历史
→ Summary

最近历史
→ 保留原文

结构化规则
→ 精确保留

当前Query
→ 完整保留
```

最终：

Context=System+Constraints+OldSummary+RecentMessages+CurrentQuery\boxed{ Context = System + Constraints + Old Summary + Recent Messages + Current Query }

------

# 一、先明确一个问题：我们要管理谁？

这里容易混淆。

我们现在有：

```python
state.messages
```

假设存了：

```text
30条历史消息
```

但 LLM 当前不一定需要全部 30 条。

所以 ContextManager 要做：

```text
30条历史
↓
挑最近6条
↓
较老24条压缩成Summary
↓
最终只给模型：
Summary + 最近6条
```

------

# 二、先实现最简单的 Recent History

我们原来：

```python
context.extend(
    state.messages
)
```

改成：

```python
recent_messages = (
    state.messages[-6:]
)

context.extend(
    recent_messages
)
```

如果：

```text
state.messages共有20条
```

那么：

```python
state.messages[-6:]
```

就是：

```text
最后6条
```

例如：

```text
第15条
第16条
第17条
第18条
第19条
第20条
```

前 14 条不会直接送给本次 LLM。

------

# 三、但是前面的历史直接扔掉也不行

比如第 2 条消息用户说：

```text
我的研究方向是跨域序列推荐。
```

虽然它很旧，但当前可能仍然有价值。

所以不能：

```text
旧历史
→ 全部删除
```

而是：

```text
旧历史
→ 压缩
→ conversation_summary
```

例如原来有：

```text
User：我是研二学生。
Assistant：好的。

User：我研究CDSR。
Assistant：了解。

User：我正在学习Agent。
Assistant：...
```

压缩以后：

```text
用户是正在学习Agent的计算机研究生，
研究方向涉及跨域序列推荐。
```

一大堆历史就变成一个更短的 Summary。

------

# 四、State 现在长这样

```python
class AgentState(BaseModel):

    messages: list[dict] = Field(
        default_factory=list
    )

    conversation_summary: str = ""

    constraints: dict = Field(
        default_factory=dict
    )
```

这里：

```text
messages
→ 最近保留的原始历史

conversation_summary
→ 更旧历史的压缩结果
```

这两者是互补的。

------

# 五、什么时候应该压缩？

我们可以先用非常简单的规则：

```python
if len(state.messages) > 10:
```

意思：

> 历史消息超过 10 条，就做一次压缩。

注意我们现在只是为了学习，所以按“消息条数”判断。

真正工程里以后会更关心：

```text
Token Count
```

因为：

```text
10条很短的消息
```

和：

```text
10篇超长论文摘要
```

Token 数完全不是一个量级。

------

# 六、假设我们只保留最近 6 条

那么：

```python
recent_n = 6
```

如果总共：

```python
len(state.messages) == 14
```

旧消息就是：

```python
old_messages = (
    state.messages[:-recent_n]
)
```

最近消息：

```python
recent_messages = (
    state.messages[-recent_n:]
)
```

这个切片很重要。

假设：

```python
a = [1, 2, 3, 4, 5]
```

那么：

```python
a[-2:]
```

得到：

```python
[4, 5]
```

而：

```python
a[:-2]
```

得到：

```python
[1, 2, 3]
```

所以：

```text
[:-recent_n]
→ 较旧部分

[-recent_n:]
→ 最近部分
```

------

# 七、让 LLM 总结旧消息

我们可以给 `ContextManager` 加一个异步方法：

```python
async def summarize_history(
    self,
    client: LLMClient,
    state: AgentState,
    recent_n: int = 6
):
```

为什么：

```python
async def
```

？

因为它内部要调用：

```python
await client.chat(...)
```

需要访问 LLM。

------

# 八、先找出旧消息

```python
old_messages = (
    state.messages[:-recent_n]
)
```

如果没有旧消息：

```python
if not old_messages:
    return
```

------

# 九、构造 Summary Prompt

例如：

```python
summary_messages = [
    {
        "role": "system",
        "content": (
            "请总结下面的历史对话。"
            "保留用户长期目标、"
            "重要事实、已做决定和未完成任务。"
            "删除寒暄和重复内容。"
            "要求简洁准确。"
        )
    },
    {
        "role": "user",
        "content": str(old_messages)
    }
]
```

然后：

```python
summary = await client.chat(
    summary_messages
)
```

LLM 得到旧历史并生成：

```text
用户正在学习Agent，
已经掌握HTTP、Pydantic和async，
当前正在学习Context Engineering。
```

------

# 十、然后 Update State

如果 Summary 成功：

```python
if summary:
    state.conversation_summary = summary
```

接着：

```python
state.messages = (
    state.messages[-recent_n:]
)
```

也就是：

```text
旧历史
→ 已经压缩进 summary

state.messages
→ 只留下最近6条
```

State 从：

```text
messages: 20条
summary: ""
```

变成：

```text
messages: 最近6条
summary: 旧14条的摘要
```

这就是：

Context Compression\boxed{\text{Context Compression}}

------

# 十一、但是这里藏着一个重要问题

假设原来已经有：

```python
state.conversation_summary = (
    "用户已经学过HTTP。"
)
```

又来了很多历史。

如果我们直接：

```python
state.conversation_summary = summary
```

新的 Summary 可能把：

```text
“用户已经学过HTTP”
```

覆盖掉。

所以更合理的是：

> 新 Summary 应该同时考虑“旧 Summary + 新的旧消息”。

------

# 十二、所以 Summary Prompt 应该改成

```python
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
```

这就变成：

```text
旧Summary
       +
刚刚准备删除的旧Messages
       ↓
LLM
       ↓
新的、更完整Summary
```

这叫：

Incremental Summarization\boxed{\text{Incremental Summarization}}

增量摘要。

------

# 十三、完整的 `summarize_history()`

可以写成：

```python
async def summarize_history(
    self,
    client: LLMClient,
    state: AgentState,
    recent_n: int = 6
) -> None:

    if len(state.messages) <= recent_n:
        return

    old_messages = (
        state.messages[:-recent_n]
    )

    summary_messages = [
        {
            "role": "system",
            "content": (
                "请更新对话摘要。"
                "保留长期目标、重要事实、"
                "关键决定和未完成任务。"
                "删除寒暄和重复内容。"
                "要求简洁准确。"
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

------

# 十四、这里的执行顺序很重要

假设目前：

```text
state.messages = 12条
recent_n = 6
```

执行：

```text
① 判断 12 > 6

② 取前6条
   → old_messages

③ 旧summary + old_messages
   → 交给LLM总结

④ 得到新的summary

⑤ 更新
   state.conversation_summary

⑥ state.messages
   只留下最后6条
```

于是 Context 就不会无限增长。

------

# 十五、什么时候调用 `summarize_history()`？

我们可以在每一轮回答完成、更新历史后检查。

例如：

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

然后：

```python
await manager.summarize_history(
    client=client,
    state=state,
    recent_n=6
)
```

所以完整一轮：

```text
Current Query
↓
build_context()
↓
LLM
↓
Answer
↓
append user
↓
append assistant
↓
历史是否过长？
↓
summarize_history()
↓
更新 summary + recent messages
↓
下一轮
```

------

# 十六、那下一轮 Context 怎么构造？

我们已有：

```python
def build_context(...)
```

现在改成：

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

# 十七、现在整体就非常清楚了

State：

```text
conversation_summary
→ 历史精华

messages
→ 最近原始对话

constraints
→ 精确规则
```

ContextManager：

```text
System
+
Constraints
+
Summary
+
Recent Messages
+
Current Query
```

LLM：

```text
只看到当前真正需要的信息
```

------

# 十八、这已经是一个简单的 Context Budget 了

虽然我们还没有真的算 Token，但我们实际上已经开始“分配预算”。

例如：

```text
System Prompt
→ 永远保留

Constraints
→ 永远保留

Old History
→ 压缩

Recent Messages
→ 最多6条

Current Query
→ 永远保留
```

这其实就是最初级的：

Context Budgeting\boxed{\text{Context Budgeting}}

也就是：

> 不同信息获得不同的 Context 优先级。

------

# 十九、优先级可以这样理解

比如：

```text
最高优先级
↑
│ Current Query
│ System / Safety / Constraints
│ 当前Task相关Evidence
│ Recent Messages
│ Conversation Summary
│ 无关旧历史
↓
最低优先级
```

如果 Context 不够用了，优先删：

```text
无关旧历史
```

而不是删：

```text
当前用户问题
```

这其实已经非常接近成熟 Context Engineering 的思维了。

------

# 二十、这里还有一个危险：Summary Drift

假设每次都：

```text
旧Summary
+
新历史
↓
LLM再总结
```

做 100 次以后，摘要可能逐渐偏离原始信息。

这种现象可以理解为：

Summary Drift\boxed{\text{Summary Drift}}

比如最开始：

```text
用户研究的是：
Cross-Domain Sequential Recommendation
```

总结很多轮后可能慢慢变成：

```text
用户研究Recommendation
```

再后来：

```text
用户研究AI
```

越来越宽泛。

所以重要事实不要全部依赖 Summary。

再次回到：

```python
state.constraints
state.user_profile
state.current_task
```

等结构化字段。

也就是说：

Summary负责压缩语义，Structured State负责精确保真\boxed{\text{Summary负责压缩语义，Structured State负责精确保真}}

这句话很重要。

------

# 第二节练习

这次 5 道。

### 练习 1

假设：

```python
state.messages
```

有 20 条，而：

```python
recent_n = 6
```

解释：

```python
state.messages[:-recent_n]
```

和：

```python
state.messages[-recent_n:]
```

分别得到什么。

### 练习 2

为什么更新 Summary 时应该考虑：

```text
旧 conversation_summary
+
新的 old_messages
```

而不是只总结本次 old_messages？

### 练习 3

解释为什么：

```text
Summary
```

和：

```text
Structured State
```

应该同时存在。

分别适合保存什么？

### 练习 4

解释这个完整循环：

```text
build_context
↓
LLM回答
↓
current_query + answer加入messages
↓
messages过长
↓
summarize_history
↓
更新conversation_summary
↓
只保留recent messages
↓
下一轮
```

### 练习 5

为什么：

```text
Context Window很大
```

也不能得出：

```text
“所有东西都放进去最好”
```

？

除了“可能超长度”以外，再说至少两个原因。

做完这 5 题后，我们今天第三节就把这些代码**整理成一个真正能运行的 Mini Context Agent**，把 `state.py + context_manager.py + llm_client.py + main.py` 四个文件完整串起来。