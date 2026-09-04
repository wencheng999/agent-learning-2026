好，我们继续 **Day 1 第四课：Python 文件读写**。

这一课不难，但很实用。你后面做：

- RAG 读取文档
- Agent Memory 保存信息
- 读取 Prompt 模板
- 保存日志
- 读取配置文件
- 处理 TXT / JSON 数据

都会用到文件操作。

你今天主要要掌握这几个东西：

```text
open()
read()
write()
with open()
"r" / "w" / "a"
encoding="utf-8"
```

------

# 一、为什么程序要读写文件？

前面我们写的数据一般都存在变量里：

```python
name = "Tom"
```

但变量有一个问题：

> 程序一结束，变量里的数据通常就没了。

比如：

```python
memory = "用户喜欢Agent"
```

程序关掉以后，这个变量也没了。

如果你想长期保存，就要写到文件里。

比如：

```text
memory.txt
```

里面保存：

```text
用户喜欢Agent
```

下一次程序启动时，再读取回来。

所以文件读写其实就是：

```text
程序
 ↓
文件
```

两种方向：

```text
程序 → 文件
叫“写入”

文件 → 程序
叫“读取”
```

------

# 二、最基本的 `open()`

Python 打开文件使用：

```python
open()
```

例如：

```python
file = open("note.txt", "r", encoding="utf-8")
```

这里有三个重要参数：

```python
open("note.txt", "r", encoding="utf-8")
```

分别是：

```text
"note.txt"
→ 文件名

"r"
→ 打开模式

encoding="utf-8"
→ 文件编码
```

------

# 三、什么是 `"r"`？

`"r"` 是：

```text
read
```

也就是：

> 只读模式。

例如：

```python
file = open(
    "note.txt",
    "r",
    encoding="utf-8"
)

content = file.read()

print(content)

file.close()
```

假设 `note.txt` 是：

```text
Hello Agent
Hello RAG
```

输出就是：

```text
Hello Agent
Hello RAG
```

------

# 四、为什么最后要 `close()`？

因为：

```python
open()
```

打开了一个系统资源。

你可以简单理解成：

> 程序和文件建立了一个连接。

用完以后：

```python
file.close()
```

把它关掉。

否则可能导致：

```text
资源没释放
文件被占用
数据没完全写入
```

所以传统写法是：

```python
file = open(...)

...

file.close()
```

------

# 五、但是更推荐 `with open()`

现在 Python 项目里更常见：

```python
with open(
    "note.txt",
    "r",
    encoding="utf-8"
) as file:

    content = file.read()

print(content)
```

这个写法非常重要。

你后面会经常看到。

------

# 六、`with open()` 到底是什么意思？

这段：

```python
with open("note.txt", "r", encoding="utf-8") as file:
```

可以先简单理解为：

```text
打开 note.txt
 ↓
把这个文件对象交给变量 file
 ↓
进入代码块
 ↓
代码块结束
 ↓
Python 自动关闭文件
```

所以你不需要再手动：

```python
file.close()
```

这就是它最大的好处。

------

# 七、所以推荐写法是

```python
with open(
    "note.txt",
    "r",
    encoding="utf-8"
) as file:
    content = file.read()
```

比：

```python
file = open(...)
content = file.read()
file.close()
```

更安全。

因为即使中间报错，`with` 通常也会帮你正确释放资源。

------

# 八、`as file` 是什么意思？

看：

```python
with open(...) as file:
```

这里：

```python
file
```

就是一个变量名。

它代表：

> 当前打开的文件对象。

你也可以写：

```python
with open(...) as f:
```

所以很多代码里会看到：

```python
with open("data.txt", "r") as f:
    content = f.read()
```

其中：

```text
f
```

只是 `file` 的简写。

------

# 九、`read()` 是什么？

```python
content = file.read()
```

表示：

> 一次性把整个文件内容读取成字符串。

比如文件：

```text
Agent
RAG
MCP
```

执行：

```python
content = file.read()
```

得到：

```python
"Agent\nRAG\nMCP"
```

也就是说：

```python
type(content)
```

是：

```text
str
```

------

# 十、自己试一个完整例子

先创建：

```text
note.txt
```

内容：

```text
我正在学习Agent。
今天学习Python文件操作。
```

然后：

```python
with open(
    "note.txt",
    "r",
    encoding="utf-8"
) as f:

    content = f.read()

print(content)
```

输出：

```text
我正在学习Agent。
今天学习Python文件操作。
```

------

# 十一、为什么经常写 `encoding="utf-8"`？

这个对中文很重要。

如果不指定编码：

```python
open("note.txt", "r")
```

不同系统可能使用不同默认编码。

尤其 Windows 上有时容易遇到：

```text
UnicodeDecodeError
```

或者中文乱码。

所以以后处理中文文本时，我建议你养成习惯：

```python
encoding="utf-8"
```

例如：

```python
with open(
    "note.txt",
    "r",
    encoding="utf-8"
) as f:
```

------

# 十二、除了 `"r"`，还有 `"w"`

`"w"`：

```text
write
```

表示：

