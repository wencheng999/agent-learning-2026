来啦 😄 今天正式进入 **Day 3：Pydantic + 结构化数据**。

在开始之前先用 2 分钟把前两天串起来。Day 1 解决的是 Python 工程基础：类型注解、`class / self / __init__`、异常处理、文件、JSON、`.env`、Git；Day 2 解决的是网络通信基础：HTTP、GET/POST、Params、Headers、Body、Response、状态码、`requests`，最后还手写了 `SimpleAPIClient`。

现在我们已经能够做到：

```text
Python dict
   ↓
HTTP Request
   ↓
服务器
   ↓
JSON Response
   ↓
Python dict
```

但这里还有一个很现实的问题：

> **服务器或者 LLM 返回一个 dict 后，我们怎么保证里面的数据格式一定是我们想要的？**

这就是今天 Pydantic 要解决的问题。

------

# Day 3 今天学什么

今天我们主要学：

- `BaseModel`
- 字段类型约束
- 自动数据校验
- `ValidationError`
- 默认值和可选字段
- `Field`
- 嵌套模型
- `model_dump()`
- `model_validate()`
- 为什么 Agent / Tool Calling / Structured Output 特别依赖 Pydantic

今天学完以后，你应该能看懂这种代码：

```python
from pydantic import BaseModel


class SearchInput(BaseModel):
    query: str
    top_k: int = 5


data = SearchInput(
    query="Agent",
    top_k=3
)

print(data.query)
print(data.top_k)
```

------

# 第一课：Pydantic 到底是干什么的？

我们先不用急着写代码。

假设你调用一个 API，返回：

```python
data = {
    "name": "Tom",
    "age": 20
}
```

你当然可以直接：

```python
print(data["name"])
```

但问题来了。

如果服务器返回的是：

```python
data = {
    "name": "Tom",
    "age": "abc"
}
```

你本来希望：

```python
age
```

是：

```python
int
```

结果现在是：

```python
str
```

如果程序后面执行：

```python
data["age"] + 1
```

就可能出问题。

------

# Pydantic 的核心作用

你可以把 Pydantic 理解为：

> **给 Python 数据加一层“结构说明 + 自动检查”。**

比如我们规定：

```text
User
│
├── name：必须是 str
└── age：必须是 int
```

然后数据来了：

```python
{
    "name": "Tom",
    "age": 20
}
```

Pydantic 检查：

```text
name 是 str ✅
age 是 int  ✅
```

通过。

如果：

```python
{
    "name": "Tom",
    "age": "abc"
}
```

Pydantic 就会告诉你：

> age 不符合要求。

所以：

Pydantic = 数据结构定义 + 数据校验\boxed{\text{Pydantic = 数据结构定义 + 数据校验}}

------

# 为什么普通类型注解还不够？

你第一天学过：

```python
age: int
```

但 Python 的类型注解本身一般不会强制检查。

例如：

```python
age: int = "abc"

print(age)
```

Python 很可能照样运行。

也就是说：

```text
类型注解
→ 主要是“告诉你应该是什么类型”

Pydantic
→ 真的去检查数据
```

这是一个非常重要的区别。

------

# 第一个 Pydantic 模型

先安装：

```bash
python -m pip install pydantic
```

然后写：

```python
from pydantic import BaseModel


class User(BaseModel):
    name: str
    age: int
```

这里你已经认识很多东西了：

```python
class User
```

定义类。

但这次它不是普通：

```python
class User:
```

而是：

```python
class User(BaseModel):
```

意思是：

> `User` 继承了 Pydantic 的 `BaseModel`。

“继承”我们之前还没正式讲，不过你现在可以先简单理解：

> `User` 获得了 `BaseModel` 提供的数据校验能力。

------

# 创建对象

```python
user = User(
    name="Tom",
    age=20
)
```

然后：

```python
print(user.name)
print(user.age)
```

输出：

```text
Tom
20
```

看起来是不是和之前：

```python
class Agent:
```

创建对象很像？

------

# 但是这里没有写 `__init__`

以前你写：

```python
class Agent:
    def __init__(self, name: str):
        self.name = name
```

Pydantic 里我们只写：

```python
class User(BaseModel):
    name: str
    age: int
```

为什么就能：

```python
User(name="Tom", age=20)
```

？

因为：

> `BaseModel` 已经帮你实现了初始化、字段保存和验证逻辑。

所以 Pydantic 帮你省掉了很多重复代码。

------

# 如果类型错误呢？

比如：

```python
user = User(
    name="Tom",
    age="abc"
)
```

这时 Pydantic 会报：

```text
ValidationError
```

意思：

> 数据验证失败。

大概会告诉你：

```text
age
Input should be a valid integer
```

------

# 一个非常重要的现象：Pydantic 有时会自动转换

例如：

```python
user = User(
    name="Tom",
    age="20"
)
```

注意：

```python
"20"
```

是字符串。

但是 Pydantic 在默认模式下通常会尝试把它转换成：

```python
20
```

于是：

```python
print(user.age)
print(type(user.age))
```

可能得到：

```text
20
<class 'int'>
```

