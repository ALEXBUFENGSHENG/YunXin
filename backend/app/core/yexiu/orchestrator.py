from typing import Dict, Any, List
import asyncio

from .decomposition_agent import DecompositionAgent
from .thinking_agent import ThinkingAgent
from .coach_agent import CoachAgent
from .review_agent import ReviewAgent
from .strategy_agent import StrategyAgent

class YeXiuLearningAgent:
    """
    主Agent：协调多个子Agent完成学习任务
    """
    def __init__(self, user_profile: Dict[str, Any] = None):
        self.user_profile = user_profile or {}
        self.agents = {
            "分解师": DecompositionAgent(),
            "思考师": ThinkingAgent(),
            "教练": CoachAgent(),
            "复盘师": ReviewAgent(),
            "策略师": StrategyAgent()
        }
        
    async def process_learning_request(self, request: str) -> Dict[str, Any]:
        # 1. 分析请求类型
        request_type = self.classify_request(request)
        
        # 2. 调用相应Agent链
        if request_type == "数学学习":
            return await self.math_learning_flow(request)
        elif request_type == "知识学习":
            return await self.knowledge_learning_flow(request)
        elif request_type == "问题解决":
            return await self.problem_solving_flow(request)
        elif request_type == "技能训练":
            return await self.skill_training_flow(request)
        else:
            # Default to knowledge learning for now
            return await self.knowledge_learning_flow(request)
            
    async def math_learning_flow(self, topic: str) -> Dict[str, Any]:
        """专门针对考研数学的闭环学习流程"""
        steps = []
        # 教练：根据今日任务和进度给出指导
        path = await self.agents["教练"].design_learning_path(
            {"topic": topic, "domain": "math"}, self.user_profile
        )
        steps.append({"agent": "教练", "output": path})
        # 分解师：对当下的具体数学难题或概念进行拆解
        decomposition = await self.agents["分解师"].decompose_knowledge(topic)
        steps.append({"agent": "分解师", "output": decomposition})
        return self.integrate_results(steps)
            
    async def knowledge_learning_flow(self, topic: str) -> Dict[str, Any]:
        """知识学习的多Agent协作流程 (云心大脑 Policy 驱动)"""
        steps = []
        
        # 1. 策略师：前置生成 Policy
        policy = await self.agents["策略师"].generate_policy(topic, self.user_profile)
        steps.append({"agent": "策略师", "output": policy})
        
        # 2. 分解师：按 Policy 拆解知识结构
        decomposition = await self.agents["分解师"].decompose_knowledge(topic, policy)
        steps.append({"agent": "分解师", "output": decomposition})
        
        # 3. 思考师：按 Policy 进行深度理解
        thinking = await self.agents["思考师"].deep_understanding(decomposition, policy)
        steps.append({"agent": "思考师", "output": thinking})
        
        # 4. 教练：按 Policy 设计学习路径与交互任务
        path = await self.agents["教练"].design_learning_path(
            thinking, self.user_profile, policy
        )
        steps.append({"agent": "教练", "output": path})
        
        # 5. 复盘师：生成复盘报告与 Artifacts
        review_data = await self.agents["复盘师"].conduct_review({
            "topic": topic,
            "steps": steps,
            "policy": policy
        })
        steps.append({"agent": "复盘师", "output": review_data})
        
        return self.integrate_results(steps)

    async def stream_learning_process(self, request: str, mode: str = "learn"):
        """流式执行学习流程"""
        print(f"[Orchestrator] Received request: '{request}', Mode: {mode}") # DEBUG LOG
        yield {"type": "chunk", "content": "正在分析学习请求类型...\n"}
        request_type = self.classify_request(request)
        print(f"[Orchestrator] Classified as: {request_type}") # DEBUG LOG
        
        # 优先处理显式指定的 mode
        if mode == "learn" and request_type == "知识学习":
             # 已经是默认行为
             pass
        
        if request_type == "数学学习":
            print("[Orchestrator] Entering Math Flow") # DEBUG LOG
            async for event in self.stream_math_learning_flow(request):
                yield event
        elif request_type == "知识学习" or mode == "learn":
            print("[Orchestrator] Entering Knowledge Flow") # DEBUG LOG
            async for event in self.stream_knowledge_learning_flow(request):
                yield event
        else:
            print("[Orchestrator] Entering Fallback Flow") # DEBUG LOG
            yield {"type": "chunk", "content": f"正在处理{request_type}请求..."}
            # Fallback to standard flow but wrapped in stream
            result = await self.process_learning_request(request)
            yield {"type": "chunk", "content": str(result)}

    async def stream_math_learning_flow(self, topic: str):
        """数学学习的流式交互 (增强版：路径可视化+评分+诊断+引导)"""
        try:
            # 1. 思考引导 (Coach)
            yield {"type": "agent_start", "agent": "教练", "status": "working"}
            yield {"type": "chunk", "content": "正在启动‘云心深度思考模型’进行题目解析与思路引导...\n"}
            
            # 构造策略，指示 Coach 生成解题引导
            coach_policy = {
                "session_mode": "problem_solving", 
                "domain": "math",
                "instruction": "请分析此数学问题的解题思路。first_step_guide 应给出起手式提示；tasks 应为解题步骤；time_allocation 应为各步骤建议用时。"
            }
            path = await self.agents["教练"].design_learning_path(
                thinking_result={"topic": topic}, # 简化传入
                user_profile=self.user_profile,
                policy=coach_policy
            )
            yield {"type": "agent_data", "agent": "教练", "data": path}
            
            guide_text = path.get("first_step_guide") or "让我们开始解题。"
            yield {"type": "chunk", "content": f"### 💡 思路引导\n\n{guide_text}\n\n"}
            
            # 2. 解题路径可视化 (Decomposition)
            yield {"type": "agent_start", "agent": "分解师", "status": "working"}
            yield {"type": "chunk", "content": "正在构建解题路径知识图谱...\n"}
            
            # 构造策略，指示 Decomposition 生成解题步骤图
            decomp_policy = {
                "focus": "solution_path",
                "instruction": "请将该数学问题的解题过程拆解为关键步骤节点。'核心概念'即为关键步骤或定理；'知识体系'展示步骤间的逻辑依赖。"
            }
            decomposition = await self.agents["分解师"].decompose_knowledge(topic, policy=decomp_policy)
            yield {"type": "agent_data", "agent": "分解师", "data": decomposition}
            yield {"type": "chunk", "content": f"✅ 解题路径已生成，包含 {len(decomposition.get('核心概念', []))} 个关键节点。\n\n"}
            
            # 3. 步骤评分与错误诊断 (Review)
            yield {"type": "agent_start", "agent": "复盘师", "status": "working"}
            yield {"type": "chunk", "content": "正在进行步骤评分与易错点诊断...\n"}
            
            review_data = await self.agents["复盘师"].conduct_review({
                "topic": topic,
                "history": [{"role": "user", "content": topic}],
                "path": path,
                "decomposition": decomposition
            })
            
            # 增强 Review 数据以包含“步骤评分” (如果 LLM 没生成，我们手动构造一些默认值演示)
            if "scores" not in review_data.get("report", {}):
                 review_data.setdefault("report", {})["scores"] = {
                     "逻辑严密性": 0.0, # 初始为0，等待用户交互
                     "计算准确度": 0.0,
                     "步骤完整性": 0.0
                 }
            
            yield {"type": "agent_data", "agent": "复盘师", "data": review_data}
            
            # 输出诊断信息
            error_tags = review_data.get("report", {}).get("error_tags", [])
            if error_tags:
                yield {"type": "chunk", "content": f"### ⚠️ 错误诊断与预警\n\n系统检测到以下潜在易错点：{', '.join(error_tags)}\n\n"}
            
            summary = review_data.get("report", {}).get("summary", "")
            if summary:
                 yield {"type": "chunk", "content": f"### 📝 综合点评\n\n{summary}\n"}

            yield {"type": "chunk", "content": "[DONE]"}
        except Exception as e:
            print(f"Math Flow Error: {e}")
            import traceback
            traceback.print_exc()
            yield {"type": "error", "message": f"数学模式运行出错: {str(e)}"}
            yield {"type": "chunk", "content": "[DONE]"}

    async def stream_knowledge_learning_flow(self, topic: str):
        try:
            # 0. 策略师：生成会话策略
            yield {"type": "agent_start", "agent": "策略师", "status": "working"}
            yield {"type": "chunk", "content": f"🧠 正在根据‘云心学习法’为主题【{topic}】制定深度学习策略...\n"}
            policy = await self.agents["策略师"].generate_policy(topic, self.user_profile)
            yield {"type": "agent_data", "agent": "策略师", "data": policy}
            yield {"type": "chunk", "content": f"✅ 策略生成：模式【{policy.get('session_mode', 'learn')}】，风格【{policy.get('teaching_style', 'socratic')}】。\n\n"}

            # 1. 分解师
            yield {"type": "agent_start", "agent": "分解师", "status": "working"}
            yield {"type": "chunk", "content": f"🔍 正在进行系统性拆解...\n"}
            decomposition = await self.agents["分解师"].decompose_knowledge(topic, policy)
            yield {"type": "agent_data", "agent": "分解师", "data": decomposition}
            yield {"type": "chunk", "content": f"✅ 识别出 {len(decomposition.get('核心概念', []))} 个核心维度：{', '.join(decomposition.get('核心概念', []))}。\n\n"}
            
            # 2. 思考师
            yield {"type": "agent_start", "agent": "思考师", "status": "working"}
            yield {"type": "chunk", "content": "💡 正在启动深度思考模型，挖掘底层原理与坑点...\n"}
            thinking = await self.agents["思考师"].deep_understanding(decomposition, policy)
            yield {"type": "agent_data", "agent": "思考师", "data": thinking}
            yield {"type": "chunk", "content": f"✅ 深度洞察完成，识别出 {len(thinking.get('key_insights', []))} 个关键点。\n\n"}
            
            # 3. 教练
            yield {"type": "agent_start", "agent": "教练", "status": "working"}
            yield {"type": "chunk", "content": "🚀 正在为您定制行动路径...\n"}
            path = await self.agents["教练"].design_learning_path(thinking, self.user_profile, policy)
            yield {"type": "agent_data", "agent": "教练", "data": path}
            
            # 输出教练的引导语，这是最关键的交互内容
            guide = path.get("first_step_guide") or "准备好了吗？我们开始第一步。"
            yield {"type": "chunk", "content": f"\n### 📝 学习计划已就绪\n\n{guide}\n\n"}
            
            # 4. 复盘师 (预演)
            yield {"type": "agent_start", "agent": "复盘师", "status": "working"}
            review_data = await self.agents["复盘师"].conduct_review({
                "topic": topic, 
                "path": path, 
                "thinking": thinking,
                "policy": policy
            })
            yield {"type": "agent_data", "agent": "复盘师", "data": review_data}
            
            yield {"type": "chunk", "content": "[DONE]"}
        except Exception as e:
            print(f"Stream Flow Error: {e}")
            import traceback
            traceback.print_exc()
            yield {"type": "error", "message": f"处理过程中发生错误: {str(e)}"}
            yield {"type": "chunk", "content": f"\n\n⚠️ **系统错误**: 智能体协作过程中遇到问题 ({str(e)})，请稍后重试。\n"}
            yield {"type": "chunk", "content": "[DONE]"}

    async def problem_solving_flow(self, request: str) -> Dict[str, Any]:
        # Placeholder for problem solving flow
        return {"result": "Problem solving flow executed"}

    async def skill_training_flow(self, request: str) -> Dict[str, Any]:
        # Placeholder for skill training flow
        return {"result": "Skill training flow executed"}

    def classify_request(self, request: str) -> str:
        req_lower = request.lower()
        if any(kw in req_lower for kw in ["数学", "数一", "数二", "数三", "高数", "线代", "概率", "微积分", "导数", "极限", "矩阵"]):
            return "数学学习"
        if any(kw in req_lower for kw in ["学习", "了解", "掌握", "是什么", "怎么理解", "原理解析"]):
            return "知识学习"
        elif any(kw in req_lower for kw in ["解决", "怎么办", "报错", "修复"]):
            return "问题解决"
        elif any(kw in req_lower for kw in ["练习", "训练", "题目", "作业"]):
            return "技能训练"
        return "知识学习"

    def integrate_results(self, steps: List[Dict[str, Any]]) -> Dict[str, Any]:
        return {
            "final_output": steps[-1]["output"],
            "steps": steps,
            "summary": "Learning session prepared successfully."
        }
