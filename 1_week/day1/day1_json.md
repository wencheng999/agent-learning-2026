好，我们继续 **Day 1 第五课：JSON + `.env` 环境变量**。

这一课开始和真正的 LLM / Agent 开发非常接近了。以后你调用大模型时会经常看到：

```python
messages = [
    {
        "role": "user",
        "content": "什么是Agent？"
    }
]
```

Tool Calling 又可能返回：

```json
{
  "name": "search",
  "arguments": {
    "query": "Agent"
  }
}
```

而 API Key、模型名、Base URL 又通常放在：

```text
.env
```

所以这一课重点解决两个问题：

Python 数据怎么和 JSON 相互转换？\boxed{\text{Python 数据怎么和 JSON 相互转换？}}

以及：

API Key 为什么要放到 .env，而不是直接写在代码里？\boxed{\text{API Key 为什么要放到 .env，而不是直接写在代码里？}}

------

# 一、先搞清楚 JSON 到底是什么

JSON 全称：

```text
JavaScript Object Notation
```

你不用关心它最开始来自 JavaScript。

对你现在来说，最简单的理解就是：

> **JSON 是一种非常通用的数据交换格式。**

比如我们有一个用户：

```json
{
  "name": "Tom",
  "age": 20,
  "major": "Computer Science"
}
```

这就是 JSON。

你会发现它和 Python 的：

```python
user = {
    "name": "Tom",
    "age": 20,
    "major": "Computer Science"
}
```

非常像。

所以可以先粗略理解：

```text
JSON Object
      ↕
Python dict
```

------

# 二、JSON 为什么对 Agent 很重要？

因为很多 API 都通过 JSON 传递数据。

比如你以后调用 LLM：

```text
Python程序
   ↓
构造JSON请求
   ↓
LLM API
   ↓
返回JSON
   ↓
Python解析
```

因此：

JSON 是 Python Agent 和外部服务交流的重要语言\boxed{\text{JSON 是 Python Agent 和外部服务交流的重要语言}}

以后你会在这些地方频繁遇到 JSON：

```text
LLM messages
Tool Calling参数
HTTP API请求
HTTP API响应
配置文件
Agent State
Memory
Structured Output
```

所以一定要熟悉。

------

# 三、JSON 和 Python 的数据类型怎么对应？

最常见的是这样：

| JSON   | Python        |
| ------ | ------------- |
| object | `dict`        |
| array  | `list`        |
| string | `str`         |
| number | `int / float` |
| true   | `True`        |
| false  | `False`       |
| null   | `None`        |

例如 JSON：

```json
{
  "name": "Tom",
  "age": 20,
  "skills": ["Python", "Agent"],
  "student": true,
  "company": null
}
```

Python 对应：

```python
data = {
    "name": "Tom",
    "age": 20,
    "skills": ["Python", "Agent"],
    "student": True,
    "company": None
}
```

这里有几个区别一定要注意。

JSON 是：

```json
true
false
null
```

Python 是：

```python
True
False
None
```

大小写不一样。

------

# 四、Python 操作 JSON 要先导入 `json`

Python 自带：

```python
import json
```

不用额外安装。

接下来重点学四个函数：

```python
json.dumps()
json.loads()

json.dump()
json.load()
```

第一次看容易混。

我先给你一个最重要的规律。

```text
带 s：
dumps / loads
主要处理“字符串”

不带 s：
dump / load
主要处理“文件”
```

可以先这样记。

------

# 五、`json.dumps()`：Python → JSON 字符串

比如：

```python
import json


user = {
    "name": "Tom",
    "age": 20
}

json_text = json.dumps(user)

print(json_text)
print(type(json_text))
```

输出类似：

```text
{"name": "Tom", "age": 20}
<class 'str'>
```

注意：

原来：

```python
user
```

是：

```python
dict
```

经过：

```python
json.dumps(user)
```

变成：

```python
str
```

所以：

dumps: Python对象→JSON字符串\boxed{dumps:\ Python对象 \rightarrow JSON字符串}

------

