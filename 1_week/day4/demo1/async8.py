from pydantic import BaseModel

class ToolResult(BaseModel):
    success: bool
    source:str
    data:dict|list|str|None = None
    error:str|None = None

web_tool_result = ToolResult(success=True, source='web-tool-result', data='web-tool-result',
                             error=None)
paper_tool_result = ToolResult(success=False, source='paper-tool-result', data=None,
                               error="paper 发生错误")

