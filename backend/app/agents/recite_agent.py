from typing import Generator, List, Dict, Optional
from app.config.settings import settings
from app.services.llm_service import get_llm_service
from app.repositories.user_repo import user_repo
from app.spaced_memory import SpacedRepetitionScheduler, initialize_database


class ReciteAgent:
    """背诵模式智能体：负责从数据库获取背诵内容、提供口语化引导并记录复习。"""

    def __init__(self):
        self.llm = get_llm_service()
        self.scheduler = SpacedRepetitionScheduler()
        initialize_database(seed=False)

    def _get_user_id(self, username: str) -> Optional[int]:
        if not username:
            return None
        return user_repo.get_user_id(username)

    def _format_queue(self, words: List[Dict]) -> str:
        lines: List[str] = []
        for w in words:
            word = w.get("word") or w.get("word_text") or w.get("spelling") or w.get("content") or ""
            pronunciation = w.get("pronunciation") or w.get("pronounce") or ""
            definition = w.get("definition") or w.get("meaning") or w.get("translation") or ""
            example = w.get("example") or w.get("example_sentence") or ""
            line = f"{word} [{pronunciation}] - {definition}".strip()
            if example:
                line += f"\n例句: {example}"
            lines.append(line.strip())
        return "\n".join(lines)

    def _build_messages(self, message: str, username: str = ""):
        user_id = self._get_user_id(username)
        queue = self.scheduler.get_today_review_queue(user_id, limit=3) if user_id else []
        messages = [
            {"role": "system", "content": settings.RECITE_SYSTEM_PROMPT},
            {"role": "system", "content": settings.RECITE_OUTPUT_GUIDE},
        ]
        if queue:
            messages.append({
                "role": "system",
                "content": "今日复习/新词候选（供生成内容引用，按需取1-3个即可）：\n" + self._format_queue(queue),
            })
        else:
            messages.append({
                "role": "system",
                "content": "当前未找到待复习单词，可根据用户输入给出背诵/跟读引导，或提示用户添加词汇。",
            })
        if username:
            messages.append({"role": "system", "content": f"学习者：{username}。保持鼓励式口语引导，注意放慢语速。"})
        messages.append({"role": "user", "content": message})
        return messages

    async def chat(self, message: str, username: str = "", conversation_id: int | None = None) -> str:
        messages = self._build_messages(message, username)
        reply = await self.llm.generate_response(messages)
        if username:
            self._save_chat(username, message, reply, conversation_id)
        return reply

    async def stream(self, message: str, username: str = "", conversation_id: int | None = None) -> Generator[dict, None, None]:
        messages = self._build_messages(message, username)
        completion = self.llm.generate_stream(messages)
        full_response = ""

        async for content in completion:
            if content:
                full_response += content
                yield {
                    "type": "chunk",
                    "content": content,
                    "full_response": full_response,
                }

        yield {"type": "end", "full_response": full_response}

        if username:
            self._save_chat(username, message, full_response, conversation_id)

    def record_review(self, username: str, word_id: int, score: int, interaction_type: str = "recite_agent", response_time_ms: int | None = None):
        user_id = self._get_user_id(username)
        if not user_id:
            return
        self.scheduler.record_review(user_id, word_id, score, interaction_type, response_time_ms)

    def _save_chat(self, username: str, user_message: str, ai_reply: str, conversation_id: int | None = None):
        chat_messages = [
            {"type": "user", "content": user_message},
            {"type": "ai", "content": ai_reply},
        ]
        existing_messages = user_repo.load_chat(username, conversation_id)
        all_messages = existing_messages + chat_messages
        user_repo.save_chat(username, all_messages, conversation_id)


recite_agent = ReciteAgent()
