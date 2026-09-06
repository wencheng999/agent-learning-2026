好，我们现在正式学 **Tool Registry（工具注册表）**。这一节不难，但非常重要，因为它会把你刚刚写的：

```python
if decision.tool == "search":
    ...
elif decision.tool == "calculator":
    ...
```

改造成更像真实 Agent 工程的写法。

------

# 一、为什么需要 Tool Registry？

你刚才的 Router 是：

```python
if decision.tool == "search":
    search_args = SearchInput.model_validate(
        decision.arguments
    )

    result = search_paper(
        query=search_args.query,
        top_k=search_args.top_k
    )

elif decision.tool == "calculator":
    calculator_args = CalculatorInput.model_validate(
        decision.arguments
    )

    result = calculator(
        a=calculator_args.a,
        b=calculator_args.b
    )
```

现在只有两个 Tool，还不觉得有什么问题。

但是以后 Agent 可能有：

```text
search
calculator
weather
read_file
write_file
search_paper
read_pdf
save_note
send_email
database_query
...
```

如果一直这样：

```python
if tool == "search":
    ...

elif tool == "calculator":
    ...

elif tool == "weather":
    ...

elif tool == "read_file":
    ...

elif tool == "write_file":
    ...
```

最后就会变成：

```text
一个巨大的 if / elif
```

这会产生几个问题：

```text
① Tool越多，Router越长

② 新增一个Tool就要修改Router代码

③ Tool名字、函数、参数模型分散在很多地方

④ 不方便统一管理Tool

⑤ 不方便以后自动生成Tool Schema
```

所以工程里会有一个东西：

Tool Registry\boxed{\text{Tool Registry}}

也就是：

> **把所有可用工具统一登记在一个地方。**

------

# 二、最简单的 Tool Registry

先不考虑 Pydantic。

假设有：

```python
def search_paper(query: str, top_k: int):
    ...


def calculator(a: float, b: float):
    ...
```

可以建立：

```python
TOOL_REGISTRY = {
    "search": search_paper,
    "calculator": calculator
}
```

这个本质上就是：

```python
dict
```

里面：

```text
key
→ Tool名字

value
→ Python函数
```

所以：

```text
TOOL_REGISTRY
│
├── "search"
│      ↓
│   search_paper
│
└── "calculator"
       ↓
    calculator
```

------

# 三、函数也可以放进字典？

这是今天一个非常重要的 Python 概念。

我们之前：

```python
name = "Tom"
```

变量可以保存字符串。

```python
number = 10
```

变量可以保存整数。

实际上 Python 中：

> **函数也是对象。**

所以：

```python
func = calculator
```

是完全合法的。

注意这里没有：

```python
()
```

也就是：

```python
func = calculator
```

表示：

> 把 `calculator` 这个函数本身保存到 `func`。

而：

```python
func = calculator()
```

才表示：

> 立即执行 calculator。

------

例如：

```python
def hello():
    print("Hello")


func = hello

func()
```

运行：

```text
Hello
```

因为：

```text
func
 ↓
hello函数
```

所以：

```python
func()
```

其实就是：

```python
hello()
```

------

# 四、所以 Registry 可以动态拿函数

例如：

```python
TOOL_REGISTRY = {
    "search": search_paper,
    "calculator": calculator
}
```

然后：

```python
tool_func = TOOL_REGISTRY["calculator"]
```

此时：

```python
tool_func
```

就是：

```python
calculator
```

于是：

```python
result = tool_func(
    a=10,
    b=20
)
```

相当于：

```python
result = calculator(
    a=10,
    b=20
)
```

这样我们就不用：

```python
if tool == "calculator":
```

才能找到对应函数了。

------

# 五、但是我们现在还有 Pydantic Schema

我们不能只保存：

```text
Tool名称
+
函数
```

因为每个 Tool 还有自己的参数模型：

```text
search
├── function → search_paper
└── schema   → SearchInput


calculator
├── function → calculator
└── schema   → CalculatorInput
```

所以 Registry 可以升级。

------

# 六、真正适合我们当前代码的 Registry

写成：

```python
TOOL_REGISTRY = {
    "search": {
        "function": search_paper,
        "input_model": SearchInput
    },

    "calculator": {
        "function": calculator,
        "input_model": CalculatorInput
    }
}
```

注意结构。

最外层：

```python
TOOL_REGISTRY
```

是一个字典。

里面：

```python
"search"
```

对应：

