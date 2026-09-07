from pydantic import BaseModel
import asyncio
import httpx

query="agent"


async def search_web(client: httpx.AsyncClient,query:str):
    url="http://httpbin.org/get"
    params={"query":query}
    try:
        response = await client.get(
            url=url,
            params=params,
            timeout=10,
        )
        response.raise_for_status()
        return response.json()
    except TimeoutError as e:
        print("时间超时")
        print(e)
        return None
    except Exception as e:
        print(e)
        return None
async def search_rag(client: httpx.AsyncClient,query:str):
    url="http://httpbin.org/get"
    params={"query":query}
    try:
        response = await client.get(
            url=url,
            params=params,
            timeout=10,
        )
        response.raise_for_status()
        return response.json()
    except TimeoutError as e:
        print("时间超时")
        print(e)
        return None
    except Exception as e:
        print(e)
        return None

async def main():
    url="http://httpbin.org/get"
    params={"query":"Agent"}
    async with httpx.AsyncClient() as client:
       web_result,rag_result=await asyncio.gather(
           search_rag(client,query),search_web(client,query))
       print(web_result)
       print(rag_result)

asyncio.run(main())


