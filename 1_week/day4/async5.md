这轮整体做得很好，说明你已经把 **`asyncio` 和真正的 HTTP 请求接起来了**。练习 3、4 都已经能跑出真正的异步 HTTP 代码。主要有几个小地方需要校准一下，然后我们进入今天最后一个很重要的内容：**并发任务的超时、异常和部分失败处理**。

## 练习 1：基本正确 ✅

你说：

> `AsyncClient` 是 httpx 里的异步向服务器请求的客户端对象。

正确。可以把：

```python
httpx.AsyncClient()
```

理解成：

> 一个支持异步 GET、POST 等 HTTP 请求的客户端。

和 Day 2 的：

```python
requests
```

相比：

```text
requests
→ 主要按同步方式使用

httpx.AsyncClient
→ 支持 async / await 异步请求
```

你对：

```python
async with
```

的类比也很好，不过有一个词稍微修改一下。

不是：

> 异步打开网络请求

而应该是：

> **异步地管理 `AsyncClient` 这个资源的生命周期。**

例如：

```python
async with httpx.AsyncClient() as client:
    ...
```

意味着：

```text
进入代码块
↓
创建 AsyncClient
↓
使用网络连接等资源
↓
代码块结束
↓
自动关闭 Client / 释放网络资源
```

和：

```python
with open(...) as f:
```

思想确实类似。

------

你说：

> `await` 表示异步等待当前任务执行完毕。

基本正确，更完整一点：

> `await` 暂停当前协程，等待目标异步操作完成，并把执行机会让给其他可以运行的协程。

所以：

```python
response = await client.get(url)
```

不是整个程序都停在那里。

而是：

```text
当前HTTP请求等待服务器
       ↓
当前协程暂停
       ↓
事件循环可以运行其他协程
       ↓
服务器返回
       ↓
恢复当前协程
       ↓
response得到结果
```

------

## 练习 2：正确 ✅

你的核心理解完全正确。

同步：

```python
requests.get(url)
```

在等待服务器响应期间：

```text
当前线程阻塞
↓
不能用这个线程继续跑其他协程
```

异步：

```python
await client.get(url)
```

在等待期间：

```text
当前协程暂停
↓
事件循环去执行其他任务
↓
响应回来以后再恢复
```

这里再注意一点：

你说：

> 如果服务器一直没有响应就会一直等待。

如果**没有设置 timeout**，确实可能等待很久。

所以无论同步还是异步请求，我们都推荐：

```python
timeout=10
```

这种超时设置。

------

# 练习 3：基本正确 ✅，有两个小改进

你的代码：

```python
import httpx
import asyncio


async def main():
    params = {
        "query": "Agent",
        "top_k": 3
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(
            url="http://httpbin.org/get",
            params=params,
            timeout=10
        )

        print(response.status_code)
        print(response.url)
        print(response.json())


asyncio.run(main())
```

主体完全正确。

不过题目里给的是：

```text
https://httpbin.org/get
```

所以建议写：

```python
url="https://httpbin.org/get"
```

而不是：

```python
http://httpbin.org/get
```

平时 API 调用也应该优先使用：

HTTPS\boxed{\text{HTTPS}}

因为 HTTPS 会对通信内容进行加密。

------

还有一个工程上推荐加：

```python
response.raise_for_status()
```

改成：

```python
response = await client.get(
    url="https://httpbin.org/get",
    params=params,
    timeout=10
)

response.raise_for_status()

print(response.status_code)
print(response.url)
print(response.json())
```

这样如果服务器返回：

```text
404
429
500
```

能够直接进入异常处理。

------

# 练习 4：完全正确 ✅

你的：

```python
agent_result, rag_result = await asyncio.gather(
    search_agent(client),
    search_rag(client)
)
```

已经是真正的：

并发 HTTP 请求\boxed{\text{并发 HTTP 请求}}

执行过程：

```text
search_agent()
    ↓
发送 query=Agent
    ↓
等待服务器 ───────┐
                  │
search_rag()      │
    ↓             │
发送 query=RAG    │
    ↓             │
等待服务器 ───────┘
        ↓
两个请求并发等待
        ↓
全部完成
        ↓
agent_result
rag_result
```

这部分可以认为已经掌握了。

和练习 3 一样，建议把：

```python
"http://httpbin.org/get"
```

改成：

```python
"https://httpbin.org/get"
```

并在两个函数里加：

```python
response.raise_for_status()
```

例如：

```python
async def search_agent(client):
    response = await client.get(
        "https://httpbin.org/get",
        params={"query": "Agent"},
        timeout=10
    )

    response.raise_for_status()

    return response.json()
```

------

到这里：

httpx.AsyncClient 基础通过\boxed{\text{httpx.AsyncClient 基础通过}}

接下来进入今天最后一个很重要的问题。

# Day 4 第四课：并发任务中有一个失败怎么办？

假设 Research Agent 同时做三个任务：

```text
搜索网页
搜索论文
搜索RAG
```

