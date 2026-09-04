def call_tool(
    tool_name: str,
    query: str
) -> str | None:

    try:
        if tool_name == "search":
            return f"搜索结果：{query}"

        elif tool_name == "calculator":
            return "计算结果"

        else:
            raise ValueError(
                f"未知工具：{tool_name}"
            )

    except ValueError as e:
        print(f"Tool参数错误：{e}")
        return None

    except Exception as e:
        print(f"Tool执行失败：{e}")
        return None


result = call_tool(
    tool_name="abc",
    query="Agent"
)