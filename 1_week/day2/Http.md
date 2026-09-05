来啦 😄
那我们正式开始 **Day 2：HTTP API 基础**。

今天的目标不是让你马上会“调用大模型 API”，而是先把底层逻辑弄明白。因为以后不管是：

```text
DeepSeek API
OpenAI API
Qwen API
搜索 API
天气 API
MCP Server
第三方 Tool
```

本质上都离不开：

HTTP 请求 + JSON 数据\boxed{\text{HTTP 请求 + JSON 数据}}

你今天把这个底层搞懂，后面再看 LLM API 代码就不会只是照抄。

------

# Day 2 今天要学什么？

今天我建议分成 5 小课：

```text
① HTTP 是什么
② URL / Request / Response
③ GET / POST
④ Header / Status Code / JSON
⑤ Python requests / httpx 实战
```

今天结束时，你应该能看懂这种代码：

```python
import requests

response = requests.get(
    "https://api.example.com/users"
)

print(response.status_code)
print(response.json())
```

也能看懂：

```python
response = requests.post(
    "https://api.example.com/chat",
    headers={
        "Authorization": "Bearer xxx"
    },
    json={
        "message": "Hello"
    }
)
```

------

# 第一课：HTTP 到底是什么？

先从最底层开始。

你平时打开浏览器访问：

```text
https://github.com
```

实际上发生的是：

```text
你的电脑
   ↓
发送请求
   ↓
GitHub服务器
   ↓
处理请求
   ↓
返回结果
   ↓
浏览器显示网页
```

这个“请求—响应”的通信规则，就是 HTTP。

HTTP 全称：

```text
HyperText Transfer Protocol
```

你不用死记英文。

你现在只要理解：

> **HTTP 是客户端和服务器之间通信的一套规则。**

------

# 什么叫客户端和服务器？

比如你打开浏览器：

```text
Chrome
Edge
Python程序
Postman
```

这些都可以叫：

```text
Client 客户端
```

而 GitHub、DeepSeek、OpenAI 后面的服务器叫：

```text
Server 服务端
```

所以：

```text
Client
  ↓ Request
Server
  ↓ Response
Client
```

------

# 举一个生活类比

你可以把 HTTP 想成“去餐厅点餐”。

```text
你
↓
服务员
↓
厨房
```

对应：

```text
客户端
↓
HTTP请求
↓
服务器
```

你说：

> 我要一份牛肉面。

就是 Request。

厨房做好以后：

> 给你牛肉面。

就是 Response。

------

# HTTP 最核心的两个词

你以后一定会反复看到：

```text
Request
Response
```

Request：

> 客户端发给服务器的请求。

Response：

> 服务器返回给客户端的响应。

所以：

HTTP = Request + Response\boxed{\text{HTTP = Request + Response}}

------

# 一个真实一点的例子

假设你的 Python 程序想查询天气：

```text
Python程序
    ↓
GET /weather?city=Beijing
    ↓
天气服务器
    ↓
{
  "city": "Beijing",
  "temperature": 28
}
```

这里：

```text
GET /weather?city=Beijing
```

就是请求。

而：

```json
{
  "city": "Beijing",
  "temperature": 28
}
```

就是响应。

------

# 为什么 Agent 特别依赖 HTTP？

因为 Agent 本身经常需要调用外部能力：

```text
Agent
 ↓
LLM API
 ↓
Search API
 ↓
Weather API
 ↓
Database API
 ↓
MCP Tool
```

本质都可能是：

```text
Python
 ↓
HTTP Request
 ↓
Server
 ↓
HTTP Response
```

所以如果以后看到：

```python
requests.post(...)
```

或者：

```python
httpx.AsyncClient(...)
```

你就知道：

> 它是在向某个服务器发 HTTP 请求。

------

# 第二个概念：URL

比如：

```text
https://api.example.com/users
```

这就是 URL。

简单理解：

> URL 就是服务器资源的地址。

比如：

```text
https://github.com
```

是 GitHub 首页地址。

```text
https://api.example.com/users
```

可能是用户接口地址。

```text
https://api.example.com/weather
```

可能是天气接口地址。

------

# URL 可以拆成几部分

例如：

```text
https://api.example.com/users?id=123
```

简单拆：

```text
https
↓
协议

api.example.com
↓
服务器域名

/users
↓
路径

?id=123
↓
查询参数
```

你现在先记住：

```text
协议
域名
路径
参数
```

就行。

------

# 什么是 API？

你以后会一直听：

```text
LLM API
Search API
Weather API
GitHub API
```

API 可以先简单理解：

> **别人提供给程序调用的接口。**

例如天气公司不需要把整个内部系统开放给你。

它只提供：

```text
/weather
```

接口。

你传：

```text
city=Beijing
```

它返回天气。

所以：

```text
你的程序
↓
API
↓
别人的系统
```

------

# HTTP 和 API 是什么关系？

这个经常混。

可以这样理解：

```text
API
= 提供什么功能

HTTP
= 怎么传输
```

例如：

```text
Weather API
```

提供：

> 查天气功能。

而它可能通过：

```text
HTTP
```

和你通信。

------

# REST API 是什么？

你今天先不用学理论。

只要先简单理解：

> REST API 是一种很常见的基于 HTTP 的 API 设计方式。

你经常会看到：

```text
GET /users
POST /users
GET /papers
POST /chat
```

后面我们会讲 GET / POST。

------

# 第一课你先掌握到这里

现在你应该知道：

```text
HTTP
→ 客户端和服务器通信规则

Request
→ 客户端发请求

Response
→ 服务器返回响应

URL
→ 资源地址

API
→ 程序调用功能的接口

REST API
→ 常见HTTP API设计方式
```

------

# 给你 4 个很短的小问题

你先回答这 4 个，我们再进入第二课：**HTTP Request 到底由哪些部分组成**。

### 练习 1

下面谁是客户端，谁是服务器？

```text
Python程序调用DeepSeek API
```

------

### 练习 2

下面哪个是 Request，哪个是 Response？

```text
发送：
GET /weather?city=Beijing

返回：
{
  "temperature": 28
}
```

------

### 练习 3

`URL` 你现在怎么理解？

------

### 练习 4

HTTP 和 API 有什么区别？

你按自己的话回答就行，不要求术语特别标准。