代码：

```python
web, paper, rag = await asyncio.gather(
    search_web(),
    search_paper(),
    search_rag()
)
```

理想情况：

```text
Web    ✅
Paper  ✅
RAG    ✅
```

当然很好。

但是现实经常是：

```text
Web    ✅
Paper  ❌ 超时
RAG    ✅
```

那怎么办？

总不能因为：

```text
Paper Search
```

挂掉了，就把另外两个已经成功的结果全部浪费掉。

这就是 Agent 工程里非常现实的问题：

Partial Failure：部分失败\boxed{\text{Partial Failure：部分失败}}

------

# 一、先看看默认 gather 遇到异常

例如：

```python
import asyncio


async def task1():
    await asyncio.sleep(1)
    return "Task 1 Success"


async def task2():
    await asyncio.sleep(2)
    raise ValueError("Task 2 出错")


async def task3():
    await asyncio.sleep(1)
    return "Task 3 Success"
```

然后：

```python
async def main():
    results = await asyncio.gather(
        task1(),
        task2(),
        task3()
    )

    print(results)


asyncio.run(main())
```

这里：

```python
task2()
```

抛：

```python
ValueError
```

那么：

```python
await asyncio.gather(...)
```

会把这个异常传播给外层。

所以：

```python
print(results)
```

正常情况下不会执行到。

注意：这不等于所有其他协程一定被自动取消；重点是**调用者这里收到了异常，正常的结果收集流程被打断了**。

------

# 二、最简单的处理：外层 try / except

可以：

```python
async def main():
    try:
        results = await asyncio.gather(
            task1(),
            task2(),
            task3()
        )

        print(results)

    except Exception as e:
        print(f"并发任务执行失败：{e}")
```

这样程序不会直接崩。

但是问题仍然存在：

> 我只知道“有任务失败了”，不好方便地拿到其他成功任务的结果。

所以对于 Research Agent，这还不够。

------

# 三、方式 1：`return_exceptions=True`

`asyncio.gather()` 有一个很实用的参数：

```python
return_exceptions=True
```

例如：

```python
results = await asyncio.gather(
    task1(),
    task2(),
    task3(),
    return_exceptions=True
)
```

这时：

```python
task2()
```

虽然出错了，但是异常不会直接从 `gather()` 往外抛。

而是作为一个“结果”放进 `results`。

最终大概：

```python
[
    "Task 1 Success",
    ValueError("Task 2 出错"),
    "Task 3 Success"
]
```

也就是说：

```text
results[0]
→ 正常结果

results[1]
→ Exception对象

results[2]
→ 正常结果
```

------

# 四、然后逐个检查

例如：

```python
results = await asyncio.gather(
    task1(),
    task2(),
    task3(),
    return_exceptions=True
)


for result in results:

    if isinstance(result, Exception):
        print(f"任务失败：{result}")

    else:
        print(f"任务成功：{result}")
```

这里：

```python
isinstance(result, Exception)
```

意思：

> 判断这个结果是不是一个异常对象。

最后可能输出：

```text
任务成功：Task 1 Success
任务失败：Task 2 出错
任务成功：Task 3 Success
```

这样：

一个任务失败，不影响我们拿到其他任务结果\boxed{\text{一个任务失败，不影响我们拿到其他任务结果}}

------

# 五、这特别适合 Research Agent

例如：

```python
results = await asyncio.gather(
    search_web(query),
    search_paper(query),
    search_rag(query),
    return_exceptions=True
)
```

可能：

```text
Web
→ 10篇网页结果

Paper
→ TimeoutException

RAG
→ 5条本地知识
```

我们仍然可以：

```text
保留 Web ✅
保留 RAG ✅
记录 Paper 失败 ⚠️
         ↓
继续让LLM生成回答
```

而不是整个 Agent 直接失败。

这就叫：

Graceful Degradation\boxed{\text{Graceful Degradation}}

可以理解为：

> 某个组件坏了，系统降低能力继续工作，而不是整个系统一起崩。

这个词以后做 Agent 项目和面试里都很有用。

------

# 六、方式 2：每个 Tool 自己处理异常

其实工程中我更推荐你理解这种思想。

例如：

```python
async def search_web(
    client: httpx.AsyncClient,
    query: str
):
    try:
        response = await client.get(
            "https://httpbin.org/get",
            params={"query": query},
            timeout=10
        )

        response.raise_for_status()

        return {
            "success": True,
            "source": "web",
            "data": response.json(),
            "error": None
        }

    except httpx.TimeoutException:
        return {
            "success": False,
            "source": "web",
            "data": None,
            "error": "请求超时"
        }

    except httpx.HTTPError as e:
        return {
            "success": False,
            "source": "web",
            "data": None,
            "error": str(e)
        }
```

注意这个 Tool 即使失败，也不再：

```python
raise
```

到最外面。

而是返回一个统一结构：

