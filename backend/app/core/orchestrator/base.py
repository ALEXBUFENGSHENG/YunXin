from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List
from pydantic import BaseModel

class AgentContext(BaseModel):
    """Agent 执行上下文"""
    user_id: str
    user_input: str
    conversation_id: Optional[int] = None
    memory: Optional[Dict[str, Any]] = None
    history: Optional[List[Dict[str, Any]]] = None

class AgentResult(BaseModel):
    """Agent 执行结果"""
    content: str
    data: Optional[Dict[str, Any]] = None
    next_action: Optional[str] = None

class BaseAgent(ABC):
    """Agent 抽象基类"""
    
    @abstractmethod
    async def run(self, context: AgentContext) -> AgentResult:
        """执行 Agent 逻辑"""
        pass
