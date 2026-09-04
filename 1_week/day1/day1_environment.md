好，我们继续 **Day 1 第六课：Conda / uv + Python 项目结构 + Git / GitHub**。

这一课和前面相比更偏“工程操作”。你原来的准备周要求里也明确包含了 Conda/uv、Git/GitHub，以及建立 `agent-learning-2026` 这样的长期学习仓库。

这一课你不用学得特别深。目标只有一个：

拿到一个 Python/Agent 项目，你知道怎么创建环境、安装依赖、组织代码、提交到 GitHub\boxed{\text{拿到一个 Python/Agent 项目，你知道怎么创建环境、安装依赖、组织代码、提交到 GitHub}}

------

# 一、为什么 Python 项目需要“虚拟环境”？

先想一个问题。

假设你有两个项目。

项目 A：

```text
LangChain 版本 = 0.x
Pydantic 版本 = 1.x
```

项目 B：

```text
LangChain 版本 = 新版
Pydantic 版本 = 2.x
```

如果所有 Python 包全部安装到同一个环境：

```text
电脑
 ↓
一个Python
 ↓
所有项目共用所有包
```

就很容易发生：

```text
项目A需要旧版
项目B需要新版
       ↓
     冲突
```

所以我们给每个项目创建一个独立环境。

```text
电脑
│
├── project_A
│     └── env_A
│          ├── Python
│          ├── LangChain
│          └── Pydantic
│
└── project_B
      └── env_B
           ├── Python
           ├── PyTorch
           └── Transformers
```

这就是：

# Virtual Environment

最核心的意义。

------

# 二、你现在用 Conda 完全没问题

你之前应该已经接触过：

```bash
conda create
conda activate
```

所以没必要为了 Agent 强制换工具。

例如：

```bash
conda create -n agent python=3.11
```

意思：

```text
创建一个Conda环境
名字：agent
Python版本：3.11
```

然后：

```bash
conda activate agent
```

激活。

终端前面可能出现：

```text
(agent)
```

说明现在进入这个环境。

------

# 三、安装依赖

例如：

```bash
pip install openai
pip install python-dotenv
pip install pydantic
```

这些包就装在：

```text
agent环境
```

而不是其他项目的环境里。

所以：

```text
Conda environment
        ↓
一个隔离的Python运行空间
```

这就够你理解了。

------

# 四、常用 Conda 命令

你不用背很多。

准备周先会这些：

```bash
conda create -n agent python=3.11
```

创建环境。

```bash
conda activate agent
```

进入环境。

```bash
conda deactivate
```

退出环境。

```bash
conda env list
```

查看环境。

```bash
conda remove -n agent --all
```

删除环境。

------

# 五、一个特别重要的问题：`pip` 到底装到哪个 Python？

例如你终端：

```text
(agent)
```

然后：

```bash
pip install openai
```

理论上就应该安装进当前 `agent` 环境。

但以后如果出现：

> “明明 pip install 了，PyCharm 还是报红。”

第一件事不要重复安装。

先检查：

```bash
where python
```

Windows 下可以看：

```text
当前用的是哪个python.exe
```

再：

```bash
python -m pip --version
```

查看 `pip` 属于哪个 Python。

我以后更推荐你：

```bash
python -m pip install openai
```

而不是单纯：

```bash
pip install openai
```

因为：

```bash
python -m pip
```

明确表示：

> 使用“当前这个 Python”对应的 pip。

可以减少环境混乱。

------

# 六、那 `uv` 又是什么？

你现在先不要把它想复杂。

简单理解：

> **uv 是一个更现代、更快的 Python 项目和依赖管理工具。**

它可以做很多事情：

```text
创建Python项目
管理Python版本
创建虚拟环境
安装依赖
锁定依赖版本
运行程序
```

所以以前可能：

```text
conda
+
pip
+
requirements.txt
```

现在很多项目会使用：

```text
uv
+
pyproject.toml
+
uv.lock
```

------

# 七、你要不要马上从 Conda 换 uv？

我的建议：

> **不用。**

你现在：

```text
Conda：继续熟练使用
uv：会基本操作
```

就够了。

以后你看到 GitHub 项目写：

```bash
uv sync
```

不至于完全不知道是什么。

------

# 八、uv 最基础的几个命令

假设已经安装 uv。

创建项目：

```bash
uv init agent-demo
```

目录可能类似：

