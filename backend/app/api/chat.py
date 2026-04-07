from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import json
from app.models.request import ChatRequest, StreamChatRequest, SessionCreateRequest
from app.models.response import ChatResponse
from app.agents.dispatcher import agent_dispatcher
from app.services.chat_service import chat_service

router = APIRouter()


@router.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """处理聊天请求"""
    try:
        reply = await agent_dispatcher.chat(
            request.mode,
            request.message,
            request.username,
            request.conversation_id,
            request.deep_thinking,
        )
        return ChatResponse(
            reply=reply,
            username=request.username or "用户",
            deep_thinking_used=request.deep_thinking,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@router.get("/api/chat/stream")
async def chat_stream(message: str, username: str = "", conversation_id: int | None = None, mode: str = "chat", deep_thinking: bool = False):
    """流式处理聊天请求（兼容 GET，使用查询参数）"""
    try:
        async def event_generator():
            try:
                yield f"data: {json.dumps({'type': 'ping'})}\n\n"
                stream_result = agent_dispatcher.stream(mode, message, username, conversation_id, deep_thinking)
                if hasattr(stream_result, "__aiter__"):
                    async for data in stream_result:
                        yield f"data: {json.dumps(data)}\n\n"
                else:
                    for data in stream_result:
                        yield f"data: {json.dumps(data)}\n\n"
            except Exception as e:
                print(f"Stream Error: {e}")
                error_data = {
                    'type': 'error',
                    'message': f"流式响应中断: {str(e)}"
                }
                yield f"data: {json.dumps(error_data)}\n\n"
        
        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream"
        )
    except Exception as e:
        # ... (error generator remains the same)
        def error_generator():
            data = {
                'type': 'error',
                'message': str(e)
            }
            yield f"data: {json.dumps(data)}\n\n"
        
        return StreamingResponse(
            error_generator(),
            media_type="text/event-stream"
        )


@router.post("/api/chat/stream")
async def chat_stream_post(request: StreamChatRequest):
    """流式处理聊天请求（POST，配合前端 JSON 体）"""
    try:
        async def event_generator():
            try:
                yield f"data: {json.dumps({'type': 'ping'})}\n\n"
                stream_result = agent_dispatcher.stream(
                    request.mode,
                    request.message,
                    request.username,
                    request.conversation_id,
                    request.deep_thinking
                )
                if hasattr(stream_result, "__aiter__"):
                    async for data in stream_result:
                        yield f"data: {json.dumps(data)}\n\n"
                else:
                    for data in stream_result:
                        yield f"data: {json.dumps(data)}\n\n"
            except Exception as e:
                print(f"Stream Error (POST): {e}")
                error_data = {
                    'type': 'error',
                    'message': f"流式响应中断: {str(e)}"
                }
                yield f"data: {json.dumps(error_data)}\n\n"
        
        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream"
        )
    except Exception as e:
        def error_generator():
            data = {
                'type': 'error',
                'message': str(e)
            }
            yield f"data: {json.dumps(data)}\n\n"
        
        return StreamingResponse(
            error_generator(),
            media_type="text/event-stream"
        )


@router.get("/api/chat/sessions")
async def list_sessions(username: str):
    """获取用户会话列表"""
    sessions = chat_service.list_sessions(username)
    return {"sessions": sessions}


@router.post("/api/chat/sessions")
async def create_session(request: SessionCreateRequest):
    """创建新会话"""
    session = chat_service.create_session(request.username, request.name)
    if not session:
        raise HTTPException(status_code=400, detail="创建会话失败")
    return session


@router.delete("/api/chat/sessions/{session_id}")
async def delete_session(session_id: int, username: str):
    """删除指定会话"""
    success = chat_service.delete_session(username, session_id)
    return {"success": success}


@router.get("/api/chat/sessions/{session_id}/messages")
async def get_session_messages(session_id: int, username: str):
    """获取指定会话消息"""
    messages = chat_service.get_session_messages(username, session_id)
    return {"messages": messages}


@router.get("/api/health")
async def health_check():
    """健康检查端点"""
    return {"status": "healthy", "message": "AI 助教服务运行正常"}
