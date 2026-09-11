可以。今天第一节我们专门讲 **Prompt Builder：把 Prompt 从“一大段字符串”升级成工程化组件**。

你先不用急着把它理解成什么复杂框架。今天这一节真正要解决的问题只有一个：

> **当 Prompt 越来越复杂以后，怎样让它更清楚、更容易修改、更容易复用，而不是把所有内容硬编码在 `main.py` 里。**

------

# 一、先看我们以前是怎么写 Prompt 的

最开始我们可能直接写：

```python
system_prompt = """
你是一名AI Agent课程老师。
请使用准确、通俗的中文回答用户问题。
"""
```

然后：

```python
messages = [
    {
        "role": "system",
        "content": system_prompt
    },
    {
        "role": "user",
        "content": current_query
    }
]
```

这种写法完全没问题。

对于一个简单 Chatbot：

```text
System Prompt
+
Current Query
```

已经够用了。

但是现在我们的系统开始复杂了。

以后可能需要：

```text
任务目标
用户背景
当前State
限制条件
Evidence
Tool信息
输出格式
JSON Schema
当前Query
```

如果全部写成：

```python
prompt = f"""
你是……
用户现在……
当前任务……
限制条件……
输出格式……
Schema……
Evidence……
"""
```

然后在项目里到处复制，维护起来会越来越困难。

------

# 二、为什么需要 Prompt Builder？

举个例子。

假设今天我们准备让 LLM 做：

```text
Task Analyzer
```

它的任务是分析用户问题。

你可能写：

```python
prompt = f"""
你是任务分析器。

用户问题：
{current_query}

请判断用户的任务类型、难度以及是否需要搜索。

输出JSON。
"""
```

过两天你又想增加：

```text
是否需要Planning
```

那就改 Prompt。

又过两天增加：

```text
输出必须符合Pydantic Schema
```

再改。

又想增加：

```text
不要回答用户问题，只做分析
```

继续改。

最后 Prompt 可能变成几百行。

所以我们希望：

```text
固定部分
+
动态部分
↓
统一交给一个函数/类构造
```

这就是：

Prompt Builder\boxed{\text{Prompt Builder}}

它本质上就是：

> **专门负责构造 Prompt 的 Python 代码。**

没有什么神秘的。

------

# 三、一个 Prompt 通常有哪些组成部分？

昨天我们已经学过：

Prompt=Instruction+Context+Input+Constraints+OutputFormat\boxed{ Prompt = Instruction + Context + Input + Constraints + Output Format }

现在把它放到 Task Analyzer 场景中。

------

## Instruction

告诉模型：

```text
你要干什么？
```

例如：

```text
你是一个任务分析器。
你的任务是分析用户请求，而不是直接回答用户。
```

------

## Context

告诉模型：

```text
当前有哪些背景信息？
```

例如：

```text
当前Agent支持：
- 普通回答
- 搜索
- 任务规划
```

以后也可能加入 State：

```text
用户当前正在学习Agent。
```

------

## Input

就是：

```text
用户这次真正提出的问题。
```

例如：

```text
帮我搜索2026年Agent推荐论文并总结趋势。
```

------

## Constraints

限制模型：

```text
不能干什么？
必须遵守什么？
```

例如：

```text
不要回答用户问题。
只分析任务。
difficulty只能是easy、medium、hard。
```

------

## Output Format

告诉模型：

```text
最终应该长什么样？
```

例如：

```json
{
  "intent": "research",
  "difficulty": "hard",
  "need_search": true,
  "need_planning": true
}
```

所以 Task Analyzer 的 Prompt 可以理解成：

```text
[INSTRUCTION]
你负责分析任务。

[CONTEXT]
Agent支持搜索和Planning。

[INPUT]
用户问题……

[CONSTRAINTS]
只分析，不回答。
difficulty只能……

[OUTPUT FORMAT]
必须输出JSON……
```

这就是一个结构化 Prompt。

------

# 四、第一版 Prompt Builder：最简单的函数

我们先别上类。

直接写一个函数：

```python
def build_task_analyzer_prompt(
    current_query: str
) -> str:

    prompt = f"""
[INSTRUCTION]
你是一个任务分析器。
你的任务是分析用户请求，
不要直接回答用户的问题。

[USER INPUT]
{current_query}

[CONSTRAINTS]
1. intent表示用户主要意图。
2. difficulty只能是easy、medium、hard。
3. need_search表示是否需要搜索外部信息。
4. need_planning表示是否需要拆分任务。
5. 只输出JSON，不要输出额外解释。

[OUTPUT FORMAT]
{{
    "intent": "string",
    "difficulty": "easy | medium | hard",
    "need_search": true,
    "need_planning": true
}}
"""

    return prompt
```

