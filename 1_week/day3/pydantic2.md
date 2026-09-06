这 4 道题整体都答得很好，说明你已经把 **`BaseModel`、字段类型、自动转换、`ValidationError`** 这几个核心点理解了。只有练习 1 里“强制要求”这个说法需要稍微改得更准确一点。

### 练习 1

你写的：

```python
class User(BaseModel):
    name: str
    age: int
```

其中 `User` 是你定义的 Pydantic 数据模型类，`BaseModel` 是 Pydantic 提供的基础模型类，继承它以后，`User` 就获得了数据解析和校验能力。

你说：

> `name: str` 强制要求字符串，`age: int` 强制要求整数。

这里更准确的说法应该是：

> `name` 期望最终得到 `str`，`age` 期望最终得到 `int`。

因为 Pydantic 默认不是“只要原始类型不一致就立即报错”，而是会先尝试合理转换。

例如：

```python
User(
    name="Tom",
    age="20"
)
```

虽然 `"20"` 原始类型是：

```python
str
```

但是可以转换成：

```python
20
```

所以最终：

```python
type(user.age)
```

还是：

```text
<class 'int'>
```

因此更准确的是：

Pydantic 默认要求“验证后的最终类型符合定义”\boxed{\text{Pydantic 默认要求“验证后的最终类型符合定义”}}

而不是要求“输入时原始类型必须完全一致”。

如果以后我们使用严格模式：

```python
strict=True
```

才会更接近你说的“必须本来就是这个类型”。

------

练习 2 和练习 3 都完全正确。你已经理解了：

```text
"20"
→ 可以转换
→ int 20
→ 验证成功
```

而：

```text
"abc"
→ 无法转换成 int
→ ValidationError
```

练习 4 的代码也完全正确：

```python
from pydantic import BaseModel


class SearchInput(BaseModel):
    query: str
    top_k: int


search_input = SearchInput(
    query="agent",
    top_k=5
)

print(search_input.query)
print(search_input.top_k)
```

这一部分可以通过。

Pydantic 第一课通过\boxed{\text{Pydantic 第一课通过}}

接下来正式进入今天的 **第二课：默认值、可选字段 `None`、`Field` 和参数范围约束**。这一部分开始和 Agent 的 Tool Calling 非常接近。

------

# 第二课：默认值、Optional 和 `Field`

先从你刚才的：

```python
class SearchInput(BaseModel):
    query: str
    top_k: int
```

开始。

现在如果调用：

```python
SearchInput(
    query="Agent"
)
```

会怎么样？

会报错。

因为：

```python
top_k
```

没有默认值，所以它是一个必须提供的字段。

也就是说：

```text
query  → 必填
top_k  → 必填
```

------

## 一、给字段设置默认值

如果我们希望：

> 用户不传 `top_k` 时，默认搜索 5 篇。

可以写：

```python
class SearchInput(BaseModel):
    query: str
    top_k: int = 5
```

现在：

```python
data = SearchInput(
    query="Agent"
)

print(data.top_k)
```

输出：

```text
5
```

所以这和普通 Python 函数默认参数很像：

```python
def search(
    query: str,
    top_k: int = 5
):
    ...
```

对应：

```python
class SearchInput(BaseModel):
    query: str
    top_k: int = 5
```

都表示：

> 没传的时候默认使用 5。

------

# 二、什么叫“可选字段”？

假设我们还有一个：

```text
language
```

用户可以传：

```text
"zh"
```

也可以完全不传。

可以写：

```python
class SearchInput(BaseModel):
    query: str
    top_k: int = 5
    language: str | None = None
```

这里：

```python
str | None
```

表示：

> `language` 最终可以是字符串，也可以是 `None`。

而：

```python
= None
```

表示：

> 如果调用时不提供这个字段，默认就是 `None`。

例如：

```python
data = SearchInput(
    query="Agent"
)
```

那么：

```python
print(data.language)
```

输出：

```text
None
```

------

# 三、这里有一个很重要的区别

下面两种写法看起来非常像：

```python
language: str | None
```

和：

```python
language: str | None = None
```

但在 Pydantic v2 里，它们意义不完全一样。

第一种：

```python
language: str | None
```

表示：

