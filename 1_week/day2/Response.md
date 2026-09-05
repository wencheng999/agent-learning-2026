这 4 道题整体答得很好，说明你已经基本把 **GET / POST / Params / Body / JSON** 这一层串起来了。

不过有两个小地方值得现在就纠正，不然后面写真实 API 容易踩坑。

# 一、先检查你的答案

## 练习 1：思路正确，但 Python 字典语法写错了 ⚠️

你写：

```python
Params={
    "name"="agent",
    "top_k"=5
}
```

这里 Python 字典不能用：

```python
=
```

而要用：

```python
:
```

正确：

```python
params = {
    "name": "Agent",
    "top_k": 5
}
```

不过如果题目是：

> 查询关键词为 Agent 的论文。

从语义上我更建议参数名写：

```python
params = {
    "keyword": "Agent",
    "top_k": 5
}
```

或者：

```python
params = {
    "query": "Agent",
    "top_k": 5
}
```

因为：

```python
"name"
```

更像：

> 论文名称。

而：

```python
"keyword"
```

或者：

```python
"query"
```

更像：

> 搜索关键词。

当然真实开发时，**参数叫什么不是我们自己决定的，要看 API 文档。**

例如 API 文档规定：

```text
q
limit
```

那你必须：

```python
params = {
    "q": "Agent",
    "limit": 5
}
```

不能自己改成：

```python
keyword
top_k
```

这一点以后非常重要。

------

## 练习 2：结论正确 ✅，理由稍微调整一下

你说：

> 用 POST 更适合，因为让服务器解释回答问题，不是单纯让服务器搜索查找内容。

结论：

```text
POST ✅
```

没问题。

但是不要形成：

```text
搜索 = GET
生成 = POST
```

这种绝对对应关系。

更准确的理解是：

> 这个接口需要向服务器提交一段较完整的数据，让服务器执行模型推理，因此 API 通常设计成 POST，并把输入放在 Body 中。

也就是说：

```text
POST /chat

Body:
{
    "message": "解释一下Transformer"
}
```

非常自然。

而搜索：

```text
GET /papers?query=Agent
```

确实经常使用 GET，但某些复杂搜索 API 也可能使用 POST。

所以永远记住：

GET/POST最终以API文档为准\boxed{\text{GET/POST最终以API文档为准}}

------

## 练习 3：完全正确 ✅

你说：

> `body` 可能存储请求内容或其他参数，是 Python 的 dict；`requests` 中 `json=body` 会自动把 dict 转换成 JSON 格式。

对。

比如：

```python
body = {
    "model": "qwen",
    "message": "什么是Agent？"
}
```

这是：

```text
Python dict
```

然后：

```python
requests.post(
    url,
    json=body
)
```

`requests` 会帮你做类似：

```text
dict
 ↓
JSON序列化
 ↓
放进HTTP Body
 ↓
发送给服务器
```

而且使用：

```python
json=body
```

时，`requests` 通常也会帮你设置合适的 JSON Content-Type。

这就是为什么实际代码里经常比手写：

```python
json.dumps(body)
```

方便。

------

## 练习 4：正确 ✅

你说：

> 不一定，具体要看 API 协议是什么。

核心完全正确。

术语再稍微调整一下：

> 具体看 **API 的接口定义 / API 文档**。

因为 HTTP 协议本身并不是每一个具体 API 的参数说明书。

例如某个 API 文档可能规定：

```text
POST /search?page=1

Body:
{
    "query": "Agent"
}
```

那么这个 POST 同时有：

```text
Query Params
+
Body
```

完全可以。

所以：

```text
GET → 一定只有 Params       ❌
POST → 一定只有 Body        ❌
```

不要这样死记。

------

到这里第三课：

GET / POST 基础通过\boxed{\text{GET / POST 基础通过}}

下面进入今天非常重要的一课。

# Day 2 第四课：HTTP Response 响应

前面我们一直在研究：

```text
客户端怎么发送 Request？
```

现在终于看另一半：

```text
服务器到底返回什么？
```

完整过程是：

```text
Python程序
    │
    │ HTTP Request
    ↓
服务器
    │
    │ HTTP Response
    ↓
Python程序
```

