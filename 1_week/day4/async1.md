来啦，今天正式进入 **Day 4：`async / await` 异步编程**。

前 3 天你已经完成了：

```text
Day 1
Python工程基础
→ 类型注解 / class / 异常 / JSON / .env / Git

Day 2
HTTP / API
→ GET / POST / Request / Response / requests

Day 3
Pydantic + Tool
→ BaseModel / Field / Validator
→ JSON Schema
→ 假 Tool Calling
→ Tool Registry
```

今天我们要解决一个 Agent 开发里特别现实的问题：

> **如果 Agent 要同时搜索网页、搜索论文、调用多个 API，为什么不能一个一个傻等？**

这就是异步编程要解决的问题。

------

# Day 4 今天学什么

今天按这个顺序：

```text
① 同步 vs 异步
② 阻塞是什么
③ async def
④ await
⑤ asyncio.run()
⑥ asyncio.sleep()
⑦ asyncio.gather()
⑧ 并发执行多个任务
⑨ httpx.AsyncClient
⑩ Agent为什么大量使用异步
```

学完后，你应该能自己写：

```python
async def search_web():
    ...

async def search_paper():
    ...

results = await asyncio.gather(
    search_web(),
    search_paper()
)
```

------

# 第一课：同步到底是什么？

我们之前写的代码基本都是：

```python
def task1():
    ...
```

这种普通函数。

假设：

```python
import time


def task1():
    print("任务1开始")
    time.sleep(2)
    print("任务1结束")


def task2():
    print("任务2开始")
    time.sleep(3)
    print("任务2结束")


task1()
task2()
```

执行过程：

```text
task1开始
 ↓
等待2秒
 ↓
task1结束
 ↓
task2开始
 ↓
等待3秒
 ↓
task2结束
```

总时间大约：

2+3=5 秒2+3=5\text{ 秒}

这就叫：

同步执行\boxed{\text{同步执行}}

意思是：

> 前一个任务没完成，后一个任务先等着。

------

# 二、什么叫阻塞？

这里：

```python
time.sleep(2)
```

会让当前程序：

> 在这 2 秒里面什么也不干，只等待。

这叫：

Blocking，阻塞\boxed{\text{Blocking，阻塞}}

比如：

```text
请求网页
↓
服务器3秒后才回答
↓
Python这3秒一直等
```

问题就在这里。

真实 Agent 经常有：

```text
调用LLM       4秒
搜索网页      3秒
搜索论文      2秒
查数据库      2秒
```

如果全部同步：

4+3+2+2=11 秒4+3+2+2=11\text{ 秒}

很多时间都浪费在：

```text
等待服务器响应
```

而不是 CPU 真正在计算。

------

# 三、为什么这些任务可以一起等？

假设 Agent 要做：

```text
搜索Google
搜索Arxiv
搜索数据库
```

它们之间互不依赖。

完全可以：

```text
同时发出3个请求
↓
一起等待
↓
谁先回来先处理谁
```

而不是：

```text
先搜索Google
等完
↓
再搜索Arxiv
等完
↓
再查数据库
```

所以理想情况：

```text
        ┌→ Google  3秒
开始 ───┼→ Arxiv   2秒
        └→ DB      4秒
                 ↓
              大约4秒
```

而不是：

3+2+4=9 秒3+2+4=9\text{ 秒}

------

# 四、这就是异步

异步可以先理解成：

> **当一个任务正在等待 I/O 时，不让整个程序傻等，而是先去执行其他任务。**

这里特别强调：

等待 I/O\boxed{\text{等待 I/O}}

什么叫 I/O？

现在你先理解这些：

```text
网络请求
文件读取
数据库查询
LLM API调用
Tool API调用
```

这些很多时候都属于 I/O 操作。

------

# 五、同步和异步的核心区别

同步：

```text
任务A
 ↓
等A完成
 ↓
任务B
 ↓
等B完成
 ↓
任务C
```

异步：

```text
任务A发出去
 ↓
A在等待
 ↓
先执行B
 ↓
B也在等待
 ↓
先执行C
 ↓
哪个完成就继续哪个
```

所以：

异步的核心不是“跑得更快”，而是“等待期间不浪费时间”\boxed{\text{异步的核心不是“跑得更快”，而是“等待期间不浪费时间”}}