> 这个字段允许值是 `None`，但是你仍然需要提供这个字段。

例如：

```python
SearchInput(
    query="Agent",
    language=None
)
```

可以。

但如果完全不写：

```python
SearchInput(
    query="Agent"
)
```

这个字段本身仍可能被认为是缺失。

而：

```python
language: str | None = None
```

表示：

> 字段可以是字符串，也可以是 `None`，而且不传时默认就是 `None`。

所以真实项目里，如果你想表达：

> 这个字段真的可以不传。

通常会写：

```python
language: str | None = None
```

这个区别以后看 Tool Schema 很重要。

------

# 四、为什么 Agent Tool 特别需要默认值？

假设我们的搜索工具：

```python
def search_paper(
    query: str,
    top_k: int = 5
):
    ...
```

用户说：

> 帮我搜索 Agent 论文。

LLM 可能只生成：

```json
{
  "query": "Agent"
}
```

它没有生成：

```text
top_k
```

没关系，因为我们的模型：

```python
class SearchInput(BaseModel):
    query: str
    top_k: int = 5
```

会自动得到：

```python
top_k = 5
```

所以：

```text
LLM 输出
   ↓
{
  "query": "Agent"
}
   ↓
Pydantic
   ↓
{
  query="Agent",
  top_k=5
}
```

这对 Tool Calling 特别实用。

------

# 五、但是还有一个问题

假设 LLM 返回：

```json
{
  "query": "Agent",
  "top_k": -100
}
```

从类型上看：

```python
-100
```

确实是：

```python
int
```

所以只写：

```python
top_k: int
```

并不能发现这个逻辑错误。

但是：

> 搜索前 -100 篇论文显然不合理。

这就轮到：

```python
Field
```

出场了。

------

# 六、`Field` 是什么？

先导入：

```python
from pydantic import BaseModel, Field
```

然后：

```python
class SearchInput(BaseModel):
    query: str
    top_k: int = Field(
        default=5,
        ge=1,
        le=20
    )
```

这里：

```python
Field(...)
```

可以理解为：

> 给这个字段增加更详细的规则。

------

# 七、`default=5`

```python
default=5
```

就是：

> 默认值是 5。

所以：

```python
top_k: int = Field(default=5)
```

和：

```python
top_k: int = 5
```

在默认值这一点上类似。

但是 `Field` 还能加更多限制。

------

# 八、`ge=1`

```python
ge=1
```

这里：

```text
ge
```

是：

```text
greater than or equal
```

即：

topk≥1top_k \ge 1

所以：

```python
top_k=0
```

不允许。

```python
top_k=-5
```

也不允许。

------

# 九、`le=20`

```python
le=20
```

表示：

```text
less than or equal
```

也就是：

topk≤20top_k \le 20

因此最终要求：

1≤topk≤20\boxed{1 \le top_k \le 20}

------

# 十、完整例子

```python
from pydantic import BaseModel, Field


class SearchInput(BaseModel):
    query: str

    top_k: int = Field(
        default=5,
        ge=1,
        le=20
    )
```

正常：

```python
data = SearchInput(
    query="Agent",
    top_k=10
)
```

通过。

不传：

```python
data = SearchInput(
    query="Agent"
)
```

自动：

```text
top_k = 5
```

但：

```python
SearchInput(
    query="Agent",
    top_k=-1
)
```

就会：

```text
ValidationError
```

因为：

```text
-1 < 1
```

------

# 十一、常见数字约束

你先认识这几个：

| 参数 | 含义 |
| ---- | ---- |
| `gt` | `>`  |
| `ge` | `>=` |
| `lt` | `<`  |
| `le` | `<=` |

例如：

```python
score: float = Field(
    gt=0,
    le=1
)
```

表示：

0<score≤10 < score \le 1

------

# 十二、字符串也可以限制

假设：

```python
query: str
```

用户却传：

```python
query=""
```

虽然这是：

```python
str
```

但根本没有搜索内容。

可以：

```python
query: str = Field(
    min_length=1
)
```

表示字符串长度至少为 1。

不过：

```python
"   "
```

有三个空格，也会满足长度要求。

以后如果想过滤纯空格，我们可以再做 Validator。

现在先不讲那么深。

