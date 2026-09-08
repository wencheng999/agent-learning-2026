练习1：

model_json_schema()是将pydantic的具体内容格式告诉给LLM，然后让LLM以此格式来进行输出。

model_validate()是pydantic验证某数据对象一般是dict格式是不是符合某pydantic的内容格式，如果符合就创建该内容的pydantic对象。

model_validate_json()和上面差不多，只不过dict格式可以换成json格式。

model_dump()可以将pydantic格式转为dict格式



练习2：

字符串类型。

执行后变成pydantic的ToolDecision类型。



练习3：

因为不能百分百相信LLM输出的内容，LLM输出的内容和格式也不是百分百正确的，所以要二次检查。



练习4：

Structured Output是向LLM询问问题后让LLM的初次回答的内容格式，包括要调用什么函数之类的，此时还没有调用函数，

Tool Calling是LLM通过Structured Output知道需要调用什么函数后然后具体调用什么函数来回答这个问题，然后将结果返回给用户。



练习5：

首先构造要求LLM输出的pydantic格式，然后把格式内容告诉他，LLM返回输出的字符串后，检查该字符串是不是符合pydantic要求的格式，然后返回pydantic对象，然后根据返回的对象再工具注册表中查询哪个工具并进行执行。