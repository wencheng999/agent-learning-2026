这轮答得很好，尤其练习 4 已经真正把 `asyncio.gather()` 跑起来了。现在我先把几个细节校准一下，然后直接进入下一课：**`httpx.AsyncClient`，真正做异步 HTTP 请求。**

## 练习 1：核心正确，但说法再精确一点

你说：

> 单纯调用还是会顺序执行，需要 `gather` 才能并发。

核心方向对，但更准确应该是：

```python
await task1()
await task2()
```

之所以顺序，是因为第一行明确要求：

> 等 `task1()` 完全执行完，再继续下一行。

所以：

```text
await task1()
      ↓
task1 完成
      ↓
await task2()
      ↓
task2 完成
```

而不是因为“异步函数单纯调用会顺序执行”。

实际上：

```python
task1()
```

单独这样写，甚至只是创建 coroutine，并不会直接把它执行完。

而并发除了：

```python
asyncio.gather()
```

以后还可以用：

```python
asyncio.create_task()
```

不过目前你优先掌握 `gather()` 就够了。

------

## 练习 2：完全正确 ✅

三个任务分别：

```text
2 秒
3 秒
4 秒
```

顺序执行：

2+3+4=9 秒2+3+4=9\text{ 秒}

并发执行，理想情况下：

max⁡(2,3,4)=4 秒\max(2,3,4)=4\text{ 秒}

完全正确。

------

## 练习 3：基本正确

这句：

```python
web_result, paper_result = await asyncio.gather(
    search_web(),
    search_paper()
)
```

你可以更准确地理解成：

```text
asyncio.gather(...)
→ 把多个协程组织起来并发运行，
  最后收集所有返回值。

await
→ 当前 main 等待 gather 整体完成；
  等待期间事件循环仍然可以运行这些协程。

web_result
→ 接收 search_web() 的返回值。

paper_result
→ 接收 search_paper() 的返回值。
```

所以 `await` 不只是“表示这是异步操作”，而是：

暂停当前协程，等待目标异步操作完成\boxed{\text{暂停当前协程，等待目标异步操作完成}}

同时把运行机会让给别的协程。

------

# 练习 4：完全正确 ✅

你的代码：

```python
import asyncio
import time

async def search_web() -> str:
    await asyncio.sleep(2)
    return "Web Result"

async def search_paper() -> str:
    await asyncio.sleep(3)
    return "Paper Result"

async def search_rag() -> str:
    await asyncio.sleep(1)
    return "Rag Result"

async def main():
    start = time.time()

    web_result, search_result, rag_result = await asyncio.gather(
        search_web(),
        search_paper(),
        search_rag()
    )

    print(web_result + " " + search_result + " " + rag_result)

    end = time.time()
    print(end - start)

asyncio.run(main())
```

会大约 3 秒完成。

一个小建议：

```python
search_result
```

其实对应的是：

```python
search_paper()
```

所以命名成：

```python
paper_result
```

更清晰。

另外测“耗时”时，工程里我更推荐：

```python
time.perf_counter()
```

比如：

```python
start = time.perf_counter()
...
end = time.perf_counter()

print(f"总耗时：{end - start:.2f} 秒")
```

它更适合测程序执行时间。

到这里：

asyncio.gather 基础通过\boxed{\text{asyncio.gather 基础通过}}

下面正式进入下一课。

# Day 4 第三课：`httpx.AsyncClient`

前面我们的：

```python
await asyncio.sleep(2)
```

只是**模拟网络等待**。

现在要真的进行：

```text
Python
 ↓
HTTP Request
 ↓
远程 Server
 ↓
HTTP Response
```

而且在等待服务器的时候允许其他请求继续运行。

------

# 一、为什么不继续用 `requests`？

Day 2 你学的是：

```python
import requests

response = requests.get(url)
```

`requests` 是非常好用的 HTTP 库，但它主要是**同步式**使用。

例如：

```python
response1 = requests.get(url1)
response2 = requests.get(url2)
```

执行：

```text
请求1发出去
 ↓
等待请求1
 ↓
请求1回来
 ↓
请求2发出去
 ↓
等待请求2
```

这就容易阻塞。

而今天用：

```python
httpx
```

它同时支持：

