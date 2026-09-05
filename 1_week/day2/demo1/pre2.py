# 练习2
import requests

url = "https://httpbin.org/post"

body={
    "model":"qwen",
    "message":"什么是Agent"
}

response = requests.post(url,
                         json=body,
                         timeout=10)

print(response.json())