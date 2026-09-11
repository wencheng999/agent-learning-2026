这 5 题都答得不错，说明你已经把 **Structured Output 为什么对 Agent 很重要** 理顺了。尤其第 1、4 题，已经不是“记 API”，而是在理解为什么 Agent 工程里一定要有结构化校验。

有两个小地方稍微修正一下。

你第 2 题说“因为外面有 `"""` 包起来，所以是 str”，完全正确。Python 看到：

```python
raw_output = """
{
    "need_search": true
}
"""
```

首先只知道这是：

```python
str
```

至于字符串里面的内容“长得像 JSON”，是后续：

```python
json.loads(...)
```

或者：

```python
TaskAnalysis.model_validate_json(...)
```

才会去解析它。

第 5 题也正确，只是最后写成了：

```text
task_analysisi
```

应该是：

```text
task_analysis
```

所以到目前为止你已经掌握：

```text
自然语言 User Query
        ↓
PromptBuilder
        ↓
LLM
        ↓
JSON形式的字符串
        ↓
Pydantic解析 + 验证
        ↓
TaskAnalysis对象
        ↓
AgentState
        ↓
程序根据结构化结果继续执行
```

下面正式进入今天第三节。

# Week 1 · Day 3 第三节：Validation + Retry + Repair

这一节非常实用，因为真实 LLM 并不会永远乖乖返回：

```json
{
  "intent": "research",
  "difficulty": "hard",
  "need_search": true,
  "need_planning": true
}
```

即使你的 Prompt 已经写了：

```text
只能输出JSON
不要解释
```

它仍然可能犯错。

------

# 一、LLM 的 Structured Output 会怎么出错？

我们先看几种典型情况。

第一种，LLM 特别热情：

~~~text
当然可以，下面是任务分析：

```json
{
  "intent": "research",
  "difficulty": "hard",
  "need_search": true,
  "need_planning": true
}
```
~~~

人看：

> 没问题啊。

但：

```python
TaskAnalysis.model_validate_json(
    raw_output
)
```

可能失败。

为什么？

因为整个字符串并不是：

```json
{
  ...
}
```

而是：

~~~text
当然可以……

```json
{...}
Pydantic 要的是完整合法 JSON。

---

第二种：

```json
{
  "intent": "research",
  "difficulty": "very_hard",
  "need_search": true,
  "need_planning": true
}
~~~

JSON 本身合法。

但 Schema 不合法。

因为：

```python
difficulty: Literal[
    "easy",
    "medium",
    "hard"
]
```

不允许：

```text
very_hard
```

------

第三种：

```json
{
  "intent": "research",
  "difficulty": "hard",
  "need_search": true
}
```

少了：

```python
need_planning
```

验证失败。

------

第四种：

```json
{
  "intent": "research",
  "difficulty": "hard",
  "need_search": "yes",
  "need_planning": true
}
```

这里我们本来要求：

```python
need_search: bool
```

模型却输出字符串。

是否会被 Pydantic 接受，要看具体类型和严格配置，因此工程上不能简单假设它永远严格拒绝所有可转换值。如果你特别要求严格类型，可以进一步配置 strict validation。

核心思想还是：

LLM Output 不能因为“看起来差不多”就直接相信\boxed{\text{LLM Output 不能因为“看起来差不多”就直接相信}}

------

# 二、最简单的处理方式：失败就返回 None

我们上一节已经写了：

```python
try:
    analysis = (
        TaskAnalysis.model_validate_json(
            raw_output
        )
    )

    return analysis

except ValidationError as e:
    print("验证失败：", e)
    return None
```

这个版本安全。

因为错误数据不会进入下游。

但是存在一个明显问题：

```text
LLM第一次稍微格式错了一点
↓
整个任务直接失败
```

有点浪费。

假设模型只是输出了：

```text
difficulty = "very_hard"
```

明明再告诉它一句：

> `difficulty` 只能是 `easy / medium / hard`。

它很可能第二次就改对了。

所以我们需要：

Retry\boxed{\text{Retry}}

