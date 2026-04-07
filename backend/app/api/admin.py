from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.core.auth import get_current_user
from app.models.response import UserResponse, MessageResponse, StatsResponse, SuccessResponse
from app.services.admin_service import admin_service

router = APIRouter(
    prefix="/api/admin",
    tags=["admin"],
    responses={404: {"description": "Not found"}},
    dependencies=[Depends(get_current_user)],
)


@router.get("/users", response_model=List[UserResponse])
async def get_users():
    """获取所有用户"""
    try:
        users = admin_service.get_users()
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取用户失败: {str(e)}")


@router.get("/user/{username}/messages", response_model=List[MessageResponse])
async def get_user_messages(username: str):
    """获取用户的对话消息"""
    try:
        messages = admin_service.get_user_messages(username)
        return messages
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取消息失败: {str(e)}")


@router.delete("/user/{username}", response_model=SuccessResponse)
async def delete_user(username: str):
    """删除用户及其所有消息"""
    try:
        success = admin_service.delete_user(username)
        if success:
            return {"success": True, "message": f"用户 {username} 已删除"}
        else:
            raise HTTPException(status_code=404, detail=f"用户 {username} 不存在")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除用户失败: {str(e)}")


@router.delete("/message/{message_id}", response_model=SuccessResponse)
async def delete_message(message_id: int):
    """删除单条消息"""
    try:
        success = admin_service.delete_message(message_id)
        if success:
            return {"success": True, "message": "消息已删除"}
        else:
            raise HTTPException(status_code=404, detail="消息不存在")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除消息失败: {str(e)}")


@router.get("/stats", response_model=StatsResponse)
async def get_stats():
    """获取统计数据"""
    try:
        stats = admin_service.get_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计数据失败: {str(e)}")


@router.delete("/clean", response_model=SuccessResponse)
async def clean_all_data():
    """清空所有数据"""
    try:
        success = admin_service.clean_all_data()
        if success:
            return {"success": True, "message": "所有数据已清空"}
        else:
            raise HTTPException(status_code=500, detail="清空数据失败")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"清空数据失败: {str(e)}")
