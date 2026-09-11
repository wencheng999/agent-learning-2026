这 5 题整体回答得很好。你现在已经开始形成“**数据放哪里、谁负责选、谁负责组织、谁负责通信**”这种工程思维了。我们把两个小地方校准一下，然后直接进入今天第二节。

## 先检查第一节练习

练习 1 正确。小项目把 Prompt 写在 `main.py` 没问题，但随着以后出现：

```text
Planner Prompt
Searcher Prompt
Reader Prompt
Writer Prompt
Critic Prompt
```

继续全部硬编码在 `main.py`，就会导致：

```text
main.py
既负责流程
又负责Prompt
又负责State
又负责LLM调用
```

职责越来越混乱。

所以我们才逐渐拆成：

```text
main.py
→ 控制流程

ContextManager
→ 选择信息

PromptBuilder
→ 组织Prompt

LLMClient
→ 调用模型
```

------

练习 2 完全正确。

你这句话甚至可以直接记：

ContextManager 决定拿什么，PromptBuilder 决定怎么组织\boxed{\text{ContextManager 决定拿什么，PromptBuilder 决定怎么组织}}

例如：

```text
State中有：
query
plan
50篇tool_results
8条evidence
errors
```

ContextManager 可能决定：

```text
Writer只拿：
query + evidence
```

PromptBuilder 再组织成：

```text
[USER QUERY]
...

[EVIDENCE]
...

[INSTRUCTION]
...
```

很好。

------

练习 3 思路正确，但你的代码格式有一个重要问题。

你写成：

```python
{
    "role": "user",
    "role": "system"
}
```

一个字典不能这样同时表示两个角色，因为同一个 key：

```python
"role"
```

重复了。

在 Python 中后面的值还会覆盖前面的值。

实际上应该是：

```python
[
    {
        "role": "system",
        "content": "固定规则"
    },
    {
        "role": "user",
        "content": "当前用户问题"
    }
]
```

也就是说：

一条 message = 一个 role + 一个 content\boxed{\text{一条 message = 一个 role + 一个 content}}

多条 message 再组成：

```python
list[dict]
```

另外你说“LLM 就按照这种格式接收”，对于我们现在使用的 Chat API 场景可以这样理解。更本质的原因是：

```text
system
→ 稳定规则、身份、任务约束

user
→ 当前用户提供的输入
```

这种角色分工让模型更容易区分：

> 哪些是“应该遵守的规则”，哪些是“当前需要处理的数据”。

------

练习 4 基本完全正确。

```python
schema = TaskAnalysis.model_json_schema()
```

表示：

```text
Pydantic Model
↓
JSON Schema对应的Python dict
```

然后：

```python
schema_text = json.dumps(
    schema,
    ensure_ascii=False,
    indent=2
)
```

表示：

```text
Python dict
↓
JSON格式字符串
```

例如：

```python
{"type": "string"}
```

在 Python 里面是 `dict`。

经过 `json.dumps()`：

```python
'{"type": "string"}'
```

变成 `str`。

不过有一个小细节：

> 并不是说 LLM API 只能接收 JSON 字符串。

我们这里是为了把 Schema **嵌入 Prompt 的 `content` 中**，而 `content` 是文本，所以转换成字符串更方便。

------

练习 5 完全正确。

这就是：

Single Source of Truth\boxed{\text{Single Source of Truth}}

以后真正的结构定义只有：

```python
class TaskAnalysis(BaseModel):
    ...
```

其他地方：

```text
JSON Schema
Prompt中的Output Schema
运行时Validation
```

尽可能都从它生成。

这样能减少：

Schema Drift\boxed{\text{Schema Drift}}

也就是“程序定义改了，但 Prompt 忘了跟着改”的问题。

第一节正式通过。✅

------

# Week 1 · Day 3 第二节：Structured Output + Pydantic Validation

现在进入今天非常关键的一步。

前面我们的 LLM 是：

```text
用户问题
↓
LLM
↓
一段自然语言答案
```

例如：

```python
answer = await client.chat(messages)
```

返回：

```text
这个任务比较复杂，我认为应该先进行搜索……
```

人看得懂。

但是程序不好处理。

假设 Agent 后面需要根据结果决定：

```text
要不要搜索？
要不要规划？
任务难不难？
```

程序总不能这样：

```python
if "我认为应该搜索" in answer:
```

这种方法非常脆弱。

所以我们希望 LLM 返回：

```json
{
  "intent": "research",
  "difficulty": "hard",
  "need_search": true,
  "need_planning": true
}
```

这样程序就可以直接：

```python
if result.need_search:
    ...
```

这就是：

Structured Output\boxed{\text{Structured Output}}

