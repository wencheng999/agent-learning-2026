这 5 道题基本都答对了，说明你已经把 **LLM Response 提取 + 多轮 messages 管理** 理解清楚了。只有几个小地方需要把术语再说准确一点。

练习 1 完全正确：

```python
data["choices"][0]["message"]["content"]
```

这条路径就是：

```text
data
↓
choices        一个候选结果列表
↓
[0]            取第一个候选结果
↓
message        取模型生成的消息
↓
content        取消息正文
```

所以不是背这个固定表达式，而是要养成一个习惯：

> **先看实际 JSON 结构，再一层一层取数据。**

不同 API 的响应结构可能不同，不能永远假设都是 `choices[0]["message"]["content"]`。

练习 2 也正确。更准确地说，不是“LLM 不知道第一个问题的答案”本身，而是对于典型的无状态 API，**第二次请求如果没有再次把上一轮对话传过去，模型就看不到那段历史**。

所以：

```python
messages.append({
    "role": "assistant",
    "content": answer
})
```

是在应用层保存：

```text
用户说过什么
+
模型回答过什么
```

下一次把整个 `messages` 再发送给模型。

练习 3 完全正确：

```python
messages.append({
    "role": "user",
    "content": "我叫Tom"
})

messages.append({
    "role": "assistant",
    "content": "你好Tom"
})

messages.append({
    "role": "user",
    "content": "我叫什么"
})

print(messages)
```

如果最开始还有：

```python
messages = [
    {
        "role": "system",
        "content": "你是一名老师"
    }
]
```

那么最终完整历史就是：

```text
system
↓
user
↓
assistant
↓
user
```

练习 4 完全正确：

对话历史通常由应用层管理\boxed{\text{对话历史通常由应用层管理}}

以后你学：

```text
Memory
LangGraph State
Conversation State
Context Engineering
```

本质上都会继续解决这个问题。

练习 5 也完全正确。整个链你已经能自己说出来了：

```text
用户输入
↓
append user message
↓
把整个 messages 发给 LLM
↓
HTTP Response
↓
解析 JSON
↓
提取 assistant content
↓
append assistant message
↓
下一轮
```

所以这一课可以通过。

LLM Response + Multi-turn Messages 基础通过\boxed{\text{LLM Response + Multi-turn Messages 基础通过}}

------

# Day 5 第三课：Streaming 流式输出

现在我们学一个你每天使用 ChatGPT 都能看到的现象：

> 为什么模型不是等整篇回答全部生成结束以后突然显示，而是边生成边显示？

这就是：

Streaming\boxed{\text{Streaming}}

------

## 一、普通非流式请求

我们目前写的是：

```python
response = await client.post(
    url,
    headers=headers,
    json=body
)
```

然后：

```python
data = response.json()
```

这意味着：

```text
发送请求
↓
LLM开始生成
↓
生成第1段
↓
生成第2段
↓
生成第3段
↓
全部生成完成
↓
服务器返回完整Response
↓
Python一次性得到全部回答
```

例如模型需要 10 秒生成：

```text
0秒    什么都看不到
1秒    什么都看不到
2秒    什么都看不到
...
10秒   整篇回答突然出现
```

这就是：

Non-streaming\boxed{\text{Non-streaming}}

------

# 二、Streaming 是什么？

Streaming：

```text
发送请求
↓
服务器生成一点
↓
立刻传一点
↓
再生成一点
↓
再传一点
↓
直到结束
```

用户看到的就是：

```text
Agent
Agent 是
Agent 是一种
Agent 是一种能够
Agent 是一种能够自主...
```

所以：

Streaming = 边生成，边传输，边处理\boxed{\text{Streaming = 边生成，边传输，边处理}}

------

# 三、为什么 Streaming 很重要？

主要有三个原因。

第一，**用户体验更好**。

假设模型完整生成需要 20 秒：

```text
非流式：
等20秒
↓
突然出现答案
```

流式：

```text
1秒左右
↓
已经开始看到内容
↓
后面边生成边看
```

虽然最终总时间未必大幅减少，但是：

> 用户感知到的等待时间明显降低。

第二，长回答特别适合 Streaming。

例如：

```text
生成报告
代码
论文总结
Research Agent最终报告
```

都没必要等全部生成完以后再显示。

第三，Agent 可以逐步处理模型输出。

未来一些系统可以边接收：

```text
Token / Chunk
```

边：

```text
显示
记录
解析
传给前端
```

------

# 四、Streaming 返回的不是一个完整 JSON

普通请求：

```text
服务器
↓
一个完整Response
↓
response.json()
```

Streaming 通常：

```text
服务器
↓
chunk 1
↓
chunk 2
↓
chunk 3
↓
chunk 4
...
```

这里的：

chunk\boxed{\text{chunk}}

可以理解成：

> 一小块流式数据。

例如模型最终回答：

```text
Agent 是一种智能系统
```

