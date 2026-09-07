import asyncio
import httpx

async def search_agent(client):
    response = await client.get("http://httpbin.org/get",
                                params={"query":"Agent"},
                                timeout=10)
    response.raise_for_status()
    return response.json()
async def search_rag(client):
    response = await client.get("http://httpbin.org/get",
                                params={"query":"RAG"},
                                timeout=10)
    response.raise_for_status()
    return response.json()


async def main():
    async with httpx.AsyncClient() as client:
        agent_result,rag_result = await asyncio.gather(search_agent(client),

                                                 search_rag(client))
        print(agent_result)
        print(rag_result)

asyncio.run(main())