也就是：

```text
"20"
 ↓
Pydantic
 ↓
20
```

这叫：

> **类型解析 / 类型转换**

------

# 那 `"abc"` 为什么不行？

因为：

```text
"20"
```

可以合理转换为：

```python
20
```

但：

```text
"abc"
```

没法变成：

```python
int
```

所以就报：

```text
ValidationError
```

------

# Agent 为什么特别需要这个？

假设以后 LLM 做 Structured Output，返回：

```json
{
  "tool": "search",
  "query": "Agent",
  "top_k": 5
}
```

你的程序希望：

```text
tool  → str
query → str
top_k → int
```

于是可以定义：

```python
from pydantic import BaseModel


class ToolCall(BaseModel):
    tool: str
    query: str
    top_k: int
```

然后把 LLM 输出交给 Pydantic。

如果 LLM 返回：

```json
{
  "tool": "search",
  "query": "Agent",
  "top_k": "abc"
}
```

Pydantic 就能及时发现：

> `top_k` 不合法。

而不是让错误一路传到真正 Tool 执行的时候才爆炸。

所以：

Pydantic 是 LLM Structured Output 和 Tool Calling 的基础工具之一\boxed{\text{Pydantic 是 LLM Structured Output 和 Tool Calling 的基础工具之一}}

------

# 再举一个你之后会遇到的 Tool 例子

假设搜索工具：

```python
def search_paper(
    query: str,
    top_k: int
):
    ...
```

我们可以定义输入模型：

```python
class SearchInput(BaseModel):
    query: str
    top_k: int
```

LLM 决定调用：

```json
{
  "query": "Agent",
  "top_k": 5
}
```

先：

```text
LLM输出
 ↓
SearchInput
 ↓
Pydantic校验
 ↓
通过
 ↓
真正执行search_paper()
```

整个流程会非常安全。

------

# `BaseModel` 可以先怎么理解？

你现在把：

```python
BaseModel
```

理解成：

> Pydantic 提供的一个“数据模型基础类”。

你定义：

```python
class User(BaseModel):
```

相当于告诉 Python：

> 我现在不是在写普通业务类，而是在定义一种结构化数据格式。

例如：

```text
User
├── name
└── age
```

------

# 看一个完整例子

```python
from pydantic import BaseModel


class Paper(BaseModel):
    title: str
    year: int
    score: float


paper = Paper(
    title="Agent Research",
    year=2026,
    score=0.95
)

print(paper.title)
print(paper.year)
print(paper.score)
```

输出：

```text
Agent Research
2026
0.95
```

------

# Pydantic 模型和 dict 有什么区别？

普通字典：

```python
paper = {
    "title": "Agent Research",
    "year": 2026
}
```

取：

```python
paper["title"]
```

Pydantic：

```python
paper = Paper(
    title="Agent Research",
    year=2026,
    score=0.95
)
```

取：

```python
paper.title
```

更重要的是：

```text
dict
→ 本身不会按照你定义的 schema 自动校验

Pydantic Model
→ 会按照字段定义自动验证
```

------

# `ValidationError`

实际开发不能只让程序直接崩掉。

所以可以：

```python
from pydantic import BaseModel
from pydantic import ValidationError


class User(BaseModel):
    name: str
    age: int


try:
    user = User(
        name="Tom",
        age="abc"
    )

except ValidationError as e:
    print("数据验证失败")
    print(e)
```

这里又和 Day 1：

```python
try / except
```

串起来了。

流程：

```text
外部数据
 ↓
Pydantic
 ↓
验证成功？
 ├─ 是 → 得到模型对象
 └─ 否 → ValidationError
             ↓
           except
```

------

# 第一课现在你要记住 5 个核心概念

| 概念              | 含义                    |
| ----------------- | ----------------------- |
| `BaseModel`       | Pydantic 数据模型基础类 |
| 字段类型          | 规定数据应该是什么类型  |
| Validation        | 检查数据是否合法        |
| 类型转换          | 合理情况下自动转换类型  |
| `ValidationError` | 验证失败时的异常        |

------

# 第一课练习

先做 4 道，不难。

### 练习 1

解释下面：

```python
class User(BaseModel):
    name: str
    age: int
```

这里：

```text
User
BaseModel
name: str
age: int
```

分别是什么意思？

------

### 练习 2

下面会成功还是报错？

```python
user = User(
    name="Tom",
    age="20"
)
```

你觉得最终：

```python
type(user.age)
```

大概是什么？

------

### 练习 3

下面：

```python
user = User(
    name="Tom",
    age="abc"
)
```

为什么会产生 `ValidationError`？

------

### 练习 4

你自己写一个：

```python
class SearchInput(BaseModel):
```

要求有：

```text
query：str
top_k：int
```

然后创建：

```python
SearchInput(
    query="Agent",
    top_k=5
)
```

最后打印：

```python
query
top_k
```

你把这 4 道做完，我们继续 **第二课：默认值、Optional、Field，以及如何给 `top_k` 加 `1~20` 的范围限制**。这部分会开始非常像真正的 Tool 参数验证。