这 5 道题整体做得不错，尤其是练习 4，你已经开始从“会写 Prompt”过渡到“会给 Agent 定规则”了。

不过里面有几个非常值得现在就纠正的细节，尤其是：**Few-shot 不是必选项、JSON 必须真的是合法 JSON、`none` 要和 Schema 对齐。**

# 练习 1：有 2 点对，1 点需要修正

你说这个 Prompt 的问题是：

1. 没给输出格式；
2. 没写示例；
3. 没有限制格式规则。

第 1、3 点正确。

但是：

> “没有写示例”

**不一定是问题。**

因为我们刚学过：

```text
Zero-shot
→ 没示例

Few-shot
→ 有少量示例
```

很多任务 Zero-shot 就完全能做好。

所以不能认为：

没有 Few-shot = Prompt 写错了\boxed{\text{没有 Few-shot = Prompt 写错了}}

更好的三个问题应该是：

```text
① “处理问题”这个Task太模糊

② 没说明允许使用什么工具 / 有什么上下文

③ 没有Constraints和Output Format
```

例如原 Prompt：

```text
你是一个非常厉害的AI专家，
请帮我处理下面的问题。

用户问题：
计算10加20。
```

模型会不知道：

```text
我要直接回答30？
还是调用calculator？
还是解释计算步骤？
还是返回JSON？
```

所以核心问题是：

Task Boundary 不明确\boxed{\text{Task Boundary 不明确}}

------

# 练习 2：完全正确 ✅

你现在可以正式记成：

```text
Instruction
→ 需要模型完成什么任务

Context
→ 完成任务需要知道的背景信息

Input
→ 本次真正需要处理的数据

Constraints
→ 允许做什么、不能做什么

Output Format
→ 最终结果必须长什么样
```

这一题通过。

------

# 练习 3：完全正确 ✅

A：

```text
直接分类，没有示例
```

所以：

Zero-shot\boxed{\text{Zero-shot}}

B：

```text
先给1个输入输出例子
再让模型完成新任务
```

所以：

One-shot\boxed{\text{One-shot}}

完全正确。

------

# 练习 4：思路很好，但有几个非常重要的工程细节

你写的 Prompt 已经包含：

```text
Role              ✅
Task              ✅
Available Tools   ✅
Constraints       ✅
Output Format     ✅
Few-shot          ✅
Fallback / none   ✅
```

整体思路很好。

但我们现在开始进入 Agent 工程，所以 **JSON 必须真的合法**。

你目前例如：

```json
{
"tool": "calculator"
"arguments":{
    "a": 10,
    "b": 20,
    "operation": "add"
}
}
```

这里：

```text
"calculator"
```

后面缺一个：

```text
,
```

正确：

```json
{
  "tool": "calculator",
  "arguments": {
    "a": 10,
    "b": 20,
    "operation": "add"
  }
}
```

------

## 第二个例子也有两个小错误

你写：

```text
"query"："agent"
```

这里用了中文：

```text
：
```

JSON 必须是英文冒号：

```text
:
```

而且：

```json
{
  "tool": "search_paper",
  "arguments": {
    "query": "agent",
    "top_k": 10
  }
}
```

才是合法 JSON。

------

# 重点：`none` 应该怎么写？

你写：

```json
{
  "tool": none,
  "arguments": none
}
```

这不是合法 JSON。

JSON 里没有：

```text
none
```

JSON 的空值是：

```text
null
```

但对于我们这个 Agent，我更建议设计为：

```json
{
  "tool": "none",
  "arguments": {}
}
```

为什么？

因为我们可以定义：

```python
class ToolDecision(BaseModel):
    tool: Literal[
        "calculator",
        "search_paper",
        "none"
    ]

    arguments: dict
```

所以：

```python
"tool": "none"
```

仍然是合法的工具决策状态。

而：

```python
"arguments": {}
```

表示：

> 不需要任何 Tool 参数。

这样上层程序特别容易判断：

```python
if decision.tool == "none":
    ...
```

------

# 你的 Prompt 我帮你整理成一个更规范的版本

```text
你是一个 Agent 工具决策器。

你的任务是：
根据用户当前的问题，从可用工具中选择最合适的工具，
并生成调用该工具所需要的参数。

当前可用工具只有：

1. calculator
   用于执行加减乘除数学计算。

2. search_paper
   用于搜索学术论文。

规则：

1. 只能从 calculator、search_paper、none 中选择。
2. 禁止编造不存在的工具。
3. 如果用户的问题不适合任何已有工具，选择 none。
4. 参数必须根据用户问题生成，不要编造不必要的信息。
5. 只输出合法 JSON。
6. 不要输出 Markdown。
7. 不要添加任何解释文字。

输出格式：

{
  "tool": "calculator | search_paper | none",
  "arguments": {}
}

示例1：

用户：
计算10加20

输出：

{
  "tool": "calculator",
  "arguments": {
    "a": 10,
    "b": 20,
    "operation": "add"
  }
}

示例2：

用户：
查找10篇Agent相关论文

输出：

{
  "tool": "search_paper",
  "arguments": {
    "query": "Agent",
    "top_k": 10
  }
}

示例3：

用户：
北京现在天气怎么样？

输出：

{
  "tool": "none",
  "arguments": {}
}
```

