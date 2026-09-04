好，那我们就正式开始 **Day 1：Agent 开发需要的 Python 工程基础**。

按照你前面的学习路线，准备周本来就要求你先熟悉 Python、Git/GitHub、Conda/uv、Pydantic 和 `async/await` 等基础。
我们不重新从 `print()`、`for` 循环讲 Python，而是专门学以后写 **RAG、Tool Calling、LangGraph、MCP、Agent** 时真正高频出现的 Python 写法。

今天 Day 1 我建议分成四部分：

```text
Day 1
│
├── ① Python 类型注解          ← 现在先学这个
├── ② class / 异常 / 文件 / .env
├── ③ Conda / uv / 项目结构
└── ④ Git / GitHub
```

我们先只学第一部分。你把第一部分真正搞懂后，再继续下一部分。

------

# 第一课：Python 类型注解 Type Hints

## 1. 为什么学 Agent 一定会遇到类型注解？

你以后经常会看到这种代码：

```python
def search_paper(
    query: str,
    top_k: int = 5
) -> list[str]:
    ...
```

刚开始可能觉得：

```text
query: str
top_k: int
-> list[str]
```

这些东西很多余。

其实在现代 Python AI 工程里非常重要。

因为你后面会接触：

```text
Pydantic
FastAPI
LangChain
LangGraph
MCP
Tool Calling
Structured Output
```

它们都大量依赖 Python 类型系统。

例如以后定义一个 Agent Tool：

```python
def search_paper(query: str, top_k: int = 5) -> list[str]:
    ...
```

光看定义，程序员就知道：

```text
query
↓
字符串

top_k
↓
整数

函数返回
↓
字符串列表
```

所以第一件事要理解：

> **类型注解不是 Agent 特有知识，而是现代 Python AI 工程的基础。**

------

# 2. 先看没有类型注解的 Python

例如：

```python
def add(a, b):
    return a + b
```

现在我问你：

```text
a 是什么类型？

b 是什么类型？

返回什么类型？
```

光看函数定义：

> 不知道。

它可能这么用：

```python
add(1, 2)
```

结果：

```text
3
```

也可能：

```python
add("Agent", "RAG")
```

结果：

```text
AgentRAG
```

因为 Python 是动态类型语言。

------

# 3. 加上类型注解

我们可以写：

```python
def add(a: int, b: int) -> int:
    return a + b
```

这里：

```python
a: int
```

表示：

> 希望 `a` 是整数。

```python
b: int
```

表示：

> 希望 `b` 是整数。

而：

```python
-> int
```

表示：

> 希望函数返回一个整数。

所以整个函数可以读成一句中文：

> 接收两个整数 `a` 和 `b`，返回一个整数。

------

# 4. 注意一个非常重要的问题

很多初学者会认为：

```python
a: int
```

意味着 Python 会强制 `a` 必须是整数。

其实：

> **不是。**

例如：

```python
def add(a: int, b: int) -> int:
    return a + b


print(add("Hello ", "Agent"))
```

Python 在很多情况下仍然可能正常运行：

```text
Hello Agent
```

所以：

Type Hint≠运行时强制类型检查\boxed{\text{Type Hint} \neq \text{运行时强制类型检查}}

类型注解主要用于：

```text
代码可读性
IDE提示
静态检查
框架自动解析
Pydantic/FastAPI等工具
```

这个概念一定要记住。

------

# 5. 基本类型

最常见几个：

```python
name: str = "Agent"

age: int = 20

score: float = 95.5

is_active: bool = True
```

分别：

| 类型    | 含义   | 示例      |
| ------- | ------ | --------- |
| `str`   | 字符串 | `"Agent"` |
| `int`   | 整数   | `10`      |
| `float` | 浮点数 | `3.14`    |
| `bool`  | 布尔   | `True`    |

以后 Agent 代码中大量出现。

------

# 6. 函数参数类型

例如：

```python
def greet(name: str) -> str:
    return f"Hello, {name}"
```

调用：

```python
result = greet("小王")

print(result)
```

输出：

```text
Hello, 小王
```

这里：

```text
name: str
```

表示：

> 输入名称应该是字符串。

而：

```text
-> str
```

表示：

> 最终返回字符串。

------

# 7. 为什么 `-> 返回类型` 很重要？

例如以后有一个搜索工具：

