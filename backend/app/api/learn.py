from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import json
from app.models.request import LearnRequest, LearnStreamRequest, LearnFeedbackRequest
from app.models.response import LearnResponse
from app.agents.learn_agent import learn_agent
from app.services.learn_service import learn_service

router = APIRouter()


@router.post("/yexiu")
async def yexiu_learn(request: LearnRequest):
    """处理大脑驱动的学习请求"""
    try:
        result = await learn_service.handle_yexiu_learn(
            goal=request.goal or request.message,
            username=request.username,
            conversation_id=request.conversation_id
        )
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/feedback")
async def learn_feedback(request: LearnFeedbackRequest):
    """提交任务回答并获取反馈"""
    try:
        result = await learn_service.handle_feedback(
            topic=request.topic,
            user_answer=request.user_answer,
            phase=request.phase,
            session_data=request.session_data
        )
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/learn", response_model=LearnResponse)
async def learn(request: LearnRequest):
    """处理学习请求"""
    try:
        reply = await learn_agent.chat(
            request.goal,
            request.message,
            request.username,
            request.conversation_id,
            request.context,
            request.constraints,
            request.time_budget,
            request.preferred_format,
        )
        return LearnResponse(
            reply=reply,
            username=request.username or "用户",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@router.post("/api/learn/stream")
async def learn_stream(request: LearnStreamRequest):
    """流式处理学习请求"""
    try:
        async def event_generator():
            try:
                stream_result = learn_agent.stream(
                    request.goal,
                    request.message,
                    request.username,
                    request.conversation_id,
                    request.context,
                    request.constraints,
                    request.time_budget,
                    request.preferred_format,
                    mode=request.mode
                )
                if hasattr(stream_result, "__aiter__"):
                    async for data in stream_result:
                        yield f"data: {json.dumps(data)}\n\n"
                else:
                    for data in stream_result:
                        yield f"data: {json.dumps(data)}\n\n"
            except Exception as e:
                print(f"Learn Stream Error: {e}")
                error_data = {
                    "type": "error",
                    "message": f"学习流响应中断: {str(e)}"
                }
                yield f"data: {json.dumps(error_data)}\n\n"

        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream"
        )
    except Exception as e:
        def error_generator():
            data = {
                "type": "error",
                "message": str(e)
            }
            yield f"data: {json.dumps(data)}\n\n"

        return StreamingResponse(
            error_generator(),
            media_type="text/event-stream"
        )
