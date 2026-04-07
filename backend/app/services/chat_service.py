import json
from typing import List, Dict, Optional
from app.services.llm_service import get_llm_service
from app.repositories.user_repo import user_repo
from app.core.orchestrator.orchestrator import orchestrator


class ChatService:
    """聊天业务服务"""
    
    async def handle_chat_request(self, message: str, username: str, conversation_id: int | None = None, deep_thinking: bool = False) -> str:
        """处理聊天请求
        
        Args:
            message: 用户消息
            username: 用户名
            conversation_id: 会话 ID，用于把消息绑定到指定会话
        Returns:
            str: AI 回复
        """
        if deep_thinking:
            reply = await self._run_deep_thinking(message, username)
        else:
            reply = await orchestrator.handle(
                user_input=message, 
                user_id=username, 
                conversation_id=conversation_id,
                mode="auto"
            )
        
        # 保存对话
        if username:
            self._save_chat(username, message, reply, conversation_id)
        
        return reply
    
    async def handle_stream_chat_request(self, message: str, username: str, conversation_id: int | None = None, deep_thinking: bool = False):
        """处理流式聊天请求
        
        Args:
            message: 用户消息
            username: 用户名
            conversation_id: 会话 ID，用于把消息绑定到指定会话
        Yields:
            dict: 流式响应数据
        """
        if deep_thinking:
            async for item in self._deep_thinking_stream(message, username, conversation_id):
                yield item
            return

        messages = get_llm_service().build_messages(message, username)
        completion = get_llm_service().generate_stream(messages)
        full_response = ""
        async for content in completion:
            if content:
                full_response += content
                yield {
                    'type': 'chunk',
                    'content': content,
                    'full_response': full_response
                }
        yield {
            'type': 'end',
            'full_response': full_response
        }
        if username:
            self._save_chat(username, message, full_response, conversation_id)

    def _parse_json_list(self, text: str, fallback: list[str]):
        raw = (text or "").strip()
        if raw.startswith("```"):
            parts = raw.split("\n")
            parts = parts[1:]
            if parts and parts[-1].strip().startswith("```"):
                parts = parts[:-1]
            raw = "\n".join(parts).strip()
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, list) and parsed:
                return parsed
        except Exception:
            pass
        return fallback

    async def _run_deep_thinking(self, message: str, username: str) -> str:
        plan_prompt = f"""任务：{message}
先列出3-6个关键疑问/子任务，用JSON数组返回，聚焦求解路径而非空话。"""
        plan_messages = get_llm_service().build_messages(plan_prompt, username)
        questions = self._parse_json_list(
            await get_llm_service().generate_response(plan_messages),
            ["澄清需求与目标", "列出已知条件与公式", "选择求解策略"]
        )

        answers = []
        for q in questions:
            answer_prompt = f"问题：{q}\n请给出简明解答或求解步骤，必要时附示例/公式/伪代码。"
            answer_messages = get_llm_service().build_messages(answer_prompt, username)
            ans = await get_llm_service().generate_response(answer_messages)
            answers.append(ans.strip())

        check_prompt = f"""任务：{message}
问题：{questions}
回答：{answers}
请生成3-5条自检要点：可能错误/反例/边界条件/改进方向，用JSON数组。"""
        check_messages = get_llm_service().build_messages(check_prompt, username)
        self_check = self._parse_json_list(
            await get_llm_service().generate_response(check_messages),
            ["检查假设是否成立", "用简单/极端样例验证", "与已知公式或定理对照"]
        )

        lines = ["【深度思考：计划→解答→自检】", "", "· 关键疑问："]
        for i, q in enumerate(questions, 1):
            lines.append(f"  {i}. {q}")
        lines.append("\n· 分步解答：")
        for i, ans in enumerate(answers, 1):
            lines.append(f"  {i}. {ans}")
        lines.append("\n· 自检要点：")
        for i, c in enumerate(self_check, 1):
            lines.append(f"  {i}. {c}")
        return "\n".join(lines)

    async def _deep_thinking_stream(self, message: str, username: str, conversation_id: int | None = None):
        current = ""

        def emit(text: str):
            nonlocal current
            current += text
            return {
                'type': 'chunk',
                'content': text,
                'full_response': current
            }

        yield emit("【深度思考：计划→解答→自检】\n\n")
        plan_prompt = f"""任务：{message}
先列出3-6个关键疑问/子任务，用JSON数组返回，聚焦求解路径而非空话。"""
        plan_messages = get_llm_service().build_messages(plan_prompt, username)
        questions = self._parse_json_list(
            await get_llm_service().generate_response(plan_messages),
            ["澄清需求与目标", "列出已知条件与公式", "选择求解策略"]
        )

        yield emit("· 关键疑问：\n")
        for i, q in enumerate(questions, 1):
            yield emit(f"  {i}. {q}\n")

        yield emit("\n· 分步解答：\n")
        answers = []
        for i, q in enumerate(questions, 1):
            answer_prompt = f"问题：{q}\n请给出简明解答或求解步骤，必要时附示例/公式/伪代码。"
            answer_messages = get_llm_service().build_messages(answer_prompt, username)
            ans = await get_llm_service().generate_response(answer_messages)
            answers.append(ans.strip())
            yield emit(f"  {i}. {answers[-1]}\n")

        check_prompt = f"""任务：{message}
问题：{questions}
回答：{answers}
请生成3-5条自检要点：可能错误/反例/边界条件/改进方向，用JSON数组。"""
        check_messages = get_llm_service().build_messages(check_prompt, username)
        self_check = self._parse_json_list(
            await get_llm_service().generate_response(check_messages),
            ["检查假设是否成立", "用简单/极端样例验证", "与已知公式或定理对照"]
        )

        yield emit("\n· 自检要点：\n")
        if isinstance(self_check, list):
            for i, c in enumerate(self_check, 1):
                yield emit(f"  {i}. {c}\n")
        else:
            yield emit(f"  1. {self_check}\n")

        yield {
            'type': 'end',
            'full_response': current
        }
        if username:
            self._save_chat(username, message, current, conversation_id)
    
    def _save_chat(self, username: str, user_message: str, ai_reply: str, conversation_id: int | None = None):
        """保存对话
        
        Args:
            username: 用户名
            user_message: 用户消息
            ai_reply: AI 回复
            conversation_id: 会话 ID，用于把消息绑定到指定会话
        """
        # 构建对话消息
        chat_messages = [
            {"type": "user", "content": user_message},
            {"type": "ai", "content": ai_reply}
        ]
        
        # 加载现有对话（按会话 ID）
        existing_messages = user_repo.load_chat(username, conversation_id)
        
        # 合并消息
        all_messages = existing_messages + chat_messages
        
        # 保存到数据库
        user_repo.save_chat(username, all_messages, conversation_id)

    def list_sessions(self, username: str) -> List[Dict]:
        """获取用户会话列表"""
        return user_repo.get_user_sessions(username)

    def create_session(self, username: str, name: Optional[str] = None) -> Optional[Dict]:
        """创建用户新会话"""
        return user_repo.create_session(username, name)

    def delete_session(self, username: str, session_id: int) -> bool:
        """删除指定会话"""
        return user_repo.delete_session(username, session_id)

    def get_session_messages(self, username: str, session_id: int) -> List[Dict]:
        """获取指定会话消息"""
        return user_repo.get_session_messages(username, session_id)
    
    def get_chat_history(self, username: str) -> List[Dict]:
        """获取聊天历史
        
        Args:
            username: 用户名
        
        Returns:
            List[Dict]: 聊天历史
        """
        return user_repo.load_chat(username)
    
    def clear_chat(self, username: str) -> bool:
        """清空聊天历史
        
        Args:
            username: 用户名
        
        Returns:
            bool: 是否清空成功
        """
        return user_repo.clear_chat(username)


# 创建全局聊天服务实例
chat_service = ChatService()
