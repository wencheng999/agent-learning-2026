import requests
url = "https://httpbin.org/get"

headers = {
    "User-Agent": "AgentLearning/1.0"
}

response = requests.get(
    url,
    headers=headers
)
print(response.url)
print(response.status_code)
print(response.json())