然后：

```python
prompt = build_task_analyzer_prompt(
    current_query="帮我研究最近两年的Agent推荐论文"
)
```

就会自动生成 Prompt。

------

# 五、这里为什么有 `{{` 和 `}}`？

你可能马上会注意到：

```python
{{
    "intent": "string"
}}
```

为什么不是：

```python
{
    "intent": "string"
}
```

因为外面用了：

```python
f"""
...
"""
```

在 f-string 中：

```python
{xxx}
```

表示：

> 把变量 `xxx` 的值插进来。

例如：

```python
name = "Tom"

text = f"你好，{name}"
```

得到：

```text
你好，Tom
```

但是我们现在真的想让 Prompt 里面出现 JSON 的：

```text
{
}
```

并不是插变量。

所以在 f-string 里面要写：

```python
{{
}}
```

最终生成出来的时候才是：

```text
{
}
```

这个以后你写 JSON Prompt 时会经常遇到。

------

# 六、但这一版还有一个问题

我们现在把：

```python
current_query
```

直接插到了一个大字符串里：

```python
f"""
...
[USER INPUT]
{current_query}
...
"""
```

能不能用？

可以。

但 Chat API 本来已经给我们提供了：

```text
system
user
assistant
```

不同角色。

所以实际上更好的方法通常不是：

```text
把所有东西拼成一个巨大字符串
```

而是：

```text
固定规则
→ system message

当前用户输入
→ user message
```

所以 Prompt Builder 更好的返回值可以不是：

```python
str
```

而是：

```python
list[dict]
```

也就是直接生成：

```python
messages
```

------

# 七、第二版：Prompt Builder 直接构造 messages

例如：

```python
def build_task_analyzer_messages(
    current_query: str
) -> list[dict]:

    system_prompt = """
[ROLE]
你是一个任务分析器。

[TASK]
分析用户请求，
但不要直接回答用户的问题。

[CONSTRAINTS]
1. difficulty只能是easy、medium、hard。
2. need_search必须是true或false。
3. need_planning必须是true或false。
4. 只返回JSON。
5. 不要添加额外说明。

[OUTPUT FORMAT]
{
    "intent": "string",
    "difficulty": "easy | medium | hard",
    "need_search": true,
    "need_planning": true
}
"""

    messages = [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": current_query
        }
    ]

    return messages
```

然后：

```python
messages = build_task_analyzer_messages(
    "帮我研究最近两年的Agent推荐论文"
)
```

得到：

```python
[
    {
        "role": "system",
        "content": "..."
    },
    {
        "role": "user",
        "content": "帮我研究最近两年的Agent推荐论文"
    }
]
```

再：

```python
result = await client.chat(
    messages
)
```

是不是已经和我们之前的 `LLMClient` 接起来了？

------

# 八、为什么这种写法更清晰？

因为职责非常明确：

```text
system
→ 告诉模型规则是什么

user
→ 告诉模型当前数据是什么
```

而不是：

```text
所有信息全部揉在一个字符串里
```

这也是我们昨天一直讲的：

Organize\boxed{\text{Organize}}

Context Engineering 不只是：

```text
挑哪些信息
```

还包括：

```text
这些信息怎么组织
```

------

# 九、现在出现一个非常重要的问题

我们已经有：

```python
ContextManager
```

现在又来了：

```python
PromptBuilder
```

你可能会问：

> 这两个东西是不是重复了？

这个问题非常关键。

------

# 十、ContextManager 和 PromptBuilder 到底有什么区别？

先看 ContextManager。

它主要解决：

WHAT\boxed{\text{WHAT}}

也就是：

> **这一次 LLM 应该看到哪些信息？**

例如 Writer 当前需要：

```text
user_query
evidence
summary
constraints
```

但是不需要：

```text
50篇raw tool_results
error logs
```

所以：

```text
ContextManager
→ 决定“拿什么”
```

------

PromptBuilder 主要解决：

HOW\boxed{\text{HOW}}

也就是：

> **这些信息怎么组织成 Prompt / messages？**

例如：

```text
[ROLE]
...

[TASK]
...

[EVIDENCE]
...

[CONSTRAINTS]
...

[OUTPUT FORMAT]
...
```

所以：

```text
PromptBuilder
→ 决定“怎么写、怎么组织”
```

这两个可以这样理解：

```text
AgentState
    ↓
ContextManager
    ↓
选择：
query + evidence + constraints
    ↓
PromptBuilder
    ↓
组织成：
system/user messages
    ↓
LLMClient
```

所以一个非常好记的区别：

ContextManager=选材料\boxed{ ContextManager = 选材料 }PromptBuilder=按格式把材料做成菜\boxed{ PromptBuilder = 按格式把材料做成菜 }