```python
def search(query: str) -> str:
    ...
```

你马上知道：

```text
输入
↓
字符串

输出
↓
字符串
```

另外一个：

```python
def search(query: str) -> list[str]:
    ...
```

你马上知道：

```text
输入
↓
字符串

输出
↓
多个字符串
```

对于几百行甚至几千行 Agent 项目来说，这非常重要。

------

# 8. list 类型

以前可能写：

```python
papers = [
    "ReAct",
    "Toolformer",
    "Agent Paper"
]
```

现在可以：

```python
papers: list[str] = [
    "ReAct",
    "Toolformer",
    "Agent Paper"
]
```

意思：

> `papers` 是一个列表，并且列表里面应该放字符串。

因此：

```python
list[str]
```

可以拆成：

```text
list
↓
列表

[str]
↓
列表元素是str
```

例如：

```python
scores: list[int] = [90, 85, 92]
```

表示：

> 整数列表。

------

# 9. 这在 Agent 中会大量出现

例如：

```python
def search_papers(query: str) -> list[str]:
    return [
        "Paper A",
        "Paper B",
        "Paper C"
    ]
```

意思：

```text
用户查询
query
↓
搜索论文
↓
返回论文列表
```

非常常见。

------

# 10. dict 类型

例如：

```python
user = {
    "name": "Tom",
    "major": "Computer Science"
}
```

可以写成：

```python
user: dict[str, str] = {
    "name": "Tom",
    "major": "Computer Science"
}
```

这里：

```python
dict[str, str]
```

意思：

```text
dict[
    key类型,
    value类型
]
```

所以：

```python
dict[str, str]
```

就是：

> Key 是字符串，Value 也是字符串。

------

比如：

```python
scores: dict[str, int] = {
    "Tom": 90,
    "Jack": 85
}
```

这里：

```text
key
↓
str

value
↓
int
```

------

# 11. 为什么 Agent 特别喜欢 dict？

以后最常见的 LLM Message：

```python
message = {
    "role": "user",
    "content": "什么是Agent？"
}
```

本质就是：

```text
dict
```

再比如：

```python
messages = [
    {
        "role": "system",
        "content": "You are an AI assistant."
    },
    {
        "role": "user",
        "content": "What is RAG?"
    }
]
```

它本质上就是：

```text
list
 ↓
dict
 ↓
key-value
```

所以：

> **list + dict 是以后 Agent 开发最常用的两个 Python 数据结构。**

------

# 12. 多层类型怎么看？

比如：

```python
messages: list[dict[str, str]]
```

第一次看到可能觉得很复杂。

不要整个看。

从里面向外读。

先看：

```python
dict[str, str]
```

表示：

```text
字符串 → 字符串
```

的字典。

然后：

```python
list[
    dict[str, str]
]
```

表示：

> 很多个这样的字典组成一个列表。

所以：

```python
messages: list[dict[str, str]]
```

实际就是：

```python
messages = [
    {
        "role": "system",
        "content": "..."
    },
    {
        "role": "user",
        "content": "..."
    }
]
```

以后你会天天看到这种结构。

------

# 13. set 和 tuple 简单知道

### tuple

```python
position: tuple[int, int] = (10, 20)
```

表示：

> 两个整数组成的元组。

------

### set

```python
tools: set[str] = {
    "search",
    "calculator",
    "weather"
}
```

表示：

> 字符串集合。

Agent 初期：

```text
list
dict
```

远比它们重要。

所以知道即可。

------

# 14. 一个非常重要的类型：None

例如：

```python
def search_user(user_id: int):
    ...
```

如果用户不存在怎么办？

可能：

```python
return None
```

所以可以写：

```python
def search_user(user_id: int) -> str | None:
    ...
```

这里：

```python
str | None
```

表示：

> 返回值要么是字符串，要么是 `None`。

例如：

```python
def search_user(user_id: int) -> str | None:

    if user_id == 1:
        return "Tom"

    return None
```

调用：

```python
result = search_user(2)

print(result)
```

输出：

```text
None
```

------

# 15. `Optional` 又是什么？

有些项目你会看到：

```python
from typing import Optional


def search_user(user_id: int) -> Optional[str]:
    ...
```

实际上：

```python
Optional[str]
```

基本可以理解成：

```python
str | None
```

所以：