```text
agent-demo/
├── pyproject.toml
├── README.md
└── ...
```

进入：

```bash
cd agent-demo
```

安装依赖：

```bash
uv add openai
```

继续：

```bash
uv add pydantic
uv add python-dotenv
```

运行：

```bash
uv run python main.py
```

你现在会这几个就够了。

------

# 九、`pyproject.toml` 是什么？

以后你很容易看到：

```text
pyproject.toml
```

你现在把它理解成：

> **Python 项目的配置和依赖说明文件。**

例如可能类似：

```toml
[project]
name = "agent-demo"
version = "0.1.0"

dependencies = [
    "openai",
    "pydantic",
    "python-dotenv"
]
```

意思：

```text
项目名是什么
版本是什么
需要哪些Python包
```

所以别人拿到项目以后，就知道需要安装：

```text
openai
pydantic
python-dotenv
```

------

# 十、`requirements.txt` 又是什么？

旧一点或者很常见的 Python 项目里，你会看到：

```text
requirements.txt
```

里面：

```text
openai
pydantic
python-dotenv
httpx
```

安装：

```bash
pip install -r requirements.txt
```

所以以后看到：

```text
requirements.txt
```

你就理解：

> 这是项目依赖列表。

------

# 十一、这两个需要都会吗？

至少看得懂：

```text
requirements.txt
→ 传统、仍然非常常见

pyproject.toml
→ 现代Python项目越来越常见
```

你现在没必要研究 Python Packaging 标准细节。

------

# 十二、接下来是最重要的：项目目录怎么组织？

很多初学者所有代码都放：

```text
main.py
```

刚开始：

```python
100行
```

没问题。

以后：

```python
1000行
```

就崩了。

比如一个 Agent 项目不能长期这样：

```text
main.py

里面包含：
LLM代码
Tool代码
Memory代码
Config代码
RAG代码
所有东西
```

应该拆开。

------

# 十三、一个最简单的 Agent 项目结构

比如：

```text
agent-demo/
│
├── main.py
├── config.py
│
├── tools/
│   ├── search.py
│   └── calculator.py
│
├── memory/
│   └── memory.json
│
├── data/
│
├── .env
├── .env.example
├── .gitignore
└── README.md
```

分别干嘛？

------

## `main.py`

程序入口：

```text
运行Agent
```

比如：

```python
from config import MODEL

print(MODEL)
```

以后：

```python
agent.run()
```

也可能在这里。

------

## `config.py`

放配置：

```text
API Key
模型
Base URL
一些全局配置
```

比如：

```python
import os
from dotenv import load_dotenv

load_dotenv()

MODEL = os.getenv("LLM_MODEL")
```

------

## `tools/`

放 Agent 的工具：

```text
tools/
├── search.py
├── calculator.py
└── weather.py
```

以后非常典型。

------

## `memory/`

保存：

```text
长期记忆
用户信息
JSON文件
```

------

## `data/`

保存：

```text
RAG文档
测试数据
PDF
TXT
```

------

## `.env`

真实秘密：

```text
API_KEY
BASE_URL
```

不能上传。

------

## `.env.example`

公开模板：

```text
LLM_API_KEY=your_api_key
```

可以上传。

------

## `.gitignore`

告诉 Git：

> 哪些文件不要提交。

例如：

```text
.env
__pycache__/
.venv/
.idea/
```

------

## `README.md`

这是以后非常重要的东西。

里面说明：

```text
这个项目干嘛
怎么安装
怎么运行
有哪些功能
```

找实习时 GitHub 项目的 README 很重要。

------

# 十四、你原来的 Agent 学习仓库应该怎么组织？

你的路线已经规划了：

```text
agent-learning-2026/

01_llm_api/
02_tool_calling/
03_rag/
04_react/
05_langgraph/
06_memory/
07_mcp/
08_multi_agent/
09_agent_eval/
10_deep_research/
```

这个结构是合理的。

你可以再补几个根目录文件：

```text
agent-learning-2026/
│
├── 01_llm_api/
├── 02_tool_calling/
├── 03_rag/
├── 04_react/
├── 05_langgraph/
├── 06_memory/
├── 07_mcp/
├── 08_multi_agent/
├── 09_agent_eval/
├── 10_deep_research/
│
├── .gitignore
├── .env.example
└── README.md
```

真实 `.env`：

```text
.env
```

