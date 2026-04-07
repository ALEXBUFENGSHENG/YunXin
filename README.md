# 🤖 AI 智能助教 (AI Smart Assistant)

> 一个集成了全双工语音通话、科学记忆算法与大模型思维链的下一代 AI 教学辅助平台。

!\[Vue.js]\(<https://img.shields.io/badge/vuejs-%2335495e.svg?style=flat&logo=vuedotjs&logoColor=%234FC08D> null)
!\[FastAPI]\(<https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi> null)
!\[Python]\(<https://img.shields.io/badge/python-3670A0?style=flat&logo=python&logoColor=ffdd54> null)
!\[MySQL]\(<https://img.shields.io/badge/mysql-%2300f.svg?style=flat&logo=mysql&logoColor=white> null)
!\[LangChain]\(<https://img.shields.io/badge/🦜🔗_LangChain-black> null)

## 📁 项目构造 (Project Structure)

本项目采用 **前后端分离** 的标准架构设计，结合微服务与领域驱动思想划分模块，以下是核心目录树说明：

```text
YunXinOne/
├── backend/                  # ⚙️ FastAPI 后端服务目录
│   ├── app/                  # 后端核心业务代码 (领域划分)
│   │   ├── agents/           # LangChain 智能体与大模型逻辑编排
│   │   ├── api/              # API 路由层 (Controllers)
│   │   ├── config/           # 全局环境与配置管理
│   │   ├── core/             # 核心组件 (鉴权、中间件等)
│   │   ├── models/           # 数据库 ORM 模型与 Pydantic 实体类
│   │   ├── repositories/     # 数据库访问层 (CRUD 操作)
│   │   └── services/         # 业务逻辑服务层
│   ├── main.py               # FastAPI 服务启动入口
│   ├── mysql_storage.py      # MySQL 连接与存储底层实现
│   └── requirements.txt      # Python 依赖清单
│
├── frontend/                 # 🖥️ Vue 3 + Vite 前端服务目录
│   ├── src/                  # 前端源代码 (组件、视图、状态管理等)
│   ├── public/               # 静态资源文件
│   ├── package.json          # Node.js 依赖与脚本
│   ├── tailwind.config.js    # Tailwind CSS 样式配置
│   └── vite.config.js        # Vite 构建与代理配置
│
├── model_cache/              # 🧠 本地深度学习模型缓存 (如 FunASR 语音模型)
├── chat_history/             # 💬 会话与音频数据的本地持久化留存目录
├── docker-compose.yml        # 🐳 容器化编排配置文件 (用于一键生产环境部署)
├── run.sh                    # 🚀 本地开发环境一键启动/重启脚本
│
├── CALL_FRAMEWORK.md         # 📚 API 调用与前后端交互框架说明文档
├── DEPLOY.md                 # 📚 生产环境服务器部署指南
└── USER_MANUAL.md            # 📚 终端用户使用手册
```

## 🛠 技术栈概览 (Tech Stack)

### 🖥️ 前端 (Frontend)

- **Core**: Vue 3 (Composition API) + Vite 5
- **UI Framework**: Element Plus + Tailwind CSS
- **Network**: Axios (REST API) + **WebSocket** (全双工实时流)
- **Audio**: Web Audio API - 前端 VAD (语音活动检测) 与音频重采样

### ⚙️ 后端 (Backend)

- **Framework**: FastAPI (Python 3.10+) - 高性能异步 Web 框架
- **Database**: MySQL 8.0
- **Architecture**: 基于 LangChain 编排，支持接入本地或云端 LLM

### 🧠 人工智能与语音 (AI & Speech)

- **LLM Kernel**: 兼容 OpenAI 接口 (支持接入 DeepSeek-V3, Qwen, ChatGPT 或本地 Ollama)
- **ASR (语音识别)**: 阿里 FunASR (SenseVoiceSmall) - 本地毫秒级响应
- **TTS (语音合成)**: 微软 Edge-TTS - 免费且高度拟真
- **Memory Algorithm**: SM-2 间隔重复记忆算法 - 科学规划复习

## ✨ 核心亮点 (Key Features)

1. **🗣️ 全双工实时语音通话 (Full-Duplex Call)**: 支持随时打断 (Barge-in)，模拟真人对话体验。
2. **🎓 科学记忆闭环**: 内置 SM-2 算法，背诵小达人模块可根据“忘记/模糊/认识”自动安排复习队列。
3. **🧠 高强度用脑模式**: 针对复杂理科或代码问题，自动触发 **CoT (思维链)**，执行“计划->执行->反思”三部曲。

## ⚙️ 环境配置 (Configuration)

在启动项目之前，您需要配置相关的环境变量（如数据库密码、大模型 API Key 等）：

1. 进入 `backend` 目录，复制配置模板：
   ```bash
   cd backend
   cp .env.example .env
   ```
2. 编辑 `.env` 文件，填入您的实际参数：
   - `DB_PASSWORD`: MySQL 数据库密码
   - `LLM_API_KEY` / `OPENAI_API_KEY`: 您选择的大模型 API Key

## 🚀 快速启动 (Quick Start)

我们提供了一个极为简便的一键启动脚本：

```bash
# 赋予执行权限并启动
chmod +x run.sh
./run.sh
```

**访问地址**:

- 前端界面: <http://localhost:5080>
- 后端 API Docs: <http://localhost:8090/docs>

*如果需要手动启动或部署，请参考* *[DEPLOY.md](./DEPLOY.md)* *和* *[CALL\_FRAMEWORK.md](./CALL_FRAMEWORK.md)。*

## 🤝 参与贡献 (Contributing)

欢迎任何形式的贡献！如果您发现了 Bug 或有新功能建议，请通过提交 [Issue](#) 或发起 [Pull Request](#) 来帮助我们改进。

## 📄 开源协议 (License)

本项目基于 [MIT License](./LICENSE) 开源，允许自由使用、修改和分发。

***