> 写入模式。

例如：

```python
with open(
    "note.txt",
    "w",
    encoding="utf-8"
) as f:

    f.write("Hello Agent")
```

执行后，`note.txt` 里面变成：

```text
Hello Agent
```

------

# 十三、这里一定要注意：`"w"` 会覆盖原文件

假设原文件是：

```text
AAA
BBB
CCC
```

执行：

```python
with open("note.txt", "w", encoding="utf-8") as f:
    f.write("Agent")
```

文件最后只剩：

```text
Agent
```

原来的：

```text
AAA
BBB
CCC
```

被覆盖了。

所以：

"w"=写入+覆盖\boxed{"w" = 写入 + 覆盖}

这个很重要。

------

# 十四、如果文件不存在呢？

如果：

```python
with open("new.txt", "w", encoding="utf-8") as f:
    f.write("Hello")
```

而：

```text
new.txt
```

原本不存在，

Python 会自动创建它。

所以 `"w"`：

```text
文件存在
→ 覆盖

文件不存在
→ 创建
```

------

# 十五、那我不想覆盖，怎么办？

用：

```python
"a"
```

`a`：

```text
append
```

表示：

> 追加。

例如原文件：

```text
Agent
```

执行：

```python
with open(
    "note.txt",
    "a",
    encoding="utf-8"
) as f:

    f.write("\nRAG")
```

最后变成：

```text
Agent
RAG
```

而不是覆盖。

------

# 十六、所以最重要的三个模式

你先记：

| 模式  | 含义             |
| ----- | ---------------- |
| `"r"` | 读取             |
| `"w"` | 写入，覆盖原内容 |
| `"a"` | 追加             |

简单记忆：

```text
r = read
w = write
a = append
```

------

# 十七、`write()` 不会自动换行

比如：

```python
with open("test.txt", "w", encoding="utf-8") as f:
    f.write("Agent")
    f.write("RAG")
```

结果：

```text
AgentRAG
```

不是：

```text
Agent
RAG
```

因为 `write()` 不会自动换行。

如果想换行：

```python
f.write("Agent\n")
f.write("RAG\n")
```

------

# 十八、`\n` 就是换行符

前面你已经用过：

```python
print(f"Agent：{name}\n模型：{model}")
```

文件里也是一样：

```python
f.write("Agent\n")
```

表示：

```text
Agent
然后换一行
```

------

# 十九、读取文件还有 `readline()`

除了：

```python
read()
```

还有：

```python
readline()
```

区别：

```python
read()
```

读取整个文件。

```python
readline()
```

一次读取一行。

例如文件：

```text
Agent
RAG
MCP
```

代码：

```python
with open("note.txt", "r", encoding="utf-8") as f:
    line = f.readline()

print(line)
```

结果：

```text
Agent
```

------

# 二十、还有 `readlines()`

```python
lines = f.readlines()
```

会把每一行变成列表元素。

比如文件：

```text
Agent
RAG
MCP
```

得到：

```python
[
    "Agent\n",
    "RAG\n",
    "MCP"
]
```

也就是：

```python
list[str]
```

------

# 二十一、三种读取方式怎么选？

| 方法          | 作用           |
| ------------- | -------------- |
| `read()`      | 整个文件       |
| `readline()`  | 一行           |
| `readlines()` | 所有行组成列表 |

初期最常用：

```python
read()
```

------

# 二十二、其实还能直接遍历文件

这是很常见的写法：

```python
with open(
    "note.txt",
    "r",
    encoding="utf-8"
) as f:

    for line in f:
        print(line)
```

这样一行一行读取。

对于大文件，比直接：

```python
f.read()
```

一次性全部放内存更合理。

------

# 二十三、这里顺便理解 `strip()`

假设：

```python
for line in f:
    print(line)
```

每一行可能自带：

```text
\n
```

所以经常会写：

```python
for line in f:
    line = line.strip()
    print(line)
```

`strip()`：

> 去掉字符串两端空白，包括空格和换行符。

比如：

```python
text = "  Agent\n"
```

执行：

```python
text.strip()
```

得到：

```text
Agent
```

这个以后处理文本数据非常常见。

------

# 二十四、为什么 RAG 特别需要文件操作？

以后做最简单 RAG：

```text
PDF / TXT
   ↓
读取文件
   ↓
文本
   ↓
切块
   ↓
Embedding
   ↓
Vector DB
```

最开始：

```text
读取文件
```

就离不开文件操作。

比如：

```python
def load_document(path: str) -> str:
    with open(
        path,
        "r",
        encoding="utf-8"
    ) as f:
        return f.read()
```

以后你会反复写这种函数。

------

# 二十五、Agent Memory 也会用到

比如我们现在做一个极简 Memory：

```python
def save_memory(memory: str):
    with open(
        "memory.txt",
        "a",
        encoding="utf-8"
    ) as f:
        f.write(memory + "\n")
```

调用：

```python
save_memory("用户喜欢Agent")
save_memory("用户正在学习Python")
```

文件：

```text
用户喜欢Agent
用户正在学习Python
```

