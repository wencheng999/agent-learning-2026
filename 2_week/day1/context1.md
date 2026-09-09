这 5 道题整体掌握得不错，尤其练习 1、3、4，说明你已经真正理解了 **任务拆解为什么是 Agent Planning 的基础**。练习 2 和练习 5 有几个关键点值得现在修正一下，然后我们正式进入本周核心内容：**Context Engineering**。

# 一、练习 1：完全正确 ✅

你的回答抓住了三个关键原因：

```text
复杂任务
↓
存在多个子目标
↓
不同子任务可能调用不同工具
↓
部分子任务还可以并发
```

比如：

```text
研究 Agent 推荐
│
├── 搜论文              → Paper Search
├── 搜最新网页信息       → Web Search
├── 读取论文             → PDF Reader
├── 对论文进行比较       → LLM
└── 生成最终报告         → LLM
```

而：

```text
20 × 5
```

直接：

```text
Calculator
↓
100
```

就结束了。

如果非要拆：

```text
理解20
→ 理解5
→ 理解乘法
→ 计算
→ 检查
→ 总结
```

反而浪费：

```text
Token
Latency
API Cost
```

所以：

Planning 的目标不是“尽可能拆”，而是“拆到合适粒度”\boxed{\text{Planning 的目标不是“尽可能拆”，而是“拆到合适粒度”}}

------

# 二、练习 2：方向正确，但可以进一步变成“可执行计划”

你写：

```text
1. 搜索2025年至今的大模型在跨域推荐的应用
2. 总结创新点
3. 比较异同
4. 总结这些方法
5. 判断哪些思想适合加入LLM4CDSR
```

大方向没问题。

但第 2～4 步稍微存在重复：

```text
总结创新点
比较方法
总结这些方法
```

如果是给 Agent Planner 用，我们希望每一步更加：

```text
具体
输入明确
输出明确
依赖明确
```

例如我会调整成：

```text
Task 1
检索2025年至今LLM用于跨域推荐、
跨域序列推荐及相近方向的论文。

        ↓

Task 2
筛选真正与“LLM + 跨域推荐”相关的论文，
排除仅使用传统文本编码器或与CDR无关的工作。

        ↓

Task 3
分别提取每篇论文的：
- 问题
- 动机
- LLM如何使用
- 核心模块
- 创新点
- 局限

        ↓

Task 4
横向比较论文，
归纳最近两年的主要技术路线和共同趋势。

        ↓

Task 5
分析LLM4CDSR当前框架的不足，
建立：
“现有问题 ↔ 可借鉴思想”
的对应关系。

        ↓

Task 6
筛选出适合加入LLM4CDSR的方向，
从：
创新性
可实现性
与基线兼容性
实验成本
撞点风险
进行排序。
```

你会发现第 6 步必须依赖：

```text
Task 1～5
```

而 Task 1 中的多组搜索又可能：

```text
并发执行
```

这才开始变成真正的 Agent Plan。

------

# 三、练习 3：很好 ✅

你提到了一个非常关键的问题：

> 有的后续任务依赖前面任务的输出，如果还没拿到输入就直接调用工具，可能产生无效执行。

例如：

```text
Task 1：
搜索论文
↓
得到论文ID

Task 2：
根据论文ID读取PDF
```

那么不能：

```python
await asyncio.gather(
    search_paper(),
    read_pdf()
)
```

因为：

```text
read_pdf()
```

需要先知道：

```text
paper_id
```

所以应该：

```python
papers = await search_paper()

pdf = await read_pdf(
    papers[0]["id"]
)
```

这正好和你之前 Day 4 学的：

```text
独立任务
→ 可以 gather()

依赖任务
→ 顺序 await
```

彻底连接起来了。

------

# 四、练习 4：完全正确 ✅

这其实叫：

Coverage\boxed{\text{Coverage}}

Few-shot 示例最好覆盖主要决策边界。

如果只有：

```text
calculator
calculator
calculator
```

模型主要学到：

> 遇到问题好像都应该选 calculator。

而：

```text
calculator
search_paper
none
```

覆盖了：

```text
工具A
工具B
无需工具
```

这比三个高度重复的例子有价值很多。

以后如果有 10 个 Tool，也不意味着一定要给 10 个示例，但应该重点覆盖：

```text
容易混淆的工具
边界情况
none情况
异常参数情况
```

------

# 五、练习 5：这里要重点修正一个概念

你说：

> Prompt 负责 LLM 初步的格式输出。

这个范围太窄了。

Prompt 不只是负责格式。

Prompt 更广泛负责：

```text
告诉模型：
你要做什么
有哪些背景
有哪些规则
应该关注什么
不应该做什么
结果怎么输出
```

