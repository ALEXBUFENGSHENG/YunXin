from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime


class ChatResponse(BaseModel):
    """聊天响应模型"""
    reply: str
    username: str
    deep_thinking_used: bool = False


class LearnResponse(BaseModel):
    """学习响应模型"""
    reply: str
    username: str


class UserResponse(BaseModel):
    """用户响应模型"""
    id: int
    username: str
    created_at: datetime
    updated_at: datetime


class MessageResponse(BaseModel):
    """消息响应模型"""
    id: int
    user_id: int
    message_type: str
    content: str
    timestamp: datetime
    session_id: int | None = None


class StatsResponse(BaseModel):
    """统计数据响应模型"""
    total_users: int
    total_messages: int
    active_users: int
    message_types: dict
    today_messages: int


class SuccessResponse(BaseModel):
    """成功响应模型"""
    success: bool
    message: str


class StreamMessage(BaseModel):
    """流式消息模型"""
    type: str
    content: Optional[str] = None
    full_response: Optional[str] = None
    message: Optional[str] = None
