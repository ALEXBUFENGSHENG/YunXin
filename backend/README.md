# AI 语音助手后端 (AI Voice Assistant Backend)

## 📌 项目简介
本项目是一个基于 **FastAPI** 构建的高性能 AI 语音助手后端服务。它集成了先进的 LLM（大语言模型）、本地语音识别（SenseVoice）、语音合成（Edge-TTS）以及全双工实时通话功能。此外，项目还包含了一个基于间隔重复算法（Spaced Repetition）的记忆/学习模块，旨在提供智能化的语言学习体验。

## 🌟 核心功能

### 1. 🤖 多模型 LLM 支持
*   **兼容性**: 支持 OpenAI 格式接口（可接入 DeepSeek, Qwen, ChatGPT 等）及 Ollama 本地模型。
*   **流式对话**: 支持 SSE (Server-Sent Events) 流式输出，降低首字延迟。

### 2. 🗣️ 全双工语音交互 (Full-Duplex)
*   **实时通话**: 基于 WebSocket 实现低延迟的全双工通话。
*   **本地识别**: 集成阿里 **FunASR (SenseVoiceSmall)** 模型，支持高精度中英混合识别，无需上传音频，隐私安全。
*   **语音合成**: 集成 **Edge-TTS**，提供自然流畅的语音播报。
*   **VAD 支持**: 内置语音活动检测，智能断句。

### 3. 🧠 记忆与学习模块 (Memory & Learning)
*   **背诵小达人**: 提供基于 **SM-2 (SuperMemo-2)** 变体的间隔重复记忆算法。
*   **智能复习**: 根据用户对单词的掌握程度（忘记/模糊/认识），自动规划最佳复习时间。
*   **进度追踪**: 实时记录学习进度和记忆强度。

### 4. 🛡️ 基础服务
*   **用户认证**: 完整的 JWT 注册/登录流程。
*   **数据持久化**: MySQL 存储用户数据和完整对话历史。
*   **管理后台**: 提供用户管理和系统统计 API。

## 🛠️ 技术栈

*   **Framework**: FastAPI, Uvicorn
*   **AI/LLM**: LangChain, OpenAI SDK
*   **Speech**: FunASR (SenseVoice), Edge-TTS
*   **Database**: MySQL (PyMySQL)
*   **Tools**: Python 3.10+, FFmpeg

## 🚀 快速开始

### 前置要求
1.  **Python 3.10+**
2.  **MySQL 数据库**: 确保服务已启动。
3.  **FFmpeg**: 必须安装并配置到系统环境变量中（用于音频处理）。

### 1. 安装依赖
```bash
cd backend
pip install -r requirements.txt
```

### 2. 环境变量配置
复制 `.env.example` (如有) 或新建 `.env` 文件，填入以下配置：

```ini
# 数据库配置
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=ai_assistant

# LLM 配置 (示例: DeepSeek)
LLM_PROVIDER=openai
LLM_API_KEY=your_api_key
LLM_BASE_URL=https://api.deepseek.com
LLM_MODEL=deepseek-chat

# JWT 配置
JWT_SECRET_KEY=your_secret_key
```

### 3. 初始化数据库
确保 MySQL 中已创建 `ai_assistant` 数据库，表结构会在首次运行时自动检查/创建（或使用 `scripts/update_db.py`）。
对于记忆模块，运行初始化脚本：
```bash
python -m app.init_learning_db
```

### 4. 启动服务
```bash
python main.py
# 或使用 uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
*   API 文档地址: `http://localhost:8000/docs`

## 📂 目录结构说明

*   `main.py`: 项目主入口，包含核心路由和 WebSocket 逻辑。
*   `app/`: 模块化业务代码。
    *   `api/`: 路由定义。
    *   `services/`: 业务逻辑封装 (Chat, Speech等)。
    *   `spaced_memory.py`: 记忆算法核心。
*   `scripts/`: 实用工具脚本（模型下载、数据修复等）。

---

