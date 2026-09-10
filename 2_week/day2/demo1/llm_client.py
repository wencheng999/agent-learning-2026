import httpx
import json

class LLMClient:
    def __init__(self,
                 api_key: str,
                 base_url: str,
                 model: str,
                 timeout: int=60):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.timeout = timeout

    def _build_headers(self)->dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }


    async def chat(self,messages:list[dict])->dict|None:
        url=(self.base_url+"/chat/completions")
        body={
            "model":self.model,
            "messages":messages,
        }
        try:
            async with httpx.AsyncClient() as client:
                response=await client.post(url,
                                           headers=self._build_headers(),
                                           json=body,
                                           timeout=self.timeout
                                           )
                response.raise_for_status()
                data=response.json()
                content = (
                    data["choices"][0]
                    ["message"]
                    ["content"]
                )

                return content
        except httpx.TimeoutException as e:
            print(f"LLM请求超时：{e}")
            return None
        except httpx.HTTPError as e:
            print(f"LLM请求失败：{e}")
            return None

    async def stream_chat(
            self,messages:list[dict]
    )->str|None:
        url = (self.base_url + "/chat/completions")
        body = {
            "model": self.model,
            "messages": messages,
            "stream":True
        }
        full_content = ""
        try:
            async with httpx.AsyncClient() as client:
                async with client.stream(
                        "POST",
                        url,
                        headers=self._build_headers(),
                        json=body,
                        timeout=self.timeout
                ) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if not line:
                            continue
                        if line == "data: [DONE]":
                            break
                        if not line.startswith("data: "):
                            continue

                        json_text = line[6:]

                        chunk_data = json.loads(
                            json_text
                        )

                        content = (
                            chunk_data["choices"][0]
                            ["delta"]
                            .get("content")
                        )

                        if content:
                            print(
                                content,
                                end="",
                                flush=True
                            )
                        if type(content) is str:
                            full_content += content

            print()
            return full_content
        except httpx.TimeoutException as e:
            print(f"\nLLM请求超时：{e}")
            return None
        except httpx.HTTPError as e:
            print(f"\nLLM请求失败：{e}")
            return None