你以后调用 LLM、搜索 Tool、天气 API 时，**真正判断调用有没有成功，主要就靠 Response。**

------

# 二、一个 HTTP Response 里有什么？

先简单理解成：

```text
HTTP Response
│
├── Status Code
│      状态码
│
├── Headers
│      响应头
│
└── Body
       响应数据
```

例如：

```text
HTTP/1.1 200 OK

Content-Type: application/json

{
    "temperature": 28
}
```

这里：

```text
200
→ Status Code

Content-Type
→ Response Headers

{"temperature": 28}
→ Response Body
```

------

# 三、Status Code 是什么？

Status Code：

> **服务器告诉客户端：你刚才这个请求处理得怎么样。**

例如最经典：

```text
200
```

表示：

> 请求成功。

你以后写：

```python
response = requests.get(url)
```

然后：

```python
print(response.status_code)
```

可能输出：

```text
200
```

所以：

```python
response.status_code
```

非常重要。

------

# 四、HTTP 状态码为什么是三位数字？

你以后会看到很多：

```text
200
201
400
401
403
404
429
500
503
```

不用一个个死背。

首先看：

> **第一位数字。**

可以粗略分：

| 开头  | 含义             |
| ----- | ---------------- |
| `2xx` | 成功             |
| `3xx` | 重定向           |
| `4xx` | 客户端这边有问题 |
| `5xx` | 服务器这边有问题 |

对 Agent 开发来说：

```text
2xx
4xx
5xx
```

最重要。

------

# 五、200：成功

最常见：

```text
200 OK
```

意思：

> 请求成功，服务器正常返回结果。

例如：

```python
response = requests.get(
    "https://api.example.com/weather"
)

print(response.status_code)
```

输出：

```text
200
```

服务器 Body：

```json
{
    "city": "Hefei",
    "temperature": 28
}
```

这就是最理想情况。

------

# 六、201：创建成功

例如：

```text
POST /users
```

创建新用户。

服务器可能返回：

```text
201 Created
```

意思：

> 新资源成功创建。

你现阶段知道即可。

------

# 七、400：Bad Request

```text
400 Bad Request
```

一般表示：

> 你发送的请求有问题。

例如服务器要求：

```json
{
    "query": "Agent"
}
```

你却发送：

```json
{
    "abc": "Agent"
}
```

服务器不知道怎么处理。

可能：

```text
400
```

所以：

```text
400
→ 请求格式 / 参数等有问题
```

------

# 八、401：Unauthorized

这个你以后调用 LLM API 会特别常见。

```text
401 Unauthorized
```

通常表示：

> 身份认证失败。

例如：

```python
headers = {
    "Authorization": "Bearer wrong_key"
}
```

API Key 错了。

服务器：

```text
401
```

所以以后看到：

```text
401
```

第一反应：

```text
API Key 对吗？
Authorization Header 对吗？
Token 过期了吗？
```

------

# 九、403：Forbidden

```text
403 Forbidden
```

和 401 有一点区别。

可以先粗略理解：

```text
401
→ “我不知道你是谁 / 认证失败”

403
→ “我知道你是谁，但你没有权限”
```

例如：

```text
你登录成功了
但是
你没有访问某资源的权限
```

可能返回：

```text
403
```

初期不用特别纠结 401/403 的所有标准细节，知道这个区别就够。

------

# 十、404：Not Found

这个应该很熟：

```text
404 Not Found
```

表示：

> 请求的资源或者路径不存在。

例如：

正确 API：

```text
https://api.example.com/chat
```

你写成：

```text
https://api.example.com/chatt
```

多了一个：

```text
t
```

服务器可能：

```text
404
```

所以：

```text
404
→ URL / Path 很可能写错了
```

------

# 十一、429：非常重要！

这个对 LLM API 尤其重要。

```text
429 Too Many Requests
```

通常表示：

> 请求太频繁，或者超过某种额度 / 限流规则。

以后 Agent 一旦开始：

```text
并发调用多个 Tool
多 Agent 同时请求 LLM
循环 Planning
批量调用 Embedding
```

很容易遇到：

```text
429
```

比如：

```text
1秒内请求太多次
 ↓
服务器限流
 ↓
429
```

解决方法以后会学：