程序下次再启动：

```python
def load_memory() -> str:
    with open(
        "memory.txt",
        "r",
        encoding="utf-8"
    ) as f:
        return f.read()
```

这就是最原始版的：

```text
Long-term Memory
```

当然真正 Agent Memory 会复杂很多，但底层思想是类似的：

```text
保存
+
读取
```

------

# 二十六、文件不存在怎么办？

比如：

```python
with open(
    "abc.txt",
    "r",
    encoding="utf-8"
) as f:
```

如果 `abc.txt` 不存在：

```text
FileNotFoundError
```

这就刚好连接上一课：

```python
try / except
```

可以写：

```python
def load_file(path: str) -> str | None:

    try:
        with open(
            path,
            "r",
            encoding="utf-8"
        ) as f:

            return f.read()

    except FileNotFoundError:
        print(f"文件不存在：{path}")
        return None
```

你看，现在前面知识已经开始串起来了。

------

# 二十七、这一段你应该能看懂

```python
def load_file(path: str) -> str | None:

    try:
        with open(
            path,
            "r",
            encoding="utf-8"
        ) as f:

            content = f.read()

        return content

    except FileNotFoundError:
        print(f"文件不存在：{path}")
        return None
```

这里已经同时用了：

```text
函数
类型注解
str | None
try / except
with open
read
return
f-string
```

这就是我们前几课串起来的效果。

------

# 二十八、文件路径也要简单理解一下

比如：

```python
open("note.txt")
```

表示：

> 当前工作目录下的 `note.txt`。

如果文件在：

```text
data/note.txt
```

可以：

```python
open("data/note.txt")
```

Windows 虽然经常看到：

```text
C:\Users\xxx\data.txt
```

但 Python 项目里我更建议以后使用：

```python
pathlib
```

例如：

```python
from pathlib import Path


path = Path("data") / "note.txt"

print(path)
```

得到：

```text
data\note.txt
```

或者不同系统对应的正确路径格式。

------

# 二十九、`pathlib` 为什么值得学？

以后你的项目可能：

```text
agent-project/
│
├── data/
│   ├── papers/
│   └── memory/
│
├── prompts/
├── src/
└── main.py
```

用：

```python
Path
```

管理路径更舒服。

例如：

```python
from pathlib import Path


DATA_DIR = Path("data")
MEMORY_FILE = DATA_DIR / "memory.txt"
```

然后：

```python
with open(
    MEMORY_FILE,
    "r",
    encoding="utf-8"
) as f:
    ...
```

你现在只要认识即可，不需要深挖。

------

# 三十、再教你一个常用方法：`exists()`

```python
from pathlib import Path


path = Path("note.txt")

if path.exists():
    print("文件存在")
else:
    print("文件不存在")
```

以后非常实用。

------

# 三十一、比如安全读取 Memory

```python
from pathlib import Path


def load_memory(
    path: str
) -> str:

    file_path = Path(path)

    if not file_path.exists():
        return ""

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as f:

        return f.read()
```

如果文件不存在：

```python
return ""
```

而不是报错。

------

# 三十二、这一课你最应该记住的内容

核心就这些：

```text
open()
with open()

"r"
"w"
"a"

read()
readline()
readlines()

write()

encoding="utf-8"

FileNotFoundError

Path
exists()
```

不是所有都要背，但最少要能看懂。

------

# 三十三、给你几个练习

## 练习 1

假设：

```text
note.txt
```

里面内容：

```text
Agent
RAG
MCP
```

写代码读取整个文件，并打印出来。

要求使用：

```python
with open(...)
```

------

## 练习 2

创建：

```text
memory.txt
```

写入：

```text
用户正在学习Agent
```

然后再追加一行：

```text
用户正在学习Python
```

最后文件应该是：

```text
用户正在学习Agent
用户正在学习Python
```

------

## 练习 3

写一个函数：

```python
def load_file(
    path: str
) -> str | None:
```

要求：

- 文件存在：返回内容
- 文件不存在：打印错误信息并返回 `None`

必须用：

```python
try / except FileNotFoundError
```

------

## 练习 4

写两个函数：

```python
save_memory()
load_memory()
```

要求：

```python
save_memory("用户喜欢Agent")
```

把内容追加进：

```text
memory.txt
```

而：

```python
load_memory()
```

读取并返回全部 Memory。

------

# 三十四、这节的验收标准

如果我给你：

```python
def load_document(
    path: str
) -> str | None:

    try:
        with open(
            path,
            "r",
            encoding="utf-8"
        ) as f:

            return f.read()

    except FileNotFoundError:
        return None
```

你能完整解释：

```text
path是什么
str | None什么意思
try干嘛
with open干嘛
"r"什么意思
encoding为什么写utf-8
f是什么
read()返回什么
为什么捕获FileNotFoundError
```

那么：

Python 文件操作基础通过\boxed{\text{Python 文件操作基础通过}}

然后我们就可以进入 Day 1 第五课：**JSON + `.env` 环境变量**。这一课会开始非常接近以后真实的 LLM API 和 Agent 配置。