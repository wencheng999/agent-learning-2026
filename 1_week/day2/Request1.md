答得很好，4 道题的核心都对。只有第 1 题有一个术语上的小地方，我帮你校准一下，然后我们直接进入 **Day 2 第二课：HTTP Request 到底由什么组成**。

## 先检查你的答案

### 练习 1：基本正确 ✅

你说：

> 客户端是 Python 程序，服务器是 DeepSeek API。

前半句完全正确：

```text
Python程序 → Client 客户端
```

后半句严格来说应该是：

```text
DeepSeek 的服务器 / API 服务 → Server 服务端
DeepSeek API → 服务器对外提供的接口
```

也就是说，**API 本身不是服务器**。

可以想象成：

```text
你的 Python 程序
      │
      │ 调用
      ↓
  DeepSeek API        ← 对外的“窗口”
      │
      ↓
DeepSeek Server       ← 后面的服务器
```

比如去银行：

```text
银行柜台 → API
银行内部系统 → Server
你 → Client
```

以后我们经常为了方便说“请求 DeepSeek API”，完全没问题，但概念上你知道 API 是接口就行。

------

### 练习 2：完全正确 ✅

```text
GET /weather?city=Beijing
→ Request

{"temperature": 28}
→ Response
```

就是：

Client发Request，Server返回Response\boxed{\text{Client发Request，Server返回Response}}

------

### 练习 3：基本正确 ✅

你说：

> URL 就是获取功能的资源地址。

可以稍微改成：

> **URL 是网络上某个资源或接口的地址。**

因为 URL 不一定都是“功能”，也可能是：

```text
网页
图片
文件
API接口
```

例如：

```text
https://github.com
```

是网页地址。

而：

```text
https://api.example.com/weather
```

可能是 API 地址。

------

### 练习 4：完全正确 ✅

你说：

> HTTP 是客户端和服务器之间使用的一种传输数据的协议，而 API 是服务器提供给客户端的程序功能接口。

这个表述已经很好了。

一句话记：

HTTP解决“怎么通信”，API解决“提供什么功能”\boxed{\text{HTTP解决“怎么通信”，API解决“提供什么功能”}}

例如：

```text
天气API
→ 提供查询天气的功能

HTTP
→ Python和天气服务器之间如何发送请求、返回结果
```

所以第一课可以通过。

------

# Day 2 第二课：一个 HTTP Request 到底包含什么？

这是今天非常重要的一部分。

以后你看到：

```python
response = requests.post(
    url,
    headers=headers,
    params=params,
    json=data
)
```

如果不知道 HTTP Request 的结构，就会感觉：

> 怎么突然这么多东西？

学完这一课你就知道每一块在干嘛。

一个 HTTP 请求最核心可以先理解为：

```text
HTTP Request
│
├── Method      请求方法
├── URL         请求地址
├── Headers     请求头
├── Parameters  请求参数
└── Body        请求体
```

不是每个请求都必须五样全有，但这几个是以后最常见的。

------

# 一、Method：告诉服务器“我想干什么”

比如：

```text
GET
POST
PUT
DELETE
```

都是 HTTP Method。

你今天重点先掌握两个：

```text
GET
POST
```

### GET

通常表示：

> **我要获取数据。**

比如：

```text
GET /weather
```

意思：

> 我要查询天气。

又比如：

```text
GET /papers
```

意思：

> 我要获取论文。

------

### POST

通常表示：

> **我要向服务器提交数据，让服务器处理。**

比如调用大模型：

```text
POST /chat
```

同时发送：

```json
{
  "message": "什么是Agent？"
}
```

相当于：

> 我把问题提交给服务器，你帮我处理，然后返回答案。

所以现在先粗略记：

```text
GET
→ 拿东西

POST
→ 送数据过去让服务器处理
```

后面下一课会专门深入讲 GET 和 POST。

------

# 二、URL：告诉服务器“我要找谁”

例如：

```text
https://api.example.com/weather
```

可以想：

```text
Method：我要干什么
URL：我要在哪里干
```

例如：

```text
GET https://api.example.com/weather
```

含义就是：

> 向这个地址获取天气信息。

------

# 三、Parameters：请求参数

假设天气 API 是：

