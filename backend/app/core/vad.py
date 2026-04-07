import torch
import numpy as np
import asyncio

class VADManager:
    def __init__(self):
        self.model = None
        self.utils = None
        self.is_ready = False
        # 自适应底噪相关
        self.noise_level = 0.0005 # 初始底噪估计
        self.alpha = 0.05 # 底噪更新率
        
    def _load_silero_sync(self):
        # 检查本地缓存是否存在 (简单检查，避免 torch.hub 内部长时间挂起)
        import os
        hub_dir = os.path.expanduser("~/.cache/torch/hub/snakers4_silero-vad_master")
        if not os.path.exists(hub_dir) and not os.getenv("FORCE_VAD_DOWNLOAD"):
            # 如果缓存不存在且没有强制下载标记，直接跳过 (假设离线环境)
            # return None, None
            pass # 还是尝试一下吧，但加个 timeout

        return torch.hub.load(
            repo_or_dir='snakers4/silero-vad',
            model='silero_vad',
            force_reload=False,
            onnx=False
        )

    async def load_model(self):
        """异步加载 Silero VAD 模型"""
        try:
            print("正在加载 Silero VAD 模型...")
            
            # 设置 10 秒超时
            try:
                self.model, self.utils = await asyncio.wait_for(
                    asyncio.to_thread(self._load_silero_sync), 
                    timeout=10.0
                )
                self.is_ready = True
                print("Silero VAD 模型加载成功")
            except asyncio.TimeoutError:
                print("Silero VAD 加载超时 (可能是网络原因)，将使用能量检测降级方案。")
                self.model = None
                self.is_ready = False
        except Exception as e:
            print(f"Silero VAD 加载失败: {e}")
            self.model = None
            self.is_ready = False
            return

    def is_speech(self, audio_chunk: np.ndarray, sample_rate: int = 16000) -> bool:
        """
        检测是否为人声 (包含自适应底噪逻辑)
        """
        energy = np.mean(audio_chunk ** 2)
        
        # 1. 更新底噪估计 (仅当能量较低时更新，避免把人声算进去)
        # 假设人声能量通常远大于底噪，我们只在能量较低时更新底噪
        # 简单的策略：如果当前能量 < 3 * noise_level，我们认为这可能是新的底噪环境
        if energy < 3 * self.noise_level:
            self.noise_level = (1 - self.alpha) * self.noise_level + self.alpha * energy
        
        # 确保底噪不无限接近0
        self.noise_level = max(self.noise_level, 0.0001)

        if not self.is_ready or self.model is None:
            # Fallback: 基于自适应能量检测
            # 阈值 = 底噪 * 倍数 (e.g. 5倍) + 固定偏移
            threshold = self.noise_level * 5 + 0.0005
            
            # 限制最大阈值，防止太不灵敏
            threshold = min(threshold, 0.01)
            
            is_active = energy > threshold
            # if is_active:
            #    print(f"DEBUG: VAD Active (Energy={energy:.5f} > Thr={threshold:.5f}, Noise={self.noise_level:.5f})")
            return is_active

        # Silero VAD 逻辑...

        # 准备 Tensor
        # Silero VAD 期望 (batch, time) 或 (time)
        tensor = torch.from_numpy(audio_chunk)
        
        # 确保是 float32
        if isinstance(audio_chunk, np.ndarray) and audio_chunk.dtype != np.float32:
             tensor = tensor.float()
             
        # 推理
        try:
            speech_prob = self.model(tensor, sample_rate).item()
            return speech_prob > 0.5
        except Exception as e:
            print(f"VAD Error: {e}")
            return False

vad_manager = VADManager()