------

# 三、Retry 是什么？

Retry 很简单：

> 第一次失败，再尝试一次。

例如 API 请求失败：

```text
第一次请求
↓
503
↓
等待
↓
重新请求
```

这是网络层 Retry。

而我们现在讨论的是：

```text
第一次LLM Structured Output
↓
Validation失败
↓
重新让LLM生成
```

这是输出层 Retry。

最简单可以写：

```python
for attempt in range(3):
    raw_output = await client.chat(
        messages
    )

    try:
        return TaskAnalysis.model_validate_json(
            raw_output
        )

    except ValidationError:
        continue
```

意思：

```text
最多尝试3次
```

------

# 四、但是“原样 Retry”不够聪明

假设第一次 Prompt：

```text
difficulty只能是
easy、medium、hard
```

模型还是输出：

```text
very_hard
```

如果第二次我们把**完全一样的 Prompt**再发一遍：

```text
同一个Prompt
↓
重新生成
```

可能成功。

但也可能继续犯同样的错误。

更聪明的办法是：

把错误信息反馈给 LLM\boxed{\text{把错误信息反馈给 LLM}}

也就是：

```text
你刚才返回：
"difficulty": "very_hard"

验证失败：
difficulty必须是
easy / medium / hard

请修正后重新输出。
```

这就不只是单纯 Retry 了。

这叫：

Repair\boxed{\text{Repair}}

------

# 五、Retry 和 Repair 区别

你可以这样记：

```text
Retry
→ “再来一次”

Repair
→ “你刚才这里错了，根据错误修一下再来一次”
```

例如：

```text
Retry：

Prompt
↓
LLM错误
↓
同样Prompt
↓
LLM再生成
```

而 Repair：

```text
Prompt
↓
LLM错误
↓
Validation Error
↓
原始输出 + 错误原因
↓
Repair Prompt
↓
LLM修正
```

通常：

Repair 比盲目 Retry 信息更充分\boxed{\text{Repair 比盲目 Retry 信息更充分}}

------

# 六、我们先看看 `ValidationError`

假设：

```python
raw_output = """
{
    "intent": "research",
    "difficulty": "very_hard",
    "need_search": true,
    "need_planning": true
}
"""
```

然后：

```python
try:
    result = (
        TaskAnalysis.model_validate_json(
            raw_output
        )
    )

except ValidationError as e:
    print(e)
```

你可能看到类似：

```text
difficulty
Input should be
'easy', 'medium' or 'hard'
```

这其实特别有价值。

因为：

```python
e
```

不仅是在告诉程序：

> 错了。

还告诉你：

> **哪里错、为什么错。**

这正好可以反馈给 LLM。

------

# 七、第一版 Repair

可以构造：

```python
repair_messages = [
    {
        "role": "system",
        "content": (
            "你负责修复结构化输出。"
            "请严格按照要求修正JSON。"
            "只返回修正后的JSON，"
            "不要解释。"
        )
    },
    {
        "role": "user",
        "content": f"""
[INVALID OUTPUT]
{raw_output}

[VALIDATION ERROR]
{str(e)}

请修复以上输出。
"""
    }
]
```

然后：

```python
repaired_output = await client.chat(
    repair_messages
)
```

再：

```python
analysis = (
    TaskAnalysis.model_validate_json(
        repaired_output
    )
)
```

于是：

```text
第一次输出
↓
验证失败
↓
Repair Prompt
↓
第二次输出
↓
再次验证
```

------

# 八、但是 Repair Prompt 最好也告诉模型 Schema

否则模型知道：

```text
刚才错了
```

但未必完全知道：

```text
正确结构到底是什么
```

所以加入：

```python
schema = (
    TaskAnalysis.model_json_schema()
)
```

再：

```python
schema_text = json.dumps(
    schema,
    ensure_ascii=False,
    indent=2
)
```

Repair Prompt：

