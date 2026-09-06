这轮整体做得很好，说明你已经开始真正理解 **Pydantic 的嵌套模型** 了。四道题里，练习 2 和练习 4 基本完全正确；练习 1 需要补充一个关键点，练习 3 的 `model_validate()` 还差“返回什么”这一层。另外你代码里有一行多余的 `openpyxl` 导入，要删掉。

## 练习 1：基本正确，还要补一个关键点

你说：

> `arguments` 是用继承 `BaseModel` 的 `SearchArguments` 类创建的，所以会检查属性是否合法。

这个方向是对的。

更完整的原因是这里：

```python
class ToolCall(BaseModel):
    tool: str
    arguments: SearchArguments
```

已经明确告诉 Pydantic：

```python
arguments: SearchArguments
```

意思是：

> `arguments` 最终必须是一个 `SearchArguments` 对象。

所以即使创建时传进去的是普通字典：

```python
tool_call = ToolCall(
    tool="search",
    arguments={
        "query": "Agent",
        "top_k": 5
    }
)
```

Pydantic 也会：

```text
dict
 ↓
按照 SearchArguments 结构验证
 ↓
转换
 ↓
SearchArguments 对象
```

因此：

```python
type(tool_call.arguments)
```

不是：

```python
dict
```

而是：

```text
SearchArguments
```

这个“**嵌套字典自动解析成嵌套 Pydantic Model**”是这一课最重要的地方之一。

------

## 练习 2：全部正确 ✅

你的判断：

```python
type(tool_call)
```

是：

```text
ToolCall
type(tool_call.tool)
```

是：

```text
str
type(tool_call.arguments)
```

是：

```text
SearchArguments
type(tool_call.arguments.top_k)
```

是：

```text
int
```

全部正确。

数据结构可以想成：

```text
tool_call
│
├── tool
│   └── str
│
└── arguments
    └── SearchArguments
        ├── query
        │   └── str
        └── top_k
            └── int
```

------

## 练习 3：`model_dump()` 正确，`model_validate()` 再补一步

你说：

> `tool_call.model_dump()` 将 `ToolCall` 类型转为 `dict`。

正确：

```text
Pydantic Model
      ↓
model_dump()
      ↓
Python dict
```

例如：

```python
data = tool_call.model_dump()

print(type(data))
```

得到：

```text
<class 'dict'>
```

第二个：

```python
ToolCall.model_validate(raw_data)
```

你说：

> 验证 `raw_data` 是不是符合 `ToolCall` 格式。

这个也对，但还缺一个非常重要的结果：

> **如果验证成功，它会返回一个真正的 `ToolCall` 对象。**

例如：

```python
raw_data = {
    "tool": "search",
    "arguments": {
        "query": "Agent",
        "top_k": 5
    }
}

tool_call = ToolCall.model_validate(raw_data)
```

现在：

```python
type(tool_call)
```

就是：

```text
ToolCall
```

所以完整方向是：

```text
外部 dict
   ↓
model_validate()
   ↓
验证
   ↓
成功
   ↓
ToolCall 对象
```

如果失败：

```text
ValidationError
```

所以记住这两个方向：

model_validate(): 外部数据 → Pydantic Model\boxed{\text{model\_validate(): 外部数据 → Pydantic Model}}model_dump(): Pydantic Model → dict\boxed{\text{model\_dump(): Pydantic Model → dict}}

以后处理 LLM Structured Output 时特别重要。

------

# 练习 4：主体完全正确 ✅

你的代码：

```python
from pydantic import BaseModel

class Paper(BaseModel):
    title: str
    year: int

class SearchResult(BaseModel):
    query: str
    papers: list[Paper]

search1 = SearchResult(
    query="打印论文",
    papers=[
        {
            "title": "Agent Paper A",
            "year": 2026
        },
        {
            "title": "Agent Paper B",
            "year": 2025
        },
    ]
)

print(search1.papers[0].title)
print(search1.papers[1].year)
```

完全正确。

输出：

```text
Agent Paper A
2025
```

而且这里很关键：

你传的是：

```python
papers=[
    {"title": "...", "year": 2026},
    {"title": "...", "year": 2025}
]
```

里面明明是：

```text
dict
```

但因为：

```python
papers: list[Paper]
```

所以 Pydantic 会自动变成：

```text
list
│
├── Paper对象
└── Paper对象
```

因此：

```python
search1.papers[0].title
```

才能直接访问。

------

## 不过你第一行这个要删掉

你写了：

```python
from openpyxl.styles.builtins import title
```

这个和当前程序完全没有关系。

而且你的：

```python
title: str
```

也根本不需要从 `openpyxl` 导入 `title`。

直接：

```python
from pydantic import BaseModel
```

就够了。

以后看到 IDE 自动导入一些奇怪东西时要注意。

比如你只是写：

```python
title: str
```

这里的：

```text
title
```

只是你自己定义的字段名，不需要 import。

这个和你之前莫名其妙出现：

```python
from sympy.codegen.ast import none
```

是类似问题。

所以有一个很实用的习惯：

> **如果 IDE 自动加了一个你完全不知道为什么存在的 import，先别急着接受。**