Optional[str]≈str∣NoneOptional[str] \approx str | None

现代 Python 代码里你会越来越多看到：

```python
str | None
```

但旧一点的库和代码仍然大量使用：

```python
Optional[str]
```

两种都要看懂。

------

# 16. Agent 中为什么经常出现 Optional？

例如：

```python
def search(
    query: str,
    domain: str | None = None
):
    ...
```

意思：

```text
query
↓
必须提供

domain
↓
可以提供
也可以不提供
```

例如：

```python
search("Agent")
```

也可以：

```python
search(
    query="Agent",
    domain="arxiv"
)
```

------

# 17. Union 类型

有时候变量可能是多种类型。

例如：

```python
from typing import Union


value: Union[str, int]
```

表示：

```text
value
```

可以是：

```text
str
```

或者：

```text
int
```

现代写法：

```python
value: str | int
```

更加直观。

------

# 18. 一个你以后非常常见的类型：Literal

例如 Agent Router。

Agent 判断接下来走：

```text
search
```

还是：

```text
answer
```

我们可能写：

```python
from typing import Literal


def route() -> Literal["search", "answer"]:
    ...
```

什么意思？

返回值只能是：

```text
"search"
```

或者：

```text
"answer"
```

不能：

```text
"hello"
```

这种类型以后在：

```text
LangGraph
Router
Agent State
Structured Output
```

里非常常见。

------

# 19. 举一个未来 LangGraph 风格的例子

以后你可能看到：

```python
from typing import Literal


def router(
    question: str
) -> Literal["search", "answer"]:

    if "最新" in question:
        return "search"

    return "answer"
```

意思就是：

```text
Question
   ↓
 Router
 /     \
search answer
```

是不是已经有一点 Agent 的感觉了？

------

# 20. `TypedDict` 也非常重要

这一块提前让你认识一下。

以后 LangGraph State 经常会看到：

```python
from typing import TypedDict


class AgentState(TypedDict):
    question: str
    answer: str
```

看起来像 class。

但实际表达的是：

> 一个有固定字段结构的字典。

例如：

```python
state: AgentState = {
    "question": "什么是RAG？",
    "answer": "..."
}
```

这样 IDE 就知道：

```text
state必须包含：

question: str
answer: str
```

以后 LangGraph 你会反复遇到它。

现在不用深入。

先知道：

TypedDict→给dict定义结构\boxed{TypedDict \rightarrow 给dict定义结构}

------

# 21. 一个完整 Agent 风格例子

现在把刚才的知识组合起来。

```python
from typing import Literal


def classify_query(
    query: str
) -> Literal["search", "chat"]:

    if "最新" in query:
        return "search"

    return "chat"


def search(
    query: str,
    top_k: int = 5
) -> list[str]:

    return [
        f"Result {i}: {query}"
        for i in range(top_k)
    ]


query: str = "最新Agent论文"

route = classify_query(query)

if route == "search":

    results: list[str] = search(
        query=query,
        top_k=3
    )

    print(results)
```

你现在其实已经可以读懂：

```text
User Query
    ↓
classify_query()
    ↓
  Router
    ↓
"search"
    ↓
search()
    ↓
list[str]
```

这个思想以后就是：

# Agent Router

的最简单雏形。

------

# 22. Python 参数默认值

注意：

```python
def search(
    query: str,
    top_k: int = 5
):
```

这里：

```python
top_k: int = 5
```

包含两个信息。

第一个：

```text
: int
```

类型是整数。

第二个：

```text
= 5
```

默认值为 5。

所以：

```python
search("Agent")
```

实际上相当于：

```python
search(
    query="Agent",
    top_k=5
)
```

也可以：

```python
search(
    query="Agent",
    top_k=10
)
```

以后 Tool 参数会大量使用默认值。

------

# 23. 为什么函数参数最好写名字？

例如：

```python
search("Agent", 10)
```

虽然可以。

但是大型项目更推荐：

```python
search(
    query="Agent",
    top_k=10
)
```

更清楚。

一眼知道：

```text
Agent → query
10 → top_k
```

以后我们写项目时尽量养成这个习惯。

------

# 24. 现在认识一下 `**kwargs`

你以后看 AI 框架代码一定会遇到：

```python
def run(**kwargs):
    ...
```

先不用深入底层。

你现在只需要知道：