服务器可能分成：

```text
chunk1 → "Agent"
chunk2 → " 是一种"
chunk3 → "智能"
chunk4 → "系统"
```

具体怎么分不是固定的，也不一定一个汉字一个 chunk。

------

# 五、请求 Body 通常需要告诉服务器要 Streaming

很多兼容接口会通过：

```python
body = {
    "model": self.model,
    "messages": messages,
    "stream": True
}
```

注意：

```python
"stream": True
```

表示：

> 请不要等整份回答生成完成后一次性返回，而是使用流式方式返回。

具体字段还是要看你所使用 API 的文档，但这个设计非常常见。

------

# 六、httpx 怎么读取流？

以前：

```python
response = await client.post(...)
```

Streaming 时可以使用类似：

```python
async with client.stream(
    "POST",
    url,
    headers=headers,
    json=body
) as response:
    ...
```

这里出现：

```python
client.stream(...)
```

你可以理解为：

> 发起一个流式 HTTP 请求。

------

# 七、为什么又是 `async with`？

和之前：

```python
async with httpx.AsyncClient() as client:
```

一样，流式 Response 也是需要管理网络资源的。

所以：

```python
async with client.stream(...) as response:
```

表示：

```text
建立流式连接
↓
不断读取数据
↓
读取结束
↓
自动正确关闭连接
```

------

# 八、读取每一行

一种常见方式：

```python
async for line in response.aiter_lines():
    print(line)
```

这里第一次看到：

```python
async for
```

不要慌。

普通循环：

```python
for item in items:
    ...
```

异步流：

```python
async for item in async_items:
    ...
```

你可以先理解：

> 数据不是一次性全部准备好的，而是一块一块异步到达，所以每来一块就循环处理一块。

------

# 九、`aiter_lines()` 是什么？

```python
response.aiter_lines()
```

可以理解成：

> 异步地逐行读取服务器流式返回的内容。

所以：

```python
async for line in response.aiter_lines():
    print(line)
```

执行过程：

```text
服务器发送第1行
↓
line
↓
print

服务器发送第2行
↓
line
↓
print

服务器发送第3行
↓
line
↓
print
```

------

# 十、真实流式数据经常还有协议包装

很多 API 不是直接返回：

```text
Agent
是一种
智能系统
```

而可能类似：

```text
data: {...}

data: {...}

data: {...}

data: [DONE]
```

这种格式常见于：

SSE：Server-Sent Events\boxed{\text{SSE：Server-Sent Events}}

今天不深入 SSE 网络协议，你只需要知道：

> 流式 API 通常会给每个 chunk 加一层协议格式，因此我们还要解析每一块数据。

------

# 十一、举一个简化示例

假设服务器返回：

```text
data: {"content": "Agent"}

data: {"content": " 是一种"}

data: {"content": "智能系统"}

data: [DONE]
```

那么程序可能：

```python
async for line in response.aiter_lines():

    if not line:
        continue

    if line == "data: [DONE]":
        break

    if line.startswith("data: "):
        json_text = line[6:]
```

为什么：

```python
line[6:]
```

？

因为：

```text
"data: "
```

正好有 6 个字符。

例如：

```python
line = 'data: {"content": "Agent"}'
```

那么：

```python
line[6:]
```

得到：

```text
{"content": "Agent"}
```

也就是纯 JSON 字符串。

------

# 十二、然后把 JSON 字符串转成 Python

Day 1 又回来了：

```python
import json

chunk_data = json.loads(json_text)
```

于是：

```text
JSON string
↓
json.loads()
↓
Python dict
```

然后：

```python
content = chunk_data["content"]
```

就能拿到：

```text
Agent
```

------

# 十三、逐块打印

如果：

```python
print(content)
```

默认每次换行。

我们希望像 ChatGPT 一样连续显示，所以可以：

```python
print(
    content,
    end="",
    flush=True
)
```

这里两个新参数简单解释一下。

```python
end=""
```

表示打印完成以后**不要自动换行**。

例如：

```python
print("Agent", end="")
print(" 是一种", end="")
```

得到：

```text
Agent 是一种
```

而不是：

```text
Agent
 是一种
```

------

# 十四、`flush=True`

```python
flush=True
```

可以简单理解：

> 尽快把当前内容真正显示到终端，而不是让输出缓冲区等一会再统一显示。

对于 Streaming 很适合。

所以：

```python
print(
    content,
    end="",
    flush=True
)
```

基本就是：

> 每收到一块内容，立刻接着打印。

------

# 十五、一个简化版 Streaming Client

注意下面只是演示结构，具体 Chunk JSON 路径要根据真实服务商返回格式调整。

