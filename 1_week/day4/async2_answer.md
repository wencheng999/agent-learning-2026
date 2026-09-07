练习1：

因为这是声明了这是个异步函数，单纯调用还是会顺序执行，如果需要异步并发则需要gather并发函数，把异步函数放进去。



练习2：

第一个大约9秒，第二个大约4秒



练习3：

asyncio.gather  表示并发执行异步函数

await 表示这是一个异步执行操作

web_result 把search_web()的结果放进去

paper_result 把search_paper()的结果放进去



练习4：