# 六、为什么要变成 JSON 字符串？

因为网络传输最终传输的不是 Python 的 `dict` 对象。

通常需要转成类似：

```json
{
  "name": "Tom",
  "age": 20
}
```

这样的标准格式。

例如：

```text
Python dict
    ↓
json.dumps()
    ↓
JSON字符串
    ↓
通过HTTP发送
```

以后调用 API 就经常涉及这一层。

不过很多 Python HTTP/LLM 库会自动帮你转换，所以不一定每次都手写 `json.dumps()`。

但你必须知道底层大概发生了什么。

------

# 七、中文有一个非常重要的问题

假设：

```python
data = {
    "topic": "人工智能",
    "content": "我正在学习Agent"
}
```

然后：

```python
json_text = json.dumps(data)

print(json_text)
```

你有可能看到：

```text
{"topic": "\u4eba\u5de5\u667a\u80fd", ...}
```

这不是乱码。

只是 JSON 默认可能把中文转成 Unicode 转义。

如果想直接看到中文：

```python
json_text = json.dumps(
    data,
    ensure_ascii=False
)
```

这样输出：

```json
{"topic": "人工智能", "content": "我正在学习Agent"}
```

所以以后处理中文 JSON，我建议记住：

```python
ensure_ascii=False
```

------

# 八、让 JSON 更好看：`indent`

比如：

```python
json_text = json.dumps(
    data,
    ensure_ascii=False,
    indent=2
)

print(json_text)
```

输出：

```json
{
  "topic": "人工智能",
  "content": "我正在学习Agent"
}
```

这里：

```python
indent=2
```

表示缩进两个空格。

所以以后写配置、Debug、保存结果时经常会写：

```python
json.dumps(
    data,
    ensure_ascii=False,
    indent=2
)
```

------

# 九、`json.loads()`：JSON 字符串 → Python

现在反过来。

假设：

```python
json_text = '''
{
    "name": "Tom",
    "age": 20
}
'''
```

注意现在它只是：

```python
str
```

然后：

```python
data = json.loads(json_text)

print(data)
print(type(data))
```

结果：

```text
{'name': 'Tom', 'age': 20}
<class 'dict'>
```

所以：

loads: JSON字符串→Python对象\boxed{loads:\ JSON字符串 \rightarrow Python对象}

------

# 十、`dumps` 和 `loads` 正好相反

可以记：

```text
Python dict
    ↓ dumps
JSON string
    ↓ loads
Python dict
```

比如：

```python
import json


data = {
    "name": "Tom",
    "age": 20
}

json_text = json.dumps(data)

new_data = json.loads(json_text)
```

最终：

```python
new_data
```

又是 Python 字典。

------

# 十一、什么情况下 Agent 会用 `loads()`？

例如 LLM 返回：

```text
'{"tool": "search", "query": "Agent"}'
```

注意：

> 看起来像 JSON，但实际上可能只是一个字符串。

你要：

```python
result = json.loads(response)
```

才能变成：

```python
{
    "tool": "search",
    "query": "Agent"
}
```

然后就可以：

```python
print(result["tool"])
```

得到：

```text
search
```

所以：

```text
LLM返回JSON字符串
       ↓
json.loads()
       ↓
Python dict
       ↓
程序继续处理
```

这和后面的 Structured Output / Tool Calling 联系非常紧密。

------

# 十二、如果 JSON 格式错了怎么办？

比如：

```python
json_text = '''
{
    "name": "Tom",
    "age": 20,
}
'''
```

最后多了一个逗号。

执行：

```python
json.loads(json_text)
```

可能报：

```text
JSONDecodeError
```

所以你前一课的异常处理马上又用到了。

```python
import json


try:
    data = json.loads(json_text)

except json.JSONDecodeError as e:
    print(f"JSON解析失败：{e}")
```

你看，现在知识已经开始串起来了：

```text
JSON
+
try / except
```

------

# 十三、接下来是 `json.dump()`

前面的：

```python
json.dumps()
```

是转字符串。

而：

```python
json.dump()
```

主要是：

