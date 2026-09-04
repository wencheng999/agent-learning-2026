好，我们继续讲这一部分。

这三个东西是 Python 面向对象里最核心的基础：

```text
class
__init__
self
```

你后面看很多 Agent 代码时，会经常看到：

```python
class Agent:
    def __init__(self, model, tools):
        self.model = model
        self.tools = tools
```

如果这几行你真正看懂了，后面很多框架代码其实就没那么神秘了。

------

# 一、先不讲 `class`，先看一个现实问题

假设现在我们要保存一个用户的信息：

```python
name = "Tom"
age = 20
major = "Computer Science"
```

这没问题。

但是如果有第二个人：

```python
name2 = "Jack"
age2 = 22
major2 = "AI"
```

第三个人：

```python
name3 = "Lucy"
age3 = 21
major3 = "Software Engineering"
```

你会发现变量越来越乱：

```text
name
age
major

name2
age2
major2

name3
age3
major3
```

如果有 100 个用户，就很麻烦。

所以我们想：

> 能不能定义一种“用户模板”，以后所有用户都按照这个模板创建？

这就是：

```python
class
```

------

# 二、`class` 到底是什么？

最简单地理解：

> **class 就是“类”，它相当于创建对象的模板。**

比如：

```python
class User:
    pass
```

这里我们定义了一个：

```text
User 类
```

你可以把它理解成：

```text
用户设计图
```

但是注意：

```python
class User:
```

本身还不是具体用户。

它只是规定：

> “以后 User 类型的对象应该长什么样。”

------

# 三、类和对象的关系

可以这样理解：

```text
class
=
模板 / 图纸

object
=
根据模板创建出来的具体东西
```

比如汽车。

```text
汽车设计图
↓
class Car
```

根据设计图造出的：

```text
宝马
奔驰
奥迪
```

就是不同的对象。

------

再比如：

```python
class User:
    ...
```

是用户模板。

然后：

```python
user1 = User()
user2 = User()
```

就是两个不同的对象。

所以：

Class→Object\boxed{Class \rightarrow Object}

也就是：

```text
类
↓
实例化
↓
对象
```

------

# 四、第一个完整 class

来看：

```python
class User:

    def __init__(self, name, age):
        self.name = name
        self.age = age
```

然后：

```python
user1 = User("Tom", 20)
```

现在：

```python
print(user1.name)
print(user1.age)
```

输出：

```text
Tom
20
```

这几行非常重要，我们一点一点拆。

------

# 五、先看这一行

```python
class User:
```

意思：

> 定义一个名字叫 `User` 的类。

相当于定义一个模板。

------

# 六、然后看到：

```python
def __init__(self, name, age):
```

这里的：

```python
__init__
```

是一个特殊方法。

你现在可以先把它理解成：

> **创建对象时自动执行的初始化函数。**

------

# 七、为什么叫 `__init__`？

`init` 就是：

```text
initialize
```

也就是：

> 初始化。

所以：

```python
__init__()
```

的作用就是：

> 创建对象时，给这个对象设置初始数据。

------

# 八、什么时候执行 `__init__`？

比如：

```python
user1 = User("Tom", 20)
```

当执行这一行时：

Python 会自动调用：

```python
__init__()
```

大概可以理解成：

```text
User("Tom", 20)
       ↓
Python 创建 User 对象
       ↓
自动调用 __init__
       ↓
name = "Tom"
age = 20
```

所以你不需要自己写：

```python
user1.__init__(...)
```

通常是 Python 自动做的。

------

# 九、那 `self` 到底是什么？

这是最关键的。

先给结论：

> **self 表示“当前这个对象自己”。**

例如：

```python
user1 = User("Tom", 20)
```

此时初始化 `user1` 时：

```python
self
```

就代表：

```python
user1
```

------

再创建：

```python
user2 = User("Jack", 22)
```

此时：

```python
self
```

就代表：

```python
user2
```

所以：

self=当前正在操作的那个对象\boxed{self = 当前正在操作的那个对象}

------

# 十、用一个非常直观的例子看 `self`

代码：

```python
class User:

    def __init__(self, name, age):
        self.name = name
        self.age = age
```

创建：

```python
user1 = User("Tom", 20)
```

你可以脑子里暂时把：

```python
self.name = name
```

理解成：

```python
user1.name = "Tom"
```

把：

```python
self.age = age
```

理解成：

```python
user1.age = 20
```

所以最终：

```text
user1
│
├── name = "Tom"
└── age = 20
```

------

然后：

```python
user2 = User("Jack", 22)
```

执行时：

```python
self
```

变成 `user2`。

所以：

```text
user2
│
├── name = "Jack"
└── age = 22
```

两个对象互不影响。

------

# 十一、这里有一个特别容易混淆的地方

看：

```python
def __init__(self, name, age):
    self.name = name
```

这里左右两个 `name` 不完全是一回事。

左边：

```python
self.name
```

表示：

> 当前对象身上的 `name` 属性。

右边：

```python
name
```

表示：

> 调用 `__init__` 时传进来的参数。

比如：

```python
user1 = User("Tom", 20)
```

