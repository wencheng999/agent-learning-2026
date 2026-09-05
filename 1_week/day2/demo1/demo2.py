import requests


url = "https://httpbin.org/post"

body = {
    "model": "qwen",
    "message": "什么是Agent？"
}

response = requests.post(
    url,
    json=body
)

print(response.status_code)
print(response.json())