------

# 十三、给字段写 `description`

这个对于 Agent 特别重要。

例如：

```python
class SearchInput(BaseModel):
    query: str = Field(
        description="用户需要搜索的关键词"
    )

    top_k: int = Field(
        default=5,
        ge=1,
        le=20,
        description="返回的搜索结果数量"
    )
```

为什么 description 对 Agent 很重要？

因为后面做 Tool Calling 时，大模型会看到类似的 Tool Schema：

```text
query
→ 用户需要搜索的关键词

top_k
→ 返回的搜索结果数量
```

于是模型更容易知道：

> 每个参数到底应该填什么。

所以：

Field description 不只是给程序员看，也可以帮助 LLM 理解 Tool 参数\boxed{\text{Field description 不只是给程序员看，也可以帮助 LLM 理解 Tool 参数}}

这个非常重要。

------

# 十四、现在我们的 SearchInput 已经很像真实 Tool Schema 了

```python
from pydantic import BaseModel, Field


class SearchInput(BaseModel):

    query: str = Field(
        min_length=1,
        description="需要搜索的关键词"
    )

    top_k: int = Field(
        default=5,
        ge=1,
        le=20,
        description="返回结果数量"
    )

    language: str | None = Field(
        default=None,
        description="搜索语言，可选"
    )
```

于是：

```text
SearchInput
│
├── query
│    ├── str
│    ├── 必填
│    └── 最少1个字符
│
├── top_k
│    ├── int
│    ├── 默认5
│    └── 1~20
│
└── language
     ├── str或None
     └── 默认None
```

这已经是很标准的结构化 Tool 参数定义了。

------

# 十五、Pydantic 验证流程

比如 LLM 返回：

```python
raw_data = {
    "query": "Agent",
    "top_k": 100
}
```

交给：

```python
SearchInput(**raw_data)
```

以后我们会专门讲：

```python
**
```

这里你之前接触过 `**kwargs`，它相当于把字典展开。

大概等价于：

```python
SearchInput(
    query="Agent",
    top_k=100
)
```

然后：

```text
Pydantic
 ↓
query是str ✅
top_k是int ✅
top_k <= 20 ❌
 ↓
ValidationError
```

这就是为什么：

> “类型正确”并不代表“数据一定合法”。

Pydantic 能同时做：

```text
类型校验
+
业务范围约束
```

------

# 十六、再连接一下 Agent Tool Calling

以后你可能定义：

```python
class SearchInput(BaseModel):
    query: str
    top_k: int = Field(
        default=5,
        ge=1,
        le=20
    )
```

LLM 生成：

```json
{
  "query": "最新Agent论文",
  "top_k": 5
}
```

完整流程：

```text
用户问题
   ↓
LLM
   ↓
决定调用 search_paper
   ↓
生成参数
   ↓
{
  "query": "...",
  "top_k": 5
}
   ↓
Pydantic验证
   ↓
SearchInput对象
   ↓
调用真实Tool
```

所以 Pydantic 和 Tool Calling 的关系你现在应该开始能感觉到了。

------

# 第二课练习

这次 4 题。

### 练习 1

解释下面三行分别有什么区别：

```python
name: str
name: str = "Tom"
name: str | None = None
```

------

### 练习 2

下面：

```python
top_k: int = Field(
    default=5,
    ge=1,
    le=20
)
```

请解释：

```text
default
ge
le
```

分别是什么意思。

------

### 练习 3

写一个：

```python
class SearchInput(BaseModel):
```

要求：

```text
query
→ str
→ 至少1个字符

top_k
→ int
→ 默认5
→ 最小1
→ 最大10

language
→ str或None
→ 默认None
```

------

### 练习 4

判断下面哪些会通过，哪些会 `ValidationError`：

```python
SearchInput(
    query="Agent",
    top_k=5
)
SearchInput(
    query="Agent",
    top_k=0
)
SearchInput(
    query="Agent",
    top_k=100
)
SearchInput(
    query="Agent"
)
SearchInput(
    query="",
    top_k=5
)
```

你做完之后，我们下一课就讲 **嵌套 Pydantic Model + `model_dump()` + `model_validate()`**。那一部分会开始像真正的 LLM Structured Output。