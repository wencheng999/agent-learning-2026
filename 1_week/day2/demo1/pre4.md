url表示请求的资源地址是什么。
headers 保存 HTTP 请求的一些附加元信息。
json=body 表示让 requests 把 body 作为 JSON 请求体发送，并自动进行 JSON 序列化。
timeout=10表示请求响应的最大时间是多少，防止无限时间等待服务器响应。
具体是： 建立连接等待时间+ 等待服务器传回数据的时间
raise_for_status()主动检查 HTTP 状态码，如果是错误状态则抛出异常。
response.json()表示解析 Response Body 中的 JSON，并转换成对应的 Python 对象。