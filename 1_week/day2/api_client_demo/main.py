from api_client import SimpleAPIClient
from config import Config

config = Config()
client = SimpleAPIClient(base_url=config.base_url,
                         timeout=config.timeout)
get_result=client.get("/get",params={
    "query":"Agent",
    "top_k":3
})
if get_result is not None:
    print(get_result)

post_result=client.post("/post",body={
    "model":"qwen",
    "message":"什么是Agent"
})
if post_result is not None:
    print(post_result)