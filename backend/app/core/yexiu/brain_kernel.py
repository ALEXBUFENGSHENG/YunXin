import re
import json
from typing import Dict, List, Any, Optional

class BrainKernel:
    """
    学习大脑核心引擎：处理 KP 验证、掌握度计算、Artifacts 提取
    """
    
    KP_KEY_PATTERN = re.compile(r'^[a-z0-9_]{2,32}\.[a-z0-9_]{2,32}\.[a-z0-9_]{2,80}$')
    
    @classmethod
    def validate_kp_key(cls, kp_key: str) -> bool:
        """验证 KP Key 命名规范: domain.area.concept"""
        return bool(cls.KP_KEY_PATTERN.match(kp_key))

    @classmethod
    def calculate_mastery_delta(cls, 
                                scores: Dict[str, float], 
                                effort: Dict[str, float], 
                                error_tags: List[str],
                                has_review_card: bool = False) -> float:
        """
        方案 B: 掌握度更新公式
        Δ = Δ_score + Δ_effort + Δ_error + Δ_review
        """
        # 1. 基础增量 (s - 0.6) * 0.08
        mastery_score = scores.get("mastery", 0.6)
        delta_score = 0.08 * (mastery_score - 0.6)
        
        # 2. 高强度思考奖励
        # attempt_quality (0-1), self_check_done (0-1)
        attempt_q = effort.get("attempt_quality", 0)
        self_check = effort.get("self_check_done", 0)
        delta_effort = 0.04 * attempt_q + 0.03 * self_check
        
        # 3. 错因惩罚
        error_weights = {
            "概念不清": 0.06,
            "审题偏差": 0.04,
            "步骤缺失": 0.03,
            "迁移失败": 0.03,
            "计算粗心": 0.015,
            "表达不清": 0.015
        }
        delta_error = -sum(error_weights.get(tag, 0.02) for tag in error_tags)
        
        # 4. 复习触发修正
        delta_review = -0.02 if has_review_card else 0
        
        total_delta = delta_score + delta_effort + delta_error + delta_review
        
        # 限制单次波动
        return max(-0.12, min(0.08, total_delta))

    @classmethod
    def extract_artifacts(cls, session_output: Dict[str, Any]) -> Dict[str, Any]:
        """
        从会话输出中提取结构化 Artifacts (A+B+C)
        """
        # 寻找 ReviewAgent 的输出
        review_data = {}
        for step in session_output.get("steps", []):
            if step.get("agent") == "复盘师":
                review_data = step.get("output", {})
                break
        
        report = review_data.get("report", {})
        arts = review_data.get("artifacts", {})
        
        return {
            "scores": report.get("scores", {"mastery": 0.6, "thinking_depth": 0.6}),
            "error_tags": report.get("error_tags", []),
            "effort": report.get("effort", {"attempt_quality": 0, "self_check_done": 0}),
            "next_actions": arts.get("next_actions", []),
            "review_cards": arts.get("review_cards", []),
            "kp_updates": arts.get("kp_updates", [])
        }

brain_kernel = BrainKernel()
