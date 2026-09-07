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

async def main():
    results = await asyncio.gather(
        task1(),
        task2(),
        task3(),
        return_exceptions=True
    )

    print(results)


asyncio.run(main())