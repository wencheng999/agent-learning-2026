import asyncio

async def search_paper()->list:
    print("开始搜索论文")
    await asyncio.sleep(2)
    return ["Paper A","Paper B"]

async def main():
    result = await search_paper()
    print(result)


asyncio.run(main())