也可以放根目录，但是不要 Git 提交。

------

# 十五、Git 到底是什么？

很多初学者把：

```text
Git
```

和：

```text
GitHub
```

当成一个东西。

不是。

你可以这样理解。

### Git

是：

> **版本控制工具。**

安装在你电脑上。

它负责：

```text
记录代码历史
管理版本
创建分支
恢复旧版本
```

------

### GitHub

是：

> **网上托管 Git 仓库的平台。**

所以：

```text
本地电脑
   ↓
Git管理代码
   ↓
push
   ↓
GitHub
```

------

# 十六、为什么程序员需要 Git？

比如今天：

```text
Agent v1
```

可以运行。

明天：

```text
你大改代码
```

结果：

```text
彻底跑不起来
```

如果没有 Git：

> 完蛋，只能自己一点一点找。

有 Git：

```text
版本1
版本2
版本3
版本4
```

你可以回到之前正常工作的版本。

所以：

Git=代码的时间机器\boxed{Git = 代码的时间机器}

这个理解很形象。

------

# 十七、最基本 Git 流程

假设创建项目：

```text
agent-learning-2026
```

进入：

```bash
cd agent-learning-2026
```

初始化：

```bash
git init
```

意思：

> 告诉 Git：“从现在开始管理这个目录。”

------

# 十八、`git status`

```bash
git status
```

非常重要。

它告诉你：

```text
哪些文件改了
哪些没提交
哪些是新文件
```

如果以后不知道 Git 当前什么情况：

```bash
git status
```

先看。

------

# 十九、`git add`

假设：

```text
main.py
```

修改了。

执行：

```bash
git add main.py
```

或者：

```bash
git add .
```

`.` 表示：

> 当前目录所有变化。

------

# 二十、什么叫“暂存区”？

Git 可以简单理解成三层：

```text
工作目录
   ↓
git add
   ↓
暂存区
   ↓
git commit
   ↓
Git本地仓库
```

### 工作目录

你正在写代码的地方。

比如：

```text
main.py被修改
```

------

### 暂存区

表示：

> “我决定这部分改动准备提交了。”

执行：

```bash
git add .
```

进入暂存区。

------

### Git 仓库

执行：

```bash
git commit
```

真正创建一个版本。

------

# 二十一、`git commit`

例如：

```bash
git commit -m "add basic llm client"
```

这里：

```text
-m
```

表示：

```text
message
```

后面是这次提交的说明。

比如：

```bash
git commit -m "finish day1 python basics"
```

以后你翻历史就知道：

```text
这个版本干了什么
```

------

# 二十二、不要写这种 commit

```bash
git commit -m "123"
git commit -m "修改"
git commit -m "aaa"
```

虽然能用，但很差。

稍微写具体：

```text
add json config loader
fix memory file loading
implement tool calling demo
add rag reranker
```

以后做项目非常有帮助。

------

# 二十三、那 `git push` 是什么？

前面：

```bash
git commit
```

只是保存到：

```text
你的电脑
```

还没到 GitHub。

执行：

```bash
git push
```

才会：

```text
本地Git仓库
     ↓
GitHub远程仓库
```

------

# 二十四、完整流程

所以你每天写代码，最典型就是：

```bash
git status
```

看看变化。

然后：

```bash
git add .
```

然后：

```bash
git commit -m "finish json and env practice"
```

最后：

```bash
git push
```

形成：

```text
写代码
 ↓
git status
 ↓
git add
 ↓
git commit
 ↓
git push
 ↓
GitHub
```

这个流程以后要变成本能。

------

# 二十五、`git clone` 是什么？

假设 GitHub 上有一个项目：

```text
awesome-agent
```

你想下载下来。

一般不是：

> 浏览器下载 ZIP。

而是：

```bash
git clone <仓库地址>
```

它会：

```text
GitHub
 ↓
完整仓库
 ↓
本地
```

包括 Git 版本历史和远程仓库信息。

以后你复现 Agent 项目会经常：

```bash
git clone ...
```

------

# 二十六、`git pull` 是什么？

假设：

```text
GitHub上的代码更新了
```

你本地还是旧版本。

执行：

```bash
git pull
```

大致就是：

```text
远程GitHub
   ↓
获取新代码
   ↓
更新本地
```

------

# 二十七、`push` 和 `pull`

非常好记：

```text
push
推上去

pull
拉下来
```

即：