------

# 一、Structured Output 到底解决什么问题？

普通自然语言：

```text
这个问题涉及最近论文，因此我认为需要进行外部搜索，
而且任务比较复杂，建议先规划。
```

人一眼就懂。

程序却得自己“猜”。

结构化输出：

```json
{
  "intent": "research",
  "difficulty": "hard",
  "need_search": true,
  "need_planning": true
}
```

程序马上知道：

```python
need_search == True
need_planning == True
```

所以：

Structured Output=把LLM输出变成程序容易消费的数据\boxed{ Structured\ Output = 把LLM输出变成程序容易消费的数据 }

这对 Agent 极其重要。

因为 Agent 后面经常需要：

```text
LLM判断
↓
程序读取判断结果
↓
执行下一步
```

------

# 二、先定义 TaskAnalysis

创建：

```text
schemas.py
```

写：

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

这就是我们希望模型最终提供的数据结构。

比如：

```python
TaskAnalysis(
    intent="research",
    difficulty="hard",
    need_search=True,
    need_planning=True
)
```

------

# 三、第一步：Prompt 引导模型输出 JSON

我们上一节已经写：

```python
messages = build_task_analyzer_messages(
    current_query
)
```

里面告诉模型：

```text
只输出符合Schema的JSON。
不要输出Markdown。
不要输出额外解释。
```

然后：

```python
raw_output = await client.chat(
    messages
)
```

模型可能返回：

```python
raw_output = """
{
    "intent": "research",
    "difficulty": "hard",
    "need_search": true,
    "need_planning": true
}
"""
```

注意现在：

```python
type(raw_output)
```

依然是：

```python
str
```

虽然它“长得像 JSON”。

这一点很重要。

------

# 四、长得像 JSON，不等于已经是 Python 对象

比如：

```python
raw_output = """
{
    "need_search": true
}
"""
```

这是：

```python
str
```

不是：

```python
dict
```

所以不能直接：

```python
raw_output["need_search"]
```

因为字符串不能按照 JSON key 这样访问。

我们必须：

```text
JSON字符串
↓
解析
↓
Python对象
```

而且还需要：

```text
验证结构
```

这就是 Pydantic 出场的地方。

------

# 五、使用 `model_validate_json()`

直接：

```python
analysis = (
    TaskAnalysis.model_validate_json(
        raw_output
    )
)
```

这一行非常重要。

可以理解为：

```text
raw_output
JSON字符串
      ↓
model_validate_json()
      ↓
先解析JSON
      ↓
检查字段
      ↓
检查类型
      ↓
检查Literal限制
      ↓
TaskAnalysis对象
```

所以：

```python
type(analysis)
```

现在是：

```python
TaskAnalysis
```

------

# 六、现在就能使用属性了

例如：

```python
print(analysis.intent)
```

得到：

```text
research
print(analysis.difficulty)
```

得到：

```text
hard
print(analysis.need_search)
```

得到：

```text
True
```

甚至：

```python
if analysis.need_search:
    print("下一步应该执行搜索")
```

这就是为什么 Agent 特别依赖 Structured Output。

因为现在：

```text
LLM的语言输出
↓
变成程序的控制信号
```

------

# 七、这已经有一点“Agent 决策”的味道了

例如：

```python
if analysis.need_search:
    print("调用搜索工具")

if analysis.need_planning:
    print("先让Planner拆解任务")
```

未来就可能变成：

```text
用户问题
↓
Analyzer
↓
need_search = True
↓
Search Tool
```

或者：

```text
用户问题
↓
Analyzer
↓
need_search = False
↓
直接回答
```

所以你现在虽然还没有正式学习 Tool Calling，但已经开始接触 Agent 的核心模式：

LLM负责判断，程序负责执行\boxed{\text{LLM负责判断，程序负责执行}}

这句话一定要记住。

------

# 八、`model_validate_json()` 到底帮我们验证什么？

假设正确：

```json
{
  "intent": "research",
  "difficulty": "hard",
  "need_search": true,
  "need_planning": true
}
```

通过。

但如果 LLM 返回：

```json
{
  "intent": "research",
  "difficulty": "super_hard",
  "need_search": true,
  "need_planning": true
}
```

注意：

```python
difficulty: Literal[
    "easy",
    "medium",
    "hard"
]
```

根本不允许：

```text
super_hard
```

于是：

```python
TaskAnalysis.model_validate_json(
    raw_output
)
```

就会失败。

这就是：

Validation\boxed{\text{Validation}}

------

# 九、为什么这是好事，而不是坏事？

初学的时候可能会觉得：

> 报错不是不好吗？

这里恰恰相反。

假设不验证。

