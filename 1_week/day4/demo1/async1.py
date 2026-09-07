import asyncio

async def task1():
    print("任务1开始")

    await asyncio.sleep(4)

    print("任务1结束")

async def task2():
    print("任务2开始")

async def main():
     await task1()
     await task2()


asyncio.run(main())