所以：

Prompt = 引导模型行为\boxed{\text{Prompt = 引导模型行为}}

而不仅是：

```text
“规定输出格式”
```

------

你说：

> Schema 在 API 层验证格式。

这里也需要稍微修正。

## JSON Schema 本身是什么？

Schema 本质上是：

> **数据结构说明书。**

例如：

```json
{
  "type": "object",
  "properties": {
    "tool": {
      "type": "string"
    }
  }
}
```

它描述：

```text
数据应该长什么样
```

但是它是否在 API 层直接约束模型，要看你使用的 API。

比如：

### 我们之前自己做的方法

```text
Pydantic
↓
model_json_schema()
↓
Schema
↓
塞进Prompt
↓
LLM自己尽量遵守
```

这里 Schema 并没有自动“验证”。

------

某些模型 API 原生支持 Structured Output 时：

```text
Schema
↓
直接作为API参数提供
↓
模型生成阶段受到Schema约束
```

这时候 Schema 才真正参与 API 层面的结构约束。

所以更准确地记：

```text
Prompt
→ 引导

Schema
→ 描述结构 / 某些API中直接约束结构

Pydantic
→ 程序运行时解析和验证

Retry
→ 验证失败之后重新尝试
```

可以画成：

```text
        LLM生成前
           │
           ↓
Prompt ────┤
           │
Schema ────┤
           ↓
        LLM输出
           ↓
       Pydantic
           ↓
       是否合法？
       /      \
     是        否
     ↓         ↓
   继续       Retry
```

所以这句话现在可以记住：

Prompt负责引导，Schema负责描述/约束，Pydantic负责验证，Retry负责恢复\boxed{\text{Prompt负责引导，Schema负责描述/约束，Pydantic负责验证，Retry负责恢复}}

------

# Task Decomposition 这一块通过 ✅

到目前为止你已经掌握：

```text
Prompt Engineering
├── Instruction
├── Context
├── Input
├── Constraints
├── Output Format
│
├── Zero-shot
├── One-shot
├── Few-shot
│
└── Task Decomposition
    ├── 复杂任务拆解
    ├── 依赖关系
    ├── 并发关系
    └── 避免Over-planning
```

接下来正式进入这一周很重要的一块。

# Week 1 · Context Engineering

你以后做 Agent，会越来越频繁看到这个词：

Context Engineering\boxed{\text{Context Engineering}}

这两年 Agent 开发里，它的重要性已经不只是：

> “Prompt 写得好不好。”

而是：

> **模型在当前这一步，到底应该看到什么信息？**

------

# 一、先区分 Prompt Engineering 和 Context Engineering

我们刚刚一直在研究：

```text
Prompt怎么写？
```

例如：

```text
你是一个论文搜索Agent。

请选择合适的工具。

只能输出JSON。
```

这主要属于：

Prompt Engineering\boxed{\text{Prompt Engineering}}

但是一个真实 Agent 还需要知道：

```text
用户到底问了什么？

之前聊了什么？

现在正在执行哪个任务？

有哪些Tool？

之前哪些Tool已经执行过？

Tool返回了什么？

有哪些论文证据？

用户有哪些要求？

还剩多少上下文空间？
```

这些东西共同组成：

Context\boxed{\text{Context}}

------

所以：

### Prompt Engineering

重点：

```text
怎么描述任务？
```

### Context Engineering

重点：

```text
模型当前应该看到哪些信息？
这些信息怎么组织？
哪些应该放进去？
哪些不应该放进去？
```

------

# 二、举个非常直观的例子

用户问：

```text
LLM4CDSR有哪些可以改进的地方？
```

假设我们给 LLM：

```text
你是一名推荐系统专家。
请分析LLM4CDSR有哪些可以改进的地方。
```

Prompt 写得没有明显问题。

但是模型根本没看到：

```text
LLM4CDSR论文
LLM4CDSR代码
你当前已经做的修改
Qwen-4B物品语义嵌入
当前实验结果
```

那么它只能：

```text
凭通用知识猜
```

所以 Prompt 再漂亮：

```text
也不够。
```

------

如果我们给它：

```text
System：
你是一名CDSR研究员。

Context：
- LLM4CDSR论文相关Methods
- 当前源代码结构
- 用户已经替换Qwen-4B语义嵌入
- 用户画像尚未实现
- 最近实验结果

Task：
分析下一步最值得修改的位置。
```

答案自然会具体得多。

这就是：

Garbage Context In → Garbage Answer Out\boxed{\text{Garbage Context In → Garbage Answer Out}}