LLM 返回：

```json
{
  "difficulty": "超级无敌难"
}
```

程序继续往后执行。

后面：

```python
if difficulty == "hard":
    ...
```

永远匹配不到。

问题可能到很后面才暴露。

而 Pydantic 是：

```text
数据一进程序
↓
马上检查
↓
不合法
↓
立即报错
```

这叫：

Fail Fast\boxed{\text{Fail Fast}}

尽早失败。

比让错误数据偷偷流入后面的 Agent 流程安全得多。

------

# 十、捕获 `ValidationError`

如果我们直接：

```python
analysis = TaskAnalysis.model_validate_json(
    raw_output
)
```

验证失败后，程序可能直接抛异常。

所以：

```python
from pydantic import ValidationError
```

然后：

```python
try:

    analysis = (
        TaskAnalysis.model_validate_json(
            raw_output
        )
    )

except ValidationError as e:

    print(
        "LLM输出验证失败：",
        e
    )
```

这和你之前学过的异常处理完全接上了。

------

# 十一、注意还有一种错误：JSON 本身就坏了

LLM 可能输出：

```text
{
    "intent": "research",
    "difficulty": "hard",
```

少了后面。

这都不是完整 JSON。

`model_validate_json()` 同样会失败。

因此它不只是检查：

```text
difficulty是否合法
```

它还负责：

```text
JSON能不能被解析
字段是否存在
字段类型是否正确
字段约束是否合法
```

所以非常方便。

------

# 十二、完整代码现在是这样

```python
from pydantic import ValidationError

from schemas import TaskAnalysis


async def analyze_task(
    client,
    current_query: str
) -> TaskAnalysis | None:

    messages = (
        build_task_analyzer_messages(
            current_query
        )
    )

    raw_output = await client.chat(
        messages
    )

    if raw_output is None:
        return None

    try:

        analysis = (
            TaskAnalysis.model_validate_json(
                raw_output
            )
        )

        return analysis

    except ValidationError as e:

        print(
            "Structured Output验证失败：",
            e
        )

        return None
```

这个函数非常值得理解。

------

# 十三、逐行理解 `analyze_task()`

输入：

```python
client
```

负责调用 LLM。

输入：

```python
current_query
```

是用户当前问题。

先：

```python
messages = build_task_analyzer_messages(
    current_query
)
```

构造 Prompt。

然后：

```python
raw_output = await client.chat(
    messages
)
```

获得 LLM 原始文本。

如果 API 本身失败：

```python
if raw_output is None:
    return None
```

否则：

```python
TaskAnalysis.model_validate_json(
    raw_output
)
```

做：

```text
解析 + 验证
```

成功：

```python
return analysis
```

失败：

```python
return None
```

所以整个函数的类型：

```python
-> TaskAnalysis | None
```

非常合理。

------

# 十四、这个返回类型你现在应该能读懂了

```python
async def analyze_task(
    ...
) -> TaskAnalysis | None:
```

表示这个函数最终可能：

```text
成功
→ TaskAnalysis

失败
→ None
```

比如：

```python
analysis = await analyze_task(
    client,
    current_query
)
```

后面必须先判断：

```python
if analysis is None:
    print("任务分析失败")
    return
```

然后才能安全：

```python
print(
    analysis.need_search
)
```

------

# 十五、`model_validate()` 和 `model_validate_json()` 再彻底区分一次

这个很容易混。

如果你已经有 Python dict：

```python
data = {
    "intent": "research",
    "difficulty": "hard",
    "need_search": True,
    "need_planning": True
}
```

用：

```python
analysis = TaskAnalysis.model_validate(
    data
)
```

因为：

```text
Python dict
↓
Pydantic Model
```

------

如果你现在有 JSON 字符串：

```python
raw_output = """
{
    "intent": "research",
    "difficulty": "hard",
    "need_search": true,
    "need_planning": true
}
"""
```

用：

```python
analysis = (
    TaskAnalysis.model_validate_json(
        raw_output
    )
)
```

因为：

```text
JSON string
↓
解析
↓
Pydantic Model
```

所以记：

```text
dict
→ model_validate()

JSON string
→ model_validate_json()
```

------

# 十六、那么 `json.loads()` 呢？

你可能会想到我们之前学过：

```python
json.loads()
```

能不能这样：

```python
data = json.loads(
    raw_output
)

analysis = TaskAnalysis.model_validate(
    data
)
```

完全可以。

它实际上就是分成两步：

```text
JSON String
↓
json.loads()
↓
Python dict
↓
model_validate()
↓
TaskAnalysis
```

而：

```python
TaskAnalysis.model_validate_json(
    raw_output
)
```

帮我们把这个流程结合起来了。

