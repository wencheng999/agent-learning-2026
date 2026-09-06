练习1：

因为arguments是用继承了BaseModel数据基准类的SearchArguments类创建的，用这个类创建的对象会检查其属性是不是合法的。



练习2：



```
type(tool_call) 是ToolCall类型

type(tool_call.tool) 是字符串类型

type(tool_call.arguments) 是SearchArguments类型

type(tool_call.arguments.top_k) 是int类型
```





练习3：

tool_call.model_dump()表示将tool_call的ToolCall类型转为dict类型。

ToolCall.model_validate(raw_data)表示验证raw_data是不是符合ToolCall类型格式，如果验证成功，它会返回一个真正的 `ToolCall` 对象。