这个说法很重要。

------

# 六、第一个 `async def`

普通函数：

```python
def hello():
    print("Hello")
```

异步函数：

```python
async def hello():
    print("Hello")
```

区别就是：

```text
def
↓
普通同步函数

async def
↓
异步函数 / 协程函数
```

例如：

```python
async def search_paper():
    print("搜索论文")
```

------

# 七、直接调用异步函数会发生什么？

你可能会写：

```python
async def hello():
    print("Hello")


hello()
```

你可能以为输出：

```text
Hello
```

但实际上：

```python
hello()
```

并不会像普通函数一样直接执行。

它会得到一个：

```text
coroutine object
```

也就是：

协程对象\boxed{\text{协程对象}}

------

# 八、什么是 coroutine？

这里不用学复杂定义。

你现在先理解：

> `async def` 定义的是一个异步任务模板，而调用它时会创建一个“等待被执行的协程对象”。

例如：

```python
async def hello():
    print("Hello")


coro = hello()
```

现在：

```python
coro
```

表示：

```text
一个准备执行的异步任务
```

但还没真正运行。

------

# 九、怎么真正运行？

这时需要：

```python
asyncio.run()
```

先：

```python
import asyncio
```

然后：

```python
import asyncio


async def hello():
    print("Hello")


asyncio.run(
    hello()
)
```

这次就会输出：

```text
Hello
```

所以：

```text
async def
↓
定义异步函数

hello()
↓
生成协程对象

asyncio.run(...)
↓
启动异步程序并执行协程
```

------

# 十、`asyncio.run()` 可以先怎么理解？

你现在把：

```python
asyncio.run(main())
```

理解成：

> **启动异步运行环境，然后把这个异步任务跑完。**

真实程序最常见：

```python
async def main():
    ...


if __name__ == "__main__":
    asyncio.run(main())
```

`if __name__ == "__main__":` 我们以后工程化时再深入。

目前你写：

```python
asyncio.run(main())
```

就够了。

------

# 十一、第一个完整异步程序

```python
import asyncio


async def main():
    print("开始")
    print("结束")


asyncio.run(main())
```

执行：

```text
开始
结束
```

看起来和普通程序没区别。

因为我们还没有：

```python
await
```

------

# 十二、`await` 是今天最重要的关键词

假设：

```python
async def task():
    await ...
```

`await` 可以先理解成：

> **这里需要等待一个异步操作，但是等待时允许程序先去执行其他异步任务。**

这和：

```python
time.sleep()
```

有本质区别。

------

# 十三、对比 `time.sleep()` 和 `asyncio.sleep()`

普通同步：

```python
import time

time.sleep(2)
```

表示：

> 整个当前线程直接阻塞 2 秒。

异步：

```python
import asyncio

await asyncio.sleep(2)
```

表示：

> 当前这个协程暂停 2 秒，但事件循环可以去执行其他协程。

所以：

```text
time.sleep()
→ 我睡了，其他人也别干

await asyncio.sleep()
→ 我先等2秒，你们其他任务继续干
```

这个比喻非常重要。

------

# 十四、写第一个有等待的异步函数

```python
import asyncio


async def task1():
    print("任务1开始")

    await asyncio.sleep(2)

    print("任务1结束")
```

注意：

```python
await
```

一般必须写在：

```python
async def
```

里面。

不能普通：

```python
def task1():
    await ...
```

这样不行。

------

# 十五、完整运行

```python
import asyncio


async def task1():
    print("任务1开始")

    await asyncio.sleep(2)

    print("任务1结束")


async def main():
    await task1()


asyncio.run(main())
```

执行：

```text
任务1开始
等待约2秒
任务1结束
```

------

# 十六、为什么 main 里面也要 `await task1()`？

因为：

```python
task1()
```

是一个协程。

你必须告诉 Python：

> 我要等待这个异步任务执行完成。

所以：

```python
await task1()
```

流程：

```text
main()
 ↓
await task1()
 ↓
task1开始
 ↓
await asyncio.sleep(2)
 ↓
暂停task1
 ↓
2秒后恢复
 ↓
task1结束
 ↓
回到main
```

------

# 十七、一个特别重要的规律

