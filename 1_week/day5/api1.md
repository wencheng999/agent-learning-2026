好，今天正式进入 **Day 5：真实 LLM API 调用**。

前四天其实都是在给今天铺路。你现在已经会：

```text
Day 1
Python工程基础
.env / JSON / class / exception

Day 2
HTTP API
POST / Headers / Body / Response

Day 3
Pydantic
Structured Data / Schema / Tool Registry

Day 4
async / await
httpx.AsyncClient / gather / ToolResult
```

所以今天我们终于把这些东西真正接到：

大语言模型 LLM\boxed{\text{大语言模型 LLM}}

上。

今天我建议按这个顺序学：

```text
Day 5：LLM API

① LLM API到底在请求什么
② messages：system / user / assistant
③ model / temperature / max_tokens 等参数
④ .env读取 API Key
⑤ 手写一个 LLM Client
⑥ 用 httpx.AsyncClient 真正调用模型
⑦ 解析 LLM Response
⑧ 多轮对话为什么要保存 messages
⑨ Streaming 流式输出
⑩ Structured Output + Pydantic
```

今天不会上 LangChain。仍然坚持：

> **先把底层搞懂，再上框架。**

------

# 第一课：一次 LLM API 调用到底发生了什么？

你现在其实已经具备理解它的全部知识。

假设用户输入：

```text
什么是 Agent？
```

程序不会直接把这几个字“扔给模型”。

一般会构造一个 HTTP 请求：

```text
Python程序
   ↓
构造 messages
   ↓
构造 JSON Body
   ↓
加入 API Key
   ↓
HTTP POST
   ↓
LLM服务器
   ↓
模型生成答案
   ↓
HTTP Response
   ↓
JSON
   ↓
Python dict
   ↓
提取模型回答
```

所以 LLM API 本质上仍然是你 Day 2 学的：

HTTP Request → HTTP Response\boxed{\text{HTTP Request → HTTP Response}}

并没有突然出现什么神秘东西。

------

# 二、LLM 请求为什么通常使用 POST？

比如我们会发送：

```python
body = {
    "model": "xxx",
    "messages": [
        {
            "role": "user",
            "content": "什么是Agent？"
        }
    ]
}
```

这是要把一批数据提交给服务器进行模型推理。

所以通常：

```python
POST
```

而不是：

```python
GET
```

你 Day 2 已经学过：

```text
GET
→ 常用于读取 / 查询资源

POST
→ 常用于提交数据并让服务器处理
```

LLM 推理显然更符合后者。

------

# 三、最核心的数据结构：`messages`

以后你学 Agent，会天天见到这个：

```python
messages = [
    {
        "role": "user",
        "content": "什么是Agent？"
    }
]
```

它本质是什么？

先看 Python 类型：

```text
messages
→ list

messages[0]
→ dict
```

所以：

```python
messages: list[dict]
```

------

# 四、一条 Message 通常有哪些东西？

最基础：

```python
{
    "role": "user",
    "content": "什么是Agent？"
}
```

两个核心字段：

```text
role
→ 谁说的话

content
→ 说了什么
```

------

# 五、最常见的三个 Role

你现阶段先掌握：

```text
system
user
assistant
```

------

## 1. `system`

例如：

```python
{
    "role": "system",
    "content": "你是一名AI Agent课程老师，请用通俗易懂的方式回答。"
}
```

它主要告诉模型：

> 你应该扮演什么角色、遵循什么规则、以什么方式完成任务。

可以理解成：

```text
System Message
↓
给模型设定总体行为规则
```

------

## 2. `user`

```python
{
    "role": "user",
    "content": "什么是Agent？"
}
```

就是：

> 用户当前提出的问题。

------

## 3. `assistant`

例如：

```python
{
    "role": "assistant",
    "content": "Agent是一种能够感知、决策并执行动作的智能系统。"
}
```

表示：

> 模型之前回复过什么。

这个在多轮对话里特别重要。

