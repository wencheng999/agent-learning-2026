import httpx


response = httpx.get(
    "https://httpbin.org/get",
    timeout=10
)

print(response.status_code)
print(response.json())