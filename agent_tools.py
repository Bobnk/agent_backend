from datetime import datetime

# 工具1：获取当前系统时间
def get_current_time() -> str:
    now = datetime.now()
    return now.strftime("%Y‑%m‑%d %H:%M:%S")


# 描述交给大模型看！大模型靠这段文字判断什么时候调用这个工具
tools_def = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "获取服务器当前的日期和时间，用户问现在几点、今天几号的时候使用",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]

# 根据工具名字分发执行
def dispatch_tool(tool_name: str, tool_args: dict):
    if tool_name == "get_current_time":
        return get_current_time()
    else:
        return f"错误：不存在工具 {tool_name}"
