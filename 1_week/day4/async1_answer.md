练习1：

def hello():这个是普通的函数

async def hello():这个是异步函数，在调用时一般加上await



练习2：

会得到一个异步对象，因为这还是一个准备执行的异步任务，真正执行需要asyncio.run(hello())



练习3：

asyncio.run(main())表示执行异步任务main函数

await task()表示执行并等待 `task()` 这个异步任务完成，在等待期间可以让其他可运行的协程继续执行。



练习4：

time.sleep(2)表示整个任务阻塞2秒钟，不允许其他任务继续运行，而await asyncio.sleep(2)只是阻塞当前的一个异步任务2秒钟，但是允许其他异步任务继续运行。



