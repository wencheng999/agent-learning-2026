这 5 道题整体都答对了，说明你已经把 **Streaming 的核心思想**理解清楚了。只有两个表述稍微修正一下，然后我们把 Streaming 正式封装进前面写的 `LLMClient`。

## 练习 1：正确 ✅

你说得对。

普通非流式：

```text
用户发送问题
↓
LLM完整生成
↓
全部生成结束
↓
一次性返回完整回答
```

Streaming：

```text
用户发送问题
↓
LLM生成一部分
↓
立即传一部分
↓
再生成
↓
再传输
...
```

不过“用户不用等待”稍微改成：

> **用户不需要等待整个答案生成完成，就可以更早看到第一部分内容。**

因为第一块内容本身也需要一点首字延迟。

所以 Streaming 主要改善的是：

感知等待时间和交互体验\boxed{\text{感知等待时间和交互体验}}

不一定意味着整个回答生成总耗时明显减少。

------

## 练习 2：正确 ✅

你对：

```python
async for line in response.aiter_lines():
```

理解很好。

更准确地整理：

```text
response.aiter_lines()
→ 创建一个异步逐行读取流式Response的迭代器

async for
→ 每当下一行数据异步到达，就处理这一行；
  等下一行期间，事件循环可以调度其他协程

line
→ 当前这一轮拿到的一行数据
```

这里有一点要注意：

> `async for` 本身不是“发现阻塞就自动执行其他任务”的魔法。

真正让出执行机会的是它内部等待异步数据到达的过程。

但你现在的理解方向是对的。

------

## 练习 3：正确 ✅

因为 Streaming 返回的不是：

```text
一个完整 JSON
```

而通常是：

```text
chunk1
chunk2
chunk3
...
```

所以不能像普通请求一样简单：

```python
data = response.json()
```

然后一次得到整篇回答。

而是要：

```python
async for ...
```

逐块读取、逐块解析、逐块拼接。

------

## 练习 4：完全正确 ✅

```python
print(
    content,
    end="",
    flush=True
)
```

其中：

```python
end=""
```

表示：

> 打印完之后不要自动换行。

例如：

```python
print("Agent", end="")
print(" 是一种", end="")
```

最终：

```text
Agent 是一种
```

而：

```python
flush=True
```

表示：

> 尽快把当前输出刷新到终端。

特别适合 Streaming。

------

## 练习 5：完全正确 ✅

你的：

```python
full_content = ""

content = "Agent"
full_content += content

content = " 是一种"
full_content += content

content = " 智能系统"
full_content += content

print(full_content)
```

最终：

```text
Agent 是一种 智能系统
```

完全正确。

实际 Streaming 只是把这段：

```python
content = ...
```

换成：

```python
每一次服务器刚刚返回的 chunk
```

而已。

所以：

Streaming 基础通过\boxed{\text{Streaming 基础通过}}

------

# Day 5 第四课：把 Streaming 封装进 `LLMClient`

我们现在原来的 Client 大概是：

```python
class LLMClient:

    async def chat(
        self,
        messages: list[dict]
    ) -> str | None:
        ...
```

这是：

```text
非流式 chat()
```

现在新增：

```python
stream_chat()
```

让 Client 同时支持：

```text
LLMClient
│
├── chat()
│   └── 完整回答一次返回
│
└── stream_chat()
    └── 边生成边显示
```

------

## 一、先看方法定义

```python
async def stream_chat(
    self,
    messages: list[dict]
) -> str | None:
```

这里最终仍然返回：

```python
str | None
```

为什么？

因为虽然我们中途不断打印：

```text
chunk1
chunk2
chunk3
```

但最终还会把所有 chunk 拼起来：

```python
full_content
```

然后：

```python
return full_content
```

------

# 二、构造 URL

和普通 `chat()` 一样：

```python
url = (
    self.base_url
    + "/chat/completions"
)
```

------

# 三、构造 Body

这次：

```python
body = {
    "model": self.model,
    "messages": messages,
    "stream": True
}
```

和普通请求最大的区别：

```python
"stream": True
```

告诉服务器：

> 使用流式方式返回。

------