上下文本身错了、不完整、无关，Prompt 写得再好也救不回来。

------

# 三、Context 不等于“越多越好”

这是 Context Engineering 最重要的第一条。

很多人会认为：

> 模型上下文窗口有几十万 Token，那我把所有信息全部塞进去不就完了？

不一定。

假设用户：

```text
比较论文A和论文B的创新点。
```

你给模型：

```text
论文A全文
论文B全文
另外50篇论文
用户过去1000轮聊天
全部代码
Git日志
20个工具说明
所有搜索结果
```

模型虽然“看到了更多”，但会出现：

```text
真正重要的信息
被大量无关信息淹没
```

这叫：

Context Noise\boxed{\text{Context Noise}}

上下文噪声。

------

# 四、Context Engineering 的目标

不是：

Maximum Context\text{Maximum Context}

而是：

Right Context\boxed{\text{Right Context}}

也就是：

> 在正确的时候，把正确的信息，以正确的形式，交给正确的模型调用。

你可以记一句：

Right Information+Right Time+Right Format\boxed{ \text{Right Information} + \text{Right Time} + \text{Right Format} }

------

# 五、一个 Agent 的 Context 可能包含什么？

先建立总体框架。

```text
Agent Context
│
├── 1. Instructions
│
│   └── 当前Agent规则
│
├── 2. User Input
│
│   └── 用户当前问题
│
├── 3. Conversation History
│
│   └── 历史对话
│
├── 4. Task State
│
│   └── 当前执行到了哪一步
│
├── 5. Tool Definitions
│
│   └── 当前有哪些工具
│
├── 6. Tool Results
│
│   └── 工具返回什么
│
├── 7. Retrieved Knowledge
│
│   └── RAG / Web / Papers
│
├── 8. Memory
│
│   └── 长期有用信息
│
└── 9. Output Constraints
    └── 输出要求
```

这就是一个典型 Agent 调用 LLM 时可能看到的上下文。

------

# 六、Context Window 是什么？

模型一次能够处理的信息不是无限的。

它有：

Context Window\boxed{\text{Context Window}}

简单理解：

> 一次模型调用能够放进去的总 Token 范围。

其中可能包括：

```text
System Prompt
+
User Input
+
Conversation History
+
Retrieved Documents
+
Tool Results
+
Examples
+
模型准备输出的空间
```

因此上下文是一种：

有限资源\boxed{\text{有限资源}}

------

# 七、举一个 Token Budget 思想

假设为了理解，虚构一个模型最大支持：

```text
10000 tokens
```

你放进去：

```text
System Prompt       1000
History             3000
RAG Documents       5000
Tool Definitions    1000
```

已经：

```text
10000
```

那模型还要：

```text
输出回答
```

怎么办？

所以你不能无限塞。

真实工程里必须考虑：

Context Budget\boxed{\text{Context Budget}}

------

# 八、Conversation History 就是 Context 的一部分

Day 5 我们学过：

```python
messages = [
    system,
    user,
    assistant,
    user,
    assistant,
    ...
]
```

对话越来越长：

```text
messages ↑
↓
tokens ↑
↓
latency ↑
↓
cost ↑
↓
最终可能超过Context Window
```

所以：

> “把所有历史永远完整保存并发送”

不是成熟的 Memory 策略。

------

# 九、怎么办？

最简单有三种思路。

### 方法 1：只保留最近 N 轮

比如：

```text
最近5轮
```

更早丢掉。

------

### 方法 2：把老对话总结

例如：

原来：

```text
100轮对话
```

压缩：

```text
用户正在学习Agent；
已经掌握HTTP、Pydantic、async；
当前学习Context Engineering。
```

这就是：

Conversation Summarization\boxed{\text{Conversation Summarization}}

------

### 方法 3：需要时再检索

不是所有历史一直塞进去。

而是：

```text
当前问题
↓
搜索Memory
↓
找到相关历史
↓
只放相关内容
```

这开始接近：

```text
Long-term Memory
```

后面会专门学。

------

# 十、Tool Definitions 也属于 Context

假设 Agent 有：

```text
2个工具
```

没什么问题。

但是如果未来：

```text
100个Tools
```

你每次把 100 个工具全部描述给模型：

```text
很浪费
```

而且模型容易：

```text
Tool Selection Confusion
```

所以成熟系统可能：

```text
用户问题
↓
先筛选相关Tool
↓
只给模型5个相关Tool
↓
模型再选择
```

这也是：

Context Engineering\boxed{\text{Context Engineering}}

不只是 Prompt 技巧。

------

# 十一、Tool Result 也不能无限塞

比如搜索工具返回：

```text
100篇论文
每篇摘要500字
```