> **把 Python 数据直接写到 JSON 文件。**

比如：

```python
import json


user = {
    "name": "Tom",
    "age": 20,
    "skills": ["Python", "Agent"]
}


with open(
    "user.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        user,
        f,
        ensure_ascii=False,
        indent=2
    )
```

执行后会创建：

```text
user.json
```

内容：

```json
{
  "name": "Tom",
  "age": 20,
  "skills": [
    "Python",
    "Agent"
  ]
}
```

------

# 十四、这里和上一课结合起来了

注意：

```python
with open(...) as f:
```

是你刚刚学过的文件操作。

然后：

```python
json.dump(user, f)
```

就是：

> 把 `user` 这个 Python 对象写进 `f` 所代表的文件。

所以：

```text
Python dict
    ↓
json.dump()
    ↓
JSON文件
```

------

# 十五、`json.load()`：读取 JSON 文件

现在反过来：

```python
import json


with open(
    "user.json",
    "r",
    encoding="utf-8"
) as f:

    user = json.load(f)


print(user)
print(type(user))
```

结果：

```text
{'name': 'Tom', 'age': 20, 'skills': ['Python', 'Agent']}
<class 'dict'>
```

所以：

load: JSON文件→Python对象\boxed{load:\ JSON文件 \rightarrow Python对象}

------

# 十六、四个函数现在统一一下

这是这节最重要的一张表：

| 方法           | 方向          | 主要处理 |
| -------------- | ------------- | -------- |
| `json.dumps()` | Python → JSON | 字符串   |
| `json.loads()` | JSON → Python | 字符串   |
| `json.dump()`  | Python → JSON | 文件     |
| `json.load()`  | JSON → Python | 文件     |

最简单的口诀：

```text
s = string
```

所以：

```text
dumps / loads
→ 字符串

dump / load
→ 文件
```

这个记住就行。

------

# 十七、用 JSON 做一个最简单的 Agent Memory

前面我们的 Memory 是：

```text
memory.txt
```

里面：

```text
用户喜欢Agent
用户正在学习Python
```

这种结构不够方便。

如果以后 Memory 复杂一点：

```python
memory = {
    "name": "Tom",
    "interests": [
        "Agent",
        "RAG"
    ],
    "learning_stage": "Python基础"
}
```

就适合保存成：

```text
memory.json
```

例如：

```python
import json


def save_memory(memory: dict) -> None:

    with open(
        "memory.json",
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            memory,
            f,
            ensure_ascii=False,
            indent=2
        )
```

调用：

```python
memory = {
    "interests": ["Agent", "RAG"],
    "stage": "Python基础"
}

save_memory(memory)
```

最终：

```json
{
  "interests": [
    "Agent",
    "RAG"
  ],
  "stage": "Python基础"
}
```

已经比 TXT 更结构化了。

------

# 十八、读取 Memory

```python
def load_memory() -> dict | None:

    try:
        with open(
            "memory.json",
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)

    except FileNotFoundError:
        return None
```

这里你现在应该能看懂几乎全部代码。

它已经同时用了：

```text
类型注解
函数
try / except
with open
JSON
return None
```

------

# 十九、接下来进入 `.env`

这一块非常重要。

假设以后调用一个 LLM：

```python
api_key = "sk-123456789abcdef"
```

如果你直接写在：

```text
main.py
```

里面：

```python
client = Client(
    api_key="sk-123456789abcdef"
)
```

然后：

```text
git add .
git commit
git push
```

上传 GitHub。

那么：

> **你的 API Key 可能直接公开。**

这很危险。

别人可能使用你的：

```text
API额度
账号资源
模型调用次数
```

所以 API Key 一般不要直接写进源代码。

------

# 二十、`.env` 是干什么的？

`.env`：

> 用来保存环境配置，例如 API Key、模型名、Base URL 等。

例如创建：

```text
.env
```

内容：

```text
LLM_API_KEY=sk-xxxxxxxx
LLM_MODEL=qwen
LLM_BASE_URL=https://example.com/v1
```

注意一般不需要：

```text
""
```

