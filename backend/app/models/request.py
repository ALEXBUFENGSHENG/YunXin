from pydantic import BaseModel
from typing import Optional


class ChatRequest(BaseModel):
    """聊天请求模型"""
    message: str
    username: str = ""
    conversation_id: int | None = None
    mode: str = "chat"
    deep_thinking: bool = False


class StreamChatRequest(BaseModel):
    """流式聊天请求模型"""
    message: str
    username: str = ""
    conversation_id: int | None = None
    mode: str = "chat"
    deep_thinking: bool = False


class LearnRequest(BaseModel):
    """学习请求模型"""
    goal: str
    message: str = ""
    context: str = ""
    constraints: str = ""
    time_budget: Optional[str] = None
    preferred_format: Optional[str] = None
    username: str = ""
    conversation_id: int | None = None


class LearnStreamRequest(BaseModel):
    """流式学习请求模型"""
    goal: str
    message: str = ""
    context: str = ""
    constraints: str = ""
    time_budget: Optional[str] = None
    preferred_format: Optional[str] = None
    username: str = ""
    conversation_id: int | None = None
    stream: bool = True
    mode: str = "learn"


class SessionCreateRequest(BaseModel):
    """会话创建请求模型"""
    username: str
    name: Optional[str] = None


class LearnFeedbackRequest(BaseModel):
    """学习反馈请求模型"""
    topic: str
    user_answer: str
    phase: Optional[str] = None
    session_data: Optional[dict] = None
