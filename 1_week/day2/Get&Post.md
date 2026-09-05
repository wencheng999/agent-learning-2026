这 4 道题整体答得很好，说明你已经把 **Method / URL / Params / Headers / Body** 的框架建立起来了。只有练习 4 的一个表述需要稍微纠正一下，然后我们就进入 **Day 2 第三课：GET 和 POST**。

## 练习 1：完全正确 ✅

请求：

```text
GET https://api.example.com/weather?city=Hefei&days=3
```

你拆得对：

```text
Method：
GET

URL 主体：
https://api.example.com/weather

Params：
city=Hefei
days=3
```

如果放到 Python 里，以后通常会写：

```python
url = "https://api.example.com/weather"

params = {
    "city": "Hefei",
    "days": 3
}
```

然后：

```python
requests.get(
    url,
    params=params
)
```

库会帮你组合成类似：

```text
https://api.example.com/weather?city=Hefei&days=3
```

------

## 练习 2：正确 ✅

你说：

> Authorization 是当前请求用户访问某网站的凭证，比如 LLM API Key。

基本正确。

更准确一点：

```text
Authorization
→ 告诉服务器“这个客户端有没有权限访问”
```

常见形式：

```text
Authorization: Bearer <token>
```

其中：

```text
Bearer
```

可以暂时理解成：

> “后面这个 Token 是我的访问凭证。”

例如：

```python
headers = {
    "Authorization": f"Bearer {api_key}"
}
```

而：

```text
Content-Type: application/json
```

你理解得也对：

> 告诉服务器“我发送过去的数据是什么格式”。

例如：

```text
application/json
```

表示：

> Body 按 JSON 格式解析。

------

## 练习 3：完全正确 ✅

你已经能正确拆分：

```text
POST
→ Method

https://api.example.com/chat
→ URL

{
  "model": "qwen",
  "message": "推荐三篇Agent论文"
}
→ Body
```

非常好。

以后真实的 LLM 请求，结构基本就是这个思路。

------

# 练习 4：核心对，但纠正一个地方

你说：

> Params 是向某个网站发送请求的参数，会加到 URL 后面，表示具体调用哪个 URL 功能。

前半句对：

> Params 经常放到 URL 后面。

但：

> “表示具体调用哪个 URL 功能”

不太准确。

**具体调用哪个接口/资源，主要由 URL 的 Path 决定。**

例如：

```text
/weather
```

决定：

> 调天气接口。

而：

```text
city=Hefei
```

决定：

> 在天气接口里，我具体想查合肥。

所以可以这样理解：

```text
URL Path
→ 我要调用什么资源/接口

Params
→ 我对这次请求有什么具体条件或参数

Body
→ 我要提交给服务器处理的数据
```

例如：

```text
GET /papers?keyword=Agent&top_k=10
```

其中：

```text
/papers
→ 查论文

keyword=Agent
→ 查什么关键词

top_k=10
→ 我要多少条
```

这个区别以后做 Search Tool、RAG API 时非常常见。

所以第二课：

HTTP Request 结构基础通过\boxed{\text{HTTP Request 结构基础通过}}

------

# Day 2 第三课：GET 和 POST 到底有什么区别？

这两个以后你会天天遇到。

先从最简单的理解开始：

```text
GET
→ 从服务器获取数据

POST
→ 向服务器提交数据，让服务器进行处理
```

比如：

```text
GET /papers?keyword=Agent
```

意思：

> 给我找 Agent 相关论文。

而：

```text
POST /chat
```

Body：

```json
{
  "message": "什么是Agent？"
}
```

意思：

> 我把这个问题交给你，请处理并生成答案。

------

# 一、先理解 GET

假设有个用户系统。

你想查用户：

```text
GET /users/123
```

服务器返回：

```json
{
  "id": 123,
  "name": "Tom"
}
```

整个过程：

```text
客户端
 ↓
我要用户123的信息
 ↓
GET /users/123
 ↓
服务器
 ↓
返回用户数据
```

