from typing import Dict, Any, Optional
from .base import AgentContext, AgentResult
from .intent_router import IntentRouter
from app.services.llm_service import get_llm_service

class Orchestrator:
    """
    中央调度器：负责意图识别、路由分发、上下文管理
    """
    
    def __init__(self):
        self.router = IntentRouter()
        self.chains = {} # 注册的 Agent 链
        
    def register_chain(self, name: str, chain_instance):
        self.chains[name] = chain_instance
        
    async def handle(self, user_input: str, user_id: str, conversation_id: Optional[int] = None, mode: str = "auto") -> str:
        """
        处理用户请求的主入口
        """
        # 1. 构建上下文
        context = AgentContext(
            user_id=user_id,
            user_input=user_input,
            conversation_id=conversation_id
        )
        
        # 2. 意图路由
        if mode == "auto":
            intent = await self.router.route(context)
        else:
            intent = mode.upper() # 允许外部强制指定 (如 'LEARN', 'CHAT')
            
        print(f"[Orchestrator] Intent: {intent}")
        
        # 3. 分发执行
        if intent == "LEARN":
            if "learning_chain" in self.chains:
                result = await self.chains["learning_chain"].run(context)
                return result.content
            else:
                return "⚠️ 学习系统暂未就绪"
                
        elif intent == "VOICE":
            # 语音链路暂留接口
            return "语音模式正在建设中..."
            
        else: # CHAT (Default)
            return await self._simple_chat(context)
            
    async def _simple_chat(self, context: AgentContext) -> str:
        """普通聊天回退逻辑"""
        messages = get_llm_service().build_messages(context.user_input, context.user_id)
        return await get_llm_service().generate_response(messages)

from .learning_chain import LearningChain

# 全局单例
orchestrator = Orchestrator()
# 注册默认链
orchestrator.register_chain("learning_chain", LearningChain())