```text
https://api.example.com/weather
```

但服务器还不知道：

> 你到底想查哪个城市？

所以需要参数：

```text
city=Beijing
```

最后 URL 可能变成：

```text
https://api.example.com/weather?city=Beijing
```

这里：

```text
?
```

后面的：

```text
city=Beijing
```

就是查询参数。

可以拆成：

```text
city
 ↓
参数名

Beijing
 ↓
参数值
```

------

如果多个参数：

```text
https://api.example.com/weather?city=Beijing&days=3
```

这里：

```text
city=Beijing
```

和：

```text
days=3
```

之间用：

```text
&
```

连接。

所以：

```text
?
→ 参数开始

&
→ 多个参数之间分隔
```

------

# 四、在 Python 里一般不会自己手拼 URL

虽然可以：

```python
url = "https://api.example.com/weather?city=Beijing&days=3"
```

但是以后更常写：

```python
params = {
    "city": "Beijing",
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

库会自动帮你生成类似：

```text
?city=Beijing&days=3
```

所以第一天学过的：

```python
dict
```

现在又出现了。

这就是为什么我们前面先补 Python 基础。

------

# 五、Headers：请求的“附加说明”

这个概念第一次学很容易觉得抽象。

你可以把 Header 理解成：

> **请求附带的一些元信息，告诉服务器这个请求的一些额外信息。**

例如：

```python
headers = {
    "Authorization": "Bearer xxx",
    "Content-Type": "application/json"
}
```

以后调用 LLM API 你会经常看到。

------

## `Authorization`

例如：

```text
Authorization: Bearer sk-xxxx
```

它是在告诉服务器：

> 我是谁，这是我的访问凭证。

所以它经常和：

```text
API Key
```

联系在一起。

这时候昨天 `.env` 就串起来了：

```text
.env
 ↓
API_KEY
 ↓
os.getenv()
 ↓
Authorization Header
 ↓
发送给LLM服务器
```

------

比如：

```python
api_key = os.getenv("LLM_API_KEY")

headers = {
    "Authorization": f"Bearer {api_key}"
}
```

你现在应该已经能读懂这里的：

```python
f"Bearer {api_key}"
```

因为第一天学过 f-string。

------

# 六、`Content-Type`

另一个很常见：

```text
Content-Type: application/json
```

意思可以理解为：

> “我这次发送给你的数据是 JSON 格式。”

比如你发送：

```json
{
  "message": "Hello"
}
```

就可能告诉服务器：

```text
Content-Type: application/json
```

服务器看到以后就知道：

> 好，我按照 JSON 来解析。

------

# 七、Header 不等于 Body

这两个一定不要混。

例如：

```python
headers = {
    "Authorization": "Bearer xxx",
    "Content-Type": "application/json"
}
```

这是：

```text
请求说明信息
```

而：

```python
data = {
    "message": "什么是Agent？"
}
```

是：

```text
真正希望服务器处理的数据
```

可以用快递来类比：

```text
快递单上的：
收件信息、类型等
≈ Headers

箱子里面真正的东西
≈ Body
```

------

# 八、Body：真正发送给服务器的数据

假设调用 LLM：

```text
POST /chat
```

Body：

```json
{
  "model": "qwen",
  "message": "什么是Agent？"
}
```

也就是说：

```text
Request
│
├── Method
│   POST
│
├── URL
│   /chat
│
├── Headers
│   Authorization: Bearer xxx
│   Content-Type: application/json
│
└── Body
    {
      "model": "qwen",
      "message": "什么是Agent？"
    }
```

这个结构非常重要。

以后你调用真实 LLM API，其实就是在构造这些东西。

------

# 九、拿一个“迷你 LLM 请求”来看

假设存在一个接口：

```text
https://api.example.com/chat
```

你想问：

> 什么是 Agent？

可能发送：

```text
POST https://api.example.com/chat
```

Header：

```text
Authorization: Bearer abc123
Content-Type: application/json
```

Body：

```json
{
  "model": "qwen",
  "message": "什么是Agent？"
}
```

服务器处理以后：

```text
Response
```

可能：

```json
{
  "answer": "Agent是一种能够..."
}
```

所以完整过程：

```text
Python客户端
     │
     │ Request
     │
     │ POST /chat
     │ Authorization
     │ JSON Body
     ↓
   Server
     │
     │ 推理
     ↓
 Response
     │
     │ JSON
     ↓
