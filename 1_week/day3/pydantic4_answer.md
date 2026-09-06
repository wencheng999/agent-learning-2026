练习1：

```
tool: Literal[
    "search",
    "calculator"
]
```

要求tool这个字段只能是"search","calculator"这两个字符串，写其他内容会报错，说明当前只做了查找和计算这两个功能，tool: str要求tool只要是个字符串就能运行成功，没有严格限制。



练习2：

Action(action="search") 和Action(action="answer")能通过，Action(action="calculator") 和Action(action="abc")不能通过。



练习4：

model_config = ConfigDict(
    extra="forbid"
)
表示严禁模型中出现未声明的额外字段，表示某个模型功能只接受特定的字段。