```python
{
    "function": search_paper,
    "input_model": SearchInput
}
```

所以可以画成：

```text
TOOL_REGISTRY
│
├── search
│    │
│    ├── function
│    │      ↓
│    │   search_paper
│    │
│    └── input_model
│           ↓
│       SearchInput
│
└── calculator
     │
     ├── function
     │      ↓
     │   calculator
     │
     └── input_model
            ↓
        CalculatorInput
```

这样一个 Tool 需要的信息都放在一起了。

------

# 七、怎么根据 Tool 名找到信息？

假设：

```python
decision.tool
```

是：

```text
search
```

那么：

```python
tool_info = TOOL_REGISTRY[
    decision.tool
]
```

相当于：

```python
tool_info = TOOL_REGISTRY["search"]
```

最终：

```python
tool_info
```

就是：

```python
{
    "function": search_paper,
    "input_model": SearchInput
}
```

------

然后：

```python
tool_func = tool_info["function"]
```

得到：

```python
search_paper
```

再：

```python
input_model = tool_info["input_model"]
```

得到：

```python
SearchInput
```

于是我们已经动态找到了：

```text
Tool名字
 ↓
对应函数
+
对应Pydantic模型
```

------

# 八、然后动态验证参数

以前你写：

```python
search_args = SearchInput.model_validate(
    decision.arguments
)
```

现在不需要写死：

```python
SearchInput
```

可以：

```python
args = input_model.model_validate(
    decision.arguments
)
```

假如当前：

```python
input_model = SearchInput
```

那么这句其实就是：

```python
args = SearchInput.model_validate(
    decision.arguments
)
```

如果当前：

```python
input_model = CalculatorInput
```

它自动变成：

```python
args = CalculatorInput.model_validate(
    decision.arguments
)
```

是不是开始有点“自动路由”的感觉了？

------

# 九、现在遇到最后一个问题

Search Tool 调用：

```python
search_paper(
    query=args.query,
    top_k=args.top_k
)
```

Calculator：

```python
calculator(
    a=args.a,
    b=args.b
)
```

参数名又不一样。

我们难道还是要：

```python
if search:
    ...

elif calculator:
    ...
```

？

不用。

这里正好可以使用你之前见过的：

```python
**
```

------

# 十、`**` 字典解包

假设：

```python
data = {
    "a": 10,
    "b": 20
}
```

执行：

```python
calculator(**data)
```

相当于：

```python
calculator(
    a=10,
    b=20
)
```

这叫：

字典解包\boxed{\text{字典解包}}

也就是：

```python
{
    "a": 10,
    "b": 20
}
```

展开成：

```text
a=10,
b=20
```

------

再例如：

```python
data = {
    "query": "Agent",
    "top_k": 3
}
```

那么：

```python
search_paper(**data)
```

相当于：

```python
search_paper(
    query="Agent",
    top_k=3
)
```

------

# 十一、刚好 Pydantic 可以 `model_dump()`

前面已经学过：

```python
args.model_dump()
```

可以：

```text
Pydantic对象
↓
dict
```

比如：

```python
args = SearchInput(
    query="Agent",
    top_k=3
)
```

那么：

```python
args.model_dump()
```

得到：

```python
{
    "query": "Agent",
    "top_k": 3
}
```

然后：

```python
tool_func(
    **args.model_dump()
)
```

如果：

```python
tool_func = search_paper
```

就相当于：

```python
search_paper(
    query="Agent",
    top_k=3
)
```

这一步非常漂亮。

------

# 十二、于是整个 Router 可以简化成这样

以前：

```python
if decision.tool == "search":
    ...

elif decision.tool == "calculator":
    ...
```

现在变成：

```python
tool_info = TOOL_REGISTRY[
    decision.tool
]

tool_func = tool_info["function"]
input_model = tool_info["input_model"]

args = input_model.model_validate(
    decision.arguments
)

result = tool_func(
    **args.model_dump()
)
```

没有任何：

```python
if
elif
```

了。

------

# 十三、完整代码

我们把之前的 Demo 改造一下。

