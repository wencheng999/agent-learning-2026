# 练习3
import requests

url="https://httpbin.org/get"

params={
    "query":"Agent",
    "top_k":3
}
try:
    response = requests.get(url,
                            params=params,
                            timeout=10)
    response.raise_for_status()
except requests.Timeout as e:
    print(f"请求超时:{e}")
except requests.RequestException as e:
    print(e)


print(response.status_code)
print(response.url)
print(response.json())