------

# 十一、举个你更熟悉的论文例子

假设 State 里面有：

```python
state = {
    "user_query": "分析哪些Agent技术适合LLM4CDSR",
    "tool_results": ["50篇论文"],
    "evidence": [
        "Evidence A",
        "Evidence B",
        "Evidence C"
    ],
    "constraints": {
        "language": "Chinese"
    }
}
```

Writer 工作。

------

ContextManager 先决定：

```text
需要：
user_query
evidence
constraints

不需要：
50篇原始tool_results
```

得到：

```python
selected_context = {
    "user_query": "...",
    "evidence": [
        "Evidence A",
        "Evidence B",
        "Evidence C"
    ],
    "constraints": {
        "language": "Chinese"
    }
}
```

这一步是：

Select\boxed{\text{Select}}

------

然后 PromptBuilder：

```text
[USER QUESTION]
分析哪些Agent技术适合LLM4CDSR

[EVIDENCE]
1. Evidence A
2. Evidence B
3. Evidence C

[CONSTRAINTS]
使用中文回答

[INSTRUCTION]
只能根据证据进行分析……
```

这一步是：

Organize\boxed{\text{Organize}}

所以二者并不完全一样。

------

# 十二、不过小项目里一定要拆两个类吗？

不一定。

这是非常重要的工程思想。

我们现在为了学习，把概念拆开：

```text
ContextManager
PromptBuilder
```

让你知道它们分别负责什么。

但是如果项目非常小：

```python
class ContextManager:

    def build_context(...):
        ...
```

一个类同时完成：

```text
选择
+
组织
```

也完全合理。

所以不要陷入：

> “是不是每个概念都必须创建一个 class？”

不是。

架构是为了降低复杂度，不是为了制造复杂度\boxed{\text{架构是为了降低复杂度，不是为了制造复杂度}}

等以后你的 Research Agent 真正变复杂：

```text
Planner Prompt
Searcher Prompt
Reader Prompt
Writer Prompt
Critic Prompt
```

再单独抽：

```python
PromptBuilder
```

就非常有价值。

------

# 十三、现在进一步升级：不要手写 Output Format

刚才我们写：

```text
[OUTPUT FORMAT]
{
    "intent": "string",
    "difficulty": "easy | medium | hard",
    ...
}
```

但是问题来了。

假设 Python 中真正定义：

```python
class TaskAnalysis(BaseModel):
    intent: str
    difficulty: Literal[
        "easy",
        "medium",
        "hard"
    ]
    need_search: bool
    need_planning: bool
```

如果哪一天你改成：

```python
difficulty: Literal[
    "simple",
    "medium",
    "complex"
]
```

但忘了改 Prompt。

就出现：

```text
Python Schema：
simple / medium / complex

Prompt：
easy / medium / hard
```

二者冲突。

这很危险。

------

# 十四、所以让 Pydantic Schema 自动生成 Prompt

先定义：

```python
from typing import Literal
from pydantic import BaseModel


class TaskAnalysis(BaseModel):

    intent: str

    difficulty: Literal[
        "easy",
        "medium",
        "hard"
    ]

    need_search: bool

    need_planning: bool
```

然后：

```python
schema = TaskAnalysis.model_json_schema()
```

我们之前已经学过：

```python
model_json_schema()
```

意思：

Pydantic模型定义→JSONSchema\boxed{ Pydantic模型定义 \rightarrow JSON Schema }

------

# 十五、Schema 大概长这样

```python
{
    "properties": {
        "intent": {
            "type": "string"
        },
        "difficulty": {
            "enum": [
                "easy",
                "medium",
                "hard"
            ]
        },
        "need_search": {
            "type": "boolean"
        },
        "need_planning": {
            "type": "boolean"
        }
    },
    ...
}
```

这样就不用自己手工维护 Output Format 了。

------

# 十六、但是直接 `str(schema)` 不太漂亮

可以：

```python
str(schema)
```

但得到的是 Python dict 风格：

```text
{'properties': {'intent': ...}}
```

我们希望变成标准、漂亮的 JSON：

```json
{
  "properties": {
    ...
  }
}
```

所以可以：

```python
import json


schema_text = json.dumps(
    schema,
    ensure_ascii=False,
    indent=2
)
```

这里你应该认识：

```python
json.dumps()
```

意思是：

Python对象→JSON字符串\boxed{ Python对象 \rightarrow JSON字符串 }

------

`ensure_ascii=False`：

```python
ensure_ascii=False
```

主要让中文不要变成：

```text
\u4f60\u597d
```

而是正常显示：

```text
你好
```

------

`indent=2`：

```python
indent=2
```

负责漂亮缩进。