```python
{
    "success": False,
    "source": "web",
    "data": None,
    "error": "请求超时"
}
```

------

# 七、成功也返回同一种格式

成功：

```python
{
    "success": True,
    "source": "web",
    "data": {...},
    "error": None
}
```

失败：

```python
{
    "success": False,
    "source": "web",
    "data": None,
    "error": "请求超时"
}
```

这样上层 Agent 特别好处理。

例如：

```python
results = await asyncio.gather(
    search_web(client, "Agent"),
    search_paper(client, "Agent"),
    search_rag(client, "Agent")
)
```

然后：

```python
for result in results:

    if result["success"]:
        print(
            f"{result['source']} 成功"
        )

    else:
        print(
            f"{result['source']} 失败："
            f"{result['error']}"
        )
```

------

# 八、为什么统一返回结构这么重要？

因为 Agent 上层就不用写：

```text
Web失败一种格式

Paper失败另外一种格式

RAG失败又一种格式
```

统一变成：

```text
ToolResult
│
├── success
├── source
├── data
└── error
```

这其实已经开始涉及一个很重要的工程思想：

统一 Tool Result Schema\boxed{\text{统一 Tool Result Schema}}

你昨天学 Pydantic 后，应该马上想到：

> 这个东西是不是也可以定义成 Pydantic？

完全可以。

------

# 九、用 Pydantic 定义 ToolResult

例如：

```python
from pydantic import BaseModel


class ToolResult(BaseModel):
    success: bool
    source: str
    data: dict | list | str | None = None
    error: str | None = None
```

成功：

```python
return ToolResult(
    success=True,
    source="web",
    data=response.json(),
    error=None
)
```

失败：

```python
return ToolResult(
    success=False,
    source="web",
    data=None,
    error="请求超时"
)
```

看到了吗？

Day 3 的：

```text
Pydantic
```

和 Day 4 的：

```text
Async Tool
```

现在正式连接起来了。

------

# 十、超时为什么特别重要？

假设三个 Tool：

```text
Web     2秒
Paper   永远不回来
RAG     1秒
```

如果 Paper 没有 timeout：

```text
整个 gather
↓
永远等 Paper
```

所以 Agent Tool 基本都应该考虑：

```python
timeout=10
```

例如：

```python
response = await client.get(
    url,
    timeout=10
)
```

如果超过限制：

```text
httpx.TimeoutException
```

然后：

```python
except httpx.TimeoutException:
```

进行处理。

------

# 十一、Agent 需要的思路不是“永不出错”

这个工程思想非常重要。

不现实的目标：

```text
每个 Tool 永远成功
```

真实目标：

```text
Tool可能失败
↓
能发现失败
↓
能记录失败
↓
能重试 / 降级 / 忽略
↓
Agent仍尽可能完成任务
```

所以未来你还会学：

```text
Retry
Fallback
Timeout
Circuit Breaker
```

今天先掌握：

```text
Timeout
+
Partial Failure
```

就够了。

------

# 十二、一个简化版 Research Agent

现在你已经能看懂：

```python
async def research(
    client: httpx.AsyncClient,
    query: str
):

    results = await asyncio.gather(
        search_web(client, query),
        search_paper(client, query),
        search_rag(client, query),
        return_exceptions=True
    )

    valid_results = []

    for result in results:

        if isinstance(result, Exception):
            print(f"某个工具失败：{result}")
            continue

        valid_results.append(result)

    return valid_results
```

它的思想：

```text
并发三个Tool
     ↓
一个失败也不要全部崩
     ↓
过滤失败结果
     ↓
留下成功证据
     ↓
继续后面的LLM总结
```

这已经很像你未来 Deep Research Agent 的 Retrieval 层了。

------

# 这一课练习

## 练习 1

解释：

```python
await asyncio.gather(
    task1(),
    task2(),
    task3(),
    return_exceptions=True
)
```

这里：

```text
return_exceptions=True
```

有什么作用？

------

## 练习 2

假设三个任务：

```text
task1 → "A"

task2 → ValueError("失败")

task3 → "C"
```

使用：

```python
return_exceptions=True
```

以后，`results` 大概是什么？

------

## 练习 3

解释为什么 Agent 中：

```text
3个工具
2个成功
1个失败
```

通常不应该直接让整个 Agent 失败。

什么叫“部分失败”和“降级继续工作”？

------

## 练习 4

自己定义：

```python
class ToolResult(BaseModel):
```

要求字段：

```text
success: bool

source: str

data:
dict / list / str / None
默认 None

error:
str / None
默认 None
```

然后分别创建一个：

```text
成功的 Web ToolResult
```

以及：

```text
失败的 Paper ToolResult
```

这轮做完后，**Day 4 的 async/await 主体就基本结束了**。然后我们可以在今天最后做一个小综合，把：

```text
Pydantic
+
Tool Registry
+
asyncio.gather
+
httpx.AsyncClient
+
ToolResult
```

串成一个简化版的 **异步 Multi-Tool Runner**。