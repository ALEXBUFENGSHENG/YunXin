import json
from typing import Dict, List, Any
from app.services.llm_service import get_llm_service

class DecompositionAgent:
    """
    专门负责系统拆解（基于系统拆解策略）
    """
    async def decompose_knowledge(self, topic: str, policy: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        针对主题进行系统性拆解 (Policy 驱动)
        """
        policy_str = json.dumps(policy, ensure_ascii=False) if policy else "默认通用策略"
        prompt = f"""
        你现在是“学习系统”中的【分解师】。
        任务：针对主题【{topic}】，在策略 Policy 的指导下进行系统性拆解。
        
        策略指导：{policy_str}
        
        要求：
        1. 识别问题本质（一句话概括）。
        2. 拆解为 3-5 个核心维度（核心概念）。
        3. 建议符合策略规范的知识点 Key (kp_keys)，命名格式如 domain.area.concept。
        4. 构建知识体系树。
        5. 评估难度梯度与建议顺序。

        请以 JSON 格式输出：
        {{
            "本质": "本质描述",
            "核心概念": ["概念1", "概念2", ...],
            "kp_keys": ["math.calculus.derivative", ...],
            "知识体系": {{
                "root": "{topic}",
                "branches": {{
                    "基础层": ["点1", "点2"],
                    "应用层": ["点1", "点2"],
                    "拓展层": ["点1", "点2"]
                }}
            }},
            "关联网络": ["关联领域1", "关联领域2"],
            "难度梯度": {{"入门": "描述", "进阶": "描述", "精通": "描述"}},
            "学习路径": ["步骤1", "步骤2", "步骤3"]
        }}
        """
        
        try:
            response = await get_llm_service().generate_response([
                {"role": "system", "content": "你是一个严谨的知识架构师。请仅输出 JSON 数据。"},
                {"role": "user", "content": prompt}
            ])
            # 简单清理可能存在的 markdown 标记
            clean_json = response.replace("```json", "").replace("```", "").strip()
            decomposition = json.loads(clean_json)
        except Exception as e:
            print(f"Decomposition LLM failed: {e}")
            # 回退到基础数据结构，避免崩溃
            decomposition = {
                "核心概念": [f"{topic}基础", f"{topic}应用"],
                "知识体系": {"root": topic, "branches": {"基础层": ["定义"], "应用层": ["实践"], "拓展层": ["进阶"]}},
                "关联网络": [],
                "难度梯度": {"入门": "初识", "进阶": "掌握", "精通": "专家"},
                "学习路径": ["学习基础", "进行实践"]
            }

        return decomposition
    
    def format_as_text(self, decomposition: Dict[str, Any]) -> str:
        return f"关于 {decomposition['知识体系']['root']} 的分解:\n" + \
               f"- 核心概念: {', '.join(decomposition['核心概念'])}\n" + \
               f"- 学习路径: {' -> '.join(decomposition['学习路径'])}"

    def generate_mind_map(self, decomposition: Dict[str, Any]) -> Dict[str, Any]:
        return {"root": decomposition["知识体系"]["root"], "children": decomposition["核心概念"]}

    def create_learning_timeline(self, decomposition: Dict[str, Any]) -> List[str]:
        return [f"第{i+1}阶段: {step}" for i, step in enumerate(decomposition.get("学习路径", []))]
