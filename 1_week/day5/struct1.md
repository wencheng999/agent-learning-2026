这 3 道都答对了，而且你已经把 Streaming 的完整数据链说得比较清楚了。只有练习 3 里一个小词修正：`client.stream()` 是“**流式请求方法**”，不是“流行请求方法” 😂。除此之外没有大的问题。

你现在已经理解：

```text
非流式
message.content
→ 完整回答

流式
delta.content
→ 当前新增的一小块
```

以及：

```text
流式显示
→ print(content)

完整答案保存
→ full_content += content
```

所以：

Day 5 Streaming 基础通过\boxed{\text{Day 5 Streaming 基础通过}}

下面进入今天最后、也是非常重要的一课。

# Day 5 第五课：Structured Output + Pydantic

这部分会正式把 Day 3 和 Day 5 接起来。

Day 3 我们写过：

```python
llm_output = {
    "tool": "search",
    "arguments": {
        "query": "Agent",
        "top_k": 5
    }
}
```

但那个：

```python
llm_output
```

是我们**手写假装 LLM 返回的**。

今天我们要解决：

> 怎么让真实 LLM 返回程序容易处理的结构化数据？

------

# 一、普通 LLM 输出有什么问题？

假设我们问模型：

> 用户说“帮我找 5 篇 Agent 论文”，请判断使用哪个工具。

LLM 默认可能回答：

```text
我认为应该调用 search 工具，
搜索关键词是 Agent，
并返回 5 个结果。
```

这对人很好理解。

但是对 Python 来说非常麻烦。

你要怎么得到：

```python
tool = ?
query = ?
top_k = ?
```

难道自己：

```text
字符串切割
正则表达式
关键词搜索
```

吗？

很不稳定。

------

# 二、我们更希望 LLM 返回这种东西

```json
{
  "tool": "search",
  "arguments": {
    "query": "Agent",
    "top_k": 5
  }
}
```

然后：

```python
data = json.loads(answer)
```

得到：

```python
dict
```

再：

```python
decision = ToolDecision.model_validate(data)
```

于是：

```python
decision.tool
```

直接得到：

```text
search
```

这就是：

Structured Output\boxed{\text{Structured Output}}

------

# 三、Structured Output 是什么？

可以简单理解为：

> 不让 LLM 随便输出自然语言，而是要求它按照我们规定的数据结构输出。

例如普通回答：

```text
建议调用搜索工具，返回5篇论文。
```

结构化回答：

```json
{
  "tool": "search",
  "query": "Agent",
  "top_k": 5
}
```

所以：

```text
Free-form Output
→ 给人阅读方便

Structured Output
→ 给程序处理方便
```

Agent 非常依赖后者。

------

# 四、为什么 Agent 特别需要 Structured Output？

因为 Agent 经常要求 LLM 做的不是：

> “写一段文章。”

而是：

```text
选择哪个Tool？
参数是什么？

下一步Action是什么？

任务是否完成？

搜索关键词是什么？

规划步骤有哪些？
```

例如：

```json
{
  "action": "search",
  "query": "Agent",
  "top_k": 5
}
```

程序直接就能根据：

```python
action
```

执行下一步。

因此：

LLM负责决策+StructuredOutput负责把决策交给程序\boxed{ LLM负责决策 + Structured Output负责把决策交给程序 }

------

# 五、第一种最容易理解的方法：Prompt 要求 JSON

先定义我们 Day 3 的模型：

```python
from typing import Literal

from pydantic import BaseModel


class ToolDecision(BaseModel):
    tool: Literal[
        "search",
        "calculator"
    ]

    arguments: dict
```

然后获得它的 Schema：

```python
schema = ToolDecision.model_json_schema()
```

你已经学过：

```text
Pydantic Model
↓
model_json_schema()
↓
JSON Schema
```

------

# 六、把 Schema 告诉 LLM

例如：

```python
import json


schema_text = json.dumps(
    schema,
    ensure_ascii=False,
    indent=2
)
```

然后构造 System Message：

```python
system_prompt = f"""
你负责选择合适的工具。

你必须只返回 JSON，
不要添加 Markdown，
不要添加解释文字。

输出必须符合下面的 JSON Schema：

{schema_text}
"""
```

