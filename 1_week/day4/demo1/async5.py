import httpx
import asyncio




async def main():
    params = {
        "query": "Agent",
        "top_k": 3
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(
            url="http://httpbin.org/get",
            params=params,
            timeout = 10
        )
        print(response.status_code)
        print(response.url)
        print(response.json())


asyncio.run(main())