让 Schema 更容易阅读。

------

# 十七、于是 Prompt Builder 可以写成这样

```python
import json

from schemas import TaskAnalysis


def build_task_analyzer_messages(
    current_query: str
) -> list[dict]:

    schema = (
        TaskAnalysis.model_json_schema()
    )

    schema_text = json.dumps(
        schema,
        ensure_ascii=False,
        indent=2
    )

    system_prompt = f"""
[ROLE]
你是一个任务分析器。

[TASK]
分析用户提出的请求。
不要回答用户问题本身。

[CONSTRAINTS]
1. 请准确判断任务意图。
2. 根据任务复杂程度判断difficulty。
3. 判断是否需要外部搜索。
4. 判断是否需要任务规划。
5. 只输出符合Schema的JSON。
6. 不要输出Markdown代码块。
7. 不要输出额外解释。

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
```

这已经是一个比较像样的 Prompt Builder 了。

------

# 十八、为什么说它“工程化”了？

因为现在 Schema 的唯一真实来源是：

```python
class TaskAnalysis(BaseModel):
```

Prompt 不再手写一份假的格式。

也就是：

```text
TaskAnalysis
    ↓
model_json_schema()
    ↓
JSON Schema
    ↓
Prompt Builder
    ↓
LLM
```

以后你修改：

```python
TaskAnalysis
```

Prompt 中 Schema 也跟着变化。

这种设计有一个很重要的工程思想：

Single Source of Truth\boxed{\text{Single Source of Truth}}

中文就是：

> **单一事实来源。**

也就是说：

```text
TaskAnalysis的结构到底是什么？
```

不要：

```text
Pydantic写一份
Prompt再写一份
README再维护一份
```

而应该尽可能：

```text
Pydantic Model
→ 唯一正式定义
```

其他地方从它生成。

------

# 十九、把完整执行流程串一下

用户：

```text
帮我搜索最近两年的Agent推荐论文，
并分析哪些方向适合LLM4CDSR。
```

先：

```python
messages = build_task_analyzer_messages(
    current_query
)
```

Prompt Builder 得到：

```text
system
→ Task Analyzer规则 + JSON Schema

user
→ 用户当前问题
```

然后：

```python
raw_output = await client.chat(
    messages
)
```

LLM 可能返回：

```json
{
  "intent": "research",
  "difficulty": "hard",
  "need_search": true,
  "need_planning": true
}
```

但是注意：

> 到现在它仍然只是一个 **字符串**。

也就是说：

```python
type(raw_output)
```

大概率还是：

```python
str
```

不是：

```python
TaskAnalysis
```

所以：

```text
LLM Output
↓
还没有验证
↓
还不能完全相信
```

这恰好就是今天第二节要解决的问题：

Structured Output + Pydantic Validation\boxed{\text{Structured Output + Pydantic Validation}}

------

# 二十、这一节你先真正记住 4 个关系

```text
AgentState
→ 保存当前任务的信息

ContextManager
→ 决定这次LLM需要哪些信息

PromptBuilder
→ 决定这些信息怎么组织成Prompt/messages

LLMClient
→ 把messages真正发送给LLM API
```

最终：

```text
AgentState
     ↓
ContextManager
     ↓
Selected Context
     ↓
PromptBuilder
     ↓
messages
     ↓
LLMClient
     ↓
LLM
```

以后到了复杂 Agent：

```text
Planner
Searcher
Reader
Writer
Critic
```

每个 Node 都可能有自己的 Prompt Builder。

------

# 第一节练习

今天第一轮练习我们做 5 道，但是都不难。

1. 为什么不建议大型 Agent 项目把所有 Prompt 全都直接硬编码在 `main.py` 中？
2. 用自己的话区分：

```text
ContextManager
```

和：

```text
PromptBuilder
```

分别主要负责什么？

1. 为什么 Task Analyzer 的：

```python
current_query
```

更适合放在：

```python
{
    "role": "user"
}
```

而 Task Analyzer 的固定规则更适合放在：

```python
{
    "role": "system"
}
```

？

1. 解释这一段：

```python
schema = TaskAnalysis.model_json_schema()

schema_text = json.dumps(
    schema,
    ensure_ascii=False,
    indent=2
)
```

每一行分别干什么。

1. 为什么：

```text
直接根据 Pydantic Model 生成 JSON Schema
```

通常比：

```text
Pydantic写一套结构
+
Prompt里手写另一套Output Format
```

更可靠？

你把这 5 题回答完，我们第二节就正式把刚才的：

```text
LLM返回JSON字符串
```

升级成：

```text
LLM Output
↓
Pydantic Validation
↓
真正的 TaskAnalysis 对象
```

也就是今天很关键的 **Structured Output 实战**。