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
    result=await asyncio.gather(search_paper(),search_web())

    end = time.time()

    print(result)
    print(f"总耗时：{end - start:.2f} 秒")


asyncio.run(main())