```python
from typing import Literal

from pydantic import BaseModel, Field, ValidationError


# =========================
# 1. Tool输入模型
# =========================

class SearchInput(BaseModel):
    query: str = Field(
        min_length=1,
        description="搜索关键词"
    )

    top_k: int = Field(
        default=5,
        ge=1,
        le=10,
        description="返回结果数量"
    )


class CalculatorInput(BaseModel):
    a: float
    b: float


# =========================
# 2. LLM决策模型
# =========================

class ToolDecision(BaseModel):
    tool: Literal[
        "search",
        "calculator"
    ]

    arguments: dict


# =========================
# 3. 真正Tool
# =========================

def search_paper(
    query: str,
    top_k: int
) -> list[str]:

    return [
        f"{query} Paper {i}"
        for i in range(1, top_k + 1)
    ]


def calculator(
    a: float,
    b: float
) -> float:

    return a + b


# =========================
# 4. Tool Registry
# =========================

TOOL_REGISTRY = {
    "search": {
        "function": search_paper,
        "input_model": SearchInput
    },

    "calculator": {
        "function": calculator,
        "input_model": CalculatorInput
    }
}


# =========================
# 5. 通用Tool执行器
# =========================

def execute_tool(
    llm_output: dict
):
    try:
        # 第一层：验证LLM决策
        decision = ToolDecision.model_validate(
            llm_output
        )

        # 根据Tool名字查注册表
        tool_info = TOOL_REGISTRY[
            decision.tool
        ]

        # 找到对应函数
        tool_func = tool_info[
            "function"
        ]

        # 找到对应参数模型
        input_model = tool_info[
            "input_model"
        ]

        # 第二层：验证Tool参数
        args = input_model.model_validate(
            decision.arguments
        )

        # 执行Tool
        result = tool_func(
            **args.model_dump()
        )

        return result

    except ValidationError as e:
        print("Tool参数验证失败：")
        print(e)
        return None
```

------

# 十四、测试 Search Tool

```python
llm_output1 = {
    "tool": "search",
    "arguments": {
        "query": "Agent",
        "top_k": 3
    }
}

result = execute_tool(
    llm_output1
)

print(result)
```

执行过程：

```text
llm_output
   ↓
ToolDecision
   ↓
tool = search
   ↓
TOOL_REGISTRY["search"]
   ↓
找到：
search_paper
SearchInput
   ↓
SearchInput.model_validate()
   ↓
SearchInput对象
   ↓
model_dump()
   ↓
{
 query: Agent,
 top_k: 3
}
   ↓
**字典解包
   ↓
search_paper(
 query="Agent",
 top_k=3
)
   ↓
result
```

------

# 十五、测试 Calculator

```python
llm_output2 = {
    "tool": "calculator",
    "arguments": {
        "a": 10,
        "b": 20
    }
}

result = execute_tool(
    llm_output2
)

print(result)
```

Router 本身一行不用改。

它会自动：

```text
calculator
 ↓
TOOL_REGISTRY
 ↓
calculator函数
+
CalculatorInput
 ↓
验证
 ↓
执行
 ↓
30.0
```

------

# 十六、Tool Registry 最大的优势现在出现了

假设我们新增一个乘法 Tool：

```python
def multiply(
    a: float,
    b: float
) -> float:
    return a * b
```

模型：

```python
class MultiplyInput(BaseModel):
    a: float
    b: float
```

Registry 增加：

```python
TOOL_REGISTRY = {
    "search": {
        "function": search_paper,
        "input_model": SearchInput
    },

    "calculator": {
        "function": calculator,
        "input_model": CalculatorInput
    },

    "multiply": {
        "function": multiply,
        "input_model": MultiplyInput
    }
}
```

然后 `execute_tool()`：

```python
def execute_tool(...):
```

**完全不用改核心路由逻辑。**

这就是 Tool Registry 最核心的价值：

\boxed{\text{新增Tool ≠ 不断修改Router}}

而是：

```text
定义Tool
+
定义Schema
+
注册Tool
```

------

# 十七、不过当前代码还有一个地方需要改

我们现在：

```python
class ToolDecision(BaseModel):
    tool: Literal[
        "search",
        "calculator"
    ]
```

如果新加：

```text
multiply
```

这里也要加：

```python
tool: Literal[
    "search",
    "calculator",
    "multiply"
]
```

也就是说现在仍然有一点重复：

```text
Literal
有一份Tool列表

TOOL_REGISTRY
又有一份Tool列表
```

这个问题以后会继续优化。

最终甚至可以发展成：

```python
@tool
def search_paper(...):
    ...
```

一注册就自动：

```text
记录函数
记录Schema
记录description
生成LLM Tool Schema
```

这就是后面 LangChain、OpenAI Agents SDK 等框架会帮你做的事情。