```python
import json
import httpx


async def stream_chat(
    client: httpx.AsyncClient,
    url: str,
    headers: dict,
    body: dict
):
    async with client.stream(
        "POST",
        url,
        headers=headers,
        json=body,
        timeout=60
    ) as response:

        response.raise_for_status()

        async for line in response.aiter_lines():

            if not line:
                continue

            if line == "data: [DONE]":
                break

            if line.startswith("data: "):

                json_text = line[6:]

                chunk_data = json.loads(
                    json_text
                )

                print(chunk_data)
```

这时候先把每个 chunk 原始结构打印出来，是最好的学习方式。

因为真实 API 很可能是：

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

------

# 十六、Streaming 为什么出现 `delta`？

普通完整 Response 是：

```python
{
    "message": {
        "content": "Agent 是一种智能系统"
    }
}
```

流式 Response 每次只返回“新增的部分”。

所以很多 API 会使用：

```python
"delta"
```

可以理解成：

本次新增内容\boxed{\text{本次新增内容}}

比如：

```text
chunk1
delta.content = "Agent"

chunk2
delta.content = " 是一种"

chunk3
delta.content = "智能系统"
```

最终拼起来：

```text
Agent 是一种智能系统
```

------

# 十七、典型提取方式

如果 chunk 类似：

```python
chunk_data = {
    "choices": [
        {
            "delta": {
                "content": "Agent"
            }
        }
    ]
}
```

那么：

```python
content = (
    chunk_data["choices"][0]
    ["delta"]
    .get("content")
)
```

这里用了：

```python
.get("content")
```

而不是：

```python
["content"]
```

原因是：

> 某些 chunk 里可能没有 `content`。

例如第一块可能只告诉你：

```python
{
    "role": "assistant"
}
```

所以：

```python
.get("content")
```

如果不存在，就返回：

```python
None
```

而不会直接 `KeyError`。

------

# 十八、然后判断

```python
if content:
    print(
        content,
        end="",
        flush=True
    )
```

如果有文字就打印。

------

# 十九、完整一点的 Streaming 示例

```python
import json
import httpx


async def stream_chat(
    client: httpx.AsyncClient,
    url: str,
    headers: dict,
    body: dict
):

    async with client.stream(
        "POST",
        url,
        headers=headers,
        json=body,
        timeout=60
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

    print()
```

------

# 二十、但还有一个问题：怎么保存完整回答？

如果我们只：

```python
print(content)
```

虽然用户看到了流式文字，但最终：

```python
answer
```

在哪里？

所以需要一个：

```python
full_content = ""
```

每次：

```python
full_content += content
```

比如：

```text
初始：
""

chunk1:
"Agent"

chunk2:
"Agent 是一种"

chunk3:
"Agent 是一种智能系统"
```

最后：

```python
return full_content
```

------

# 二十一、最终 Streaming 函数思路

```python
async def stream_chat(...):

    full_content = ""

    ...

    async for line in ...:

        ...

        if content:
            print(
                content,
                end="",
                flush=True
            )

            full_content += content

    print()

    return full_content
```

这样既实现：

```text
边生成边显示
```

也能得到：

```text
最终完整 answer
```

然后我们仍然可以：

```python
messages.append({
    "role": "assistant",
    "content": answer
})
```

所以 Streaming 并不会改变多轮对话的基本逻辑。

------

# 二十二、Streaming 整个数据流

```text
用户问题
↓
messages
↓
stream=True
↓
HTTP POST
↓
LLM开始生成
↓
chunk1
↓
解析
↓
打印

chunk2
↓
解析
↓
打印

chunk3
↓
解析
↓
打印
↓
[DONE]
↓
拼出完整answer
↓
append assistant
```

------

# 二十三、非流式和流式对比

| 非流式            | Streaming            |
| ----------------- | -------------------- |
| 等完整回答        | 边生成边接收         |
| `response.json()` | `async for` 逐块读取 |
| 一次得到完整内容  | 多个 chunk           |
| 代码简单          | 解析稍复杂           |
| 短请求很好用      | 长回答体验更好       |

------

# Streaming 第一轮练习

### 练习 1

用自己的话解释：

```text
普通 LLM Response
```

和：

```text
Streaming Response
```

最大的区别是什么？

------

### 练习 2

解释：

```python
async for line in response.aiter_lines():
```

这里：

```text
async for
aiter_lines()
line
```

分别是什么意思。

------

### 练习 3

为什么 Streaming 中经常不能直接：

```python
response.json()
```

一次拿到完整内容？

------

### 练习 4

解释：

```python
print(
    content,
    end="",
    flush=True
)
```

其中：

```text
end=""
flush=True
```

分别有什么作用。

------

### 练习 5

假设依次收到：

```text
"Agent"
" 是一种"
" 智能系统"
```

请自己写代码，通过：

```python
full_content = ""
```

不断拼接，最后打印：

```text
Agent 是一种 智能系统
```

你把这一轮做完后，我们下一步就把 Streaming 真正封装进你的 `LLMClient`，然后进入 Day 5 最后一块：**Structured Output + Pydantic**。