以后看到：

```python
async def xxx():
```

调用时常常是：

```python
await xxx()
```

比如：

```python
async def search_web():
    ...
```

那么在另一个异步函数里：

```python
result = await search_web()
```

------

# 十八、但最外层怎么办？

最外层不能写：

```python
await main()
```

普通 Python 脚本里通常要：

```python
asyncio.run(main())
```

所以结构：

```python
async def task():
    ...


async def main():
    await task()


asyncio.run(main())
```

你先把这个结构记住。

------

# 十九、现在做一个返回值

异步函数和普通函数一样可以：

```python
return
```

例如：

```python
import asyncio


async def search_paper():
    await asyncio.sleep(2)

    return [
        "Paper A",
        "Paper B"
    ]


async def main():
    result = await search_paper()

    print(result)


asyncio.run(main())
```

执行：

```text
等待2秒
↓
return list
↓
result接收
```

所以：

```python
result = await search_paper()
```

和以前：

```python
result = search_paper()
```

概念类似。

区别是多了：

```python
await
```

因为它是异步函数。

------

# 二十、Agent场景下是什么样？

以后：

```python
async def search_web(
    query: str
) -> list[str]:
    ...
```

调用：

```python
web_results = await search_web(
    "Agent"
)
```

或者：

```python
async def call_llm(
    prompt: str
) -> str:
    ...
```

调用：

```python
answer = await call_llm(
    "什么是Agent？"
)
```

所以今天的知识以后会大量出现。

------

# 二十一、第一课先别急着学并发

现在我们只学到了：

```text
async def
await
asyncio.run()
asyncio.sleep()
```

但目前这段：

```python
await task1()
await task2()
```

其实还是：

```text
先等task1
再等task2
```

所以：

> **写了 async/await ≠ 自动并发。**

这是一个特别容易犯的错误。

例如：

```python
async def main():
    await task1()
    await task2()
```

如果：

```text
task1：2秒
task2：3秒
```

依然大约：

2+3=5 秒2+3=5\text{ 秒}

真正让它们并发，是下一课的：

```python
asyncio.gather()
```

这个我们等你先把当前基础弄懂再讲。

------

# 二十二、今天第一课总结

先记这几个：

| 代码              | 含义                               |
| ----------------- | ---------------------------------- |
| `def`             | 普通同步函数                       |
| `async def`       | 定义异步函数                       |
| `await`           | 等待异步任务，同时允许其他协程运行 |
| `asyncio.run()`   | 启动并运行最外层异步程序           |
| `asyncio.sleep()` | 非阻塞式等待                       |
| `time.sleep()`    | 阻塞式等待                         |

最重要的一句话：

async/await 主要用来高效处理大量等待型 I/O 任务\boxed{\text{async/await 主要用来高效处理大量等待型 I/O 任务}}

而 Agent 恰恰有大量：

```text
LLM API
HTTP API
搜索
数据库
MCP
Tool
```

所以它非常重要。

------

# 第一课练习

### 练习 1

解释：

```python
def hello():
    ...
```

和：

```python
async def hello():
    ...
```

有什么区别？

------

### 练习 2

为什么下面：

```python
async def hello():
    print("Hello")


hello()
```

不能简单理解成已经把 `hello` 执行完了？

它返回的大概是什么？

------

### 练习 3

解释：

```python
asyncio.run(main())
```

和：

```python
await task()
```

分别是什么作用？

------

### 练习 4

解释下面两个区别：

```python
time.sleep(2)
```

和：

```python
await asyncio.sleep(2)
```

重点说清楚：

> 谁会阻塞，谁允许其他异步任务继续运行。

------

### 练习 5

自己写：

```python
async def search_paper():
```

要求：

```text
开始时打印：
开始搜索论文

异步等待2秒

返回：
["Paper A", "Paper B"]
```

然后在：

```python
async def main():
```

中调用它并打印结果。

最后：

```python
asyncio.run(main())
```

把程序跑起来。

你做完这一轮后，我们进入今天真正最关键的一课：

asyncio.gather() 并发执行多个 Agent Tool\boxed{\text{asyncio.gather() 并发执行多个 Agent Tool}}

到了那里你会直观看到：**5 秒怎么变成约 3 秒。**