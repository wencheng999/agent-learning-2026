好，继续 Day 4 第二课：**`asyncio.gather()` 并发执行多个异步任务**。

这一课是今天最重要的一课，因为你会第一次真正看到：

5秒→约3秒\boxed{5秒 \rightarrow 约3秒}

------

# 一、先看“异步但不并发”

先写两个异步任务。

```python
import asyncio
import time


async def search_web():
    print("开始搜索网页")
    await asyncio.sleep(2)
    print("网页搜索完成")
    return "Web Result"


async def search_paper():
    print("开始搜索论文")
    await asyncio.sleep(3)
    print("论文搜索完成")
    return "Paper Result"
```

现在主函数这样写：

```python
async def main():
    start = time.time()

    web_result = await search_web()
    paper_result = await search_paper()

    end = time.time()

    print(web_result)
    print(paper_result)
    print(f"总耗时：{end - start:.2f} 秒")


asyncio.run(main())
```

------

# 二、你先预测一下执行顺序

代码：

```python
web_result = await search_web()
paper_result = await search_paper()
```

虽然两个函数都是：

```python
async def
```

但这里仍然是：

```text
先执行 search_web
↓
等待它完成
↓
得到 web_result
↓
再执行 search_paper
↓
等待它完成
↓
得到 paper_result
```

所以总时间大约：

2+3=5秒2 + 3 = 5\text{秒}

输出顺序大概：

```text
开始搜索网页
等待2秒
网页搜索完成
开始搜索论文
等待3秒
论文搜索完成
Web Result
Paper Result
总耗时：5.00 秒左右
```

------

# 三、为什么写了 async 还是 5 秒？

这是一个非常重要的问题。

很多初学者会以为：

> 我都写 `async def` 了，为什么没有自动并发？

因为：

```python
await search_web()
```

意思是：

> 我要等 `search_web()` 完成之后，再继续执行下一行。

而下一行正好是：

```python
await search_paper()
```

所以你还是：

```text
一个完成
↓
再执行另一个
```

因此一定记住：

async / await 本身不代表多个任务自动并发\boxed{\text{async / await 本身不代表多个任务自动并发}}

------

# 四、真正并发：`asyncio.gather()`

把 `main()` 改成：

```python
async def main():
    start = time.time()

    results = await asyncio.gather(
        search_web(),
        search_paper()
    )

    end = time.time()

    print(results)
    print(f"总耗时：{end - start:.2f} 秒")
```

完整：

```python
import asyncio
import time


async def search_web():
    print("开始搜索网页")

    await asyncio.sleep(2)

    print("网页搜索完成")

    return "Web Result"


async def search_paper():
    print("开始搜索论文")

    await asyncio.sleep(3)

    print("论文搜索完成")

    return "Paper Result"


async def main():
    start = time.time()

    results = await asyncio.gather(
        search_web(),
        search_paper()
    )

    end = time.time()

    print(results)

    print(
        f"总耗时：{end - start:.2f} 秒"
    )


asyncio.run(main())
```

------

# 五、这次执行过程是什么？

大概：

```text
开始搜索网页
开始搜索论文
```

然后两个任务一起等待。

2 秒左右：

```text
网页搜索完成
```

3 秒左右：

```text
论文搜索完成
```

最后：

```text
['Web Result', 'Paper Result']
总耗时：3.00 秒左右
```

为什么？

因为：

```text
search_web
需要2秒
        ┐
        ├── 同时运行
        │
search_paper
需要3秒
        ┘
```

总耗时主要取决于较慢的那个：

max⁡(2,3)=3秒\boxed{\max(2,3)=3\text{秒}}

而不是：

2+3=52+3=5

------

# 六、`asyncio.gather()` 可以先怎么理解？

你现在可以把它理解成：

> **把多个异步任务一起交给 asyncio，让它们并发执行，并等待它们全部完成。**

例如：

```python
results = await asyncio.gather(
    task1(),
    task2(),
    task3()
)
```

可以理解：

```text
task1 ─┐
task2 ─┼→ 一起开始
task3 ─┘
       ↓
等待全部结束
       ↓
results
```

------

