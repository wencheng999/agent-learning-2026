好，我们继续 **Day 1 第三课：异常处理 `try / except`**。

这一课和 Agent 开发关系非常大。因为你以后会频繁遇到：

```text
LLM API 请求失败
Tool 调用失败
网络超时
JSON 解析失败
文件不存在
MCP Server 连接失败
RAG 检索报错
```

如果你不会异常处理，程序一旦出问题就会直接终止。

------

# 一、什么叫“异常”？

先看一个最简单的例子：

```python
a = 10
b = 0

print(a / b)
```

运行会报错：

```text
ZeroDivisionError: division by zero
```

意思是：

> 不能除以 0。

程序执行到这里以后，通常就直接停止了。

这就是：

```text
异常 Exception
```

------

# 二、为什么 Agent 特别需要异常处理？

比如以后你写：

```python
result = call_llm()
```

正常情况下：

```text
Python
 ↓
LLM API
 ↓
成功返回
 ↓
继续执行
```

但也可能：

```text
Python
 ↓
LLM API
 ↓
429
 ↓
请求失败
```

如果没有异常处理：

```text
Agent直接崩掉
```

但更合理的是：

```text
调用失败
 ↓
捕获异常
 ↓
记录错误
 ↓
重试 / 换方案 / 返回提示
```

所以：

异常处理 = 程序出错时，不让整个系统直接崩溃\boxed{\text{异常处理 = 程序出错时，不让整个系统直接崩溃}}

------

# 三、最基本的 `try / except`

先看：

```python
try:
    result = 10 / 0
    print(result)
except:
    print("程序出错了")
```

运行结果：

```text
程序出错了
```

程序没有直接崩掉。

------

# 四、`try` 和 `except` 分别什么意思？

结构：

```python
try:
    可能出错的代码
except:
    出错以后执行的代码
```

可以这样理解：

```text
try
 ↓
先尝试执行

成功
 ↓
继续

失败
 ↓
进入 except
```

------

# 五、一步一步看执行过程

代码：

```python
try:
    result = 10 / 0
    print(result)
except:
    print("发生异常")
```

第一步：

```python
result = 10 / 0
```

发生：

```text
ZeroDivisionError
```

于是 Python 不再继续执行：

```python
print(result)
```

而是直接跳到：

```python
except:
```

执行：

```python
print("发生异常")
```

------

# 六、如果没有异常呢？

例如：

```python
try:
    result = 10 / 2
    print(result)
except:
    print("发生异常")
```

输出：

```text
5.0
```

因为：

```text
try 成功
 ↓
不会进入 except
```

------

# 七、不要长期只写裸 `except`

刚开始可以理解：

```python
except:
```

但以后工程代码里更推荐：

```python
except Exception as e:
```

例如：

```python
try:
    result = 10 / 0
except Exception as e:
    print(f"发生错误：{e}")
```

输出类似：

```text
发生错误：division by zero
```

这里：

```python
e
```

就是：

> 捕获到的异常对象。

------

# 八、`Exception as e` 到底什么意思？

看：

```python
except Exception as e:
```

可以理解成：

```text
如果发生异常
 ↓
把这个异常保存到变量 e
```

所以后面可以：

```python
print(e)
```

查看错误信息。

这在 Agent 里非常重要。

以后你可能写：

```python
try:
    result = call_tool()
except Exception as e:
    print(f"Tool调用失败：{e}")
```

------

# 九、为什么不能只打印“失败了”？

例如：

```python
except:
    print("调用失败")
```

问题是你不知道为什么失败。

可能是：

```text
网络超时
API Key错误
参数错误
服务器错误
JSON错误
```

所以更推荐：

```python
except Exception as e:
    print(f"调用失败：{e}")
```

这样至少能知道具体原因。

------

# 十、可以捕获具体异常

比如：

```python
try:
    result = 10 / 0
except ZeroDivisionError:
    print("不能除以0")
```

这样只处理：

```text
ZeroDivisionError
```

------

再比如：

```python
numbers = [1, 2, 3]

try:
    print(numbers[10])
except IndexError:
    print("列表下标越界")
```

输出：

```text
列表下标越界
```

------

# 十一、几个常见异常你先认识一下

你以后经常会见到：

| 异常                | 含义              |
| ------------------- | ----------------- |
| `ZeroDivisionError` | 除以0             |
| `IndexError`        | 列表下标越界      |
| `KeyError`          | 字典中没有这个key |
| `ValueError`        | 值不合法          |
| `TypeError`         | 类型不对          |
| `FileNotFoundError` | 文件不存在        |
| `JSONDecodeError`   | JSON解析失败      |
| `TimeoutError`      | 超时              |

不用死背，慢慢熟悉。

------

# 十二、字典的 `KeyError`

例如：

```python
user = {
    "name": "Tom"
}

print(user["age"])
```

会报：