```python
repair_messages = [
    {
        "role": "system",
        "content": (
            "你负责修复无效的结构化输出。"
            "只返回合法JSON，"
            "不要输出任何额外解释。"
        )
    },
    {
        "role": "user",
        "content": f"""
[OUTPUT SCHEMA]
{schema_text}

[INVALID OUTPUT]
{raw_output}

[VALIDATION ERROR]
{str(e)}

请根据Schema和错误信息修复输出。
"""
    }
]
```

这样模型同时看到：

```text
正确答案应该长什么样
+
自己刚才输出了什么
+
为什么错
```

Repair 成功率自然更高。

------

# 九、我们把它写成完整函数

```python
import json

from pydantic import ValidationError

from schemas import TaskAnalysis


async def analyze_task(
    client,
    current_query: str,
    max_retries: int = 2
) -> TaskAnalysis | None:

    messages = (
        build_task_analyzer_messages(
            current_query
        )
    )

    raw_output = await client.chat(
        messages
    )

    if raw_output is None:
        return None
```

到这里和上一节一样。

------

# 十、进入 Retry 循环

继续：

```python
    for attempt in range(
        max_retries + 1
    ):
```

这里为什么：

```python
max_retries + 1
```

？

假设：

```python
max_retries = 2
```

我们的意思通常是：

```text
第一次正常尝试
+
最多2次重新尝试
```

总共：

```text
3次Validation机会
```

所以：

```python
range(3)
```

得到：

```python
0, 1, 2
```

------

# 十一、先尝试验证

```python
        try:

            analysis = (
                TaskAnalysis.model_validate_json(
                    raw_output
                )
            )

            return analysis
```

如果成功：

```text
立即 return
```

函数结束。

根本不会继续 Retry。

------

# 十二、如果失败

```python
        except ValidationError as e:
```

先打印：

```python
            print(
                f"第 {attempt + 1} 次验证失败"
            )
```

但这里出现一个问题。

假设现在已经：

```python
attempt == max_retries
```

意味着重试次数用完了。

就不能继续调用 LLM。

所以：

```python
            if attempt == max_retries:
                return None
```

------

# 十三、否则开始 Repair

准备 Schema：

```python
            schema = (
                TaskAnalysis.model_json_schema()
            )

            schema_text = json.dumps(
                schema,
                ensure_ascii=False,
                indent=2
            )
```

然后：

```python
            repair_messages = [
                {
                    "role": "system",
                    "content": (
                        "你负责修复无效的JSON输出。"
                        "严格遵守给定Schema。"
                        "只返回合法JSON，"
                        "不要输出解释或Markdown。"
                    )
                },
                {
                    "role": "user",
                    "content": f"""
[OUTPUT SCHEMA]
{schema_text}

[INVALID OUTPUT]
{raw_output}

[VALIDATION ERROR]
{str(e)}

请修复输出。
"""
                }
            ]
```

调用：

```python
            raw_output = await client.chat(
                repair_messages
            )
```

注意这一行特别重要：

```python
raw_output = ...
```

不是：

```python
repaired_output = ...
```

当然写成 `repaired_output` 也行。

但这里我们直接：

> 用修复后的新输出覆盖旧的 `raw_output`。

这样下一轮循环：

```python
TaskAnalysis.model_validate_json(
    raw_output
)
```

验证的就是新版本。

------

# 十四、如果 Repair 的 LLM 请求本身失败

还应该：

```python
            if raw_output is None:
                return None
```

所以完整逻辑就是：

```text
第一次raw_output
      ↓
 Validation
   /        \
成功         失败
 ↓            ↓
return     Retry次数还有？
           /          \
          否           是
          ↓             ↓
       return None    Repair
                       ↓
                  新raw_output
                       ↓
                   再Validation
```

------

# 十五、完整版本

