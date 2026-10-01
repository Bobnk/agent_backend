from pydantic import BaseModel, Field
from typing import Optional

class ChatRequest(BaseModel):
    question: str = Field(min_length=1, description="用户提问，不能为空")
    session_id: Optional[str] = Field(default=None, description="会话id，传null则后台自动新建会话")
