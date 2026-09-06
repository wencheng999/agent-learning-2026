这组整体完成得很好，**练习 1、2、3 都是正确的**。练习 4 只有一处判断错了，而且这个地方正好可以检验你是不是真的理解了“默认值”。

## 练习 1：完全正确 ✅

你说：

```python
name: str
```

表示 `name` 最终应该是 `str`，并且**没有默认值，因此调用时必须提供**。

```python
name: str = "Tom"
```

表示最终应该是 `str`，如果不提供，默认：

```python
name = "Tom"
```

而：

```python
name: str | None = None
```

表示最终可以是：

```text
str
或
None
```

并且不传时默认：

```python
None
```

这个理解完全正确。

------

## 练习 2：完全正确 ✅

```python
top_k: int = Field(
    default=5,
    ge=1,
    le=20
)
```

就是：

1≤topk≤201\leq top_k\leq20

同时：

```text
default=5 → 不传时默认5
ge=1      → greater than or equal，大于等于1
le=20     → less than or equal，小于等于20
```

没问题。

------

# 练习 3：代码正确 ✅

你的：

```python
from pydantic import BaseModel
from pydantic import Field


class SearchInput(BaseModel):
    query: str = Field(
        min_length=1,
    )

    top_k: int = Field(
        default=5,
        ge=1,
        le=10,
    )

    language: str | None = Field(
        default=None,
    )
```

完全符合要求。

甚至可以写得稍微紧凑一点：

```python
from pydantic import BaseModel, Field


class SearchInput(BaseModel):
    query: str = Field(min_length=1)

    top_k: int = Field(
        default=5,
        ge=1,
        le=10
    )

    language: str | None = None
```

最后：

```python
language: str | None = None
```

本身就已经足够，因为题目没有要求 `language` 额外的 `Field` 约束。

但你原来的写法也完全正确。

------

# 练习 4：前 3、最后 1 个正确，中间第 4 个判断错了

前面：

```python
SearchInput(
    query="Agent",
    top_k=5
)
```

✅ 通过。

因为：

```text
query长度 >= 1
top_k在1~10之间
language没传 → 默认None
```

------

```python
SearchInput(
    query="Agent",
    top_k=0
)
```

❌ `ValidationError`

因为：

0<10<1

------

```python
SearchInput(
    query="Agent",
    top_k=100
)
```

❌ `ValidationError`

因为：

100>10100>10

这些你都答对。

------

## 你错的是这一道

你认为：

```python
SearchInput(
    query="Agent"
)
```

不会通过，因为没传 `top_k`。

其实：

它会通过\boxed{\text{它会通过}}

为什么？

因为你已经定义了：

```python
top_k: int = Field(
    default=5,
    ge=1,
    le=10
)
```

里面有：

```python
default=5
```

所以不传：

```python
top_k
```

Pydantic 自动使用：

```python
top_k = 5
```

同时：

```python
language
```

也没传，但是：

```python
language: str | None = Field(
    default=None
)
```

所以：

```python
language = None
```

最终实际得到：

```python
SearchInput(
    query="Agent",
    top_k=5,
    language=None
)
```

所以完全合法。

这个地方一定记住：

> **只要字段有默认值，调用的时候通常就可以省略。**

------

最后：

```python
SearchInput(
    query="",
    top_k=5
)
```

❌ `ValidationError`

因为：

```python
min_length=1
```

但：

```python
len("")
```

是：

```text
0
```

所以你答对。

------

因此这一课你基本可以认为：

默认值 + Optional + Field 基础通过\boxed{\text{默认值 + Optional + Field 基础通过}}

现在进入今天第三课。

# 第三课：嵌套模型 + `model_dump()` + `model_validate()`

这一课非常重要，因为以后 LLM Structured Output 不会永远只有：

```json
{
  "query": "Agent",
  "top_k": 5
}
```

真实数据往往是一层套一层的。

比如 LLM 可能返回：

```json
{
  "tool": "search",
  "arguments": {
    "query": "Agent",
    "top_k": 5
  }
}
```

你看：

```text
最外层
│
├── tool
│
└── arguments
      │
      ├── query
      └── top_k
```

这就是：

嵌套数据\boxed{\text{嵌套数据}}

------

# 一、先看普通 dict 的嵌套

比如：

```python
data = {
    "tool": "search",
    "arguments": {
        "query": "Agent",
        "top_k": 5
    }
}
```

如果想拿：

```text
Agent
```

需要：

```python
data["arguments"]["query"]
```

因为：

```text
data
 ↓
arguments
 ↓
query
```

------

# 二、Pydantic 也可以嵌套

我们先定义：

```python
from pydantic import BaseModel, Field


class SearchArguments(BaseModel):
    query: str
    top_k: int = Field(
        default=5,
        ge=1,
        le=10
    )
```

这个你已经完全会了。

然后再定义：

```python
class ToolCall(BaseModel):
    tool: str
    arguments: SearchArguments
```

重点：

```python
arguments: SearchArguments
```