这一版已经相当接近真实 Agent Prompt 了。

------

# 这里还有一个很重要的问题

假设用户问：

```text
给我找50000篇Agent论文。
```

你的 Prompt 目前可能让 LLM 返回：

```json
{
  "tool": "search_paper",
  "arguments": {
    "query": "Agent",
    "top_k": 50000
  }
}
```

但我们的工具可能要求：

```python
top_k: int = Field(
    ge=1,
    le=20
)
```

所以 Prompt 和 Pydantic 是两道防线：

```text
Prompt
→ 告诉模型应该怎么做

Pydantic
→ 即使模型没听话，也不能让非法参数过去
```

这就是为什么我们之前一直强调：

Prompt 负责引导，程序负责保证\boxed{\text{Prompt 负责引导，程序负责保证}}

这个思想非常重要。

------

# 练习 5：完全正确 ✅

你已经理解了 Role 和 Task 的区别。

```text
你是一名世界顶级Agent专家
```

主要告诉模型：

> 用什么身份、视角、风格来处理问题。

但是它没有回答：

```text
具体要做什么？
能调用什么？
不能做什么？
结果长什么样？
失败怎么办？
```

所以：

Role 只是 Prompt 的一个组成部分\boxed{\text{Role 只是 Prompt 的一个组成部分}}

而不是 Prompt 的全部。

------

# Week 1 · Day 1 第一节通过 ✅

现在你已经掌握：

```text
Prompt五部分                     ✅
Instruction                      ✅
Context                          ✅
Input                            ✅
Constraints                      ✅
Output Format                    ✅
Zero-shot                        ✅
One-shot                         ✅
Few-shot                         ✅
System vs User                   ✅
Fallback / none                  ✅
合法JSON                         ✅
Prompt ≠ 程序验证                 ✅
```

下面进入今天第二块。

# 第二节：Task Decomposition —— 为什么 Agent 要学会“拆任务”

这是从普通 LLM 应用走向 Agent 的一个非常关键变化。

------

# 一、先看一个简单问题

用户：

```text
10 + 20 等于多少？
```

完全没必要拆。

直接：

```text
计算
↓
回答
```

就行。

但是用户如果说：

```text
帮我调研2026年Agent推荐系统的发展，
找到代表性论文，
总结主要研究方向，
比较这些方法，
最后生成一份报告。
```

这时候如果直接把整个问题交给一个 LLM：

```text
用户问题
↓
LLM
↓
最终答案
```

问题就来了。

模型同时需要：

```text
理解问题
搜索论文
判断论文是否相关
阅读论文
总结
比较
组织报告
检查引用
```

任务太复杂。

所以 Agent 经常会先做：

Task Decomposition\boxed{\text{Task Decomposition}}

也就是：

> 把一个复杂目标拆成多个较小、可执行的子任务。

------

# 二、比如 Research Agent 怎么拆？

用户：

```text
研究2026年Agent推荐系统的发展趋势。
```

Planner 可以输出：

```json
{
  "tasks": [
    {
      "id": 1,
      "task": "搜索2026年Agent推荐相关论文"
    },
    {
      "id": 2,
      "task": "提取每篇论文的研究问题和创新点"
    },
    {
      "id": 3,
      "task": "按研究方向进行分类"
    },
    {
      "id": 4,
      "task": "比较不同方向的优势和不足"
    },
    {
      "id": 5,
      "task": "总结未来趋势并生成报告"
    }
  ]
}
```

现在：

```text
一个很大的任务
        ↓
Planner
        ↓
Task 1
Task 2
Task 3
Task 4
Task 5
```

这就是最基本的 Planning。

------

# 三、为什么拆任务会更好？

主要有四个原因。

第一：

```text
每一步目标更明确
```

第二：

```text
不同任务可以用不同Tool
```

例如：

```text
搜索论文
→ Paper Search Tool

网页信息
→ Web Search Tool

已有文档
→ RAG Tool

计算
→ Calculator
```

第三：

```text
一些任务可以并发
```

比如：

```text
搜Web ─────┐
搜Paper ───┼→ Evidence
搜RAG ─────┘
```

这就和你之前 Day 4 学的：

```python
asyncio.gather()
```

连接起来了。

第四：

```text
某一步失败时更容易定位
```

比如：

```text
Planning       ✅
Paper Search   ❌
Web Search     ✅
Summary        尚未执行
```

比“整个 Agent 回答不好”更容易分析。

------

# 四、但不是所有任务都应该疯狂拆

这是一个常见误区。

用户：

```text
1+1是多少？
```

如果 Agent：

```text
Step 1：理解数字1
Step 2：理解加法
Step 3：计算
Step 4：反思
Step 5：验证
Step 6：总结
```

明显过度设计。

这叫：

Over-planning\boxed{\text{Over-planning}}

会增加：

```text
Latency
Token
Cost
Failure Points
```

所以 Agent 应该：

