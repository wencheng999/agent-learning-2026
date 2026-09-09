可以，我把你这组练习整理成适合直接放进学习笔记里的“写作模块”，不再保留练习题问答形式，而是改成连贯的知识总结。

## Context Engineering 写作模块

Prompt Engineering 和 Context Engineering 是构建 LLM 应用与 Agent 系统时两个相互关联但关注点不同的概念。Prompt Engineering 主要关注如何设计模型的任务指令，即通过明确任务目标、背景信息、输入内容、约束条件以及输出格式，引导 LLM 更准确地完成任务。Context Engineering 则进一步关注模型在当前任务阶段究竟应该看到哪些信息，包括如何选择、压缩、组织和动态更新这些信息。因此，Prompt Engineering 更强调“**怎样告诉模型做什么**”，而 Context Engineering 更强调“**当前应该给模型看什么**”。

在 Agent 系统中，Context 并不是越多越好。虽然现代大语言模型能够支持较大的 Context Window，但如果把所有历史对话、搜索结果、工具信息和文档内容全部放入上下文，首先可能占用大量 Token，增加调用成本和响应延迟；其次，大量无关或重复的信息可能淹没真正重要的内容，使模型难以抓住当前任务的重点；同时，还需要为模型最终生成答案预留一定的上下文空间。因此，Context Engineering 的目标不是构造最大的上下文，而是为模型提供**当前任务真正需要的高质量上下文**。

不同 Agent 或不同工作节点所需要的 Context 也并不相同。例如，在 Research Agent 中，Planner 的主要任务是进行任务规划，因此它重点需要看到用户原始问题、当前 Agent 具备的能力、可用工具概要以及规划规则，而不需要直接读取大量论文全文。Searcher 负责执行信息检索，因此重点需要看到当前搜索子任务、搜索关键词以及可以使用的搜索工具。Writer 的职责是生成最终回答或报告，因此更加需要用户原始问题、经过筛选后的高质量 Evidence、报告结构以及写作和引用要求，而没有必要读取搜索 API 返回的全部原始数据。

工具产生的结果同样需要进行 Context 管理。例如，Paper Search 一次可能返回 100 篇论文，如果将这 100 篇论文的全部内容原封不动交给 Writer，不仅会消耗大量 Context Token，也可能因为信息过多而导致模型难以判断哪些论文真正重要，使最终总结变得宽泛。因此，更合理的过程通常是先对搜索结果进行过滤、排序或重排（Rerank），保留相关度较高的候选论文，再从这些论文中提取与当前问题直接相关的核心证据，最终只把精选 Evidence 交给 Writer。例如：

```text
Search
  ↓
100篇候选论文
  ↓
Filter / Rerank
  ↓
Top-K相关论文
  ↓
提取关键Evidence
  ↓
Writer
```

Context Engineering 可以进一步概括为四个核心过程：**Select、Compress、Organize 和 Update**。Select 负责判断当前模型调用真正需要哪些信息，避免将大量无关内容加入上下文；Compress 负责对过长的历史消息、文档或工具结果进行摘要和压缩，在尽量保留关键信息的同时减少 Token 消耗；Organize 负责决定这些信息应该以什么结构提供给 LLM，例如区分用户问题、任务计划、Evidence、Tool Result 等不同部分；Update 则负责随着 Agent 的执行不断更新 Context，例如 Search Tool 执行完成后加入搜索结果，PDF Reader 执行后加入论文证据，Planner 修改计划后更新当前任务状态。

因此，Context Engineering 的核心思想可以总结为：

Select→Compress→Organize→Update\boxed{ \text{Select} \rightarrow \text{Compress} \rightarrow \text{Organize} \rightarrow \text{Update} }

其最终目标并不是让模型“看到尽可能多的信息”，而是在正确的任务阶段，把**正确的信息，以合适的形式提供给模型**。对于复杂 Agent 系统而言，不同节点往往应该拥有不同的 Context，这也是后续学习 Agent State、Memory、RAG 以及 LangGraph 状态管理的重要基础。