这里其实就是：

```text
Pydantic
↓
JSON Schema
↓
Prompt
↓
LLM
```

LLM 就知道：

> 我的输出应该是什么结构。

------

# 七、构造 messages

例如用户：

```text
帮我找5篇Agent论文
```

我们：

```python
messages = [
    {
        "role": "system",
        "content": system_prompt
    },
    {
        "role": "user",
        "content": "帮我找5篇Agent论文"
    }
]
```

然后：

```python
answer = await client.chat(
    messages
)
```

假设 LLM 很听话，返回：

```python
answer = """
{
  "tool": "search",
  "arguments": {
    "query": "Agent",
    "top_k": 5
  }
}
"""
```

注意：

answer 现在仍然是 str\boxed{\text{answer 现在仍然是 str}}

这是特别重要的一点。

------

# 八、LLM 返回 JSON，不代表 Python 里已经是 dict

比如：

```python
answer = '{"name": "Tom", "age": 20}'
```

虽然长得像 JSON，

但：

```python
print(type(answer))
```

还是：

```text
<class 'str'>
```

因为网络里返回给我们的 content 是一段文本。

所以：

```text
LLM生成JSON文本
↓
Python拿到str
```

接下来必须解析。

------

# 九、方法一：`json.loads()`

你 Day 1 学过：

```python
data = json.loads(answer)
```

完成：

```text
JSON String
↓
json.loads()
↓
Python dict
```

例如：

```python
data = json.loads(answer)

print(type(data))
```

得到：

```text
<class 'dict'>
```

再：

```python
decision = ToolDecision.model_validate(
    data
)
```

完成：

```text
dict
↓
Pydantic验证
↓
ToolDecision对象
```

------

# 十、完整数据流

```text
用户：
帮我找5篇Agent论文
        ↓
LLM
        ↓
JSON字符串
        ↓
'{
  "tool": "search",
  ...
}'
        ↓
json.loads()
        ↓
Python dict
        ↓
ToolDecision.model_validate()
        ↓
ToolDecision对象
        ↓
decision.tool
decision.arguments
```

这样 Day 1、Day 3、Day 5 全部接起来了。

------

# 十一、但 Pydantic v2 还有一个更方便的方法

其实可以直接：

```python
decision = ToolDecision.model_validate_json(
    answer
)
```

第一次看到：

```python
model_validate_json()
```

它可以理解成：

> 直接读取 JSON 字符串，并按照当前 Pydantic Model 进行解析和验证。

所以：

```text
JSON String
↓
model_validate_json()
↓
解析 JSON
+
Pydantic验证
↓
ToolDecision对象
```

这相当于把：

```python
data = json.loads(answer)

decision = ToolDecision.model_validate(
    data
)
```

合成了一步。

------

# 十二、几个方法现在一定不要混

你已经学了：

### `model_validate()`

```python
ToolDecision.model_validate(data)
```

输入一般是：

```python
dict
```

方向：

```text
Python data
↓
Pydantic Model
```

------

### `model_validate_json()`

```python
ToolDecision.model_validate_json(
    json_text
)
```

输入是：

```text
JSON字符串
```

方向：

```text
JSON String
↓
解析 + 验证
↓
Pydantic Model
```

------

### `model_dump()`

```python
decision.model_dump()
```

方向：

```text
Pydantic Model
↓
dict
```

------

### `model_json_schema()`

```python
ToolDecision.model_json_schema()
```

方向：

```text
Pydantic类的定义
↓
JSON Schema
```

现在四个是不是已经形成完整循环了？

```text
                    model_json_schema()
Pydantic Model定义 ─────────────────────→ Schema
                                            ↓
                                           LLM
                                            ↓
                                      JSON字符串
                                            ↓
                                model_validate_json()
                                            ↓
                                      Pydantic对象
                                            ↓
                                      model_dump()
                                            ↓
                                           dict
```

这张图非常重要。

------

# 十三、如果 LLM 输出错误怎么办？

假设：

```python
answer = """
{
  "tool": "weather",
  "arguments": {}
}
"""
```

但我们要求：

```python
tool: Literal[
    "search",
    "calculator"
]
```