直接：

```text
KEY=value
```

即可。

------

# 二十一、Python 怎么读取 `.env`？

常见方式使用：

```text
python-dotenv
```

安装：

```bash
pip install python-dotenv
```

或者以后你用 uv：

```bash
uv add python-dotenv
```

然后：

```python
import os

from dotenv import load_dotenv


load_dotenv()

api_key = os.getenv("LLM_API_KEY")
model = os.getenv("LLM_MODEL")
base_url = os.getenv("LLM_BASE_URL")


print(model)
print(base_url)
```

------

# 二十二、`load_dotenv()` 干什么？

```python
load_dotenv()
```

作用简单理解：

> 找到 `.env` 文件，把里面的配置加载到当前程序的环境变量里。

比如：

```text
.env
```

有：

```text
LLM_MODEL=qwen
```

执行：

```python
load_dotenv()
```

以后：

```python
os.getenv("LLM_MODEL")
```

就能得到：

```text
qwen
```

------

# 二十三、`os.getenv()` 是什么？

例如：

```python
model = os.getenv("LLM_MODEL")
```

表示：

> 获取名字叫 `LLM_MODEL` 的环境变量。

如果：

```text
LLM_MODEL=qwen
```

那么：

```python
model
```

就是：

```text
qwen
```

如果不存在：

```python
os.getenv("ABC")
```

默认会得到：

```python
None
```

所以：

```python
api_key: str | None = os.getenv("LLM_API_KEY")
```

这个类型注解是不是又和第一课联系起来了？

------

# 二十四、可以设置默认值

比如：

```python
model = os.getenv(
    "LLM_MODEL",
    "qwen"
)
```

意思：

```text
如果环境变量存在
→ 使用环境变量

如果不存在
→ 默认使用 "qwen"
```

例如：

```python
temperature = os.getenv(
    "TEMPERATURE",
    "0.7"
)
```

但是注意：

```python
os.getenv()
```

拿到的一般是字符串。

所以：

```python
temperature = float(
    os.getenv("TEMPERATURE", "0.7")
)
```

才会转成：

```python
float
```

------

# 二十五、`.env` 最大的一个要求：不要上传 GitHub

项目里一定创建：

```text
.gitignore
```

然后写：

```text
.env
```

这样 Git 会忽略 `.env`。

你的项目：

```text
agent-learning-2026/
│
├── .env
├── .gitignore
├── main.py
└── README.md
```

`.gitignore`：

```text
.env
```

这样：

```text
API Key
```

不会正常跟着源码提交。

------

# 二十六、但是别人下载你的项目怎么办？

别人没有你的：

```text
.env
```

他怎么知道要配置哪些变量？

所以通常再提供：

```text
.env.example
```

注意里面不要放真实 Key。

例如：

```text
LLM_API_KEY=your_api_key_here
LLM_MODEL=your_model
LLM_BASE_URL=your_base_url
```

项目结构：

```text
agent-project/
│
├── .env              ← 自己真实配置，不上传
├── .env.example      ← 模板，可以上传
├── .gitignore
└── main.py
```

这是一个非常好的工程习惯。

------

# 二十七、把 `.env` 和 class 结合起来

以后项目里可能写：

```python
import os

from dotenv import load_dotenv


load_dotenv()


class Config:

    def __init__(self):
        self.api_key = os.getenv(
            "LLM_API_KEY"
        )

        self.model = os.getenv(
            "LLM_MODEL"
        )

        self.base_url = os.getenv(
            "LLM_BASE_URL"
        )
```

然后：

```python
config = Config()

print(config.model)
```

你现在是不是已经能完全看懂：

```text
class
__init__
self
os.getenv
```

是怎么组合起来的？

------

# 二十八、配置缺失怎么办？

比如：

```python
api_key = os.getenv("LLM_API_KEY")
```

可能得到：

```python
None
```

那么可以检查：

```python
if api_key is None:
    raise ValueError(
        "没有配置 LLM_API_KEY"
    )
```

完整一点：

