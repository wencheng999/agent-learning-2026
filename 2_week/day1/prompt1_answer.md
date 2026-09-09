练习1：

1）没给输出格式；

2）没有写示例；

3）没有限制格式规则；



练习2：

Instruction ：是任务要求。

Context ：是背景信息

Input ：是用户输入真正的数据

Constraints ：是限制规则

Output Format：是输出格式



练习3：

A是zero-shot

B是one-shot



练习4：

```
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



练习5：

因为输入你是一名世界顶级Agent专家让LLM扮演当前角色，但是如果没有任务，LLM就无从下手，而且没有限制规则和输出格式，LLM可能能够正常回答，但是自由度非常高，往往无法得到我们想要的输出格式内容。