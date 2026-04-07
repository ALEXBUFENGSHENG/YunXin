from app.services.learn_service import learn_service
from app.core.yexiu.orchestrator import YeXiuLearningAgent
from app.repositories.user_repo import user_repo
import json

class LearnAgent:
    """学习模式智能体，负责学习方案生成与练习反馈。"""
    
    def __init__(self):
        self.yexiu_agent = YeXiuLearningAgent()

    async def chat(
        self,
        goal: str,
        message: str = "",
        username: str = "",
        conversation_id: int | None = None,
        context: str = "",
        constraints: str = "",
        time_budget: str | None = None,
        preferred_format: str | None = None,
    ) -> str:
        response = ""
        try:
            yexiu_data = await learn_service.handle_yexiu_learn(
                goal=goal or message,
                username=username,
                conversation_id=conversation_id
            )
            
            artifacts = yexiu_data.get("artifacts", {})
            full_steps = yexiu_data.get("full_steps", [])
            
            # 构建精美的 Markdown 总结
            response = f"## 🎓 大脑方案：{goal or message}\n\n"
            
            decomposition = next((s['output'] for s in full_steps if s['agent'] == '分解师'), {})
            thinking = next((s['output'] for s in full_steps if s['agent'] == '思考师'), None)
            path = next((s['output'] for s in full_steps if s['agent'] == '教练'), {})
            
            if decomposition:
                response += "### 1. 核心拆解\n"
                response += f"- **本质**：{decomposition.get('本质', '进行深度解析中')}\n"
                response += f"- **核心维度**：{', '.join(decomposition.get('核心概念', []))}\n\n"
            
            if thinking:
                response += "### 2. 深度见解\n"
                for insight in thinking.get('key_insights', [])[:2]:
                    response += f"- 💡 {insight}\n"
            elif decomposition.get('学习路径'):
                 response += "### 2. 学习路径建议\n"
                 for p in decomposition.get('学习路径', [])[:3]:
                     response += f"- 📍 {p}\n"
            
            if path:
                response += "### 3. 个性化执行建议\n"
                response += f"- **教学风格**：{path.get('style', '引导式')}\n"
                
                # 优先使用 tasks (List[Dict])，其次兼容 steps (List[str])
                tasks = path.get('tasks', [])
                steps = path.get('steps', [])
                
                display_items = []
                if tasks and isinstance(tasks, list):
                    # 提取 description 或直接使用
                    display_items = [t.get('description', str(t)) if isinstance(t, dict) else str(t) for t in tasks]
                elif steps:
                    display_items = steps
                    
                for step in display_items[:3]:
                    response += f"- 🚀 {step}\n"
            
            if artifacts.get("review_cards"):
                response += "\n### 4. 记忆沉淀\n"
                response += f"- 已生成 **{len(artifacts['review_cards'])}** 张复习卡片进入 SM-2 队列。\n"
                response += f"- 涉及知识点：{', '.join([kp['kp_key'] for kp in artifacts.get('kp_updates', [])])}\n"

            response += "\n\n> 💡 学习计划已就绪，请按第一步开始产出。"

        except Exception as e:
            print(f"YeXiu logic failed, fallback to base: {e}")
            response = await learn_service.handle_learn_request(
                goal, message, username, conversation_id, context, constraints, time_budget, preferred_format
            )
        if username:
            user_message = goal or message
            user_repo.add_message(username, "user", user_message, conversation_id)
            user_repo.add_message(username, "ai", response, conversation_id)
        return response

    def stream(
        self,
        goal: str,
        message: str = "",
        username: str = "",
        conversation_id: int | None = None,
        context: str = "",
        constraints: str = "",
        time_budget: str | None = None,
        preferred_format: str | None = None,
        mode: str = "learn"
    ):
        # Use YeXiu agent for streaming if possible
        # This wrapper makes it an async generator compatible with the endpoint
        async def generator():
            try:
                # Use goal or message as the topic
                topic = goal or message
                async for event in self.yexiu_agent.stream_learning_process(topic, mode=mode):
                    yield event
            except Exception as e:
                yield {"type": "error", "message": str(e)}

        return generator()


learn_agent = LearnAgent()