所以 GET 最典型用途就是：

```text
查询
读取
搜索
获取
```

例如：

```text
GET /weather
GET /papers
GET /users
GET /products
```

------

# 二、GET 参数通常在哪里？

我们刚学过：

```text
GET /weather?city=Hefei&days=3
```

参数：

```text
city=Hefei
days=3
```

通常直接体现在 URL 中。

例如 Python：

```python
params = {
    "city": "Hefei",
    "days": 3
}
```

以后：

```python
requests.get(
    url,
    params=params
)
```

------

# 三、搜索特别适合 GET

比如未来你做一个 Agent Search Tool：

```text
GET /search?query=Agent&top_k=5
```

你可以理解成：

```text
搜索什么？
→ Agent

返回多少条？
→ 5
```

非常直观。

------

# 四、POST 是什么？

POST 通常用于：

> 客户端向服务器提交一批数据，让服务器执行某个操作。

例如注册用户：

```text
POST /users
```

Body：

```json
{
  "name": "Tom",
  "age": 20
}
```

意思：

> 请根据这些数据创建一个用户。

------

# 五、LLM API 为什么大量使用 POST？

假设你问：

> 什么是 Agent？

请求里面可能要发送：

```json
{
  "model": "qwen",
  "messages": [
    {
      "role": "user",
      "content": "什么是Agent？"
    }
  ],
  "temperature": 0.7
}
```

这些数据：

```text
模型
消息
参数
```

比较复杂。

如果全部塞到 URL：

```text
/chat?model=qwen&message=什么是Agent&temperature=0.7...
```

会很难管理。

所以通常：

```text
POST /chat
```

然后把复杂数据放 Body：

```text
POST /chat

Body:
{
  ...
}
```

所以：

LLM API 通常使用 POST\boxed{\text{LLM API 通常使用 POST}}

------

# 六、GET 和 POST 一个很直观的区别

假设查论文。

### GET

```text
GET /papers?keyword=Agent
```

你主要是在说：

> 我想读取/获取已有数据。

------

### POST

```text
POST /summarize
```

Body：

```json
{
  "paper": "...",
  "style": "academic"
}
```

你是在说：

> 这是数据，请帮我执行一个处理任务。

------

# 七、是不是“GET 一定没 Body，POST 一定有 Body”？

不要把它理解得这么绝对。

HTTP 协议和不同 API 的具体设计有很多细节。

但你现阶段可以按最常见实践理解：

```text
GET
→ 参数主要放 Params
→ 获取资源

POST
→ 数据主要放 Body
→ 提交/处理数据
```

这样对 Agent 开发已经够用了。

------

# 八、GET 会不会修改服务器数据？

按照良好的 REST API 设计：

```text
GET
```

应该主要用于读取，不应该因为“查询了一下”就修改服务器的重要状态。

比如：

```text
GET /users/123
```

应该只是：

> 看一下用户 123。

而不是：

> 看一下用户 123，然后把他删掉。

------

# 九、POST 可以修改服务器状态

例如：

```text
POST /users
```

可能创建用户。

```text
POST /orders
```

可能创建订单。

```text
POST /chat
```

虽然不一定永久修改业务数据，但会启动一次模型推理/处理。

所以 POST 往往代表：

> 提交一个操作请求。

------

# 十、再认识两个词：幂等和安全

这里不用深入，但以后面试或者 API 文档可能看到。

### Safe

GET 通常被设计成：

> 调用它主要是读取，不应该改变服务器状态。

------

### Idempotent

“幂等”简单理解：

> 同一个请求执行多次，结果状态和执行一次基本一样。

比如：

```text
GET /users/123
```

查 10 次还是查这个用户。

你暂时只认识这个词就行，不需要今天研究 HTTP 标准。

------

# 十一、Agent 里什么时候 GET，什么时候 POST？

假设你以后做 Research Agent：

```text
Search Tool
→ GET /search?query=...
```

因为主要是查询。

而：

```text
LLM
→ POST /chat
```

