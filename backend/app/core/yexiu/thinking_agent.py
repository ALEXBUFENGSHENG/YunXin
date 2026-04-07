import json
from typing import Dict, List, Any
from app.services.llm_service import get_llm_service

class ThinkingAgent:
    """
    负责深度思考和多角度分析（基于深度思考模型）
    """
    async def deep_understanding(self, decomposition: Dict[str, Any], policy: Dict[str, Any] = None) -> Dict[str, Any]:
        topic = decomposition.get("知识体系", {}).get("root", "未知主题")
        core_concepts = decomposition.get("核心概念", [])
        policy_str = json.dumps(policy, ensure_ascii=False) if policy else "默认深度思考策略"
        
        prompt = f"""
        你现在是“学习系统”中的【思考师】。
        任务：针对主题【{topic}】及其核心概念【{', '.join(core_concepts)}】，在策略 Policy 指导下进行深度思考。
        
        策略指导：{policy_str}
        
        要求：
        1. 多角度分析：从理论、实践、本质、关联等维度深入剖析。
        2. 追问链条（5层）：模拟“打破砂锅问到底”的过程，直达第一性原理。
        3. 思维模式匹配：识别最适合该知识的思维模型。
        4. 提取关键洞察：总结 3 个最核心、最能触及本质的观点。
        5. 识别常见坑点 (pitfalls)：为复习卡片提供素材。

        请以 JSON 格式输出：
        {{
            "thinking_process": [
                {{"perspective": "维度名称", "insights": "深入见解"}}
            ],
            "questioning_chain": [
                {{"level": 1, "question": "追问1", "answer": "回答1"}}
            ],
            "thinking_models": ["模型1", "模型2"],
            "key_insights": ["核心洞察1", "核心洞察2", "核心洞察3"],
            "common_pitfalls": ["常见坑点1", "常见坑点2"]
        }}
        """


        try:
            response = await get_llm_service().generate_response([
                {"role": "system", "content": "你是一个善于挖掘本质的哲学家和科学家。请仅输出 JSON 数据。"},
                {"role": "user", "content": prompt}
            ])
            clean_json = response.replace("```json", "").replace("```", "").strip()
            result = json.loads(clean_json)
        except Exception as e:
            print(f"Thinking LLM failed: {e}")
            # 回退逻辑
            result = {
                "thinking_process": [{"perspective": "理论", "insights": "基础理论支撑"}],
                "questioning_chain": [{"level": 1, "question": f"为什么学习{topic}？", "answer": "为了提升能力"}],
                "thinking_models": ["系统思维"],
                "key_insights": ["实践出真知"]
            }

        return result
