from fastapi import APIRouter
from app.api.chat import router as chat_router
from app.api.admin import router as admin_router
from app.api.learn import router as learn_router
from app.api.math_learn import router as math_router

# 创建主路由
api_router = APIRouter()

# 包含子路由
api_router.include_router(chat_router)
api_router.include_router(admin_router)
api_router.include_router(learn_router)
api_router.include_router(math_router)