复杂任务拆，简单任务直接做\boxed{\text{复杂任务拆，简单任务直接做}}

------

# 五、一个好的子任务应该是什么样？

比如：

```text
研究Agent推荐
```

这个子任务仍然太大。

更好的：

```text
搜索2026年1月至今标题或摘要中涉及
Agent-based Recommendation的论文。
```

更加：

```text
具体
可执行
有边界
结果可验证
```

所以好的 Task 通常满足：

```text
Specific
→ 明确

Executable
→ 能执行

Bounded
→ 有边界

Measurable
→ 能判断完成没有
```

------

# 六、Planner 的 Prompt 应该怎么写？

不能只写：

```text
把用户任务拆开。
```

可以：

```text
你是一个任务规划器。

目标：
把复杂用户请求拆成可执行子任务。

规则：

1. 每个子任务只能完成一个清晰目标。
2. 子任务之间不要重复。
3. 如果多个子任务互不依赖，应标记为可以并发。
4. 如果某任务依赖另一个任务结果，必须说明依赖关系。
5. 不要真正执行任务，只负责规划。
6. 简单问题不要过度拆解。
7. 只输出JSON。
```

然后输出：

```json
{
  "tasks": [
    {
      "id": 1,
      "description": "...",
      "depends_on": [],
      "can_parallel": true
    }
  ]
}
```

这已经开始像 LangGraph 里的 Planner Node 了。

------

# 七、这里连接了 Structured Output

我们可以定义：

```python
class Task(BaseModel):
    id: int
    description: str
    depends_on: list[int]
    can_parallel: bool
```

然后：

```python
class Plan(BaseModel):
    tasks: list[Task]
```

于是：

```text
Planner LLM
↓
JSON
↓
Plan.model_validate_json()
↓
Plan对象
↓
程序知道接下来执行哪些任务
```

这就是：

Prompt + Planning + Structured Output\boxed{\text{Prompt + Planning + Structured Output}}

------

# 八、Few-shot 在 Planner 里尤其有用

因为“怎么拆任务”有时候比较抽象。

我们可以给示例。

例如：

```text
用户：
比较Python和Java适合Agent开发的优缺点。

规划：

1. 总结Python在Agent开发中的优势和不足。
2. 总结Java在Agent开发中的优势和不足。
3. 比较两者在生态、异步、部署和AI库方面的差异。
4. 给出适用场景建议。
```

然后再给模型新的复杂问题。

模型就比较容易学会：

> 子任务应该拆到什么粒度。

Few-shot 在这里比一句：

```text
请合理拆任务
```

通常更直观。

------

# 九、Few-shot 示例怎么选才好？

不要随便找几个。

最好覆盖：

```text
普通情况
边界情况
容易混淆情况
失败 / none 情况
```

比如 Tool Agent：

```text
calculator示例
search_paper示例
none示例
```

你刚刚其实已经做得很好。

这三个例子刚好覆盖：

```text
工具A
工具B
不调用工具
```

这就是好的 Few-shot 设计。

------

# 十、输出稳定性从哪里来？

很多初学者认为：

> Prompt 写得越严格，输出就一定稳定。

实际上真正的稳定来自多层共同作用：

```text
① 明确 Prompt

② Few-shot

③ JSON Schema

④ Pydantic Validation

⑤ Retry / Repair

⑥ 原生 Structured Output
```

可以理解成：

```text
LLM层
Prompt + Examples
        ↓
API层
Schema / Structured Output
        ↓
程序层
Pydantic Validation
        ↓
失败恢复层
Retry / Repair
```

所以：

可靠 Agent 从来不是只靠 Prompt\boxed{\text{可靠 Agent 从来不是只靠 Prompt}}

这句话很重要。

------

# 第二节练习

### 练习 1

为什么下面这个任务适合拆解：

```text
帮我研究2026年Agent推荐系统，
找论文，
总结创新点，
比较方法，
最后写报告。
```

而：

```text
计算20×5
```

通常不适合拆解？

------

### 练习 2

把下面复杂任务拆成 **4～6 个子任务**：

```text
帮我分析最近两年大模型在跨域推荐中的应用，
并判断哪些思想适合加入LLM4CDSR。
```

这个题和你自己的研究比较接近，可以认真设计。

------

### 练习 3

为什么 Planner 一般应该：

```text
只规划，不执行
```

而不是一边规划一边随便开始调用工具？

------

### 练习 4

Few-shot 示例为什么不应该只给：

```text
calculator
calculator
calculator
```

三个几乎一样的例子？

为什么：

```text
calculator
search_paper
none
```

通常会更好？

------

### 练习 5

请解释下面这句话：

可靠 Agent 不能只依赖 Prompt\boxed{\text{可靠 Agent 不能只依赖 Prompt}}

Prompt、Pydantic、Schema、Retry 各自大概负责什么？

这五题做完之后，我们就可以正式进入本周非常核心的一块：

Context Engineering\boxed{\text{Context Engineering}}

也就是现在 Agent 领域越来越强调的：**不是只问“Prompt 怎么写”，而是问“模型这一刻到底应该看到哪些信息”。**