此时：

```python
name = "Tom"
```

然后：

```python
self.name = name
```

就是：

```python
user1.name = "Tom"
```

------

# 十二、可以把它想成“把参数保存到对象里”

这一段：

```python
def __init__(self, name, age):
    self.name = name
    self.age = age
```

其实就是：

```text
收到 name
↓
保存到当前对象.name

收到 age
↓
保存到当前对象.age
```

于是：

```python
User("Tom", 20)
```

最终形成：

```text
User对象
│
├── name → Tom
└── age  → 20
```

------

# 十三、为什么不能直接写：

```python
def __init__(self, name, age):
    name = name
    age = age
```

因为这样只是操作局部变量。

执行结束后，并没有把它们保存到对象里。

例如：

```python
class User:

    def __init__(self, name):
        name = name
```

然后：

```python
user1 = User("Tom")

print(user1.name)
```

会出问题。

因为对象身上根本没有：

```python
user1.name
```

------

正确的是：

```python
self.name = name
```

这表示：

> 把 `name` 真正保存为当前对象的属性。

------

# 十四、什么叫“属性”？

比如：

```python
user1.name
user1.age
```

这里：

```text
name
age
```

就叫：

> 对象的属性。

因此：

```python
self.name = name
```

相当于给对象添加一个属性：

```text
name
```

------

# 十五、完整运行一次

代码：

```python
class User:

    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age


user1 = User(
    name="Tom",
    age=20
)

print(user1.name)
print(user1.age)
```

执行过程：

### 第一步

Python 看到：

```python
User(...)
```

创建一个 User 对象。

------

### 第二步

自动调用：

```python
__init__
```

此时大概是：

```text
self = user1
name = "Tom"
age = 20
```

------

### 第三步

执行：

```python
self.name = name
```

于是：

```python
user1.name = "Tom"
```

------

### 第四步

执行：

```python
self.age = age
```

于是：

```python
user1.age = 20
```

------

最终：

```text
user1
│
├── name = "Tom"
└── age = 20
```

------

# 十六、`class` 不仅可以保存数据，还可以有“行为”

比如用户可以自我介绍。

```python
class User:

    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age

    def introduce(self):
        print(f"我叫{self.name}，今年{self.age}岁")
```

然后：

```python
user1 = User("Tom", 20)

user1.introduce()
```

输出：

```text
我叫Tom，今年20岁
```

------

# 十七、这里 `self` 又出现了

```python
def introduce(self):
```

这个 `self` 还是：

> 当前调用这个方法的对象。

比如：

```python
user1.introduce()
```

此时：

```python
self
```

就是：

```python
user1
```

因此：

```python
self.name
```

就是：

```python
user1.name
```

------

如果：

```python
user2 = User("Jack", 22)
user2.introduce()
```

此时 `self` 就变成：

```python
user2
```

所以输出：

```text
我叫Jack，今年22岁
```

------

# 十八、所以 `self` 最核心的价值是什么？

因为同一个类可以创建很多对象：

```text
User
│
├── user1
├── user2
├── user3
└── user4
```

类里面的方法不可能提前知道：

> “你到底正在操作哪一个对象？”

所以通过：

```python
self
```

表示：

> 当前对象。

因此：

```python
self.name
```

就是：

> 当前对象的 name。

------

# 十九、一个特别重要的理解

假设：

```python
user1.introduce()
```

Python 在概念上可以近似理解为：

```python
User.introduce(user1)
```

也就是说：

```text
user1
```

自动作为：

```text
self
```

传进去了。

这也是为什么你调用的时候写：

```python
user1.introduce()
```

没有手动传：

```python
self
```

但是定义方法必须写：

```python
def introduce(self):
```

------

# 二十、`self` 是 Python 关键字吗？

严格来说：

> **不是。**

你理论上甚至可以写：

```python
class User:

    def __init__(abc, name):
        abc.name = name
```

也能工作。

但是：

> Python 社区统一约定第一个参数写 `self`。

所以永远写：

```python
self
```

不要自己起别的名字。

------

# 二十一、现在开始和 Agent 联系起来

假设我们以后写一个 Agent：

```python
class Agent:

    def __init__(
        self,
        name: str,
        model: str
    ):
        self.name = name
        self.model = model
```

创建：

```python
agent1 = Agent(
    name="ResearchAgent",
    model="Qwen"
)
```

那么：

```text
agent1
│
├── name  = ResearchAgent
└── model = Qwen
```

这就是一个 Agent 对象。

------

再加入工具：

```python
class Agent:

    def __init__(
        self,
        name: str,
        model: str,
        tools: list[str]
    ):
        self.name = name
        self.model = model
        self.tools = tools
```

创建：

```python
agent = Agent(
    name="ResearchAgent",
    model="Qwen",
    tools=[
        "search",
        "read_pdf",
        "calculator"
    ]
)
```

现在对象里面：

```text
ResearchAgent
│
├── model
│      └── Qwen
│
└── tools
       ├── search
       ├── read_pdf
       └── calculator
```

你以后看到真正 Agent Framework 里的代码，本质上复杂很多，但底层这个思想没有变。