```python
import os

from dotenv import load_dotenv


load_dotenv()


api_key = os.getenv("LLM_API_KEY")

if api_key is None:
    raise ValueError(
        "请在 .env 中配置 LLM_API_KEY"
    )
```

你又看到上一课：

```python
raise ValueError
```

重新出现了。

------

# 二十九、以后真实 LLM 项目大概就是这种结构

例如：

```text
agent-learning-2026/
│
├── .env
├── .env.example
├── .gitignore
│
├── config.py
├── main.py
│
└── memory/
    └── memory.json
```

`config.py`：

```python
import os

from dotenv import load_dotenv


load_dotenv()


API_KEY = os.getenv("LLM_API_KEY")
MODEL = os.getenv(
    "LLM_MODEL",
    "qwen"
)
```

`main.py`：

```python
from config import API_KEY, MODEL


print(MODEL)
```

以后再换成：

```text
LLM Client
```

就非常自然了。

------

# 三十、`.env` 不等于真正的“加密”

这里再提醒你一下。

`.env` 的主要作用是：

> 把秘密配置和源代码分离。

并不是：

> `.env` 本身自动加密 API Key。

如果别人拿到了你的电脑或者 `.env` 文件，依然能看到 Key。

所以核心原则是：

```text
不要写进源码
不要上传GitHub
不要截图公开
不要提交.env
```

------

# 三十一、这一课最需要掌握的东西

你今天其实只需要真正记牢这些：

```text
JSON：

json.dumps()
Python → JSON字符串

json.loads()
JSON字符串 → Python

json.dump()
Python → JSON文件

json.load()
JSON文件 → Python
```

以及：

```text
.env：

load_dotenv()

os.getenv()

.gitignore

.env.example
```

这就够了。

------

# 三十二、给你几个练习

这次也分成两个 JSON 练习和两个 `.env` 练习。

### 练习 1

创建：

```python
user = {
    "name": "Tom",
    "age": 20,
    "skills": [
        "Python",
        "Agent"
    ]
}
```

使用：

```python
json.dumps()
```

把它转换成 JSON 字符串。

要求：

```python
ensure_ascii=False
indent=2
```

然后打印：

```python
type(json_text)
```

看看是什么。

------

### 练习 2

把上面的：

```python
user
```

保存到：

```text
user.json
```

然后再从：

```text
user.json
```

读取回来。

要求分别使用：

```python
json.dump()
json.load()
```

最后打印：

```python
print(user_data)
print(type(user_data))
```

------

### 练习 3

创建：

```text
.env
```

内容：

```text
LLM_API_KEY=test_key_123
LLM_MODEL=qwen
LLM_BASE_URL=https://example.com/v1
```

然后 Python：

```python
load_dotenv()
```

读取三个变量并打印：

```text
model
base_url
```

API Key 可以测试是否读到，但以后真实 Key 不要直接完整打印。

比如：

```python
print(api_key is not None)
```

输出：

```text
True
```

就够了。

------

### 练习 4

写一个：

```python
class Config
```

要求有三个属性：

```text
api_key
model
base_url
```

全部从 `.env` 中读取。

如果：

```text
api_key
```

不存在：

```python
raise ValueError(
    "请配置LLM_API_KEY"
)
```

然后：

```python
config = Config()
```

打印：

```python
config.model
config.base_url
```

------

# 三十三、这节的验收标准

如果你看到：

```python
with open(
    "memory.json",
    "r",
    encoding="utf-8"
) as f:
    memory = json.load(f)
```

你能解释：

> 打开 JSON 文件，以 UTF-8 读取，然后把里面的 JSON 数据转换成 Python 对象。

再看到：

```python
load_dotenv()

api_key = os.getenv("LLM_API_KEY")
```

你能解释：

> 加载 `.env`，然后从环境变量中读取 API Key，而不是直接把 Key 写死在源代码。

那这一节就基本通过了。

而且到这里，我们的 Day 1 已经只剩最后一小块：**Conda / uv + 项目结构 + Git/GitHub 基本工作流**。完成那个以后，你的 **Day 1 就正式结束**。