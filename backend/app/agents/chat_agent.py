from app.services.chat_service import chat_service


class ChatAgent:
    """聊天模式智能体，复用现有聊天服务与存储逻辑。"""

    async def chat(self, message: str, username: str = "", conversation_id: int | None = None, deep_thinking: bool = False) -> str:
        """单轮聊天响应"""
        return await chat_service.handle_chat_request(message, username, conversation_id, deep_thinking)

    def stream(self, message: str, username: str = "", conversation_id: int | None = None, deep_thinking: bool = False):
        """流式聊天响应，生成与现有 SSE 兼容的数据块"""
        return chat_service.handle_stream_chat_request(message, username, conversation_id, deep_thinking)


chat_agent = ChatAgent()