------

# 二十二、再增加一个方法

```python
class Agent:

    def __init__(
        self,
        name: str,
        model: str,
        tools: list[str]
    ):
        self.name = name
        self.model = model
        self.tools = tools

    def show_info(self):
        print(f"Agent名称：{self.name}")
        print(f"模型：{self.model}")
        print(f"工具：{self.tools}")
```

使用：

```python
agent = Agent(
    name="ResearchAgent",
    model="Qwen",
    tools=["search", "read_pdf"]
)

agent.show_info()
```

输出：

```text
Agent名称：ResearchAgent
模型：Qwen
工具：['search', 'read_pdf']
```

------

# 二十三、所以现在你可以这样区分

## 类

```python
class Agent:
```

表示：

> Agent 模板。

------

## 对象

```python
agent = Agent(...)
```

表示：

> 根据模板真正创建出来的一个 Agent。

------

## `__init__`

```python
def __init__(...):
```

表示：

> 创建 Agent 时如何初始化。

------

## `self`

```python
self
```

表示：

> 当前这个 Agent 对象。

------

## 属性

```python
self.model
self.tools
```

表示：

> 当前 Agent 身上的数据。

------

## 方法

```python
def show_info(self):
```

表示：

> 当前 Agent 能执行的行为。

------

# 二十四、一张图记住全部

```text
               class Agent
                  模板
                    │
                    │ 实例化
                    ↓
             agent = Agent(...)
                    │
                    ↓
               一个具体对象
                    │
          ┌─────────┴─────────┐
          ↓                   ↓
        属性                  方法
        Data                Behavior
          │                   │
      self.name          self.run()
      self.model         self.search()
      self.tools         self.answer()
```

而：

```text
self
```

始终指向：

```text
当前这个具体对象
```

------

# 二十五、为什么 Agent 框架喜欢用 class？

因为 Agent 本身就非常适合表示成对象。

一个 Agent 通常拥有：

```text
数据
├── model
├── prompt
├── tools
├── memory
├── state
└── config
```

同时又拥有：

```text
行为
├── run()
├── think()
├── call_tool()
├── search()
└── answer()
```

这就是典型的：

```text
数据 + 行为
```

所以非常适合：

```python
class Agent:
```

------

# 二十六、以后你看到这种代码就应该怎么读？

比如：

```python
class ResearchAgent:

    def __init__(
        self,
        model: str,
        tools: list[str]
    ):
        self.model = model
        self.tools = tools

    def search(self, query: str):
        print(
            f"{self.model} 正在搜索：{query}"
        )
```

创建：

```python
agent = ResearchAgent(
    model="Qwen",
    tools=["web_search"]
)
```

调用：

```python
agent.search("Agentic RAG")
```

你脑子里应该翻译成：

```text
创建一个 ResearchAgent
│
├── model = Qwen
└── tools = web_search

然后

当前这个Agent
↓
执行search()
↓
query = Agentic RAG
```

输出：

```text
Qwen 正在搜索：Agentic RAG
```

------

# 二十七、这里特别测试一下你有没有真正理解 `self`

假设：

```python
class Agent:

    def __init__(self, name: str):
        self.name = name

    def say_name(self):
        print(self.name)


agent1 = Agent("SearchAgent")
agent2 = Agent("RAGAgent")

agent1.say_name()
agent2.say_name()
```

结果是：

```text
SearchAgent
RAGAgent
```

为什么？

第一次：

```python
agent1.say_name()
```

这里：

```text
self = agent1
```

所以：

```python
self.name
```

就是：

```python
agent1.name
```

也就是：

```text
SearchAgent
```

第二次：

```python
agent2.say_name()
```

则：

```text
self = agent2
```

于是：

```text
RAGAgent
```

所以：

self让同一套方法能够作用于不同对象\boxed{self让同一套方法能够作用于不同对象}

这是它最核心的意义。

------

# 二十八、你现在暂时不用学这些

这一节先不要深入：

```text
继承
多态
魔术方法
@property
classmethod
staticmethod
抽象类
metaclass
```

后面需要再讲。

你现在只需要吃透：

```text
class
object
__init__
self
attribute
method
```

------

# 二十九、给你两个练习

### 练习 1

请自己判断：

```python
class Tool:

    def __init__(
        self,
        name: str,
        description: str
    ):
        self.name = name
        self.description = description


tool = Tool(
    name="search",
    description="搜索网络信息"
)
```

回答：

1. `Tool` 是什么？
2. `tool` 是什么？
3. `self` 在创建 `tool` 时代表谁？
4. `self.name = name` 在这里最终相当于什么？
5. `tool.description` 的值是多少？

------

### 练习 2

自己写一个：

```python
class Agent
```

要求它有三个属性：

```text
name
model
tools
```

再写一个方法：

```python
show_info()
```

运行后输出类似：

```text
Agent名称：ResearchAgent
模型：Qwen
工具：['search', 'calculator']
```

你把这两个练习写出来发我，我继续帮你检查。然后下一步我们讲 **异常处理 `try/except` 和为什么 Agent 调 API/Tool 时一定要做异常处理**。