以前是：

```python
age: int
```

现在变成：

```python
arguments: SearchArguments
```

意思是：

> `arguments` 这个字段本身不是简单字符串或整数，而应该符合 `SearchArguments` 模型。

------

# 三、怎么创建？

可以：

```python
tool_call = ToolCall(
    tool="search",
    arguments=SearchArguments(
        query="Agent",
        top_k=5
    )
)
```

然后：

```python
print(tool_call.tool)
print(tool_call.arguments)
```

得到类似：

```text
search
query='Agent' top_k=5
```

如果想访问 `query`：

```python
print(tool_call.arguments.query)
```

得到：

```text
Agent
```

注意现在不是：

```python
tool_call["arguments"]["query"]
```

而是：

```python
tool_call.arguments.query
```

因为这是 Pydantic 对象。

------

# 四、其实甚至可以直接传字典

Pydantic 很方便的一点是：

```python
tool_call = ToolCall(
    tool="search",
    arguments={
        "query": "Agent",
        "top_k": 5
    }
)
```

虽然：

```python
arguments
```

传进去的是：

```python
dict
```

但是 Pydantic 看到：

```python
arguments: SearchArguments
```

会自动把：

```python
{
    "query": "Agent",
    "top_k": 5
}
```

解析成：

```python
SearchArguments(...)
```

所以：

```python
print(type(tool_call.arguments))
```

会得到类似：

```text
<class '__main__.SearchArguments'>
```

而不是普通 `dict`。

------

# 五、嵌套验证会一层一层执行

假设：

```python
tool_call = ToolCall(
    tool="search",
    arguments={
        "query": "Agent",
        "top_k": 100
    }
)
```

最外层：

```text
tool = "search"
```

没问题。

但是进入：

```text
arguments
```

以后发现：

```python
top_k = 100
```

而：

topk≤10top_k\leq10

所以最终整个：

```python
ToolCall(...)
```

都会：

```text
ValidationError
```

执行过程：

```text
ToolCall
   ↓
检查tool
   ↓
检查arguments
   ↓
SearchArguments
   ↓
检查query
   ↓
检查top_k
   ↓
100 > 10 ❌
   ↓
ValidationError
```

这就是嵌套 Pydantic Model 的价值。

------

# 六、为什么 Agent 特别需要嵌套模型？

未来一个 Tool Call 很可能就是：

```json
{
  "tool": "search_paper",
  "arguments": {
    "query": "Agent",
    "top_k": 5
  }
}
```

或者 Planning：

```json
{
  "goal": "研究Agent推荐",
  "steps": [
    {
      "id": 1,
      "action": "search"
    },
    {
      "id": 2,
      "action": "summarize"
    }
  ]
}
```

这些都是：

```text
对象
里面套对象
里面套列表
列表里面再套对象
```

所以 Pydantic 嵌套模型以后会非常常见。

------

# 七、接下来是 `model_dump()`

假设：

```python
tool_call = ToolCall(
    tool="search",
    arguments={
        "query": "Agent",
        "top_k": 5
    }
)
```

现在：

```python
tool_call
```

是：

```text
ToolCall对象
```

如果想重新变成 Python 字典：

```python
data = tool_call.model_dump()
```

然后：

```python
print(data)
print(type(data))
```

会类似：

```python
{
    "tool": "search",
    "arguments": {
        "query": "Agent",
        "top_k": 5
    }
}
```

以及：

```text
<class 'dict'>
```

所以：

model_dump()：Pydantic Model → Python dict\boxed{\text{model\_dump()：Pydantic Model → Python dict}}

------

# 八、为什么叫 `dump`？

还记得之前：

```python
json.dump()
```

吗？

这里也是类似：

> 把模型中的结构化数据“导出”出来。

所以：

```text
Pydantic对象
     ↓
model_dump()
     ↓
Python dict
```

------

# 九、为什么 Agent 要把模型变回 dict？

因为很多地方需要：

```text
dict
```

比如：

```python
requests.post(
    url,
    json=data
)
```

这里：

```python
json=
```

通常可以接收 Python 字典。

所以：

```text
Pydantic Model
      ↓
model_dump()
      ↓
dict
      ↓
HTTP JSON Body
```

很自然。

------

# 十、举个完整例子

```python
tool_call = ToolCall(
    tool="search",
    arguments={
        "query": "Agent",
        "top_k": 5
    }
)

data = tool_call.model_dump()

print(data)
```

得到：

```python
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
requests.post(
    url,
    json=data
)
```

就能作为 HTTP Body 发出去。

看到 Day 2 的知识又接上了吧。

------

# 十一、还有 `model_dump_json()`

如果你想直接得到：

```text
JSON字符串
```

可以：

```python
json_text = tool_call.model_dump_json()
```

比如：

```python
print(type(json_text))
```

得到：

```text
<class 'str'>
```

所以：

```text
model_dump()
→ Python dict

model_dump_json()
→ JSON string
```

这个和以前：

```text
json.dumps()
```

很像。

