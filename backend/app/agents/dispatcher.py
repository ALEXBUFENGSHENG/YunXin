from app.agents.chat_agent import chat_agent
from app.agents.recite_agent import recite_agent
from app.agents.learn_agent import learn_agent


class AgentDispatcher:
    """根据模式选择合适的智能体，并提供统一接口。"""

    def __init__(self):
        self.registry = {
            "chat": chat_agent,
            "recite": recite_agent,
            "learn": learn_agent,
        }

    def _select(self, mode: str, message: str = ""):
        normalized = (mode or "chat").lower()
        
        # 关键词自动增强：如果用户在普通聊天中提到“学习”、“分析”、“数一/数二/数三”等，自动切换到 learn 模式
        if normalized == "chat" and message:
            learn_keywords = ["学习", "了解", "掌握", "知识点", "考研", "数一", "数二", "数三", "数学", "怎么学"]
            if any(kw in message for kw in learn_keywords):
                return learn_agent, "learn"
                
        return self.registry.get(normalized, chat_agent), normalized

    async def chat(self, mode: str, message: str, username: str = "", conversation_id: int | None = None, deep_thinking: bool = False) -> str:
        agent, final_mode = self._select(mode, message)
        if final_mode == "learn":
            return await agent.chat(goal=message, username=username, conversation_id=conversation_id)
        if final_mode == "chat":
            return await agent.chat(message, username, conversation_id, deep_thinking)
        return await agent.chat(message, username, conversation_id)

    def stream(self, mode: str, message: str, username: str = "", conversation_id: int | None = None, deep_thinking: bool = False):
        agent, final_mode = self._select(mode, message)
        if final_mode == "learn":
            return agent.stream(goal=message, username=username, conversation_id=conversation_id)
        if final_mode == "chat":
            return agent.stream(message, username, conversation_id, deep_thinking)
        return agent.stream(message, username, conversation_id)


agent_dispatcher = AgentDispatcher()
