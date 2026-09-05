# 完整Get推荐写法

import requests


url = "https://httpbin.org/get"

params = {
    "query": "Agent",
    "top_k": 5
}

try:
    response = requests.get(
        url,
        params=params,
        timeout=10
    )

    response.raise_for_status()

    data = response.json()

    print(data)

except requests.RequestException as e:
    print(f"请求失败：{e}")