你把 100 篇全部塞给 Writer：

```text
非常浪费
```

更合理：

```text
Search
↓
100篇论文
↓
Filter / Rerank
↓
留下Top 10
↓
提取关键Evidence
↓
给Writer
```

于是：

```text
Search Agent
```

和：

```text
Writer Agent
```

看到的 Context 根本不需要完全相同。

这个思想非常重要：

不同 Agent / Node 应看到不同 Context\boxed{\text{不同 Agent / Node 应看到不同 Context}}

------

# 十二、结合未来的 Research Agent

你的 Research Agent 可能：

```text
User
↓
Planner
↓
Searcher
↓
Reader
↓
Writer
↓
Critic
```

那么每个 Node 应该看到什么？

------

## Planner

需要：

```text
用户问题
Agent能力
可用工具概要
任务规则
```

它不一定需要：

```text
全部论文全文
```

因为现在还没搜索。

------

## Searcher

需要：

```text
具体搜索子任务
搜索工具说明
已有关键词
```

不一定需要：

```text
最终报告格式的全部要求
```

------

## Reader

需要：

```text
论文内容
当前需要回答的问题
需要提取哪些Evidence
```

------

## Writer

需要：

```text
用户原始问题
经过筛选的Evidence
报告结构
引用要求
```

不一定需要：

```text
每一次搜索API的原始JSON
```

------

## Critic

需要：

```text
最终Draft
证据
检查标准
```

这就是：

Per-Node Context\boxed{\text{Per-Node Context}}

即：

> 为不同节点设计不同上下文。

这对 LangGraph 特别重要。

------

# 十三、Prompt Engineering 和 Context Engineering 的一个经典区别

假设模型答错。

初学者第一反应：

```text
Prompt是不是写得不好？
```

成熟一点会问：

```text
模型有没有看到正确的信息？
```

例如模型不知道：

```text
Paper A准确率0.42
```

那你在 Prompt 里重复十遍：

```text
请认真比较实验结果！
```

也没有用。

因为：

模型无法可靠使用它根本没看到的信息\boxed{\text{模型无法可靠使用它根本没看到的信息}}

所以错误可能不是：

```text
Instruction Problem
```

而是：

```text
Context Problem
```

------

# 十四、Context Engineering 的四个动作

你可以先记成四个词：

Select→Compress→Organize→Update\boxed{ \text{Select} \rightarrow \text{Compress} \rightarrow \text{Organize} \rightarrow \text{Update} }

------

## Select

选择：

> 哪些信息需要放进去？

------

## Compress

压缩：

> 哪些内容太长，需要摘要？

------

## Organize

组织：

> 这些信息以什么结构给模型？

------

## Update

更新：

> Tool 执行以后，Context 怎么变化？

------

例如：

```text
初始Context
↓
User Query

Search执行
↓
加入Search Result

Read PDF
↓
加入Evidence

Writer
↓
只使用精选Evidence
```

Context 会动态变化。

------

# 十五、这就是为什么 Agent 有 State

以后 LangGraph 中你会看到：

```python
class AgentState(TypedDict):
    messages: list
    plan: list
    evidence: list
    tool_results: list
```

为什么要 State？

因为 Agent 工作过程中不断产生：

```text
新信息
新计划
Tool结果
证据
中间结果
```

我们必须有地方管理。

所以：

State = Agent运行过程中的结构化上下文容器\boxed{\text{State = Agent运行过程中的结构化上下文容器}}

这个概念以后会非常重要。

------

# Context Engineering 第一轮练习

### 练习 1

用自己的话解释：

```text
Prompt Engineering
```

和：

```text
Context Engineering
```

最大的区别是什么？

------

### 练习 2

为什么：

> “模型支持很大的 Context Window，所以把所有信息全部放进去”

不是一个好的 Context Engineering 策略？

至少说出 3 个原因。

------

### 练习 3

假设 Research Agent 有：

```text
Planner
Searcher
Writer
```

请分别说明这三个 Agent 最需要看到哪些 Context。

不用写代码。

------

### 练习 4

为什么：

```text
Search Tool返回100篇论文
```

通常不应该原封不动全部传给：

```text
Writer
```

？

中间应该怎么处理？

------

### 练习 5

解释：

Select→Compress→Organize→Update\boxed{ Select \rightarrow Compress \rightarrow Organize \rightarrow Update }

这四步分别解决什么问题。

你把这轮做完以后，我们下一节会继续讲 **Context 的真正工程实现**：怎样用 `messages + state + retrieved evidence + tool results` 组织一个 Agent 的运行上下文，并结合 Python 写一个非常小的 Context Manager。