那么：

```python
ToolDecision.model_validate_json(
    answer
)
```

会：

```text
ValidationError
```

因为：

```text
weather
```

不在允许范围。

这就是：

LLM输出不能直接相信，仍然要验证\boxed{\text{LLM输出不能直接相信，仍然要验证}}

------

# 十四、如果连 JSON 都写错了呢？

比如模型返回：

```text
我建议使用search工具。

{
  "tool": "search"
}
```

这已经不是一个纯 JSON 文档。

那么：

```python
ToolDecision.model_validate_json(
    answer
)
```

也会失败。

再比如：

~~~text
```json
{
  "tool": "search"
}
模型加了 Markdown 代码块。

人看起来很好看。

但对 JSON Parser 来说：

```text
```json
~~~

这些内容不是 JSON。

也可能解析失败。

------

# 十五、所以 Prompt 里为什么经常强调

例如：

```text
只输出JSON。
不要解释。
不要添加Markdown代码块。
```

就是为了减少：

~~~text
好的，以下是结果：
```json
...
这种额外文本。

---

# 十六、但是 Prompt 约束不是 100% 可靠

这一点特别重要。

你告诉 LLM：

> 只输出 JSON。

不代表它**永远百分之百遵守**。

它仍可能：

```text
漏字段
多字段
类型错误
格式错误
加解释
加Markdown
~~~

所以工程上：

```text
Prompt
→ 尽量让模型正确输出

Pydantic
→ 对输出进行最后验证
```

也就是你前面学的：

不要完全信任 LLM 输出\boxed{\text{不要完全信任 LLM 输出}}

------

# 十七、现在可以写一个 `structured_chat()`

我们在 `LLMClient` 外面先写一个简单函数：

```python
from pydantic import ValidationError


async def get_tool_decision(
    client: LLMClient,
    user_input: str
) -> ToolDecision | None:
```

然后：

```python
schema = ToolDecision.model_json_schema()
```

转换：

```python
schema_text = json.dumps(
    schema,
    ensure_ascii=False,
    indent=2
)
```

构造 messages：

```python
messages = [
    {
        "role": "system",
        "content": f"""
你负责选择工具。

只能返回JSON。
不要返回任何额外文字。

输出必须符合：

{schema_text}
"""
    },
    {
        "role": "user",
        "content": user_input
    }
]
```

调用：

```python
answer = await client.chat(
    messages
)
```

------

# 十八、然后验证

```python
if answer is None:
    return None
```

然后：

```python
try:
    decision = (
        ToolDecision.model_validate_json(
            answer
        )
    )

    return decision

except ValidationError as e:
    print(
        f"LLM结构化输出验证失败：{e}"
    )
    return None
```

------

# 十九、完整代码

```python
import json

from pydantic import ValidationError


async def get_tool_decision(
    client: LLMClient,
    user_input: str
) -> ToolDecision | None:

    schema = (
        ToolDecision.model_json_schema()
    )

    schema_text = json.dumps(
        schema,
        ensure_ascii=False,
        indent=2
    )

    messages = [
        {
            "role": "system",
            "content": f"""
你负责选择合适的工具。

只能返回 JSON。
不要添加任何解释文字。
不要使用 Markdown 代码块。

输出必须符合下面的 Schema：

{schema_text}
"""
        },
        {
            "role": "user",
            "content": user_input
        }
    ]

    answer = await client.chat(
        messages
    )

    if answer is None:
        return None

    try:
        return ToolDecision.model_validate_json(
            answer
        )

    except ValidationError as e:
        print(
            "结构化输出验证失败："
        )
        print(e)

        return None
```

------

# 二十、调用

例如：

```python
decision = await get_tool_decision(
    client,
    "帮我找5篇Agent论文"
)
```

如果成功：

```python
print(decision.tool)
print(decision.arguments)
```

可能：

```text
search
{'query': 'Agent', 'top_k': 5}
```

然后是不是可以直接接昨天的：

```python
execute_tool(...)
```

了？

当然可以。

------

# 二十一、真正的最小 Agent 链路出来了

现在整个流程：

```text
用户：
帮我找5篇Agent论文
        ↓