```text
同步 HTTP
+
异步 HTTP
```

Agent 开发里非常实用。

------

# 二、先安装 httpx

如果还没有：

```bash
python -m pip install httpx
```

然后：

```python
import httpx
```

------

# 三、同步 httpx 其实和 requests 很像

例如：

```python
import httpx

response = httpx.get(
    "https://httpbin.org/get",
    timeout=10
)

print(response.status_code)
print(response.json())
```

这和：

```python
requests.get(...)
```

很接近。

但今天重点不是这个。

------

# 四、真正的异步 HTTP

写：

```python
import asyncio
import httpx


async def main():
    async with httpx.AsyncClient() as client:

        response = await client.get(
            "https://httpbin.org/get"
        )

        print(response.status_code)
        print(response.json())


asyncio.run(main())
```

这段代码第一次看会有两个新东西：

```python
async with
```

以及：

```python
await client.get(...)
```

我们分别讲。

------

# 五、`httpx.AsyncClient()`

以前同步：

```python
requests.get(...)
```

现在异步模式一般先创建：

```python
client = httpx.AsyncClient()
```

它可以理解成：

> 一个专门负责异步 HTTP 请求的客户端对象。

也就是：

```text
AsyncClient
│
├── get()
├── post()
├── headers
├── timeout
└── connection
```

------

# 六、为什么写 `async with`？

你 Day 1 学文件时写过：

```python
with open(...) as f:
```

还记得它的作用：

> 使用完资源后自动关闭。

`AsyncClient` 也需要管理：

```text
网络连接
连接池
底层资源
```

所以推荐：

```python
async with httpx.AsyncClient() as client:
    ...
```

意思可以先理解为：

> 创建异步 HTTP Client，在这个代码块中使用；结束后自动正确关闭。

它和：

```python
with open(...)
```

思想非常相似。

只不过这是异步资源，所以：

```python
async with
```

------

# 七、为什么 `client.get()` 前面需要 await？

这里：

```python
response = await client.get(url)
```

因为异步 HTTP 请求需要等待服务器响应。

执行：

```text
发出 HTTP GET
      ↓
服务器还没回复
      ↓
await
      ↓
当前协程暂停
      ↓
事件循环可以运行其他任务
      ↓
服务器返回
      ↓
恢复当前协程
      ↓
得到 response
```

这就是异步的真正用途。

------

# 八、和 requests 对比一下

同步：

```python
response = requests.get(url)
```

可以理解：

```text
请求发出去
↓
当前线程一直等
↓
Response
```

异步：

```python
response = await client.get(url)
```

可以理解：

```text
请求发出去
↓
当前协程等待
↓
其他协程可以继续运行
↓
Response回来
↓
恢复
```

这就是关键区别。

------

# 九、Response 的知识完全复用 Day 2

httpx 中仍然有：

```python
response.status_code
response.text
response.json()
response.raise_for_status()
```

所以：

```python
response = await client.get(url)

response.raise_for_status()

data = response.json()
```

你已经会了。

也就是说 Day 2 的 HTTP 知识完全没浪费。

------

# 十、带 Params 的 GET

比如：

```python
import asyncio
import httpx


async def main():
    url = "https://httpbin.org/get"

    params = {
        "query": "Agent",
        "top_k": 3
    }

    async with httpx.AsyncClient() as client:

        response = await client.get(
            url,
            params=params,
            timeout=10
        )

        response.raise_for_status()

        print(response.url)
        print(response.json())


asyncio.run(main())
```

这一部分和 `requests` 几乎一样：

```text
url
params=
timeout=
```

只是：

```python
requests.get(...)
```

变成：

```python
await client.get(...)
```

------

# 十一、异步 POST

POST 也是：

```python
import asyncio
import httpx


async def main():
    url = "https://httpbin.org/post"

    body = {
        "model": "qwen",
        "message": "什么是Agent？"
    }

    async with httpx.AsyncClient() as client:

        response = await client.post(
            url,
            json=body,
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        print(data)


asyncio.run(main())
```

是不是和你 Day 2 写的：

```python
requests.post(
    url,
    json=body,
    timeout=10
)
```

几乎一样？

主要变化：

```python
response = await client.post(...)
```

------

# 十二、真正并发两个 HTTP 请求