# 七、`gather()` 返回什么？

例如：

```python
results = await asyncio.gather(
    search_web(),
    search_paper()
)
```

假设：

```python
search_web()
```

返回：

```text
"Web Result"
```

而：

```python
search_paper()
```

返回：

```text
"Paper Result"
```

那么：

```python
results
```

大概是：

```python
[
    "Web Result",
    "Paper Result"
]
```

也就是：

> 按传入 `gather()` 的顺序，把每个协程的返回值收集起来。

注意这一点很重要。

------

# 八、完成顺序和结果顺序不一定一样

这里：

```python
search_web()
```

2 秒完成。

```python
search_paper()
```

3 秒完成。

所以完成顺序：

```text
web
↓
paper
```

结果：

```python
[
    "Web Result",
    "Paper Result"
]
```

看起来一样。

但假设：

```python
results = await asyncio.gather(
    slow_task(),
    fast_task()
)
```

即使：

```text
fast_task
```

先完成，

`results` 依然通常按照你传进去的顺序：

```python
[
    slow_task的结果,
    fast_task的结果
]
```

所以：

gather 的结果顺序看“传入顺序”，不是完成顺序\boxed{\text{gather 的结果顺序看“传入顺序”，不是完成顺序}}

这个以后很实用。

------

# 九、可以直接拆包结果

比如：

```python
web_result, paper_result = await asyncio.gather(
    search_web(),
    search_paper()
)
```

这里相当于：

```python
results = [
    "Web Result",
    "Paper Result"
]
```

然后：

```python
web_result = results[0]
paper_result = results[1]
```

所以推荐写：

```python
web_result, paper_result = await asyncio.gather(
    search_web(),
    search_paper()
)
```

然后：

```python
print(web_result)
print(paper_result)
```

这在 Agent 里会非常常见。

------

# 十、Agent 场景一下就出来了

假设你的 Research Agent 要同时：

```text
搜网页
搜论文
搜本地RAG
```

可以：

```python
web_result, paper_result, rag_result = (
    await asyncio.gather(
        search_web(query),
        search_paper(query),
        search_rag(query)
    )
)
```

然后：

```text
三个信息源并发搜索
↓
全部完成
↓
合并结果
↓
交给LLM总结
```

这就是 Deep Research Agent 非常典型的结构。

------

# 十一、同步版 vs 并发版对比

同步式异步代码：

```python
web_result = await search_web()
paper_result = await search_paper()
rag_result = await search_rag()
```

假设：

```text
web   2秒
paper 3秒
rag   4秒
```

总时间：

2+3+4=9秒2+3+4=9\text{秒}

而：

```python
web_result, paper_result, rag_result = (
    await asyncio.gather(
        search_web(),
        search_paper(),
        search_rag()
    )
)
```

大约：

max⁡(2,3,4)=4秒\max(2,3,4)=4\text{秒}

前提是：

> 这三个任务彼此独立，而且主要在等待 I/O。

------

# 十二、什么时候不能直接并发？

比如：

```text
任务B必须使用任务A的结果
```

例如：

```text
先搜索论文
↓
拿到论文ID
↓
再读取PDF
```

那你就不能：

```python
await asyncio.gather(
    search_paper(),
    read_pdf()
)
```

因为：

```python
read_pdf()
```

还不知道读哪篇论文。

应该：

```python
paper = await search_paper()

pdf = await read_pdf(
    paper["id"]
)
```

也就是说：

有依赖关系的任务必须按依赖顺序执行\boxed{\text{有依赖关系的任务必须按依赖顺序执行}}

适合 `gather()` 的是：

> 互相独立、可以同时开始的任务。

------

# 十三、并发不是并行

这个概念现在简单认识一下。

### 并发 Concurrent

多个任务：

```text
A等待
↓
切B
↓
B等待
↓
切C
```

重点是：

> 在等待期间切换任务。

### 并行 Parallel

比如有多个 CPU 核：

```text
CPU1真正算A
CPU2真正算B
```

是真正同时计算。

所以我们今天讲的：

```python
asyncio
```

主要解决：

I/O 并发\boxed{\text{I/O 并发}}

