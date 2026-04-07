import json
from typing import Dict, List, Any
from app.services.llm_service import get_llm_service

class ReviewAgent:
    """
    负责学习复盘和优化（基于云心复盘模型）
    """
    async def conduct_review(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        # 策略约束：{policy_str}  # 暂时移除 policy_str 以避免转义问题
        
        prompt = f"""
        你现在是“云心学习系统”中的【复盘师】。
        任务：针对本次学习会话，按照 Policy 要求生成深度复盘报告与结构化产物 (Artifacts)。
        
        会话数据：(数据已省略，直接根据上下文生成)
        
        要求（必须包含 A+B+C）：
        A. 行动项与复习卡：
           - 生成 1-3 条下一步具体行动项 (next_actions)。
           - 生成 2-5 张复习卡片 (review_cards: concept/procedure/pitfall/mistake/template)。
        B. 评分与错因：
           - 评分 (scores): mastery (掌握度), thinking_depth (思考深度) [0-1]。
           - 错因标签 (error_tags): 从 [概念不清, 步骤缺失, 计算粗心, 审题偏差, 迁移失败] 中选择。
        C. KP 更新：
           - 建议本次涉及的知识点 (kp_updates)，key 格式 domain.area.concept。
           - 为每个 KP 提供掌握度 delta 建议及证据。

        格式规范：
        - 所有数学公式必须使用 LaTeX 格式，并用 $ 包裹（行内）或 $$ 包裹（独立）。
        - 文本支持 Markdown。
        - **严禁输出不合法的 JSON 转义字符**。

        请以 JSON 格式输出：
        {{
            "report": {{
                "summary": "会话总结",
                "scores": {{ "mastery": 0.8, "thinking_depth": 0.9 }},
                "error_tags": ["概念不清"],
                "effort": {{ "attempt_quality": 1.0, "self_check_done": 1.0 }}
            }},
            "artifacts": {{
                "next_actions": [{{ "action": "动作", "eta_min": 10 }}],
                "review_cards": [{{ "type": "pitfall", "content": "内容", "source": "来源" }}],
                "kp_updates": [{{ "kp_key": "domain.area.concept", "delta": 0.05, "evidence": "证据" }}]
            }}
        }}
        """
        try:
            # 简化 prompt，移除可能导致转义错误的复杂 JSON 注入
            # 改为让 LLM 直接基于上下文（Conversation History）生成，而不是再次注入 session_data
            
            response = await get_llm_service().generate_response([
                {"role": "system", "content": "你是一个严谨的学习评估专家。请仅输出 JSON 数据。"},
                {"role": "user", "content": f"基于以下会话历史进行复盘：{json.dumps(session_data.get('history', []), ensure_ascii=False)[:2000]}... \n\n {prompt}"}
            ])
            clean_json = response.replace("```json", "").replace("```", "").strip()
            # 尝试修复常见的 JSON 转义错误
            clean_json = clean_json.replace("\\'", "'") 
            result = json.loads(clean_json)
            
            # 兼容性处理
            if "report" in result and "scores" in result["report"]:
                result["scores"] = result["report"]["scores"]
            return result
        except Exception as e:
            print(f"Review LLM failed: {e}")
            return {
                "report": {
                    "summary": "基础复盘",
                    "scores": {"mastery": 0.7, "thinking_depth": 0.6},
                    "error_tags": [],
                    "effort": {"attempt_quality": 0.8, "self_check_done": 0.5}
                },
                "artifacts": {
                    "next_actions": [{"action": "继续坚持练习", "eta_min": 30}],
                    "review_cards": [],
                    "kp_updates": []
                }
            }
