练习1：

"search" 一般表示LLM调用的工具名称。

"function" 表示将具体调用的函数名给function。

search_paper 表示具体的函数名

"input_model"表示输入的模型格式。

SearchInput 表示具体输入格式是SearchInput对象格式。



练习2：首先从工具封装列表获取实际的工具名称是多少，然后根据工具名将实际工具函数给tool_func，然后在获取实际的输入格式是什么格式，然后检查实际的输入内容是不是符合函数格式，最后调用该函数得到结果。



练习3：

因为**可以对字典进行解包，而**model_dump()函数可以将pydantic转为dict格式，所以就是**args.model_dump()这种输入格式。