现在重点来了。

假设：

```python
async def request1(client):
    response = await client.get(
        "https://httpbin.org/get",
        params={"query": "Agent"}
    )
    return response.json()


async def request2(client):
    response = await client.get(
        "https://httpbin.org/get",
        params={"query": "RAG"}
    )
    return response.json()
```

然后：

```python
async def main():
    async with httpx.AsyncClient() as client:

        result1, result2 = await asyncio.gather(
            request1(client),
            request2(client)
        )

        print(result1)
        print(result2)
```

最后：

```python
asyncio.run(main())
```

现在执行：

```text
请求 Agent ──────┐
                 ├→ 同时等待服务器
请求 RAG   ──────┘
                 ↓
            返回两个结果
```

这才是真正的：

异步并发 HTTP\boxed{\text{异步并发 HTTP}}

------

# 十三、为什么两个函数都传同一个 client？

你看到：

```python
request1(client)
request2(client)
```

而不是每个函数里面都：

```python
httpx.AsyncClient()
```

原因是：

> 一个 Client 可以复用网络连接。

真实工程里通常不希望：

```text
请求1
→ 新建Client
→ 请求
→ 关闭

请求2
→ 新建Client
→ 请求
→ 关闭
```

而是：

```text
建立一个AsyncClient
       ↓
   ┌───┴───┐
请求1     请求2
   │         │
   └───┬────┘
       ↓
复用连接资源
```

这叫：

```text
connection pooling
连接池
```

今天知道概念就够了。

------

# 十四、异常处理

`httpx` 有自己的异常类型。

例如：

```python
try:
    response = await client.get(
        url,
        timeout=10
    )

    response.raise_for_status()

except httpx.TimeoutException:
    print("请求超时")

except httpx.RequestError as e:
    print(f"网络请求失败：{e}")

except httpx.HTTPStatusError as e:
    print(f"HTTP状态错误：{e}")
```

你可以先理解：

```text
TimeoutException
→ 请求超时

RequestError
→ 网络层请求错误

HTTPStatusError
→ raise_for_status() 检测到4xx/5xx
```

注意异常继承关系有细节，我们今天先不展开。

------

# 十五、把 Agent 场景带进来

以后你的 Research Agent 可能是：

```python
async def search_web(client, query):
    ...


async def search_paper(client, query):
    ...


async def search_news(client, query):
    ...
```

然后：

```python
web, paper, news = await asyncio.gather(
    search_web(client, query),
    search_paper(client, query),
    search_news(client, query)
)
```

这就是你之后 Deep Research Agent 中非常真实的一段逻辑：

```text
用户：
研究 Agent 推荐

        ↓

并发查询
├── Web
├── Papers
└── News

        ↓

Evidence Pool
```

所以今天学的 async 并不是纯 Python 语法题，而是直接为你后面的 Research Agent 做准备。

------

# 这一课练习

这次做 4 道。

第一题，解释下面代码：

```python
async with httpx.AsyncClient() as client:
    response = await client.get(url)
```

重点解释：

```text
AsyncClient
async with
await
response
```

各自是什么。

第二题，解释为什么：

```python
requests.get(url)
```

和：

```python
await client.get(url)
```

在等待服务器响应的时候行为不一样。

第三题，自己写一个异步 GET：

```text
URL：
https://httpbin.org/get

params：
query = Agent
top_k = 3

timeout = 10
```

要求使用：

```python
httpx.AsyncClient()
```

然后打印：

```python
response.status_code
response.url
response.json()
```

第四题，自己写两个异步函数：

```python
search_agent(client)
search_rag(client)
```

两个都访问：

```text
https://httpbin.org/get
```

但 Params 分别：

```text
query=Agent
query=RAG
```

然后用：

```python
asyncio.gather()
```

并发执行，并分别打印两个返回结果。

这一轮做完之后，我们再讲 Day 4 最后一个非常重要的工程问题：

异步任务的异常、超时和部分失败怎么办？\boxed{\text{异步任务的异常、超时和部分失败怎么办？}}

因为真实 Agent 里经常出现：

> 3 个 Tool 并发调用，2 个成功，1 个超时。

我们要学会不能因为一个 Tool 挂了，让整个 Research Agent 全崩掉。