------

# 六、一个完整 messages 示例

```python
messages = [
    {
        "role": "system",
        "content": "你是一名AI Agent课程老师。"
    },
    {
        "role": "user",
        "content": "什么是Agent？"
    }
]
```

可以画成：

```text
messages
│
├── message 1
│   ├── role = system
│   └── content = 课程老师
│
└── message 2
    ├── role = user
    └── content = 什么是Agent？
```

------

# 七、LLM API 请求 Body

一个非常典型的请求结构：

```python
body = {
    "model": "你的模型名称",

    "messages": [
        {
            "role": "system",
            "content": "你是一名AI助手。"
        },
        {
            "role": "user",
            "content": "什么是Agent？"
        }
    ]
}
```

注意：

```python
body
```

现在还是：

```text
Python dict
```

然后我们会：

```python
await client.post(
    url,
    json=body
)
```

Day 2 学过：

```text
Python dict
   ↓
json=body
   ↓
JSON序列化
   ↓
HTTP Request Body
```

------

# 八、API Key 放在哪里？

一般不是：

```python
body = {
    "api_key": ...
}
```

而是通过 HTTP Header，例如很多兼容接口采用：

```python
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}
```

你是不是觉得很熟？

Day 2 已经学过：

```text
Authorization
→ 身份认证

Content-Type
→ Body是什么格式
```

所以：

```text
.env
 ↓
API Key
 ↓
Authorization Header
 ↓
HTTP Request
 ↓
LLM Server确认：
你有没有权限调用？
```

------

# 九、为什么 API Key 不能直接写代码里？

错误：

```python
api_key = "sk-xxxxxxxxxxxx"
```

然后提交 GitHub。

非常危险。

所以我们继续使用 Day 1 学过的：

```text
.env
```

例如：

```env
LLM_API_KEY=你的key
LLM_BASE_URL=你的接口地址
LLM_MODEL=你的模型名
```

然后：

```python
import os

from dotenv import load_dotenv


load_dotenv()

api_key = os.getenv("LLM_API_KEY")
base_url = os.getenv("LLM_BASE_URL")
model = os.getenv("LLM_MODEL")
```

------

# 十、`.env` 到底在这个流程里干什么？

例如：

```env
LLM_API_KEY=xxxx
LLM_MODEL=xxxx
```

经过：

```python
load_dotenv()
```

然后：

```python
os.getenv("LLM_API_KEY")
```

得到 Key。

完整：

```text
.env
│
├── LLM_API_KEY
├── LLM_BASE_URL
└── LLM_MODEL
        ↓
load_dotenv()
        ↓
os.getenv()
        ↓
Python变量
        ↓
构造HTTP请求
```

------

# 十一、先写一个配置类

创建：

```python
import os

from dotenv import load_dotenv


load_dotenv()


class LLMConfig:

    def __init__(self):
        self.api_key = os.getenv(
            "LLM_API_KEY"
        )

        self.base_url = os.getenv(
            "LLM_BASE_URL"
        )

        self.model = os.getenv(
            "LLM_MODEL"
        )

        if not self.api_key:
            raise ValueError(
                "缺少 LLM_API_KEY"
            )

        if not self.base_url:
            raise ValueError(
                "缺少 LLM_BASE_URL"
            )

        if not self.model:
            raise ValueError(
                "缺少 LLM_MODEL"
            )
```

现在你应该能全部看懂。

------

# 十二、为什么这里主动 `raise ValueError`？

假设：

```python
api_key = None
```

如果我们不检查，程序可能继续：

```text
构造Request
↓
发到远程服务器
↓
401
↓
才发现没有Key
```

不如程序启动时就：

```python
if not self.api_key:
    raise ValueError(...)
```

这叫：

Fail Fast\boxed{\text{Fail Fast}}

也就是：

> 明明配置已经错了，就尽早报错，不要让错误继续传播。

这是很重要的工程思想。

------

# 十三、开始手写 `LLMClient`

