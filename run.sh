#!/bin/bash

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}正在重启 AI 助教项目...${NC}"

# 获取项目根目录
PROJECT_ROOT=$(pwd)

# 1. 杀死旧进程
echo -e "${GREEN}1. 清理旧进程...${NC}"
lsof -ti:8090 | xargs kill -9 2>/dev/null
lsof -ti:5080 | xargs kill -9 2>/dev/null
sleep 2

# 2. 启动后端
echo -e "${GREEN}2. 启动后端服务 (FastAPI)...${NC}"
cd "$PROJECT_ROOT/backend"
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi
nohup python3 -u main.py > backend.log 2>&1 &
echo -e "${BLUE}后端已在后台启动 (PID: $!), 日志: backend/backend.log${NC}"

# 3. 启动前端
echo -e "${GREEN}3. 启动前端服务 (Vite)...${NC}"
cd "$PROJECT_ROOT/frontend"
nohup npm run dev > frontend.log 2>&1 &
echo -e "${BLUE}前端已在后台启动 (PID: $!), 日志: frontend/frontend.log${NC}"

echo -e "${BLUE}----------------------------------------${NC}"
echo -e "访问地址:"
echo -e "前端界面: ${GREEN}http://localhost:5080${NC}"
echo -e "后端 API: ${GREEN}http://localhost:8090${NC}"
echo -e "后端文档: ${GREEN}http://localhost:8090/docs${NC}"
echo -e "${BLUE}----------------------------------------${NC}"
echo -e "${RED}提示: 服务已在后台运行。如果需要停止，请使用 lsof -ti:8090,5080 | xargs kill -9${NC}"