------

这轮可以认为：

Pydantic 嵌套模型 + model_dump + model_validate 基础通过\boxed{\text{Pydantic 嵌套模型 + model\_dump + model\_validate 基础通过}}

下面继续今天的第四课，也是 Pydantic 非常重要的一块。

# 第四课：`Literal` + 自定义 Validator + 更严格的 Tool Schema

我们现在已经可以定义：

```python
class ToolCall(BaseModel):
    tool: str
    arguments: SearchArguments
```

但这里存在一个问题。

如果 LLM 返回：

```python
{
    "tool": "abc",
    "arguments": {
        "query": "Agent",
        "top_k": 5
    }
}
```

从类型上看：

```python
"abc"
```

确实是：

```python
str
```

所以：

```python
tool: str
```

会通过。

但是我们的 Agent 根本没有：

```text
abc Tool
```

怎么办？

这就是 `Literal` 的作用。

------

# 一、`Literal`：限制只能取几个固定值

第一天你其实已经见过：

```python
from typing import Literal
```

现在它和 Pydantic 结合起来会非常实用。

比如 Agent 只有三个动作：

```text
search
calculator
answer
```

可以：

```python
from typing import Literal
from pydantic import BaseModel


class ToolCall(BaseModel):
    tool: Literal[
        "search",
        "calculator",
        "answer"
    ]
```

那么：

```python
ToolCall(tool="search")
```

✅ 可以。

```python
ToolCall(tool="calculator")
```

✅ 可以。

但是：

```python
ToolCall(tool="abc")
```

❌ `ValidationError`

因为：

```text
abc
```

不在允许集合里。

所以：

Literal = 字段只能从指定值中选择\boxed{\text{Literal = 字段只能从指定值中选择}}

------

# 二、为什么 Tool Calling 特别需要 Literal？

假设 Agent 现在只有：

```text
Search Tool
Calculator Tool
```

那么最差的设计：

```python
tool: str
```

意味着 LLM 可以返回任何字符串：

```text
search
calculator
weather
abc
hello
随便什么
```

而：

```python
tool: Literal[
    "search",
    "calculator"
]
```

就把合法动作空间限制住了。

可以理解成：

```text
LLM 输出
   ↓
tool = ?
   ↓
只能是：
search / calculator
   ↓
其他全部拒绝
```

这能显著降低 Tool 参数错误。

------

# 三、完整一点的 ToolCall

可以写：

```python
from typing import Literal

from pydantic import BaseModel, Field


class SearchArguments(BaseModel):
    query: str = Field(
        min_length=1
    )

    top_k: int = Field(
        default=5,
        ge=1,
        le=10
    )


class ToolCall(BaseModel):
    tool: Literal["search"]
    arguments: SearchArguments
```

现在：

```python
ToolCall(
    tool="search",
    arguments={
        "query": "Agent",
        "top_k": 5
    }
)
```

可以。

但是：

```python
ToolCall(
    tool="weather",
    arguments={
        "query": "Agent",
        "top_k": 5
    }
)
```

直接验证失败。

------

# 四、但 `min_length=1` 还有一个漏洞

之前：

```python
query: str = Field(
    min_length=1
)
```

可以拦住：

```python
query=""
```

但：

```python
query="     "
```

怎么办？

这有 5 个空格。

所以：

```python
len("     ")
```

是：

```text
5
```

满足：

```python
min_length=1
```

但实际上这个 query 没有意义。

这时候就需要：

# 自定义 Validator

------

# 五、`field_validator`

Pydantic v2 可以：

```python
from pydantic import (
    BaseModel,
    Field,
    field_validator
)
```

然后：

```python
class SearchArguments(BaseModel):

    query: str = Field(
        min_length=1
    )

    top_k: int = Field(
        default=5,
        ge=1,
        le=10
    )

    @field_validator("query")
    @classmethod
    def validate_query(
        cls,
        value: str
    ) -> str:

        if not value.strip():
            raise ValueError(
                "query不能为空"
            )

        return value
```

第一次看有点多，我们拆开。

------

# 六、`@field_validator("query")`

这一行：

```python
@field_validator("query")
```

意思：

> 下面这个验证函数专门负责验证 `query` 字段。

也就是说：

```text
输入 query
 ↓
Pydantic基础验证
 ↓
field_validator
 ↓
我们自己的额外规则
```

------

# 七、为什么有一个 `@`？

这叫：

```text
Decorator
装饰器
```

你以后 Agent 框架里会非常经常看到：

```python
@tool
@classmethod
@staticmethod
@field_validator
```

今天先不要深入装饰器原理。

暂时理解：

> `@field_validator("query")` 是在告诉 Pydantic：“下面这个函数是 query 的验证器。”

就够了。

------

# 八、`value` 是谁？

这里：

```python
def validate_query(
    cls,
    value: str
) -> str:
```

其中：

```python
value
```

就是当前传进来的：

```python
query
```

例如：

```python
SearchArguments(
    query="Agent"
)
```

那么：

```text
value = "Agent"
```

如果：

```python
SearchArguments(
    query="   "
)
```

那么：