```text
Retry
指数退避
限制并发
等待后重试
```

这也是为什么昨天学：

```python
try / except
```

非常重要。

------

# 十二、500：服务器内部错误

```text
500 Internal Server Error
```

一般表示：

> 请求到服务器了，但服务器自己处理的时候出错。

例如：

```text
客户端请求
   ↓
服务器
   ↓
内部程序崩了
   ↓
500
```

这时候不一定是你代码的问题。

但也不能看到 500 就百分之百认为和你的请求无关，有些服务端实现也可能因为特殊输入触发 500。

现阶段先理解：

```text
5xx
→ 优先怀疑服务器端问题
```

------

# 十三、503：服务器暂时不可用

```text
503 Service Unavailable
```

可能：

```text
服务器过载
服务器维护
服务暂时不可用
```

Agent 以后也可能需要：

```text
稍后重试
```

------

# 十四、最重要的状态码先记这些

你不用背几十个。

先记：

```text
200 → 成功

400 → 请求有问题

401 → 身份认证失败

403 → 没权限

404 → 地址/资源不存在

429 → 请求过多 / 被限流

500 → 服务器内部错误

503 → 服务暂时不可用
```

尤其 Agent：

200, 400, 401, 429, 500\boxed{200,\ 400,\ 401,\ 429,\ 500}

以后特别常见。

------

# 十五、Python 怎么拿 Status Code？

例如：

```python
import requests

response = requests.get(
    "https://api.example.com/data"
)

print(response.status_code)
```

这里：

```python
response
```

不是服务器返回的纯文本本身。

它是：

> 一个 Response 对象。

可以把它理解成：

```text
response
│
├── status_code
├── headers
├── text
├── json()
└── ...
```

这个又和昨天的：

```text
对象
属性
方法
```

联系起来了！

------

# 十六、`response.status_code`

这里：

```python
response.status_code
```

是：

> Response 对象的一个属性。

还记得昨天：

```python
agent1.name
```

吗？

一样：

```text
agent1.name
→ Agent对象的name属性

response.status_code
→ Response对象的status_code属性
```

所以你昨天学 `class / object` 现在直接用上了。

------

# 十七、`response.text`

如果服务器返回：

```json
{
    "name": "Tom"
}
```

我们可以：

```python
print(response.text)
```

得到类似：

```text
{"name": "Tom"}
```

注意：

```python
response.text
```

通常是：

```text
str
```

也就是服务器返回 Body 的文本形式。

------

# 十八、`response.json()`

如果服务器返回的是 JSON：

```json
{
    "name": "Tom",
    "age": 20
}
```

我们可以：

```python
data = response.json()
```

然后：

```python
print(data)
print(type(data))
```

可能得到：

```text
{'name': 'Tom', 'age': 20}

<class 'dict'>
```

也就是说：

```text
服务器 JSON Response
        ↓
response.json()
        ↓
Python dict
```

是不是和昨天：

```python
json.loads()
```

非常像？

------

# 十九、`response.text` 和 `response.json()` 的区别

这个非常重要。

### `response.text`

```python
text = response.text
```

得到：

```text
字符串 str
```

例如：

```python
'{"name":"Tom"}'
```

------

### `response.json()`

```python
data = response.json()
```

得到：

```python
{
    "name": "Tom"
}
```

通常是：

```text
dict
```

所以：

```text
response.text
→ 原始文本

response.json()
→ 把JSON解析成Python对象
```

------

# 二十、注意一个语法差异

你看：

```python
response.status_code
```

没有：

```text
()
```

而：

```python
response.json()
```

有：

```text
()
```

为什么？

因为：

```python
status_code
```

是属性。

而：

```python
json()
```

是方法。

还记得昨天：

```python
agent.name
```

和：

```python
agent.show_info()
```

吗？

完全一样：

```text
属性
→ response.status_code

方法
→ response.json()
```

这个连接非常重要。

------

# 二十一、什么时候用 `.text`，什么时候用 `.json()`？

如果服务器说：

```text
Content-Type: application/json
```

通常：

```python
response.json()
```

最好用。

因为你可以：

```python
data = response.json()

print(data["name"])
```

但如果：

```text
HTML
TXT
普通字符串
```

