# 完整Post推荐写法
import requests

url="https://httpbin.org/post"
body={
    "model":"qwen",
    "message":"agent 是什么？"
}
try:
    response = requests.post(url,
                             json=body,
                             timeout=10)
    response.raise_for_status()
    data=response.json()
    print(data)
except requests.RequestException as e:
    print(e)