------

# 十二、接下来是 `model_validate()`

这个名字非常直观：

```python
model_validate()
```

就是：

> 使用某个 Pydantic Model 去验证一份外部数据。

假设 API / LLM 给我们：

```python
raw_data = {
    "tool": "search",
    "arguments": {
        "query": "Agent",
        "top_k": 5
    }
}
```

这是：

```text
dict
```

我们想检查它是不是合法 ToolCall。

可以：

```python
tool_call = ToolCall.model_validate(
    raw_data
)
```

然后：

```python
print(type(tool_call))
```

得到：

```text
ToolCall
```

所以：

model_validate()：外部数据 → 校验 → Pydantic Model\boxed{\text{model\_validate()：外部数据 → 校验 → Pydantic Model}}

------

# 十三、和直接 `ToolCall(**raw_data)` 有什么区别？

你前面也可以：

```python
tool_call = ToolCall(
    **raw_data
)
```

这同样能够验证。

而：

```python
ToolCall.model_validate(raw_data)
```

语义更加清楚：

> “我现在有一份外部数据，请按照 ToolCall Schema 验证。”

以后处理：

```text
API Response
LLM Structured Output
数据库结果
外部JSON
```

时经常会看到：

```python
model_validate()
```

------

# 十四、完整 LLM 数据流已经出现了

假设 LLM 返回：

```python
raw_output = {
    "tool": "search",
    "arguments": {
        "query": "最新Agent论文",
        "top_k": 5
    }
}
```

第一步：

```python
tool_call = ToolCall.model_validate(
    raw_output
)
```

变成：

```text
经过校验的 ToolCall对象
```

然后：

```python
tool_call.tool
```

得到：

```text
search
```

以及：

```python
tool_call.arguments.query
```

得到：

```text
最新Agent论文
```

于是可以：

```python
search_paper(
    query=tool_call.arguments.query,
    top_k=tool_call.arguments.top_k
)
```

你看，这已经开始非常像真正 Tool Calling 了。

------

# 十五、把整个过程画出来

```text
LLM / API 返回
      ↓
Python dict
      ↓
ToolCall.model_validate()
      ↓
Pydantic验证
      ↓
合法？
 ┌────┴────┐
 │         │
是         否
↓          ↓
ToolCall  ValidationError
对象
↓
读取字段
↓
执行Tool
```

反方向：

```text
Pydantic对象
      ↓
model_dump()
      ↓
Python dict
      ↓
HTTP / JSON / 保存文件
```

所以两个方向一定记住：

model_validate(): 外部数据 → Model\boxed{\text{model\_validate(): 外部数据 → Model}}model_dump(): Model → dict\boxed{\text{model\_dump(): Model → dict}}

------

# 十六、这节再补一个列表嵌套

假设：

```python
class Paper(BaseModel):
    title: str
    year: int
```

然后搜索结果：

```python
class SearchResult(BaseModel):
    query: str
    papers: list[Paper]
```

这里：

```python
papers: list[Paper]
```

意思：

> `papers` 是一个列表，而且列表中的每一个元素都必须符合 `Paper` 模型。

数据：

```python
result = SearchResult(
    query="Agent",
    papers=[
        {
            "title": "Paper A",
            "year": 2026
        },
        {
            "title": "Paper B",
            "year": 2025
        }
    ]
)
```

Pydantic 自动得到：

```text
SearchResult
│
├── query
└── papers
     │
     ├── Paper对象
     │
     └── Paper对象
```

所以：

```python
result.papers[0].title
```

得到：

```text
Paper A
```

这以后处理 Agent Search Results 特别常见。

------

# 第三课练习

这次 4 道。

### 练习 1

解释：

```python
class SearchArguments(BaseModel):
    query: str
    top_k: int = 5


class ToolCall(BaseModel):
    tool: str
    arguments: SearchArguments
```

为什么：

```python
arguments
```

不是普通 `dict`？

------

### 练习 2

如果：

```python
tool_call = ToolCall(
    tool="search",
    arguments={
        "query": "Agent",
        "top_k": 5
    }
)
```

那么下面分别是什么类型？

```python
type(tool_call)

type(tool_call.tool)

type(tool_call.arguments)

type(tool_call.arguments.top_k)
```

------

### 练习 3

下面两个分别干什么？

```python
tool_call.model_dump()
```

和：

```python
ToolCall.model_validate(raw_data)
```

重点说明转换方向。

------

### 练习 4

自己写：

```python
class Paper(BaseModel)
```

包含：

```text
title: str
year: int
```

再写：

```python
class SearchResult(BaseModel)
```

包含：

```text
query: str
papers: list[Paper]
```

然后创建两个 Paper：

```text
Agent Paper A，2026
Agent Paper B，2025
```

最后打印：

```text
第一篇论文的title
第二篇论文的year
```

你把这一轮做完，下一课我们会继续学 **自定义验证 Validator + `Literal` + 更严格的 Tool Schema**。那之后 Pydantic 基础就基本齐了。