```python
def show(**kwargs):
    print(kwargs)


show(
    model="qwen",
    temperature=0.7
)
```

实际上：

```python
kwargs
```

会变成：

```python
{
    "model": "qwen",
    "temperature": 0.7
}
```

也就是：

∗∗kwargs→把多个关键字参数收集成dict\boxed{**kwargs \rightarrow 把多个关键字参数收集成dict}

为什么 AI 框架里这么常见？

因为模型参数非常多：

```text
model
temperature
max_tokens
top_p
stream
tools
...
```

框架不可能每次全部固定写死。

所以经常：

```python
**kwargs
```

------

# 25. `*args` 简单理解

例如：

```python
def add(*args):
    print(args)


add(1, 2, 3)
```

得到：

```python
(1, 2, 3)
```

所以：

∗args→多个位置参数\boxed{*args \rightarrow 多个位置参数}∗∗kwargs→多个关键字参数\boxed{**kwargs \rightarrow 多个关键字参数}

Agent 初期：

> `**kwargs` 比 `*args` 更值得留意。

------

# 26. 今天第一部分最核心的内容

你不用背所有语法。

把下面几个牢牢记住：

```text
name: str

age: int

scores: list[int]

user: dict[str, str]

str | None

Literal["search", "answer"]

def func(x: str) -> list[str]:
```

以及：

```text
*args

**kwargs
```

能看懂。

------

# 27. 第一组练习

现在你自己判断下面代码是什么意思。

### 题目 1

```python
def search(
    query: str,
    top_k: int = 5
) -> list[str]:
    ...
```

请回答：

1. `query` 是什么类型？
2. `top_k` 是什么类型？
3. `top_k` 默认值是多少？
4. 函数返回什么？

------

### 题目 2

```python
user: dict[str, int] = {
    "age": 20,
    "score": 90
}
```

请回答：

```text
dict[str, int]
```

分别代表什么？

------

### 题目 3

```python
def get_answer(
    question: str
) -> str | None:
    ...
```

`str | None` 是什么意思？

------

### 题目 4

```python
def router(
    query: str
) -> Literal["rag", "web", "chat"]:
    ...
```

这个函数可能返回哪些值？

------

# 28. 第一段你自己需要写的代码

不要复制我的答案。

自己创建：

```text
type_hint_practice.py
```

实现两个函数。

### 第一个

```text
函数名：
classify_query

输入：
query，字符串

返回：
"search"
或者
"chat"
```

规则：

> 如果 query 中含有“最新”，返回 `"search"`，否则返回 `"chat"`。

------

### 第二个

```text
函数名：
search_paper

输入：
query: str
top_k: int = 3

返回：
list[str]
```

例如：

```python
search_paper(
    query="Agent",
    top_k=3
)
```

返回类似：

```python
[
    "Agent Paper 1",
    "Agent Paper 2",
    "Agent Paper 3"
]
```

------

# 29. 你写完后应该测试

```python
query = "最新Agent论文"

route = classify_query(query)

print(route)

results = search_paper(
    query="Agent",
    top_k=3
)

print(results)
```

预期：

```text
search
['Agent Paper 1', 'Agent Paper 2', 'Agent Paper 3']
```

------

# 30. 今天这一小节的验收标准

如果现在给你：

```python
def search(
    query: str,
    top_k: int = 5,
    domain: str | None = None
) -> list[dict[str, str]]:
    ...
```

你能一眼解释成：

> 这是一个搜索函数，`query` 是字符串，`top_k` 是整数且默认 5，`domain` 可以是字符串或者不提供，最终返回一个列表，而列表里面每个元素都是 `dict[str, str]`。

那么：

Python 类型注解这一关基本通过\boxed{\text{Python 类型注解这一关基本通过}}

而且以后看到：

```python
def search_paper(query: str) -> list[str]
Literal["search", "answer"]
dict[str, str]
str | None
```

就不会再觉得陌生了。

------

## 你现在先做这一步

先不要继续往下学 `class`。

你可以直接把上面 **4 道判断题的答案 + `classify_query()` 和 `search_paper()` 两个函数代码**发给我。

我会像老师改作业一样给你检查哪里有问题，然后我们继续 **Day 1 第二课：`class` 到底是什么，以及为什么 Agent、Tool、LLM Client 都喜欢写成类。**