```text
本地
 ↓ push
GitHub
GitHub
 ↓ pull
本地
```

------

# 二十八、Branch 分支先学一个基本概念

暂时不用深入。

假设当前正式代码：

```text
main
```

你想开发一个新功能：

```text
RAG
```

但不想把稳定的 `main` 搞坏。

可以创建：

```text
rag-feature
```

分支。

简单理解：

```text
        main
         │
         ├─────────────
                       \
                    rag-feature
```

你在：

```text
rag-feature
```

随便改。

等验证没问题，再合并回：

```text
main
```

------

# 二十九、现在只需要知道这两个命令

查看：

```bash
git branch
```

创建/切换：

```bash
git switch -c rag-feature
```

以后回 main：

```bash
git switch main
```

你现在先知道就行。

不用马上练复杂 merge。

------

# 三十、`.gitignore` 特别重要

我们上一课已经提过：

```text
.env
```

绝对不应该正常提交。

所以：

```text
.gitignore
```

可以写：

```text
.env
__pycache__/
*.pyc
.venv/
.idea/
```

以后如果用 PyCharm：

```text
.idea/
```

通常也没必要提交个人 IDE 配置。

------

# 三十一、一个非常重要的安全检查

每次第一次：

```bash
git add .
```

之后，

不要直接：

```bash
git commit
```

先：

```bash
git status
```

看看有没有：

```text
.env
```

如果发现：

```text
.env
```

竟然被 Git 加进去了：

> 先处理，不要 push！

以后真实 API Key 泄露很多就是这种低级错误。

------

# 三十二、假设 `.env` 已经被 add 了怎么办？

如果还没有 commit：

```bash
git restore --staged .env
```

然后确保：

```text
.gitignore
```

有：

```text
.env
```

如果已经把真实 API Key 推到了 GitHub：

> 不能仅仅删除文件。

应该立刻：

```text
撤销/轮换这个API Key
```

因为 Git 历史里可能依然存在。

这一点以后一定记住。

------

# 三十三、GitHub README 应该怎么写？

准备周不用写得漂亮。

先：

```markdown
# Agent Learning 2026

用于记录 2026 年 Agent 技术学习过程。

## Roadmap

- LLM API
- Tool Calling
- RAG
- ReAct
- LangGraph
- Memory
- MCP
- Multi-Agent
- Agent Eval
- Deep Research
```

就够了。

后面每完成一阶段更新。

------

# 三十四、你 Day 1 结束时最好有这个结构

```text
agent-learning-2026/
│
├── 01_python_basics/
│   ├── type_hint_practice.py
│   ├── class_practice.py
│   ├── exception_practice.py
│   ├── file_practice.py
│   └── json_env_practice.py
│
├── 01_llm_api/
├── 02_tool_calling/
├── 03_rag/
├── 04_react/
├── 05_langgraph/
├── 06_memory/
├── 07_mcp/
├── 08_multi_agent/
├── 09_agent_eval/
├── 10_deep_research/
│
├── data/
│   └── user.json
│
├── .gitignore
├── .env.example
├── README.md
└── requirements.txt
```

当然目录编号你可以自己调整，不用完全照我的。

------

# 三十五、Conda + GitHub + 项目代码是什么关系？

这个一定不要混。

```text
Conda
↓
管理Python运行环境
Git
↓
管理代码版本
GitHub
↓
保存/协作Git仓库
requirements.txt
or pyproject.toml
↓
描述项目需要什么依赖
```

它们不是一回事。

------

# 三十六、为什么一般不把整个 Conda 环境上传 GitHub？

假设你的环境里面：

```text
几GB Python包
```

没必要上传。

GitHub 只保存：

```text
源代码
+
依赖说明
```

别人下载以后：

```text
clone代码
    ↓
创建自己的环境
    ↓
按照依赖文件安装
```

例如：

```bash
conda create -n agent python=3.11
conda activate agent

pip install -r requirements.txt
```

这样就能复现环境。

------

# 三十七、怎么生成 `requirements.txt`？

如果当前环境装了：

```text
openai
pydantic
python-dotenv
```

可以：

```bash
pip freeze > requirements.txt
```

得到类似：

```text
openai==...
pydantic==...
python-dotenv==...
```

不过以后真实项目更推荐谨慎维护依赖，而不是无脑把整个大环境全部 freeze。

你准备周知道这个命令即可。

------