因为要提交 Prompt / Messages 给模型处理。

再比如：

```text
Embedding API
→ POST
```

因为你要提交：

```json
{
  "input": "Agent is..."
}
```

让模型生成 embedding。

------

# 十二、来看 Python 代码长什么样

先看 GET：

```python
import requests

url = "https://api.example.com/weather"

params = {
    "city": "Hefei"
}

response = requests.get(
    url,
    params=params
)
```

你现在应该能读成：

> Python 使用 GET 方法，请求这个 URL，并附带 `city=Hefei` 参数。

------

POST：

```python
import requests

url = "https://api.example.com/chat"

body = {
    "message": "什么是Agent？"
}

response = requests.post(
    url,
    json=body
)
```

意思：

> Python 使用 POST 请求 `/chat`，把 `body` 作为 JSON 数据发送给服务器。

------

# 十三、注意 `json=body`

这里你可能会问：

```python
json=body
```

为什么右边明明是 Python 字典？

例如：

```python
body = {
    "message": "Hello"
}
```

它实际上是：

```python
dict
```

但是：

```python
requests.post(
    url,
    json=body
)
```

`requests` 会帮你把 Python 字典转换成 JSON，并发送给服务器。

也就是说大概：

```text
Python dict
 ↓
requests
 ↓ 自动转换
JSON
 ↓
HTTP Body
```

所以实际开发经常不需要自己：

```python
json.dumps(body)
```

这是非常方便的。

------

# 十四、这和昨天 JSON 的知识是什么关系？

昨天我们学：

```python
json.dumps()
```

可以：

```text
dict
 ↓
JSON string
```

现在：

```python
requests.post(
    json=body
)
```

库内部会帮你完成类似的序列化工作。

所以昨天学 JSON 不是白学。

你知道：

> Python 里的 dict 和网络里的 JSON 不是完全同一个概念，只是 requests 可以帮我做转换。

这个理解很重要。

------

# 十五、GET 和 POST 先用这张表记

|                   | GET           | POST          |
| ----------------- | ------------- | ------------- |
| 常见目的          | 获取数据      | 提交/处理数据 |
| 参数              | 常见于 Params | 常见于 Body   |
| URL是否常看到参数 | 是            | 不一定        |
| LLM Chat API      | 少见          | 很常见        |
| 搜索接口          | 很常见        | 也可能有      |

注意最后一行：

> 不是“搜索一定 GET、LLM 一定 POST”。

最终还是：

以 API 文档规定为准\boxed{\text{以 API 文档规定为准}}

这是以后最重要的工程意识。

不能自己猜。

------

# 十六、以后看 API 文档先找什么？

比如官方文档写：

```text
POST /v1/chat/completions
```

你第一眼就拆：

```text
POST
→ Method

/v1/chat/completions
→ Path
```

然后继续看：

```text
Headers
Body
Response
```

这就是以后阅读 API 文档的标准方式。

------

# 第三课练习

### 练习 1

如果你想：

> 查询关键词为 `Agent` 的前 5 篇论文。

接口：

```text
https://api.example.com/papers
```

你觉得下面哪种更符合我们目前学到的常见设计？

```text
GET
还是
POST
```

同时写出 Params。

------

### 练习 2

如果你想把：

```json
{
  "message": "解释一下Transformer"
}
```

发送给：

```text
https://api.example.com/chat
```

让服务器生成答案。

应该更适合：

```text
GET
还是
POST
```

为什么？

------

### 练习 3

请解释：

```python
response = requests.post(
    url,
    json=body
)
```

这里：

```python
json=body
```

大概发生了什么？

------

### 练习 4

判断下面说法对不对，并说原因：

> “只要是 GET，请求参数就一定放在 URL；只要是 POST，参数就一定放在 Body。”

这道题答完，我们下一课就进入 **HTTP Response：status_code、response.text、response.json()、200/400/401/404/429/500 分别是什么意思**。这个学完以后，就可以真正开始 `requests/httpx` 实战了。