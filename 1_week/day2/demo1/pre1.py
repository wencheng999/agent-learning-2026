# 练习1
import requests

url="https://httpbin.org/get"

params={
    "query":"Agent",
    "top_k":3
}

response=requests.get(url,
                       params=params,
                       timeout=10)

print(response.status_code)
print(response.url)
print(response.json())