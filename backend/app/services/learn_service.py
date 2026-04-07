from typing import List, Dict, Optional, Any
from app.services.llm_service import get_llm_service
from app.repositories.user_repo import user_repo
from app.config.settings import settings


from app.core.yexiu.orchestrator import YeXiuLearningAgent
from app.core.yexiu.brain_kernel import brain_kernel
from mysql_storage import mysql_storage

class LearnService:
    """学习业务服务"""

    async def handle_yexiu_learn(self, goal: str, username: str, conversation_id: int = None) -> Dict[str, Any]:
        """云心大脑驱动的深度学习处理"""
        # 1. 获取用户 ID
        user_id = mysql_storage.get_user_id(username)
        
        # 2. 初始化云心 Agent (带画像)
        # 暂时 mock profile，实际可从 learning_profiles 取
        agent = YeXiuLearningAgent(user_profile={"user_id": user_id, "username": username})
        
        # 3. 执行学习流 (使用统一分发逻辑以支持数学/知识/问题解决等不同模式)
        result = await agent.process_learning_request(goal)
        
        # 4. 提取并持久化 Artifacts (A+B+C)
        artifacts = brain_kernel.extract_artifacts(result)
        mysql_storage.save_learning_artifacts(user_id, conversation_id, goal, artifacts)
        
        # 5. 整合输出
        return {
            "reply": result.get("summary", "学习会话已生成"),
            "artifacts": artifacts,
            "full_steps": result.get("steps", [])
        }

    def _build_user_content(
        self,
        goal: str,
        message: str = "",
        context: str = "",
        constraints: str = "",
        time_budget: Optional[str] = None,
        preferred_format: Optional[str] = None,
    ) -> str:
        parts: List[str] = []
        if goal:
            parts.append(f"学习目标: {goal}")
        if message:
            parts.append(f"补充说明: {message}")
        if context:
            parts.append(f"背景信息: {context}")
        if constraints:
            parts.append(f"约束条件: {constraints}")
        if time_budget:
            parts.append(f"时间预算: {time_budget}")
        if preferred_format:
            parts.append(f"偏好输出: {preferred_format}")
        return "\n".join(parts) if parts else "请给出学习方案与练习建议。"

    def _build_messages(
        self,
        goal: str,
        message: str = "",
        username: str = "",
        context: str = "",
        constraints: str = "",
        time_budget: Optional[str] = None,
        preferred_format: Optional[str] = None,
    ) -> List[Dict[str, str]]:
        user_content = self._build_user_content(goal, message, context, constraints, time_budget, preferred_format)
        messages = [
            {"role": "system", "content": settings.LEARN_SYSTEM_PROMPT},
            {"role": "system", "content": settings.LEARN_OUTPUT_GUIDE},
        ]
        if username:
            messages.append({"role": "system", "content": f"学习者：{username}。"})
        messages.append({"role": "user", "content": user_content})
        return messages

    async def handle_learn_request(
        self,
        goal: str,
        message: str = "",
        username: str = "",
        conversation_id: int | None = None,
        context: str = "",
        constraints: str = "",
        time_budget: Optional[str] = None,
        preferred_format: Optional[str] = None,
    ) -> str:
        messages = self._build_messages(goal, message, username, context, constraints, time_budget, preferred_format)
        reply = await get_llm_service().generate_response(messages)
        if username:
            self._save_chat(username, goal or message, reply, conversation_id)
        return reply

    async def handle_stream_learn_request(
        self,
        goal: str,
        message: str = "",
        username: str = "",
        conversation_id: int | None = None,
        context: str = "",
        constraints: str = "",
        time_budget: Optional[str] = None,
        preferred_format: Optional[str] = None,
    ):
        messages = self._build_messages(goal, message, username, context, constraints, time_budget, preferred_format)
        completion = get_llm_service().generate_stream(messages)
        full_response = ""

        async for content in completion:
            if content:
                full_response += content
                yield {
                    "type": "chunk",
                    "content": content,
                    "full_response": full_response,
                }

        yield {
            "type": "end",
            "full_response": full_response,
        }

        if username:
            self._save_chat(username, goal or message, full_response, conversation_id)

    def _save_chat(self, username: str, user_message: str, ai_reply: str, conversation_id: int | None = None):
        chat_messages = [
            {"type": "user", "content": user_message},
            {"type": "ai", "content": ai_reply},
        ]
        existing_messages = user_repo.load_chat(username, conversation_id)
        all_messages = existing_messages + chat_messages
        user_repo.save_chat(username, all_messages, conversation_id)

    async def handle_feedback(self, topic: str, user_answer: str, phase: str = None, session_data: dict = None) -> Dict[str, Any]:
        """处理用户针对任务的回答，生成教练反馈并更新复盘"""
        from app.core.yexiu.coach_agent import CoachAgent
        from app.core.yexiu.review_agent import ReviewAgent
        
        coach = CoachAgent()
        review_agent = ReviewAgent()
        
        # 1. 获取教练反馈
        # 简单从 session_data 找 standard_answer 或直接让 LLM 评判
        standard = ""
        if session_data and "thinking" in session_data:
            standard = str(session_data["thinking"])
            
        coach_feedback = await coach.provide_feedback(user_answer, standard)
        
        # 2. 更新复盘报告 (基于新的互动)
        # 构造包含用户回答的 session_data
        updated_session = session_data or {}
        updated_session.update({
            "topic": topic,
            "user_answer": user_answer,
            "coach_feedback": coach_feedback,
            "phase": phase
        })
        
        review_update = await review_agent.conduct_review(updated_session)
        
        return {
            "coach_feedback": coach_feedback,
            "review_update": review_update
        }


learn_service = LearnService()