我们先定义：

```python
import httpx


class LLMClient:

    def __init__(
        self,
        api_key: str,
        base_url: str,
        model: str,
        timeout: int = 60
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout
```

是不是和 Day 2：

```python
SimpleAPIClient
```

非常像？

就是：

```text
保存：
API Key
Base URL
Model
Timeout
```

------

# 十四、构造 Headers

```python
def _build_headers(self) -> dict:
    return {
        "Authorization": (
            f"Bearer {self.api_key}"
        ),
        "Content-Type": "application/json"
    }
```

假设：

```python
self.api_key = "abc123"
```

最后得到：

```python
{
    "Authorization": "Bearer abc123",
    "Content-Type": "application/json"
}
```

------

# 十五、写异步 `chat()` 方法

先看整体：

```python
async def chat(
    self,
    messages: list[dict]
) -> dict | None:
```

这里：

```text
async def
→ 异步函数

messages: list[dict]
→ 接收对话消息

-> dict | None
→ 成功返回响应数据
→ 失败暂时返回None
```

------

# 十六、构造 Body

```python
body = {
    "model": self.model,
    "messages": messages
}
```

例如：

```python
messages = [
    {
        "role": "user",
        "content": "什么是Agent？"
    }
]
```

最后：

```python
body = {
    "model": "xxx",
    "messages": [
        {
            "role": "user",
            "content": "什么是Agent？"
        }
    ]
}
```

------

# 十七、发送真实 POST 请求

很多 OpenAI-compatible Chat Completion 风格接口会使用类似：

```text
/chat/completions
```

的路径。具体路径和字段最终要以你使用的模型提供商文档为准。

我们的 Client 可以暂时写成：

```python
url = (
    self.base_url
    + "/chat/completions"
)
```

然后：

```python
async with httpx.AsyncClient() as client:

    response = await client.post(
        url,
        headers=self._build_headers(),
        json=body,
        timeout=self.timeout
    )
```

现在这一句你已经全部学过了：

```text
url
→ 请求地址

headers
→ API Key等元信息

json=body
→ LLM请求内容

timeout
→ 避免长时间卡住

await
→ 等待LLM服务器时允许其他协程工作
```

这就是为什么前四天一项都不是白学。

------

# 十八、检查 Response

```python
response.raise_for_status()
```

如果：

```text
2xx
→ 正常

401
→ Key / Authentication问题

429
→ 限流等问题

5xx
→ 服务端问题
```

------

# 十九、把 JSON Response 转成 Python

```python
data = response.json()
```

所以：

```text
LLM Server
↓
JSON Response
↓
response.json()
↓
Python dict
↓
data
```

然后：

```python
return data
```

------

# 二十、第一个 `LLMClient` 完整版本

```python
import httpx


class LLMClient:

    def __init__(
        self,
        api_key: str,
        base_url: str,
        model: str,
        timeout: int = 60
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    def _build_headers(self) -> dict:
        return {
            "Authorization": (
                f"Bearer {self.api_key}"
            ),
            "Content-Type": "application/json"
        }

    async def chat(
        self,
        messages: list[dict]
    ) -> dict | None:

        url = (
            self.base_url
            + "/chat/completions"
        )

        body = {
            "model": self.model,
            "messages": messages
        }

        try:
            async with httpx.AsyncClient() as client:

                response = await client.post(
                    url,
                    headers=self._build_headers(),
                    json=body,
                    timeout=self.timeout
                )

                response.raise_for_status()

                return response.json()

        except httpx.TimeoutException as e:
            print(f"LLM请求超时：{e}")
            return None

        except httpx.HTTPError as e:
            print(f"LLM请求失败：{e}")
            return None
```

------

# 二十一、现在写 `main()`

