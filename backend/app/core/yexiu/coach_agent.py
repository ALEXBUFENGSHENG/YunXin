import json
from typing import Dict, List, Any
from app.services.llm_service import get_llm_service

class CoachAgent:
    """
    负责学习过程指导和反馈（基于教练模型）
    """
    async def design_learning_path(self, thinking_result: Dict[str, Any], user_profile: Dict[str, Any], policy: Dict[str, Any] = None) -> Dict[str, Any]:
        policy_str = json.dumps(policy, ensure_ascii=False) if policy else "默认教练引导策略"
        prompt = f"""
        你现在是“学习系统”中的【教练】。
        任务：根据思考师产出、用户画像和策略 Policy，设计个性化 30 分钟学习路径。
        
        思考产出：{json.dumps(thinking_result, ensure_ascii=False)}
        用户画像：{json.dumps(user_profile, ensure_ascii=False)}
        策略 Policy：{policy_str}

        要求：
        1. 严格遵守 Policy 中的 answer_policy（如：必须用户先尝试）。
        2. 将 30 分钟拆解为具体可执行的任务块。
        3. 明确每个任务的交付物（用户需要写出/说出什么）。
        4. 设计引导语：如何引导用户开始第一步思考。

        请以 JSON 格式输出：
        {{
            "path_type": "路径名称",
            "time_allocation": {{ "诊断": 5, "深思": 10, "练习": 10, "复盘": 5 }},
            "tasks": [
                {{ "phase": "任务阶段", "description": "描述", "deliverable": "用户需产出内容", "hint": "脚手架提示" }}
            ],
            "style": "推荐风格",
            "first_step_guide": "引导语"
        }}
        """
        try:
            response = await get_llm_service().generate_response([
                {"role": "system", "content": "你是一个极具洞察力的导师。请仅输出 JSON 数据。"},
                {"role": "user", "content": prompt}
            ])
            clean_json = response.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_json)
        except Exception as e:
            print(f"Coach LLM failed: {e}")
            return {
                "path_type": "标准路径",
                "tasks": [
                    {"phase": "阶段一", "description": "初步了解基础概念", "deliverable": "概念笔记"},
                    {"phase": "阶段二", "description": "深入实践案例", "deliverable": "代码片段"},
                    {"phase": "阶段三", "description": "总结提升与复盘", "deliverable": "复盘报告"}
                ],
                "style": "引导式",
                "first_step_guide": "让我们先从了解基础概念开始吧。"
            }

    async def coach_learning_session(self, user_input: str, user_state: Dict[str, Any]) -> str:
        # 简单包装，实际对话可更复杂
        prompt = f"作为教练，如何指导用户：{user_input}？当前状态：{user_state}"
        return await get_llm_service().generate_response([{"role": "user", "content": prompt}])
    
    async def provide_feedback(self, user_answer: str, standard_answer: str) -> Dict[str, Any]:
        prompt = f"""
        针对用户回答【{user_answer}】和标准参考【{standard_answer}】，提供云心式反馈（包含结果、过程评价、改进建议）。
        
        要求：
        1. 使用 Markdown 格式。
        2. 数学公式必须使用 LaTeX 格式，并用 $ 包裹（行内公式）或 $$ 包裹（独立公式）。例如：$E=mc^2$。
        3. 输出 JSON 格式，包含 "feedback" 字段。
        """
        try:
            response = await get_llm_service().generate_response([{"role": "user", "content": prompt}])
            clean_json = response.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_json)
        except:
            return {"feedback": "做得好！"}
