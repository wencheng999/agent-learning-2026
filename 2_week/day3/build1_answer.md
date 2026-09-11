练习1：

因为随着prompt逐渐增多，main.py的代码也会逐渐增多，导致整体逻辑可能显得非常冗余复杂。



练习2：

contextmanager主要负责抽取state里面的什么信息，promptbuilder负责如何将抽取到的信息组织起来。



练习3：

因为LLM接受基本就是按照

```
{
    "role": "user",
    "role": "system"
}
```

这种格式接受的，所以将用户提出的问题放到角色为user的字段上，固定规则放到system上。



练习4：

schema = TaskAnalysis.model_json_schema()负责将pydantic内容格式转为dict的schema格式。

schema_text = json.dumps(    schema,    ensure_ascii=False,    indent=2 )负责将dict格式转为字符串的json格式，转为LLM接收的格式。



练习5：

这叫做尽可能实现单一事实来源，当修改Pydantic Model时，JSON Schema也会发生改变，从而prompt也会改变，如果分成两套结构， 那么修改完Pydantic时，prompt里面的output Format也得自己手动改变，如果有时候自己忘记了，那么就会造成pydantic改变了，但是和output Format不符。