```text
value = "   "
```

------

# 九、`value.strip()`

第一天其实见过：

```python
strip()
```

它会去掉字符串两端空白。

所以：

```python
"   ".strip()
```

得到：

```python
""
```

于是：

```python
if not value.strip():
```

就是：

> 去掉空格以后，如果什么都没剩，说明 query 实际为空。

然后：

```python
raise ValueError(
    "query不能为空"
)
```

Pydantic 会把这个错误整合成：

```text
ValidationError
```

------

# 十、为什么最后一定 `return value`？

如果合法：

```python
return value
```

把验证后的值交回 Pydantic。

例如：

```text
Agent
 ↓
validator
 ↓
通过
 ↓
return "Agent"
 ↓
保存到 query
```

如果不 `return`，就可能出问题。

所以自定义 Validator 常见结构：

```python
@field_validator("字段名")
@classmethod
def xxx(cls, value):
    if 不合法:
        raise ValueError(...)

    return value
```

先把这个套路记住。

------

# 十一、甚至可以顺便清洗数据

比如我们希望：

```python
query="   Agent   "
```

最后自动变成：

```python
"Agent"
```

可以：

```python
@field_validator("query")
@classmethod
def validate_query(
    cls,
    value: str
) -> str:

    value = value.strip()

    if not value:
        raise ValueError(
            "query不能为空"
        )

    return value
```

这样：

```python
data = SearchArguments(
    query="   Agent   "
)

print(data.query)
```

得到：

```text
Agent
```

所以 Validator 不只是：

```text
检查
```

还可以做：

```text
清洗 + 标准化
```

------

# 十二、再加一个严格规则：禁止多余字段

假设 Tool Schema 是：

```python
class SearchArguments(BaseModel):
    query: str
    top_k: int
```

结果 LLM 返回：

```python
{
    "query": "Agent",
    "top_k": 5,
    "abc": 123
}
```

这个：

```python
abc
```

根本没有定义。

Pydantic 默认情况下，对额外字段的处理可能不是你想要的严格模式。

在 Tool Calling 里，我们通常希望：

> LLM 只能输出 Schema 允许的字段。

可以使用：

```python
from pydantic import ConfigDict
```

然后：

```python
class SearchArguments(BaseModel):

    model_config = ConfigDict(
        extra="forbid"
    )

    query: str
    top_k: int = 5
```

现在如果：

```python
SearchArguments(
    query="Agent",
    top_k=5,
    abc=123
)
```

就会：

```text
ValidationError
```

因为：

```text
abc
```

是额外字段。

------

# 十三、`extra="forbid"` 是什么意思？

就是：

禁止模型中未声明的额外字段\boxed{\text{禁止模型中未声明的额外字段}}

对于 Agent Tool Schema 很有意义。

比如我们规定：

```text
search tool
只接受：
query
top_k
```

LLM 却生成：

```json
{
  "query": "Agent",
  "top_k": 5,
  "temperature": 100,
  "whatever": "abc"
}
```

严格模式可以直接拒绝。

------

# 十四、一个比较像真实 Tool 的版本

```python
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator
)


class SearchArguments(BaseModel):

    model_config = ConfigDict(
        extra="forbid"
    )

    query: str = Field(
        description="需要搜索的关键词"
    )

    top_k: int = Field(
        default=5,
        ge=1,
        le=10,
        description="返回结果数量"
    )

    @field_validator("query")
    @classmethod
    def validate_query(
        cls,
        value: str
    ) -> str:

        value = value.strip()

        if not value:
            raise ValueError(
                "query不能为空"
            )

        return value


class ToolCall(BaseModel):

    model_config = ConfigDict(
        extra="forbid"
    )

    tool: Literal["search"]

    arguments: SearchArguments
```

现在这个 Schema 已经可以防：

```text
错误的Tool名字
错误的字段类型
top_k范围错误
query空字符串
query纯空格
额外未知字段
```

这已经开始非常接近真实 Tool Calling 的参数校验了。

------

# 今天这一课的练习

你做下面 4 个就行。

第一题，解释：

```python
tool: Literal[
    "search",
    "calculator"
]
```

和：

```python
tool: str
```

有什么区别。

第二题，下面哪些能通过？

```python
class Action(BaseModel):
    action: Literal[
        "search",
        "answer"
    ]
```

分别判断：

```python
Action(action="search")
Action(action="answer")
Action(action="calculator")
Action(action="abc")
```

第三题，自己写一个：

```python
class SearchInput(BaseModel):
```

要求 `query` 是字符串，并用 `field_validator` 做到：

```text
" Agent "
→ 最终保存成 "Agent"

"     "
→ ValidationError
```

第四题，解释：

```python
model_config = ConfigDict(
    extra="forbid"
)
```

有什么用，以及为什么在 **LLM Tool Calling** 里会比较重要。

这一轮做完，我们下一课再讲一下 **`model_json_schema()`**。那个非常关键，因为你会第一次看到：

> **Pydantic Model 是怎么真正变成一份 LLM 能理解的 Tool Schema 的。**

到了那里，Pydantic 和 Tool Calling 就彻底接上了。