```text
KeyError: 'age'
```

因为：

```text
user里没有age
```

可以：

```python
try:
    print(user["age"])
except KeyError:
    print("没有age字段")
```

------

# 十三、文件不存在

比如：

```python
with open("abc.txt", "r") as f:
    content = f.read()
```

如果文件不存在：

```text
FileNotFoundError
```

可以：

```python
try:
    with open("abc.txt", "r") as f:
        content = f.read()

except FileNotFoundError:
    print("文件不存在")
```

以后做 RAG 读 PDF、TXT 时很常见。

------

# 十四、多个 `except`

可以针对不同错误做不同处理。

例如：

```python
try:
    number = int(input("请输入数字："))
    result = 10 / number

except ValueError:
    print("请输入合法数字")

except ZeroDivisionError:
    print("不能输入0")
```

如果用户输入：

```text
abc
```

进入：

```python
ValueError
```

如果输入：

```text
0
```

进入：

```python
ZeroDivisionError
```

------

# 十五、最后再加一个通用异常

实际项目里可以写：

```python
try:
    ...

except ValueError:
    ...

except TimeoutError:
    ...

except Exception as e:
    print(f"未知错误：{e}")
```

最后的：

```python
Exception
```

相当于兜底。

------

# 十六、`else` 是什么？

`try / except` 还有一个：

```python
else
```

例如：

```python
try:
    result = 10 / 2

except ZeroDivisionError:
    print("除零错误")

else:
    print(f"计算成功：{result}")
```

如果 `try` 没报错：

```text
进入 else
```

输出：

```text
计算成功：5.0
```

------

# 十七、`finally` 是什么？

还有：

```python
finally
```

它的特点是：

> 不管成功还是失败，最后都会执行。

例如：

```python
try:
    result = 10 / 0

except ZeroDivisionError:
    print("出错了")

finally:
    print("程序结束")
```

输出：

```text
出错了
程序结束
```

------

如果没报错：

```python
try:
    result = 10 / 2
    print(result)

except ZeroDivisionError:
    print("出错了")

finally:
    print("程序结束")
```

输出：

```text
5.0
程序结束
```

------

# 十八、为什么 `finally` 有用？

它适合做：

```text
关闭文件
关闭数据库连接
释放资源
关闭网络连接
清理临时文件
```

比如：

```python
connection = None

try:
    connection = connect_database()

except Exception as e:
    print(e)

finally:
    if connection:
        connection.close()
```

意思：

> 不管前面有没有出错，最后都把连接关掉。

------

# 十九、完整结构

Python 异常处理完整结构是：

```python
try:
    ...

except SomeError:
    ...

else:
    ...

finally:
    ...
```

执行逻辑：

```text
try
 │
 ├── 出错 ──→ except
 │
 └── 成功 ──→ else
                 ↓
              finally
```

不管怎么样：

```text
finally都会执行
```

------

# 二十、Agent 里的实际例子

现在开始贴近 Agent。

假设一个 Tool：

```python
def search_web(query: str) -> str:
    ...
```

我们可能写：

```python
try:
    result = search_web("Agent")

except Exception as e:
    print(f"搜索失败：{e}")
```

以后更像：

```python
def safe_search(query: str) -> str | None:
    try:
        result = search_web(query)
        return result

    except Exception as e:
        print(f"搜索失败：{e}")
        return None
```

这样调用：

```python
result = safe_search("Agent")
```

如果成功：

```text
返回搜索结果
```

失败：

```text
返回None
```

程序不会直接崩。

------

# 二十一、Agent Tool 为什么一定要异常处理？

假设 Agent 有三个 Tool：

```text
Search Tool
Calculator Tool
Weather Tool
```

用户问：

> 北京天气怎么样？

Agent 选择：

```text
Weather Tool
```

结果天气 API 超时。

如果你没处理：

```text
整个Agent崩溃
```

如果处理：

```text
Tool调用
 ↓
Timeout
 ↓
except
 ↓
返回错误信息
 ↓
LLM重新决定下一步
```

比如：

```python
def get_weather(city: str) -> str:
    try:
        return request_weather_api(city)

    except TimeoutError:
        return "天气服务超时，请稍后重试"

    except Exception as e:
        return f"天气工具执行失败：{e}"
```

这样 Agent 还能继续。

------

# 二十二、但这里有一个工程原则

不要这样：

```python
try:
    ...
except:
    pass
```

这非常不好。

它的意思：

```text
发生错误
 ↓
什么都不做
 ↓
假装没发生
```

以后 Debug 会非常痛苦。

Agent 项目里至少：

```python
except Exception as e:
    print(e)
```

更正式一点：

```python
logger.exception(e)
```

------

# 二十三、`raise` 是什么？

有时候你不想“吃掉错误”，而是主动抛出异常。

比如：

```python
def set_top_k(top_k: int):
    if top_k <= 0:
        raise ValueError("top_k必须大于0")
```

