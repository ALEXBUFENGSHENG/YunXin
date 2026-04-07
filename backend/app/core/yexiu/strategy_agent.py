import json
from typing import Dict, List, Any
from app.services.llm_service import get_llm_service

class StrategyAgent:
    """
    负责制定和优化学习策略（基于云心策略模型）
    """
    async def generate_policy(self, topic: str, user_profile: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        根据主题和用户画像生成会话策略 (Policy)
        """
        prompt = f"""
        你现在是“云心学习系统”中的【大脑/策略师】。
        任务：针对主题【{topic}】，制定本次 30 分钟学习会话的控制策略 (Policy)。
        
        要求：
        1. 必须遵循“以用户为中心”和“高强度思考引导”原则。
        2. 强制用户先产出 (user_must_attempt_first: true)。
        3. 设定 30 分钟的 4 阶段时间分配 (诊断、深思、练习、复盘)。
        4. 规定必须沉淀的 artifacts 类型。

        请以 JSON 格式输出，严格遵守以下 Schema：
        {{
          "time_budget_min": 30,
          "session_mode": "learn|math|recite|code",
          "high_intensity": true,
          "teaching_style": "socratic|scaffold|demo_then_practice",
          "answer_policy": {{
            "user_must_attempt_first": true,
            "hint_levels": ["direction", "key_step", "half_solution", "full_solution"],
            "max_full_solution_before_attempt": 0
          }},
          "loop_plan": [
            {{"phase": "diagnose", "min": 5}},
            {{"phase": "deep_think", "min": 10}},
            {{"phase": "deliberate_practice", "min": 10}},
            {{"phase": "review_and_save", "min": 5}}
          ],
          "artifact_policy": {{
            "must_save": ["next_actions", "review_cards", "error_tags", "scores", "kp_updates"],
            "review_card_types": ["concept", "procedure", "pitfall", "template", "mistake"]
          }},
          "kp_policy": {{
            "naming_convention": "domain.area.concept",
            "max_new_kp": 5
          }}
        }}
        """
        try:
            response = await get_llm_service().generate_response([
                {"role": "system", "content": "你是一个精通认知科学与云心学习法的策略大脑。请仅输出 JSON 数据。"},
                {"role": "user", "content": prompt}
            ])
            clean_json = response.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_json)
        except Exception as e:
            print(f"Strategy Policy LLM failed: {e}")
            return {
                "time_budget_min": 30,
                "session_mode": "learn",
                "high_intensity": True,
                "teaching_style": "socratic",
                "answer_policy": {"user_must_attempt_first": True, "hint_levels": ["direction", "full_solution"]},
                "loop_plan": [{"phase": "general", "min": 30}],
                "artifact_policy": {"must_save": ["next_actions", "review_cards", "scores"]}
            }

    async def optimize_strategy(self, current_strategy: Dict[str, Any], performance_data: Dict[str, Any] = None) -> Dict[str, Any]:

        # 简单优化逻辑，实际可基于LLM
        return current_strategy

