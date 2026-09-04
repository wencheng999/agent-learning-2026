def call_tool(tool_name:str) -> str:
    if tool_name=="search":
        return "调用搜索工具成功"
    elif tool_name=="calculator":
        return "调用计算器成功"
    else:
        raise ValueError("不存在这个工具")

try:
    result=call_tool("1")
    print(result)
except ValueError as e:
    print(e)