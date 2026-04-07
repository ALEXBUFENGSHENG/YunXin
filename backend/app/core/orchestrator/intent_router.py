from typing import Dict, Any, Optional
from .base import AgentContext, AgentResult, BaseAgent
from app.services.llm_service import get_llm_service
import json

class IntentRouter:
    """意图路由组件"""
    
    async def route(self, context: AgentContext) -> str:
        """
        路由决策
        Returns: 'LEARN' | 'CHAT' | 'VOICE'
        """
        # 1. 简单规则判断
        text = context.user_input.lower()
        if not text:
            return "CHAT"
            
        # 2. 关键词启发式
        learn_keywords = ["学习", "计划", "怎么学", "路线", "教程", "复盘", "掌握", "教我", "分解"]
        if any(k in text for k in learn_keywords) and len(text) > 3: # 降低长度阈值
            return "LEARN"
            
        # 3. LLM 辅助判断 (可选，为了性能先简化)
        # if len(text) > 20:
        #     return await self._llm_route(text)
            
        return "CHAT"

    async def _llm_route(self, text: str) -> str:
        prompt = f"""
        请判断用户意图。
        用户输入: "{text}"
        
        类别定义:
        - LEARN: 用户想要学习新知识、制定计划、寻求教学指导或复盘。
        - CHAT: 普通闲聊、简单问答、问候。
        
        仅返回类别名称 (LEARN/CHAT)。
        """
        try:
            resp = await get_llm_service().generate_response([{"role": "user", "content": prompt}])
            intent = resp.strip().upper()
            return intent if intent in ["LEARN", "CHAT"] else "CHAT"
        except:
            return "CHAT"