Python客户端
```

是不是已经开始很接近你之后真正调用大模型了？

------

# 十、Params 和 Body 最容易混

先给你一个基础理解：

### Params

经常出现在 URL：

```text
/weather?city=Beijing
```

例如：

```python
params = {
    "city": "Beijing"
}
```

------

### Body

一般是独立于 URL 的请求内容。

例如：

```json
{
  "message": "什么是Agent？"
}
```

Python：

```python
json_data = {
    "message": "什么是Agent？"
}
```

后面可能：

```python
requests.post(
    url,
    json=json_data
)
```

所以可以先理解：

```text
Params
→ 常用于告诉服务器“筛选什么、查什么”

Body
→ 提交给服务器真正处理的数据
```

这不是绝对规则，具体还要看 API 的设计，但现在这么理解非常合适。

------

# 十一、把第一天知识全部串起来

假设以后写：

```python
import os

from dotenv import load_dotenv


load_dotenv()

api_key = os.getenv("LLM_API_KEY")

if api_key is None:
    raise ValueError("缺少API Key")


headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

body = {
    "model": "qwen",
    "message": "什么是Agent？"
}
```

你现在已经应该能理解：

```text
import                  ✅
load_dotenv()           ✅
os.getenv()             ✅
None                    ✅
raise ValueError        ✅
dict                    ✅
f-string                ✅

Authorization           ← 今天的新知识
Content-Type            ← 今天的新知识
Body                    ← 今天的新知识
```

这就是我们为什么不是直接上 LangChain。

底层学清楚之后，框架代码会非常容易理解。

------

# 十二、HTTPS 又是什么？

你现在经常看到：

```text
https://
```

而不是：

```text
http://
```

可以先非常简单地理解：

```text
HTTP
+
加密保护
≈
HTTPS
```

所以像：

```text
API Key
用户数据
LLM Prompt
```

这类信息在网络上传输时，一般应该通过 HTTPS。

你暂时不用学 TLS、证书、握手这些底层东西。

知道：

HTTPS = 更安全的 HTTP 通信\boxed{\text{HTTPS = 更安全的 HTTP 通信}}

就足够。

------

# 第二课你真正需要记住的结构

这一张图最重要：

```text
HTTP Request
│
├── Method
│      GET / POST
│
├── URL
│      请求地址
│
├── Params
│      查询参数
│
├── Headers
│      身份、数据格式等附加信息
│
└── Body
       真正发送的数据
```

比如：

```text
POST https://api.example.com/chat

Headers:
Authorization: Bearer xxx
Content-Type: application/json

Body:
{
    "message": "什么是Agent？"
}
```

以后看到任何 API 文档，你首先就是找：

```text
用 GET 还是 POST？
URL 是什么？
要传什么 Headers？
有没有 Params？
Body 要放什么？
```

只要这几个东西找到，基本就知道这个 API 应该怎么调用了。

------

# 第二课练习

### 练习 1

下面这个请求：

```text
GET https://api.example.com/weather?city=Hefei&days=3
```

请告诉我：

```text
Method 是什么？

URL 主体是什么？

有哪些 Params？
```

------

### 练习 2

下面：

```python
headers = {
    "Authorization": "Bearer abc123",
    "Content-Type": "application/json"
}
```

请分别解释：

```text
Authorization
```

和：

```text
Content-Type
```

大概有什么作用。

------

### 练习 3

假设向：

```text
POST https://api.example.com/chat
```

发送：

```json
{
  "model": "qwen",
  "message": "推荐三篇Agent论文"
}
```

这里：

```text
POST
https://api.example.com/chat
{
  ...
}
```

分别属于 HTTP Request 的哪一部分？

------

### 练习 4

你用自己的话解释一下：

> **Params 和 Body 有什么区别？**

这一题不用追求绝对严谨，按照你目前的理解回答就行。

等这四道做完，我们下一课专门把 **GET 和 POST** 讲透，然后就开始真正用 Python 发 HTTP 请求了。