但现在我们**先不要跳太快**。

你现在手写 Registry，就是为了以后看到：

```python
@tool
```

时知道底层大概在干什么。

------

# 十八、再优化一点：给 Tool 加描述

真正 Agent 不只要知道：

```text
Tool名字
函数
参数
```

还需要知道：

> 这个 Tool 是干什么的？

所以可以：

```python
TOOL_REGISTRY = {
    "search": {
        "function": search_paper,
        "input_model": SearchInput,
        "description": "搜索相关论文"
    },

    "calculator": {
        "function": calculator,
        "input_model": CalculatorInput,
        "description": "执行两个数字的加法"
    }
}
```

这样 Registry 中：

```text
Tool
│
├── name
├── function
├── input_model
└── description
```

越来越像真正的 Tool 定义。

------

# 十九、未来它甚至可以自动生成给 LLM 的描述

例如：

```python
for tool_name, tool_info in TOOL_REGISTRY.items():
    print(tool_name)
    print(tool_info["description"])
    print(
        tool_info["input_model"]
        .model_json_schema()
    )
```

你会得到：

```text
search

搜索相关论文

{
  query: string,
  top_k: integer,
  ...
}
```

也就是说：

```text
Tool Registry
      ↓
遍历所有Tool
      ↓
拿到：
name
description
JSON Schema
      ↓
告诉LLM
```

有没有发现我们今天前面学的：

```python
model_json_schema()
```

又接回来了？

------

# 二十、现在把所有知识串起来

一个比较完整的 Tool 生命周期：

```text
定义Pydantic输入模型
       ↓
定义Python Tool函数
       ↓
注册到Tool Registry
       ↓
Registry保存：
name
function
description
input_model
       ↓
input_model.model_json_schema()
       ↓
把Tool Schema告诉LLM
       ↓
LLM选择Tool + 生成arguments
       ↓
Registry找到Tool
       ↓
Pydantic验证arguments
       ↓
model_dump()
       ↓
**解包参数
       ↓
执行Python函数
       ↓
Tool Result
```

这张链路建议你记住。

------

# 二十一、为什么 Registry 比 if/elif 更工程化？

简单总结：

| `if / elif` Router      | Tool Registry                    |
| ----------------------- | -------------------------------- |
| Tool 越多代码越长       | Tool 统一管理                    |
| 新增 Tool 要修改 Router | 新增 Tool 主要是注册             |
| 函数和 Schema 分散      | 函数和 Schema 绑定               |
| 不方便遍历 Tool         | 可以统一遍历                     |
| 不方便生成 Schema       | 可以自动取 `model_json_schema()` |
| 扩展性一般              | 更适合 Agent                     |

所以：

Tool Registry = Agent 的工具管理中心\boxed{ \text{Tool Registry = Agent 的工具管理中心} }

------

# 这节课练习

### 练习 1

解释：

```python
TOOL_REGISTRY = {
    "search": {
        "function": search_paper,
        "input_model": SearchInput
    }
}
```

这里：

```text
"search"

"function"

search_paper

"input_model"

SearchInput
```

各自是什么。

### 练习 2

解释下面整个执行过程：

```python
tool_info = TOOL_REGISTRY[
    decision.tool
]

tool_func = tool_info["function"]

input_model = tool_info["input_model"]

args = input_model.model_validate(
    decision.arguments
)

result = tool_func(
    **args.model_dump()
)
```

这题最重要。

### 练习 3

解释：

```python
tool_func(
    **args.model_dump()
)
```

为什么：

```python
**args.model_dump()
```

可以直接作为函数参数。

比如：

```python
args.model_dump()
```

结果是：

```python
{
    "a": 10,
    "b": 20
}
```

那么最终等价于什么？

### 练习 4

你自己增加一个：

```text
multiply Tool
```

要求：

```python
multiply(a, b)
```

返回：

a×ba\times b

自己定义：

```python
MultiplyInput
multiply()
```

然后把它注册到：

```python
TOOL_REGISTRY
```

并让：

```python
execute_tool()
```

成功处理：

```python
{
    "tool": "multiply",
    "arguments": {
        "a": 6,
        "b": 7
    }
}
```

最终应该得到：

```text
42.0
```

这一轮做完，你对 **Tool Registry** 就基本掌握了。然后我们就可以结束今天的 Pydantic / Tool 工程部分，下一块进入预备周剩下的重要内容：**`async / await`**。