```python
import json

from pydantic import ValidationError

from schemas import TaskAnalysis


async def analyze_task(
    client,
    current_query: str,
    max_retries: int = 2
) -> TaskAnalysis | None:

    messages = (
        build_task_analyzer_messages(
            current_query
        )
    )

    raw_output = await client.chat(
        messages
    )

    if raw_output is None:
        return None

    for attempt in range(
        max_retries + 1
    ):

        try:

            analysis = (
                TaskAnalysis.model_validate_json(
                    raw_output
                )
            )

            return analysis

        except ValidationError as e:

            print(
                f"第 {attempt + 1} 次验证失败"
            )

            if attempt == max_retries:
                return None

            schema = (
                TaskAnalysis.model_json_schema()
            )

            schema_text = json.dumps(
                schema,
                ensure_ascii=False,
                indent=2
            )

            repair_messages = [
                {
                    "role": "system",
                    "content": (
                        "你负责修复无效的JSON输出。"
                        "请严格遵守给定Schema。"
                        "只返回合法JSON，"
                        "不要输出解释或Markdown。"
                    )
                },
                {
                    "role": "user",
                    "content": f"""
[OUTPUT SCHEMA]
{schema_text}

[INVALID OUTPUT]
{raw_output}

[VALIDATION ERROR]
{str(e)}

请修复输出。
"""
                }
            ]

            raw_output = await client.chat(
                repair_messages
            )

            if raw_output is None:
                return None
```

这段代码值得你认真看。

因为它其实已经是一个非常典型的：

LLM Reliability Loop\boxed{\text{LLM Reliability Loop}}

------

# 十六、我们实际模拟一次

用户：

```text
帮我搜索2026年的Agent推荐论文并分析趋势。
```

第一次 LLM：

```json
{
  "intent": "research",
  "difficulty": "very_hard",
  "need_search": true,
  "need_planning": true
}
```

然后：

```python
TaskAnalysis.model_validate_json(...)
```

发现：

```text
very_hard
```

不允许。

------

程序不会自己猜：

```text
very_hard大概就是hard吧，
我直接偷偷改成hard。
```

而是：

```text
Validation失败
↓
把错误告诉LLM
```

Repair Prompt：

```text
Schema要求：

difficulty =
easy / medium / hard

你刚才输出：

difficulty = very_hard

验证失败。

请修复。
```

模型第二次：

```json
{
  "intent": "research",
  "difficulty": "hard",
  "need_search": true,
  "need_planning": true
}
```

再次：

```python
TaskAnalysis.model_validate_json(...)
```

成功。

得到：

```python
TaskAnalysis(
    intent="research",
    difficulty="hard",
    need_search=True,
    need_planning=True
)
```

最后：

```python
state.task_analysis = analysis
```

------

# 十七、为什么不让 Python 自动把 `very_hard` 改成 `hard`？

这是一个值得思考的问题。

你当然可以：

```python
if difficulty == "very_hard":
    difficulty = "hard"
```

但是问题是：

> 你怎么知道所有错误应该怎么修？

今天：

```text
very_hard → hard
```

明天可能：

```text
complex → ?
extreme → ?
medium-hard → ?
```

程序自己猜，很容易产生：

Silent Error\boxed{\text{Silent Error}}

也就是：

> 数据虽然没有报错，但实际上被错误修正了。

因此更稳妥的思路通常是：

```text
明确错误
↓
重新生成/Repair
↓
再次验证
```

当然，对于完全确定的机械格式问题，例如你明确知道某个外层 Markdown code fence 可以安全剥离，也可以在应用层做确定性的预处理。但**不要随便修改模型表达的语义值**。

------

# 十八、为什么不能无限 Retry？

比如：

```python
while True:
    try:
        ...
    except:
        retry()
```

看起来：

> 总有一次能成功吧？

实际上非常危险。

因为可能出现：

```text
模型一直输出错误
↓
无限请求
↓
Token不断消耗
↓
API费用增加
↓
程序永远不结束
```

所以必须有：

```python
max_retries
```

例如：

```python
max_retries = 2
```

这就是：

Bounded Retry\boxed{\text{Bounded Retry}}

有界重试。

这是以后 Agent 工程中特别重要的思想。

------

# 十九、Retry 还有一个隐藏问题：成本

假设正常一次：

```text
1次LLM API
```

如果：

```python
max_retries = 2
```

最坏：

