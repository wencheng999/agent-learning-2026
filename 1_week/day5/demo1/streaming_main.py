import json
import httpx


async def stream_chat(
        client: httpx.AsyncClient,
        url: str,
        headers: dict,
        body: dict
):
    async with client.stream(
            "POST",
            url,
            headers=headers,
            json=body,
            timeout=60
    ) as response:

        response.raise_for_status()

        async for line in response.aiter_lines():

            if not line:
                continue

            if line == "data: [DONE]":
                break

            if line.startswith("data: "):
                json_text = line[6:]

                chunk_data = json.loads(
                    json_text
                )

                print(chunk_data)

full_content = ""
content="Agent"
full_content+=content
content=" 是一种"
full_content+=content
content=" 智能系统"
full_content+=content
print(full_content)