可以使用：

```python
response.text
```

------

# 二十二、如果返回的根本不是 JSON 呢？

例如服务器返回：

```text
Hello World
```

你却：

```python
response.json()
```

就可能报：

```text
JSONDecodeError
```

这是不是昨天又学过？

所以以后：

```python
try:
    data = response.json()

except ValueError:
    print("服务器返回的不是合法JSON")
```

知识又串起来了。

------

# 二十三、如何判断请求成功？

最直接：

```python
if response.status_code == 200:
    print("请求成功")
else:
    print("请求失败")
```

例如：

```python
response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    print(data)

else:
    print(
        f"请求失败：{response.status_code}"
    )
```

非常常见。

------

# 二十四、但是成功不一定只有 200

比如：

```text
201
204
```

也属于：

```text
2xx
```

成功状态。

所以更通用：

```python
if 200 <= response.status_code < 300:
    print("成功")
```

------

# 二十五、requests 还有一个很好用的方法

以后经常看到：

```python
response.raise_for_status()
```

意思是：

> 如果 HTTP 状态码表示错误，就主动抛异常。

比如：

```python
response = requests.get(url)

response.raise_for_status()

data = response.json()
```

如果：

```text
200
```

就正常往下。

如果：

```text
404
500
```

可能抛出：

```text
HTTPError
```

于是就可以和昨天的异常处理结合：

```python
try:
    response = requests.get(url)

    response.raise_for_status()

    data = response.json()

except requests.RequestException as e:
    print(f"请求失败：{e}")
```

这已经很像真实工程代码了。

------

# 二十六、完整流程现在变成这样

```python
import requests


url = "https://api.example.com/weather"

params = {
    "city": "Hefei"
}


try:
    response = requests.get(
        url,
        params=params
    )

    response.raise_for_status()

    data = response.json()

    print(data)

except requests.RequestException as e:
    print(f"请求失败：{e}")
```

你现在已经能理解其中绝大多数东西：

```text
requests.get
→ 发GET请求

url
→ 地址

params
→ 查询参数

response
→ 响应对象

raise_for_status()
→ 状态码错误时抛异常

response.json()
→ JSON转Python对象

try / except
→ 捕获请求异常
```

这已经非常接近真实 API 编程了。

------

# 二十七、LLM API 的 Response 又长什么样？

以后可能收到类似：

```json
{
  "id": "xxx",
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "Agent是一种..."
      }
    }
  ]
}
```

Python：

```python
data = response.json()
```

那么：

```python
data
```

是一个 Python 字典。

你可以：

```python
content = data["choices"][0]["message"]["content"]
```

最终拿到：

```text
Agent是一种...
```

这个等我们真正调用 LLM API 时再逐层拆。

------

# 二十八、现在把 Request 和 Response 连起来

完整 HTTP：

```text
Python Client
      │
      │ Request
      │
      ├── Method
      ├── URL
      ├── Params
      ├── Headers
      └── Body
      ↓
    Server
      │
      │ Response
      │
      ├── Status Code
      ├── Headers
      └── Body
      ↓
Python Client
```

这张图非常重要。

到这里你才算真正建立起：

HTTP请求—响应模型\boxed{\text{HTTP请求—响应模型}}

------

# 第四课练习

### 练习 1

下面状态码分别大概什么意思？

```text
200
401
404
429
500
```

不用特别官方，用自己的话解释。

------

### 练习 2

下面：

```python
response = requests.get(url)

print(response.status_code)
print(response.text)
```

请解释：

```text
response
status_code
text
```

分别是什么。

------

### 练习 3

服务器返回：

```json
{
  "name": "Tom",
  "age": 20
}
```

下面：

```python
data = response.json()
```

执行以后：

```python
data
```

大概是什么 Python 类型？

然后怎么取出：

```text
Tom
```

？

------

### 练习 4

为什么真实项目里：

```python
response.raise_for_status()
```

很有用？

它和我们昨天学的：

```python
try / except
```

是什么关系？

你答完这一轮，我们就进入 **Day 2 第五课：真正用 `requests` 和 `httpx` 发 HTTP 请求**。那一课我们就不再只看伪 API 了，会开始实际写完整请求代码。