调用：

```python
set_top_k(-1)
```

会主动报：

```text
ValueError: top_k必须大于0
```

------

# 二十四、为什么自己主动 `raise`？

因为有些错误是：

> 程序逻辑上不允许。

比如：

```text
top_k = -5
```

显然不合理。

所以可以提前检查：

```python
if top_k <= 0:
    raise ValueError(...)
```

而不是让错误继续传到后面。

------

# 二十五、把它放到你之前的函数里

之前：

```python
def search_paper(
    query: str,
    top_k: int = 3
) -> list[str]:

    return [
        f"{query} Paper {i}"
        for i in range(1, top_k + 1)
    ]
```

现在可以更健壮一点：

```python
def search_paper(
    query: str,
    top_k: int = 3
) -> list[str]:

    if top_k <= 0:
        raise ValueError("top_k必须大于0")

    result = []

    for i in range(1, top_k + 1):
        result.append(
            f"{query} Paper {i}"
        )

    return result
```

然后：

```python
try:
    papers = search_paper(
        query="Agent",
        top_k=-1
    )

except ValueError as e:
    print(f"参数错误：{e}")
```

输出：

```text
参数错误：top_k必须大于0
```

------

# 二十六、你以后会非常常见的一种写法

```python
try:
    response = client.chat(...)

except TimeoutError:
    ...

except Exception as e:
    ...
```

可以理解为：

```text
调用LLM
 ↓
成功
 └→ 获得response

失败
 ├→ 超时 → 单独处理
 └→ 其他错误 → 通用处理
```

------

# 二十七、异常处理和“返回 None”有什么区别？

看两个设计。

第一种：

```python
def search() -> str | None:
    try:
        ...
    except Exception:
        return None
```

调用方：

```python
result = search()

if result is None:
    ...
```

------

第二种：

```python
def search() -> str:
    if error:
        raise RuntimeError("搜索失败")
```

调用方：

```python
try:
    result = search()
except RuntimeError:
    ...
```

两种都可以。

以后工程里具体怎么设计，要看场景。

你现在只需要知道：

```text
return None
```

是：

> 函数正常结束，只不过告诉调用者“没有结果”。

而：

```python
raise
```

是：

> 明确告诉调用者“这里发生了错误”。

这个区别很重要。

------

# 二十八、给你一个非常贴近 Agent 的例子

```python
def call_tool(
    tool_name: str,
    query: str
) -> str | None:

    try:
        if tool_name == "search":
            return f"搜索结果：{query}"

        elif tool_name == "calculator":
            return "计算结果"

        else:
            raise ValueError(
                f"未知工具：{tool_name}"
            )

    except ValueError as e:
        print(f"Tool参数错误：{e}")
        return None

    except Exception as e:
        print(f"Tool执行失败：{e}")
        return None
```

调用：

```python
result = call_tool(
    tool_name="abc",
    query="Agent"
)
```

因为：

```text
abc不是合法Tool
```

所以：

```python
raise ValueError(...)
```

然后被：

```python
except ValueError as e:
```

捕获。

------

# 二十九、你需要记住的核心语法

最重要的是：

```python
try:
    ...

except Exception as e:
    ...
```

然后知道：

```python
raise ValueError(...)
```

再知道：

```python
finally:
```

最后一定执行。

这些就已经够你进入 Agent 开发了。

------

# 三十、第三课练习

## 练习 1

判断下面代码会输出什么：

```python
try:
    x = 10 / 0

except ZeroDivisionError as e:
    print("A")

finally:
    print("B")
```

------

## 练习 2

下面：

```python
def get_user(
    user_id: int
) -> str | None:

    if user_id == 1:
        return "Tom"

    return None
```

这里：

```python
return None
```

和：

```python
raise ValueError("用户不存在")
```

概念上有什么区别？

------

## 练习 3

把你之前的 `search_paper()` 改一下。

要求：

```text
query不能为空字符串

top_k必须大于0
```

如果不满足：

```python
raise ValueError(...)
```

然后用：

```python
try / except
```

调用它。

------

## 练习 4：Agent 风格小练习

写一个：

```python
def call_tool(
    tool_name: str
) -> str | None:
```

规则：

如果：

```text
tool_name == "search"
```

返回：

```text
调用搜索工具成功
```

如果：

```text
tool_name == "calculator"
```

返回：

```text
调用计算器成功
```

其他情况：

```python
raise ValueError("不存在这个工具")
```

然后在函数外：

```python
try:
    ...
except ValueError as e:
    ...
```

捕获。

------

这节你真正需要掌握的是这条链：

```text
可能失败的代码
       ↓
      try
       ↓
发生异常
       ↓
    except
       ↓
记录 / 处理
       ↓
程序继续运行
```

这就是为什么 **异常处理是 Agent 工程里非常基础但非常重要的一层**。