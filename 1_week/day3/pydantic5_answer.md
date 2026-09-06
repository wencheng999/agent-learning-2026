练习1：

model_json_schema()表示将模型对象转为schema模板格式，这个模板格式具体说明了哪些字段是什么类型，默认值多少，是不是必须的，然后给大模型，能够让大模型更好理解。

model_validate(data)表示验证data数据是不是符合数据模板类型，如果符合就创建成该pydantic类型的数据。

model_dump()表示将pydantic对象转为dict格式。



练习2：

query会出现在required，因为top_k有默认值，所以在创建pydantic对象时可以省略top_k字段，而query没有默认值，所以是必须的。





练习4：

首先用model_json_schema()方法将pydantic对象的模板格式告诉给LLM，尽量引导LLM正确生成，然后将LLM的输出再用pydantic的model_validate()函数在检查一遍，只有合法才会执行工具