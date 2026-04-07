import os
import asyncio
from typing import List, Dict, Optional
from openai import AsyncOpenAI
from app.config.settings import settings


class LLMService:
    """大语言模型服务"""
    
    def __init__(self):
        """初始化 LLM 服务"""
        # 优先使用环境变量中的API密钥
        api_key = os.getenv("LLM_API_KEY") or os.getenv("DASHSCOPE_API_KEY") or os.getenv("OPENAI_API_KEY") or settings.LLM_API_KEY
        
        # 检查是否是占位符值
        if not api_key or api_key in ["your_llm_api_key_here", "your_dashscope_api_key_here", "your_openai_api_key_here"]:
            # 演示模式：使用模拟响应
            print("⚠️  LLM API密钥未配置，启用演示模式（模拟响应）")
            self.demo_mode = True
            return
        
        self.demo_mode = False
        
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=settings.LLM_BASE_URL,
        )
        self.model = settings.LLM_MODEL
        self.temperature = settings.LLM_TEMPERATURE
    
    async def generate_response(self, messages: List[Dict[str, str]]) -> str:
        """生成LLM响应
        
        Args:
            messages: 消息列表
        
        Returns:
            str: LLM 响应内容
        """
        if hasattr(self, 'demo_mode') and self.demo_mode:
            # 演示模式：返回模拟响应
            user_message = messages[-1]['content'] if messages else "你好"
            return f"[演示模式] 这是对您消息 '{user_message}' 的模拟回复。请配置真实的LLM API密钥以获得完整功能。"
        
        try:
            completion = await self.client.chat.completions.create(
                model=self.model,
                temperature=self.temperature,
                messages=messages
            )
            return completion.choices[0].message.content
        except Exception as e:
            print(f"LLM调用失败: {str(e)}")
            raise
    
    async def generate_stream(self, messages: List[Dict[str, str]]):
        """生成流式LLM响应
        
        Args:
            messages: 消息列表
        
        Yields:
            str: 流式响应内容
        """
        if hasattr(self, 'demo_mode') and self.demo_mode:
            # 演示模式：返回模拟流式响应
            user_message = messages[-1]['content'] if messages else "你好"
            demo_text = f"[演示模式] 这是对您消息 '{user_message}' 的模拟流式回复。请配置真实的LLM API密钥以获得完整功能。"
            
            # 模拟流式输出
            for char in demo_text:
                yield char
                await asyncio.sleep(0.01)
            return
        
        try:
            completion = await self.client.chat.completions.create(
                model=self.model,
                temperature=self.temperature,
                messages=messages,
                stream=True
            )
            async for chunk in completion:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            print(f"流式LLM调用失败: {str(e)}")
            raise
    
    def build_messages(self, user_message: str, username: str = "") -> List[Dict[str, str]]:
        """构建消息列表
        
        Args:
            user_message: 用户消息
            username: 用户名
        
        Returns:
            List[Dict[str, str]]: 消息列表
        """
        messages = [
            {"role": "system", "content": settings.SYSTEM_PROMPT},
            {"role": "system", "content": settings.KNOWLEDGE_SUMMARY},
            {"role": "assistant", "content": "你好，我是你的课程助教，可以帮你理解 AI 和 Agent。"},
        ]
        
        # 如果有用户名，添加示例对话
        if username:
            messages.extend([
                {"role": "user", "content": f"我叫{username}"},
                {"role": "assistant", "content": f"你好，{username}，我是你的课程助教。"},
            ])
        
        # 添加用户当前消息
        messages.append({"role": "user", "content": user_message})
        
        return messages

# 创建全局LLM服务实例（延迟初始化）
llm_service = None

def get_llm_service():
    """获取LLM服务实例（延迟初始化）"""
    global llm_service
    if llm_service is None:
        llm_service = LLMService()
    return llm_service
