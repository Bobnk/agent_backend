from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from schemas.chat_schema import ChatRequest
from settings import settings
import httpx
import uuid
from sqlalchemy.orm import Session
from db import get_db, SessionLocal
from models import ChatHistory
from agent_tools import tools_def, dispatch_tool
from models import User
from api.user import get_current_user

router = APIRouter(prefix="/chat", tags=["Agent对话"])


async def llm_stream_generator(
    user_prompt: str,
    session_id: str
):
    headers = {
        "Authorization": f"Bearer {settings.LLM_API_KEY}",
        "Content-Type": "application/json"
    }

    # 自己临时开会话读取历史聊天记录
    db_read = SessionLocal()
    history_rows = db_read.query(ChatHistory).filter(ChatHistory.session_id == session_id).all()
    db_read.close()

    messages = []
    for row in history_rows:
        messages.append({"role": "user", "content": row.user_query})
        messages.append({"role": "assistant", "content": row.llm_answer})
    messages.append({"role": "user", "content": user_prompt})

    req_json = {
        "model": "deepseek-chat",
        "messages": messages,
        "stream": True
    }
    full_answer = ""

    async with httpx.AsyncClient(timeout=None) as client:
        async with client.stream(
                "POST",
                url=f"{settings.LLM_BASE_URL}/chat/completions",
                headers=headers,
                json=req_json
        ) as resp:
            async for line in resp.aiter_lines():
                if not line:
                    continue
                if line.startswith("data:"):
                    yield f"{line}\n\n"
                    raw = line.replace("data: ", "")
                    if raw.strip() != "[DONE]":
                        import json
                        chunk_data = json.loads(raw)
                        delta = chunk_data["choices"][0]["delta"].get("content", "")
                        full_answer += delta

    # 流式全部跑完之后，新开会话保存记录到数据库
    db_write = SessionLocal()
    try:
        new_record = ChatHistory(
            session_id=session_id,
            user_query=user_prompt,
            llm_answer=full_answer
        )
        db_write.add(new_record)
        db_write.commit()
    finally:
        db_write.close()


@router.post("/agent_chat")
async def agent_chat(user_req: ChatRequest, db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):
    messages = [
        {"role": "user", "content": user_req.question}
    ]

    headers = {
        "Authorization": f"Bearer {settings.LLM_API_KEY}",
        "Content-Type": "application/json"
    }

    # Agent思考循环，最多循环3次，防止死循环
    for _ in range(3):
        req_json = {
            "model": "deepseek-chat",
            "messages": messages,
            "stream": False,
            "tools": tools_def
        }

        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                url=f"{settings.LLM_BASE_URL}/chat/completions",
                headers=headers,
                json=req_json
            )
            resp_data = resp.json()

        choice = resp_data["choices"][0]
        finish_reason = choice["finish_reason"]

        if finish_reason == "tool_calls":
            # 需要调用本地工具
            tool_call = choice["message"]["tool_calls"][0]
            tool_name = tool_call["function"]["name"]
            tool_arguments = tool_call["function"]["arguments"]

            # 后端执行本地工具函数
            tool_result = dispatch_tool(tool_name, tool_arguments)

            # 把消息追加到上下文
            messages.append(choice["message"])
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call["id"],
                "content": tool_result
            })
            continue

        elif finish_reason == "stop":
            answer_text = choice["message"]["content"]
            return {"answer": answer_text}

    return {"answer": "达到最大工具调用轮次限制"}



@router.post("/stream_chat")
async def stream_chat(
        req: ChatRequest,
        db: Session = Depends(get_db),current_user: User = Depends(get_current_user)
):
    print("=======我进来这个POST接口了！！======", flush=True)
    if req.session_id is None:
        new_sid = str(uuid.uuid4())
        print(f"======本次会话session_id = {new_sid} ======")

    else:
        new_sid = req.session_id
        print(f"======本次会话session_id = {new_sid} ======")
    return StreamingResponse(
        llm_stream_generator(req.question, new_sid),
        media_type="text/event-stream"
    )


# 读取历史聊天记录接口（原样保留，不需要修改）
@router.get("/history/{session_id}")
def get_history(session_id: str, db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):
    rows = db.query(ChatHistory).filter(ChatHistory.session_id == session_id).all()
    return rows