```python
import asyncio


async def main():

    config = LLMConfig()

    client = LLMClient(
        api_key=config.api_key,
        base_url=config.base_url,
        model=config.model
    )

    messages = [
        {
            "role": "system",
            "content": (
                "你是一名AI Agent课程老师。"
            )
        },
        {
            "role": "user",
            "content": (
                "请用简单语言解释什么是Agent。"
            )
        }
    ]

    result = await client.chat(
        messages
    )

    print(result)


asyncio.run(main())
```

如果配置和提供商接口一致，就会真正：

```text
你的Python程序
      ↓
真实HTTP POST
      ↓
真实LLM
      ↓
真实模型回答
```

------

# 二十二、但是 `result` 为什么是一大坨？

实际 LLM Response 一般不是：

```python
{
    "answer": "Agent是什么..."
}
```

那么简单。

通常还会包含：

```text
request id
model
choices
usage
finish reason
message
token usage
...
```

所以我们下一课会专门学：

怎么从 LLM Response 里正确提取 content\boxed{\text{怎么从 LLM Response 里正确提取 content}}

这也是昨天你问嵌套 JSON 时学：

```python
data["choices"][0]["message"]["content"]
```

真正派上用场的时候。

------

# 二十三、还有一个重要问题：为什么 messages 是 list？

因为聊天不是永远只有一句。

比如：

```python
messages = [
    {
        "role": "system",
        "content": "你是一名老师。"
    },
    {
        "role": "user",
        "content": "什么是Agent？"
    },
    {
        "role": "assistant",
        "content": "Agent是一种..."
    },
    {
        "role": "user",
        "content": "那它和普通LLM有什么区别？"
    }
]
```

这就表示：

```text
System
↓
User 第1轮
↓
Assistant 第1轮
↓
User 第2轮
```

这就是：

Conversation History\boxed{\text{Conversation History}}

也就是对话历史。

后面：

```text
Memory
Context Engineering
Agent State
```

都和这个密切相关。

------

# 二十四、LLM 本身到底“记不记得上一轮”？

这个问题很重要。

假设第一次请求：

```python
messages = [
    {
        "role": "user",
        "content": "我叫Tom"
    }
]
```

模型回答以后。

第二次你只发送：

```python
messages = [
    {
        "role": "user",
        "content": "我叫什么？"
    }
]
```

对于典型无状态 API 来说，它通常并不知道前一次请求内容。

你需要自己把历史消息重新放进去：

```python
messages = [
    {
        "role": "user",
        "content": "我叫Tom"
    },
    {
        "role": "assistant",
        "content": "你好Tom。"
    },
    {
        "role": "user",
        "content": "我叫什么？"
    }
]
```

所以一个特别重要的思想是：

对话历史通常由应用层管理\boxed{\text{对话历史通常由应用层管理}}

不是简单认为：

> “模型服务器一直自动记着我。”

这对你后面学 Agent Memory 很重要。

------

# 第一课练习

先不急着真正填 API Key，先做概念 + 代码。

### 练习 1

解释：

```python
messages = [
    {
        "role": "system",
        "content": "你是一名老师。"
    },
    {
        "role": "user",
        "content": "什么是Agent？"
    }
]
```

其中：

```text
messages
role
system
user
content
```

分别是什么。

### 练习 2

解释为什么 LLM API 一般需要：

```python
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}
```

两个字段分别干什么。

### 练习 3

解释：

```python
response = await client.post(
    url,
    headers=headers,
    json=body,
    timeout=60
)
```

这里：

```text
await
client.post
url
headers
json=body
timeout
response
```

分别表示什么。

### 练习 4

为什么：

```python
async def chat(...)
```

比较适合 LLM API，而不是一定要写成普通：

```python
def chat(...)
```

？

### 练习 5

解释这个完整过程：

```text
.env
→ LLMConfig
→ LLMClient
→ messages
→ body
→ HTTP POST
→ LLM Server
→ Response
→ response.json()
```

这题最重要。

你把这一轮做完，我们下一课就正式讲 **LLM Response 的嵌套结构 + 多轮 messages 管理**，然后再进入 Streaming。