# 四、创建完整回答变量

```python
full_content = ""
```

以后：

```text
chunk 1
↓
加进去

chunk 2
↓
再加进去

chunk 3
↓
继续加
```

最后得到完整答案。

------

# 五、发起 Streaming Request

```python
async with httpx.AsyncClient() as client:

    async with client.stream(
        "POST",
        url,
        headers=self._build_headers(),
        json=body,
        timeout=self.timeout
    ) as response:
```

这里有两个：

```python
async with
```

别混。

外层：

```python
async with httpx.AsyncClient() as client:
```

负责：

> 管理 HTTP Client。

内层：

```python
async with client.stream(...) as response:
```

负责：

> 管理这次流式 HTTP Response。

可以想成：

```text
AsyncClient
│
└── Streaming Response
```

------

# 六、先检查 HTTP 状态

```python
response.raise_for_status()
```

如果：

```text
401
429
500
```

这里直接抛异常。

只有 HTTP 层正常，才继续读取流。

------

# 七、不断读取服务器返回内容

```python
async for line in response.aiter_lines():
```

流程：

```text
收到一行
↓
处理

等待下一行
↓
收到
↓
继续处理
```

------

# 八、过滤空行

```python
if not line:
    continue
```

Streaming/SSE 中可能有空行。

如果：

```python
line = ""
```

没有需要处理的数据。

所以：

```python
continue
```

直接进入下一轮循环。

------

# 九、判断结束标志

很多兼容接口可能有：

```text
data: [DONE]
```

于是：

```python
if line == "data: [DONE]":
    break
```

表示：

> 流式生成结束，退出循环。

具体结束格式以实际服务商协议为准。

------

# 十、只处理 `data:` 行

```python
if not line.startswith("data: "):
    continue
```

例如：

```text
data: {"choices": ...}
```

才是我们现在感兴趣的数据。

------

# 十一、去掉 `data:`

```python
json_text = line[6:]
```

例如：

```python
line = 'data: {"name": "Agent"}'
```

得到：

```python
json_text = '{"name": "Agent"}'
```

现在它还是：

```text
str
```

------

# 十二、JSON string → Python dict

```python
chunk_data = json.loads(
    json_text
)
```

Day 1 的知识：

```text
JSON String
↓
json.loads()
↓
Python dict
```

------

# 十三、提取这一块新增文本

很多兼容 Chat Completion 流式接口会类似：

```python
{
    "choices": [
        {
            "delta": {
                "content": "Agent"
            }
        }
    ]
}
```

所以：

```python
content = (
    chunk_data["choices"][0]
    ["delta"]
    .get("content")
)
```

这里：

```text
choices
↓
[0]
↓
delta
↓
content
```

和之前非流式：

```text
choices
↓
[0]
↓
message
↓
content
```

不一样。

------

## 为什么？

非流式拿的是：

```python
"message"
```

完整消息。

Streaming 拿的是：

```python
"delta"
```

本次新增部分。

可以记：

```text
非流式：
message.content
→ 完整回答

Streaming：
delta.content
→ 当前新增的一小块
```

------

# 十四、打印并保存

```python
if content:

    print(
        content,
        end="",
        flush=True
    )

    full_content += content
```

同时做两件事：

```text
content
├── 打印给用户
└── 保存到 full_content
```

比如：

```text
第一次：
content = "Agent"

full_content =
"Agent"
```

第二次：

```text
content = " 是一种"

full_content =
"Agent 是一种"
```

第三次：

```text
content = "智能系统"

full_content =
"Agent 是一种智能系统"
```

------

# 十五、流结束以后

```python
print()
```

因为前面的：

```python
end=""
```

一直不换行。

最后补一个正常换行。

然后：

```python
return full_content
```

把完整答案返回。

------

# 十六、完整 `stream_chat()`

