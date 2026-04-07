import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """应用配置"""
    # 应用配置
    APP_NAME: str = "AI 课程助教 API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # 数据库配置
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DB_NAME: str = "ai_assistant"
    
    # LLM 配置
    LLM_API_KEY: str = ""
    LLM_BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    LLM_MODEL: str = "qwen-plus"
    LLM_TEMPERATURE: float = 0.7
    
    # CORS 配置
    CORS_ORIGINS: list = ["*"]
    
    # 系统提示词
    SYSTEM_PROMPT: str = """
    你是一个创智云程助教Agent。
    你的目标是：
    - 回答学生关于课程方面的问题
    - 回答要通俗、准确、可教学的内容
    规则：
    - 不编造事实
    - 不确定时明确说明
    - 优先用例子解释
    - 回答控制在学生能理解的层级
    """

    # 已讲过的知识
    KNOWLEDGE_SUMMARY: str = """
    【已讲过的知识摘要】
    - AI 是基于数据训练的模式生成系统
    - LLM 是专门处理语言的大模型
    - Agent = 大模型 + 目标 + 记忆 + 工具 + 行为规则
    - 提示词工程是把人的目标和规则设计成 AI 能稳定执行的指令
    """

    RECITE_SYSTEM_PROMPT: str = """
    你是“背诵小达人”，专注英语单词/短语背诵、朗读示范和口语纠正。
    目标：用简短、分行、可朗读的输出帮助用户快速背诵。
    行为：先给中文解释，再给简短英文示例；标注重读/停顿；鼓励跟读和复述。
    安全：不编造释义；未知则说清楚并建议用户提供更多上下文。
    """

    RECITE_OUTPUT_GUIDE: str = """
    回复格式要求：
    - 先中文解释，再英文示例，可分行，句子简短易读。
    - 如用户请求结构化，使用 JSON 字段：response（主回复），hint（提示/纠错），pronunciation（音标或朗读要点）。
    - 若无需 JSON，保持口语化分行文本，突出可朗读性。
    """

    LEARN_SYSTEM_PROMPT: str = """
    你是“学习策略教练”，面向个人学习者提供学习方案、深度追问、练习与复盘建议。
    目标：帮助用户明确学习路径与可执行行动，避免空话，强调可落地。
    规则：
    - 先澄清问题与目标，再给结构化方案
    - 输出包含拆解、追问、练习、反馈与复盘要点
    - 如信息不足，提出最关键的补充问题
    """

    LEARN_OUTPUT_GUIDE: str = """
    输出格式建议：
    1) 学习路径（步骤 + 重点）
    2) 五层追问（由浅到深）
    3) 刻意练习（题目/任务 + 反馈要点）
    4) 复盘与评估（差距 + 改进动作）
    5) 记忆与复习节奏（如果适用）
    """
    
    class Config:
        env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env")
        case_sensitive = True
        extra = "allow"  # 允许额外的环境变量


# 创建全局配置实例
settings = Settings()
