from typing import Dict, Any, List, Optional
from .base import AgentContext, AgentResult, BaseAgent
from app.core.yexiu.decomposition_agent import DecompositionAgent as LegacyDecompositionAgent
from app.core.yexiu.coach_agent import CoachAgent as LegacyCoachAgent
from app.core.yexiu.review_agent import ReviewAgent as LegacyReviewAgent
import json

class LearningChain(BaseAgent):
    """
    学习链路 Agent：串联分解、规划、复盘逻辑
    Goal -> Decompose -> Plan -> Review
    """
    
    def __init__(self):
        # 复用现有 Agent 逻辑
        self.decomposer = LegacyDecompositionAgent()
        self.coach = LegacyCoachAgent()
        self.reviewer = LegacyReviewAgent()
        
    async def run(self, context: AgentContext) -> AgentResult:
        """执行完整的学习闭环"""
        topic = context.user_input
        user_id = context.user_id
        
        # 1. 任务分解 (Decompose)
        decomposition = await self.decomposer.decompose_knowledge(topic)
        
        # 2. 路径规划 (Coach)
        # 这里为了简化，假设 thinking_result 就是 decomposition 的一部分
        # 实际场景可以增加一个 ThinkingAgent 环节
        user_profile = {"id": user_id, "level": "unknown"} # 占位
        plan = await self.coach.design_learning_path(decomposition, user_profile)
        
        # 3. 模拟执行结果 (Execute - 暂略，实际交互中会分步执行)
        # 这里直接生成复盘，模拟"一次性"生成完整方案的场景
        session_data = {
            "topic": topic,
            "decomposition": decomposition,
            "plan": plan,
            "user_performance": "user requested a plan"
        }
        
        # 4. 复盘生成 (Review)
        review = await self.reviewer.conduct_review(session_data)
        
        # 5. 组装最终结果
        final_output = self._format_output(topic, decomposition, plan, review)
        
        return AgentResult(
            content=final_output,
            data={
                "decomposition": decomposition,
                "plan": plan,
                "review": review
            },
            next_action="WAIT_USER_EXECUTION"
        )
        
    def _format_output(self, topic: str, decomposition: Dict, plan: Dict, review: Dict) -> str:
        """生成 Markdown 格式的响应"""
        response = f"## 🎓 学习方案：{topic}\n\n"
        
        # 1. 核心拆解
        response += "### 1. 核心拆解\n"
        response += f"- **本质**：{decomposition.get('本质', '进行深度解析中')}\n"
        response += f"- **核心维度**：{', '.join(decomposition.get('核心概念', []))}\n\n"
        
        # 2. 学习路径
        if plan:
            response += "### 2. 个性化执行建议\n"
            response += f"- **教学风格**：{plan.get('style', '引导式')}\n"
            
            tasks = plan.get('tasks', [])
            steps = plan.get('steps', [])
            
            display_items = []
            if tasks and isinstance(tasks, list):
                display_items = [t.get('description', str(t)) if isinstance(t, dict) else str(t) for t in tasks]
            elif steps:
                display_items = steps
                
            for step in display_items[:3]:
                response += f"- 🚀 {step}\n"
        
        # 3. 记忆复盘
        artifacts = review.get("artifacts", {})
        if artifacts.get("review_cards"):
            response += "\n### 3. 记忆沉淀\n"
            response += f"- 已生成 **{len(artifacts['review_cards'])}** 张复习卡片进入 SM-2 队列。\n"
            
        response += "\n\n> 💡 系统已根据“策略”为您生成学习路径，请按第一步开始执行。"
        return response