LLM
        ↓
Structured Output
        ↓
{
 tool: search,
 arguments: {...}
}
        ↓
Pydantic
        ↓
ToolDecision
        ↓
Tool Registry
        ↓
SearchInput验证
        ↓
search_paper()
        ↓
ToolResult
```

这已经非常非常接近一个真正 Agent 的核心了。

你前五天其实已经手写出了它的大部分组件。

------

# 二十二、但要区分 Structured Output 和 Tool Calling

这点现在就讲清楚。

我们现在做的是：

```text
Prompt要求LLM
↓
返回某种JSON
↓
我们自己解析
↓
自己执行Tool
```

这叫：

Structured Output\boxed{\text{Structured Output}}

而真正的：

```text
Tool Calling / Function Calling
```

通常是模型 API 原生支持：

```text
程序把Tool定义交给模型
↓
模型专门返回Tool Call
↓
Tool Name + Arguments
↓
程序执行
```

不是简单靠 Prompt：

> “请给我 JSON。”

所以：

```text
Structured Output
≠
Tool Calling
```

但它们联系非常紧密。

你可以理解：

```text
Structured Output
→ 学会让LLM输出机器可读结构

Tool Calling
→ 专门用于LLM选择并调用工具的标准化机制
```

我们 Week 2 会正式深入 Tool Calling。

------

# 二十三、还有更强的 Structured Output

很多现代 LLM API 还支持：

```text
原生 JSON Mode
Schema-constrained Output
Native Structured Output
```

也就是 API 层面直接要求模型遵循 Schema，而不是只靠 System Prompt。

这种方式通常比：

```text
“请只输出JSON”
```

更加可靠。

不过：

> 不同模型提供商的具体请求字段不完全一样。

等你确定实际使用哪个 API 时，我们再针对它的官方接口写，不在这里背某一家 SDK 的参数。

今天先掌握最底层、通用的：

```text
JSON
+
Pydantic
+
Schema
+
Validation
```

最重要。

------

# 二十四、最后再连接 Day 3 的 Tool Registry

假设：

```python
decision = await get_tool_decision(
    client,
    "计算10加20"
)
```

LLM 返回：

```json
{
  "tool": "calculator",
  "arguments": {
    "a": 10,
    "b": 20
  }
}
```

然后：

```python
tool_info = TOOL_REGISTRY[
    decision.tool
]
```

找到：

```text
calculator
+
CalculatorInput
```

验证：

```python
args = tool_info[
    "input_model"
].model_validate(
    decision.arguments
)
```

执行：

```python
result = tool_info["function"](
    **args.model_dump()
)
```

最终：

```text
30.0
```

所以现在：

```text
真实 LLM
↓
Structured Output
↓
Pydantic
↓
Tool Registry
↓
Python Tool
```

已经彻底接上了。

------

# Day 5 最后一轮练习

### 练习 1

解释下面四个方法的区别和方向：

```python
model_json_schema()
model_validate()
model_validate_json()
model_dump()
```

------

### 练习 2

假设：

```python
answer = """
{
  "tool": "search",
  "arguments": {
    "query": "Agent",
    "top_k": 5
  }
}
"""
```

现在 `answer` 是什么 Python 类型？

执行：

```python
decision = ToolDecision.model_validate_json(
    answer
)
```

以后：

```python
decision
```

是什么类型？

------

### 练习 3

为什么已经在 Prompt 中明确要求：

```text
只输出JSON
```

以后，我们仍然需要：

```python
ToolDecision.model_validate_json(...)
```

？

------

### 练习 4

解释：

```text
Structured Output
```

和：

```text
Tool Calling
```

现在你理解的区别是什么？

------

### 练习 5

用自己的话解释整个链：

```text
Pydantic Model
→ model_json_schema()
→ Schema
→ 给LLM
→ LLM返回JSON字符串
→ model_validate_json()
→ Pydantic对象
→ Tool Registry
→ Tool执行
```

第 5 题最重要。

这轮做完，**Day 5 就可以正式结课，同时整个“预备周”也基本完成了。** 明天开始我们就能真正进入 Week 1 的 **LLM 应用基础 / Prompt / Context Engineering** 主线。