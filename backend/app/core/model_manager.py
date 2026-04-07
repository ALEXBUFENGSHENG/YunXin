from typing import Optional, Any
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor

class ModelManager:
    _instance = None
    _sensevoice_model = None
    _executor = ThreadPoolExecutor(max_workers=1)

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelManager, cls).__new__(cls)
        return cls._instance

    @classmethod
    def get_sensevoice_model(cls) -> Optional[Any]:
        """获取 SenseVoice 模型实例 (懒加载)"""
        if cls._sensevoice_model is None:
            cls.load_sensevoice_model()
        return cls._sensevoice_model

    @classmethod
    def load_sensevoice_model(cls):
        """加载 SenseVoice 模型"""
        if cls._sensevoice_model is not None:
            return

        print("正在初始化 SenseVoiceSmall 模型...")
        try:
            from funasr import AutoModel
            
            # Check for local model cache first
            # 1. Try relative to file
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            local_model_path = os.path.join(project_root, "model_cache", "iic", "SenseVoiceSmall")
            
            # 2. Try relative to cwd (if running from backend)
            if not os.path.exists(local_model_path):
                 local_model_path = os.path.join(os.getcwd(), "..", "model_cache", "iic", "SenseVoiceSmall")
            
            # 3. Try relative to cwd (if running from root)
            if not os.path.exists(local_model_path):
                 local_model_path = os.path.join(os.getcwd(), "model_cache", "iic", "SenseVoiceSmall")

            print(f"DEBUG: Checking local model path: {local_model_path}, Exists: {os.path.exists(local_model_path)}")

            if os.path.exists(local_model_path):
                print(f"Using local model from: {local_model_path}")
                model_id = local_model_path
            else:
                # 使用国内镜像加速下载
                print("Warning: Local model not found, falling back to modelscope download (might hang on lock)")
                model_id = "iic/SenseVoiceSmall"
            
            cls._sensevoice_model = AutoModel(
                model=model_id,
                trust_remote_code=True,
                device="cpu",
                disable_update=True,
            )
            print("SenseVoiceSmall 模型初始化成功")
        except Exception as e:
            print(f"SenseVoiceSmall 模型初始化失败: {e}")
            # 不抛出异常，允许服务在无语音模型情况下启动
            cls._sensevoice_model = None

    @classmethod
    async def preload_models(cls):
        """异步预加载所有模型"""
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(cls._executor, cls.load_sensevoice_model)

model_manager = ModelManager()