```python
import json

import httpx


async def stream_chat(
    self,
    messages: list[dict]
) -> str | None:

    url = (
        self.base_url
        + "/chat/completions"
    )

    body = {
        "model": self.model,
        "messages": messages,
        "stream": True
    }

    full_content = ""

    try:
        async with httpx.AsyncClient() as client:

            async with client.stream(
                "POST",
                url,
                headers=self._build_headers(),
                json=body,
                timeout=self.timeout
            ) as response:

                response.raise_for_status()

                async for line in response.aiter_lines():

                    if not line:
                        continue

                    if line == "data: [DONE]":
                        break

                    if not line.startswith("data: "):
                        continue

                    json_text = line[6:]

                    chunk_data = json.loads(
                        json_text
                    )

                    content = (
                        chunk_data["choices"][0]
                        ["delta"]
                        .get("content")
                    )

                    if content:
                        print(
                            content,
                            end="",
                            flush=True
                        )

                        full_content += content

        print()

        return full_content

    except httpx.TimeoutException as e:
        print(
            f"\nLLM请求超时：{e}"
        )
        return None

    except httpx.HTTPError as e:
        print(
            f"\nLLM请求失败：{e}"
        )
        return None
```

再次强调：

> `data: ...`、`[DONE]`、`choices[0].delta.content` 是常见兼容接口形态，不同服务商可能不同，真正使用时必须看对应 API 文档。

------

# 十七、怎么调用？

```python
answer = await client.stream_chat(
    messages
)
```

用户在终端会看到：

```text
Assistant: Agent 是一种能够……
```

不断出现。

最后：

```python
answer
```

仍然保存完整结果。

于是可以：

```python
messages.append(
    {
        "role": "assistant",
        "content": answer
    }
)
```

多轮对话仍然成立。

------

# 十八、现在你的 LLMClient 已经有两种模式

可以变成：

```python
class LLMClient:

    async def chat(...):
        ...
```

以及：

```python
    async def stream_chat(...):
        ...
```

于是应用层：

```python
answer = await client.chat(messages)
```

或者：

```python
answer = await client.stream_chat(messages)
```

底层实现虽然不同，但上层最后都得到：

```text
str answer
```

这是一个很好的 API 设计。

------

# 十九、为什么 Streaming 不是直接 `yield`？

你以后可能看到：

```python
async def stream():
    yield chunk
```

那叫：

Async Generator\boxed{\text{Async Generator}}

实际上更工程化的 Streaming Client，通常不会直接在底层：

```python
print(content)
```

而可能：

```python
yield content
```

让上层决定：

```text
打印到终端
发给网页前端
发WebSocket
保存日志
```

但这是异步生成器的知识。

**预备周现在不需要展开。**

你先掌握：

```text
读取 chunk
↓
解析 chunk
↓
打印
↓
拼完整 answer
```

足够了。

------

# 二十、Day 5 最后一块：Structured Output

学完 Streaming 后，我们这周还差一个非常关键的连接：

前面 Day 3 我们“假装 LLM 输出”：

```python
llm_output = {
    "tool": "search",
    "arguments": {
        "query": "Agent",
        "top_k": 5
    }
}
```

但真实 LLM 默认可能回答：

```text
好的，我认为你应该使用 search 工具，
搜索关键词是 Agent，返回 5 个结果。
```

这对程序非常不好处理。

我们真正希望：

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
ToolDecision.model_validate(...)
```

直接验证。

这就是：

Structured Output\boxed{\text{Structured Output}}

也是 **LLM → Agent Tool Calling** 的关键桥梁。

------

## 这一小节先做 3 道检查题

### 练习 1

解释：

```python
content = (
    chunk_data["choices"][0]
    ["delta"]
    .get("content")
)
```

为什么 Streaming 中通常是：

```text
delta
```

而普通完整 Response 中常见的是：

```text
message
```

？

### 练习 2

为什么 Streaming 时除了：

```python
print(content)
```

还需要：

```python
full_content += content
```

？

如果不保存 `full_content`，对后面的多轮 `messages` 会有什么影响？

### 练习 3

解释下面完整链：

```text
stream=True
→ client.stream()
→ response.aiter_lines()
→ line
→ 去掉 data:
→ json.loads()
→ delta.content
→ print
→ full_content
```

你把这 3 道答完，我们就进入 **Day 5 最后一课：Structured Output + Pydantic 真正连接 LLM**。这也是预备周最值得掌握的一块之一。