不是为了让复杂 CPU 计算直接快很多。

例如：

```text
LLM API请求 ✅
网页请求 ✅
数据库查询 ✅
文件I/O ✅
```

适合 async。

但是：

```text
超大矩阵计算
视频编码
CPU密集循环
```

单纯 `asyncio` 通常不是主要解决办法。

这个区别以后面试也会问。

------

# 十四、`asyncio.create_task()` 是什么？

今天先认识一下，不深入。

比如：

```python
task1 = asyncio.create_task(
    search_web()
)

task2 = asyncio.create_task(
    search_paper()
)
```

这表示：

> 把协程注册成可以被事件循环调度的 Task。

然后：

```python
result1 = await task1
result2 = await task2
```

它们也可以并发。

但你当前阶段：

优先掌握 asyncio.gather()\boxed{\text{优先掌握 asyncio.gather()}}

就够了。

`create_task()` 下一阶段再深入。

------

# 十五、一个很常见的误区

下面：

```python
task1 = search_web()
task2 = search_paper()

result1 = await task1
result2 = await task2
```

不要想当然认为一定和：

```python
asyncio.gather(...)
```

效果完全一样。

因为：

```python
search_web()
```

这里只是创建 coroutine object，

并不等于已经像 `create_task()` 那样安排它立即并发执行。

所以最稳妥、最清楚的并发写法：

```python
await asyncio.gather(
    search_web(),
    search_paper()
)
```

------

# 十六、异常怎么办？

假设：

```python
async def task1():
    return "A"


async def task2():
    raise ValueError("出错了")
```

然后：

```python
results = await asyncio.gather(
    task1(),
    task2()
)
```

其中一个任务出错时，`gather()` 会把异常传出来。

所以可以：

```python
try:
    results = await asyncio.gather(
        task1(),
        task2()
    )

except Exception as e:
    print(f"任务执行失败：{e}")
```

这又和你 Day 1 学的：

```python
try / except
```

接上了。

------

# 十七、以后 Agent 会经常遇到这种代码

例如：

```python
async def research(
    query: str
):
    try:
        web_result, paper_result = (
            await asyncio.gather(
                search_web(query),
                search_paper(query)
            )
        )

        return {
            "web": web_result,
            "paper": paper_result
        }

    except Exception as e:
        print(
            f"Research失败：{e}"
        )
        return None
```

这已经很像 Research Agent 的一个并行检索节点了。

------

# 十八、把今天目前为止知识串起来

```text
async def
↓
定义协程函数

函数()
↓
产生coroutine

await
↓
等待一个异步操作

asyncio.run()
↓
启动最外层异步程序

asyncio.gather()
↓
并发执行多个独立协程
↓
等待全部完成
↓
收集结果
```

------

# 这一课练习

## 练习 1

为什么：

```python
await task1()
await task2()
```

即使两个函数都是 `async def`，也可能还是顺序执行？

------

## 练习 2

假设：

```text
task1 → 2秒
task2 → 3秒
task3 → 4秒
```

分别计算：

```python
await task1()
await task2()
await task3()
```

大约多少秒？

而：

```python
await asyncio.gather(
    task1(),
    task2(),
    task3()
)
```

理想情况下大约多少秒？

------

## 练习 3

解释：

```python
web_result, paper_result = await asyncio.gather(
    search_web(),
    search_paper()
)
```

这里：

```text
asyncio.gather
await
web_result
paper_result
```

分别是什么作用。

------

## 练习 4

自己写三个异步函数：

```python
search_web()
search_paper()
search_rag()
```

要求：

```text
search_web
等待2秒
返回 "Web Result"

search_paper
等待3秒
返回 "Paper Result"

search_rag
等待1秒
返回 "RAG Result"
```

然后用：

```python
asyncio.gather()
```

并发执行。

最后打印三个结果和总耗时。

理想总时间应该大约：

3秒\boxed{3\text{秒}}

你把这一轮跑通以后，下一课我们就把异步真正接到昨天的 HTTP 知识上：

httpx.AsyncClient\boxed{\text{httpx.AsyncClient}}

也就是从“模拟等待”进入**真正并发 HTTP 请求**。