所以对于这种情况，通常更方便。

------

# 十七、然后把 TaskAnalysis 放入 State

现在终于跟昨天的：

```python
AgentState
```

接上。

原来：

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

今天增加：

```python
task_analysis: TaskAnalysis | None = None
```

完整：

```python
from pydantic import BaseModel, Field

from schemas import TaskAnalysis


class AgentState(BaseModel):

    messages: list[dict] = Field(
        default_factory=list
    )

    conversation_summary: str = ""

    constraints: dict = Field(
        default_factory=dict
    )

    task_analysis: TaskAnalysis | None = None
```

注意：

```python
= None
```

别忘了。

前面我们学过 Pydantic v2：

```python
task_analysis: TaskAnalysis | None
```

表示：

> 值允许是 `TaskAnalysis` 或 `None`。

但不代表：

> 创建对象时可以不传。

所以我们写：

```python
task_analysis: TaskAnalysis | None = None
```

才真正表示：

```text
这个字段可以暂时不存在结果
默认就是None
```

------

# 十八、Analyzer 完成以后 Update State

```python
analysis = await analyze_task(
    client,
    current_query
)
```

成功：

```python
if analysis is not None:

    state.task_analysis = analysis
```

于是：

```text
LLM原始输出
↓
Pydantic验证
↓
TaskAnalysis对象
↓
写入AgentState
```

State 可能变成：

```python
AgentState(
    messages=[],
    conversation_summary="",
    constraints={
        "language": "Chinese"
    },
    task_analysis=TaskAnalysis(
        intent="research",
        difficulty="hard",
        need_search=True,
        need_planning=True
    )
)
```

这时候 Agent 程序就真正“知道”：

```text
这是research任务
难度hard
需要search
需要planning
```

这里的“知道”严格来说是：

> **这些结构化判断结果已经被 Agent 程序保存到了 State。**

------

# 十九、现在把数据流完整连起来

以前：

```text
User Query
↓
LLM
↓
Natural Language Answer
```

今天已经升级成：

```text
User Query
      ↓
Prompt Builder
      ↓
Analyzer Messages
      ↓
LLMClient
      ↓
LLM
      ↓
raw_output : str
      ↓
Pydantic Validation
      ↓
TaskAnalysis
      ↓
Update AgentState
```

然后未来：

```text
AgentState.task_analysis
        ↓
need_search ?
   /             \
 True            False
  ↓                ↓
Search Tool     Direct Answer
```

到这里已经开始非常接近 Agent 了。

------

# 二十、但是现在还有一个现实问题

我们假设模型非常听话，返回：

```json
{
  "intent": "research",
  "difficulty": "hard",
  "need_search": true,
  "need_planning": true
}
```

可真实模型有时候会返回：

~~~text
当然可以，以下是分析结果：

```json
{
  "intent": "research",
  "difficulty": "hard",
  "need_search": true,
  "need_planning": true
}
或者：

```json
{
  "intent": "research",
  "difficulty": "very_hard",
  "need_search": true,
  "need_planning": true
}
~~~

那么：

```python
model_validate_json()
```

就可能失败。

这时候怎么办？

不是简单：

```text
失败
→ 放弃整个任务
```

而可能：

```text
第一次输出
↓
Validation失败
↓
把错误告诉LLM
↓
让它Repair
↓
第二次输出
↓
再次Validation
```

这就是我们今天下一节要学的：

Validation + Retry + Repair\boxed{\text{Validation + Retry + Repair}}

------

# 第二节练习

1. 为什么普通自然语言回答不适合作为 Agent 后续程序逻辑的主要控制信号，而 Structured Output 更适合？
2. 假设：

```python
raw_output = """
{
    "intent": "research",
    "difficulty": "hard",
    "need_search": true,
    "need_planning": true
}
"""
```

为什么它看起来是 JSON，但 `type(raw_output)` 仍然是 `str`？

1. 分别解释：

```python
TaskAnalysis.model_validate(data)
```

和：

```python
TaskAnalysis.model_validate_json(raw_output)
```

适合处理什么输入。

1. 为什么 Pydantic 检测到：

```json
"difficulty": "super_hard"
```

后直接报错，反而是好事？

1. 请你用自己的话解释这一整条链：

```text
User Query
→ PromptBuilder
→ LLM
→ raw_output
→ Pydantic Validation
→ TaskAnalysis
→ Update AgentState
→ 后续Agent根据task_analysis继续执行
```

你把这 5 道做完，我们下一节就专门处理一个真实 Agent 开发中非常常见的问题：**LLM 输出不符合 Schema 时，怎样 Retry 和 Repair，而不是直接整个程序失败。**