# 🤖 AI Smart Assistant (YunXin)

> A next-generation AI teaching and learning platform integrating full-duplex voice calls, scientific memory algorithms, and Large Language Model (LLM) Chain of Thought reasoning.

![Vue.js](https://img.shields.io/badge/vuejs-%2335495e.svg?style=flat&logo=vuedotjs&logoColor=%234FC08D)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi)
![Python](https://img.shields.io/badge/python-3670A0?style=flat&logo=python&logoColor=ffdd54)
![MySQL](https://img.shields.io/badge/mysql-%2300f.svg?style=flat&logo=mysql&logoColor=white)
![LangChain](https://img.shields.io/badge/🦜🔗_LangChain-black)

## 📁 Project Structure

This project adopts a standard **Frontend-Backend Separation** architecture, combined with microservices and Domain-Driven Design (DDD) concepts to divide modules. Here is an overview of the core directory tree:

```text
YunXinOne/
├── backend/                  # ⚙️ FastAPI Backend Service Directory
│   ├── app/                  # Core Business Logic (Domain Division)
│   │   ├── agents/           # LangChain Agents & LLM Orchestration
│   │   ├── api/              # API Routing Layer (Controllers)
│   │   ├── config/           # Global Environment & Configuration
│   │   ├── core/             # Core Components (Auth, Middleware, etc.)
│   │   ├── models/           # Database ORM Models & Pydantic Entities
│   │   ├── repositories/     # Data Access Layer (CRUD Operations)
│   │   └── services/         # Business Logic Service Layer
│   ├── main.py               # FastAPI Service Entry Point
│   ├── mysql_storage.py      # MySQL Connection & Storage Implementation
│   └── requirements.txt      # Python Dependencies List
│
├── frontend/                 # 🖥️ Vue 3 + Vite Frontend Service Directory
│   ├── src/                  # Frontend Source Code (Components, Views, State Management)
│   ├── public/               # Static Assets
│   ├── package.json          # Node.js Dependencies & Scripts
│   ├── tailwind.config.js    # Tailwind CSS Configuration
│   └── vite.config.js        # Vite Build & Proxy Configuration
│
├── model_cache/              # 🧠 Local Deep Learning Model Cache (e.g., FunASR)
├── chat_history/             # 💬 Local Persistence Directory for Chat & Audio Data
├── docker-compose.yml        # 🐳 Docker Compose Configuration (for 1-click Prod Deployment)
├── run.sh                    # 🚀 1-click Start/Restart Script for Local Dev Environment
│
├── CALL_FRAMEWORK.md         # 📚 Documentation: API Calls & Frontend-Backend Interaction
├── DEPLOY.md                 # 📚 Documentation: Production Deployment Guide
└── USER_MANUAL.md            # 📚 Documentation: End-User Manual
```

## 🛠 Tech Stack Overview

### 🖥️ Frontend
- **Core**: Vue 3 (Composition API) + Vite 5
- **UI Framework**: Element Plus + Tailwind CSS
- **Network**: Axios (REST API) + **WebSocket** (Full-Duplex Real-Time Stream)
- **Audio**: Web Audio API - Frontend VAD (Voice Activity Detection) and Audio Resampling

### ⚙️ Backend
- **Framework**: FastAPI (Python 3.10+) - High-performance asynchronous Web framework
- **Database**: MySQL 8.0
- **Architecture**: Orchestrated based on LangChain, supporting both local and cloud LLMs

### 🧠 AI & Speech
- **LLM Kernel**: OpenAI API Compatible (Supports DeepSeek-V3, Qwen, ChatGPT, or local Ollama)
- **ASR (Speech Recognition)**: Alibaba FunASR (SenseVoiceSmall) - Local millisecond-level response
- **TTS (Text-to-Speech)**: Microsoft Edge-TTS - Free and highly realistic
- **Memory Algorithm**: SM-2 Spaced Repetition Algorithm - Scientifically schedules reviews

## ✨ Key Features

1. **🗣️ Full-Duplex Real-Time Voice Call**: Supports "Barge-in" interruptions at any time, simulating a real human conversation experience.
2. **🎓 Scientific Memory Loop**: Built-in SM-2 algorithm. The "Recitation Master" module automatically schedules review queues based on "Forget/Blurry/Know" self-assessments.
3. **🧠 Deep Thinking Mode**: Automatically triggers **CoT (Chain of Thought)** for complex science or coding problems, executing the "Plan -> Execute -> Reflect" trilogy.

## ⚙️ Configuration

Before starting the project, you need to configure the relevant environment variables (such as Database Password, LLM API Key, etc.):

1. Navigate to the `backend` directory and copy the configuration template:
   ```bash
   cd backend
   cp .env.example .env
   ```
2. Edit the `.env` file and fill in your actual parameters:
   - `DB_PASSWORD`: Your MySQL database password
   - `LLM_API_KEY` / `OPENAI_API_KEY`: Your chosen Large Language Model API Key

## 🚀 Quick Start

We provide an extremely simple one-click startup script:

```bash
# Grant execution permission and start
chmod +x run.sh
./run.sh
```

**Access URLs**:
- Frontend UI: [http://localhost:5080](http://localhost:5080)
- Backend API Docs: [http://localhost:8090/docs](http://localhost:8090/docs)

*For manual startup or deployment, please refer to [DEPLOY.md](./DEPLOY.md) and [CALL_FRAMEWORK.md](./CALL_FRAMEWORK.md).*

## 🤝 Contributing

Contributions of any kind are welcome! If you find a bug or have suggestions for new features, please help us improve by submitting an [Issue](#) or initiating a [Pull Request](#).

## 📄 License

This project is open-sourced under the [MIT License](./LICENSE), allowing for free use, modification, and distribution.

---