# 三十八、我建议你以后不要用一个巨大 Conda 环境做所有东西

例如：

```text
base
```

装：

```text
PyTorch
TensorFlow
LangChain
FAISS
Transformers
AgentScope
...
```

最后环境会非常乱。

最好：

```text
agent-dev
```

专门用于 Agent 学习。

科研：

```text
llm4cdsr
```

继续使用另外环境。

即：

```text
科研项目
    ↓
独立环境

Agent学习
    ↓
独立环境
```

这样冲突少得多。

------

# 三十九、这一课的核心内容其实只有这些

你不用被上面的细节吓到。

真正要掌握：

### Conda

```bash
conda create
conda activate
conda deactivate
```

知道虚拟环境为什么存在。

------

### uv

知道：

```bash
uv init
uv add
uv run
```

即可。

------

### Python 项目

知道不要把所有代码都塞：

```text
main.py
```

会按功能拆文件。

------

### Git

掌握：

```bash
git status
git add .
git commit
git push
git pull
git clone
```

------

### GitHub

知道：

```text
本地Git
↓
push
↓
GitHub
```

------

### 安全

一定：

```text
.env
↓
.gitignore
```

------

# 四十、给你几个非常实际的练习

## 练习 1：环境理解题

回答：

为什么下面两个项目最好使用两个虚拟环境？

```text
Project A
Python 3.10
Pydantic 1.x

Project B
Python 3.12
Pydantic 2.x
```

------

## 练习 2：Git 流程题

假设你：

```text
修改了 main.py
```

现在想：

> 创建一个版本并上传 GitHub。

把下面命令按照正确顺序排列：

```text
git push
git add .
git status
git commit -m "update main"
```

------

## 练习 3

请解释：

```text
git add
```

和：

```text
git commit
```

有什么区别？

------

## 练习 4

为什么：

```text
.env
```

一般要放进：

```text
.gitignore
```

？

而：

```text
.env.example
```

却可以上传？

------

# 四十一、实操练习

你今天最好真正建立：

```text
agent-learning-2026
```

项目。

至少：

```text
agent-learning-2026/
│
├── 01_python_basics/
│   └── day1.py
│
├── .gitignore
├── .env.example
└── README.md
```

`.gitignore`：

```text
.env
__pycache__/
*.pyc
.idea/
```

`.env.example`：

```text
LLM_API_KEY=your_api_key
LLM_MODEL=your_model
LLM_BASE_URL=your_base_url
```

README：

```markdown
# Agent Learning 2026

Agent 技术学习代码记录。
```

然后完成一次：

```text
git init
↓
git status
↓
git add .
↓
git commit
```

如果已经建立 GitHub 仓库，再：

```text
git push
```

------

# 四十二、Day 1 到这里正式学完

回头看，我们今天已经学了：

```text
Day 1：Python / Agent工程基础

① 类型注解               ✅
   ├─ str / int
   ├─ list / dict
   ├─ Literal
   └─ str | None

② 面向对象               ✅
   ├─ class
   ├─ __init__
   ├─ self
   ├─ 属性
   └─ 方法

③ 异常处理               ✅
   ├─ try
   ├─ except
   ├─ finally
   └─ raise

④ 文件操作               ✅
   ├─ with open
   ├─ r / w / a
   └─ read / write

⑤ JSON / 环境变量         ✅
   ├─ dump / load
   ├─ dumps / loads
   ├─ .env
   └─ os.getenv

⑥ 工程工具               ✅ 学完
   ├─ Conda
   ├─ uv
   ├─ 项目结构
   ├─ Git
   └─ GitHub
```

你今天并不是“学完了 Python”，而是完成了一个更实际的目标：

具备继续学习 LLM / Agent Python 代码所需的基础\boxed{\text{具备继续学习 LLM / Agent Python 代码所需的基础}}

这就够了。

等你把上面的 **4 个小问题回答一下**，我们检查完 Day 1，下一步就可以正式进入：

# Day 2：HTTP API + REST + GET/POST + Header + JSON 请求 + `requests/httpx`

这一天会第一次真正解释：

```text
你的Python程序
        ↓
      HTTP
        ↓
    外部API服务器
        ↓
      JSON
        ↓
   返回给Python
```

等 Day 2 搞懂以后，再调用真正的 LLM API，你就不会只是“照着官方 Demo 抄几行代码”，而是会知道每一步到底在干什么。