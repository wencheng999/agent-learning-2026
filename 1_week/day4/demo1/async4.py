import asyncio
import time

async def search_web()->str:
    await asyncio.sleep(2)
    return "Web Result"

async def search_paper()->str:
    await asyncio.sleep(3)
    return "Paper Result"

async def search_rag()->str:
    await asyncio.sleep(1)
    return "Rag Result"

async def main():
    start = time.time()
    web_result,search_result,rag_result=await asyncio.gather(
        search_web(), search_paper(), search_rag())
    print(web_result+" "+search_result+" "+rag_result)
    end = time.time()
    print(end-start)

asyncio.run(main())