```text
原始请求
+
Repair 1
+
Repair 2
=
3次LLM请求
```

所以 Reliability 不是免费的。

以后做 Agent 你会经常遇到一个三角关系：

QualityLatencyCost\boxed{ Quality \quad Latency \quad Cost }

想提高可靠性：

```text
Retry更多
Critic更多
Reflection更多
```

往往意味着：

```text
延迟↑
Token↑
Cost↑
```

所以不是：

> Retry 越多越好。

而是：

> 在可靠性和成本之间找到合理平衡。

------

# 二十、现在再理解 Prompt、Schema、Pydantic、Retry

到这里，我们可以把之前零散知识终于串起来了。

```text
Prompt
↓
告诉LLM：
“我希望你怎么输出”

JSON Schema
↓
告诉LLM / 程序：
“正确结构是什么”

Pydantic
↓
真正检查：
“你返回的东西合格吗”

Retry / Repair
↓
如果不合格：
“怎么恢复”
```

所以：

Prompt=引导\boxed{ Prompt = 引导 }Schema=结构定义\boxed{ Schema = 结构定义 }Pydantic=验收\boxed{ Pydantic = 验收 }Retry/Repair=恢复\boxed{ Retry/Repair = 恢复 }

这四个角色千万不要混。

------

# 二十一、这其实是一种“防御式编程”

假设你写普通程序：

```python
data = user_input
```

你不会永远假设：

```text
用户输入100%正确
```

所以会：

```python
try:
    ...
except:
    ...
```

同理。

LLM 本质上也是一个：

```text
不完全确定的外部组件
```

因此成熟 Agent 不应该：

```text
LLM说什么
↓
我全部相信
```

而应该：

```text
LLM Output
↓
Validate
↓
合法？
├── 是 → 使用
└── 否 → Repair / Retry / Fallback
```

这就是：

Defensive LLM Engineering\boxed{\text{Defensive LLM Engineering}}

你以后找 Agent 实习，这种工程意识比“会调用 LangChain 一个接口”重要得多。

------

# 二十二、再向后看一步

现在我们的 Task Analyzer 已经能够：

```text
User Query
↓
LLM分析
↓
Structured Output
↓
Validate
↓
Repair
↓
TaskAnalysis
```

例如：

```python
analysis.need_search
```

得到：

```python
True
```

下一步程序就应该：

```python
if analysis.need_search:
    ...
```

然后怎么办？

当然是：

调用搜索工具\boxed{\text{调用搜索工具}}

这正好把我们自然地带向下一阶段：

```text
Structured Decision
↓
Tool Selection
↓
Tool Arguments
↓
Tool Execution
↓
Tool Result
```

这就是后面真正的 **Tool Calling**。

但在进入 Tool Calling 前，我们今天还应该把：

```text
PromptBuilder
+
TaskAnalysis
+
Validation
+
Retry/Repair
+
AgentState
```

完整串成一次小实战，否则容易只懂零散代码。

------

# 这节先做 5 道检查题

1. 用自己的话区分 **Retry** 和 **Repair**。为什么 Repair 通常比“完全原样重新问一次”更有针对性？
2. 为什么这里：

```python
for attempt in range(
    max_retries + 1
):
```

需要 `+1`？如果 `max_retries=2`，最多有几次验证机会？

1. 为什么一定要设置 `max_retries`，而不应该：

```python
while True:
```

一直重试？

1. 假设 LLM 输出：

```json
{
  "intent": "research",
  "difficulty": "extreme",
  "need_search": true,
  "need_planning": true
}
```

请你按照顺序描述从 **Validation 失败 → Repair → Validation 成功 → Update State** 的完整过程。

1. 用自己的话解释这四句话分别是什么意思：

```text
Prompt = 引导
Schema = 结构定义
Pydantic = 验收
Retry / Repair = 恢复
```

你做完这 5 题，我们今天最后一节就把 **Task Analyzer Mini Agent** 完整写出来，让今天的 Prompt、Structured Output、State、Context 和 Retry 真正连成一个程序。