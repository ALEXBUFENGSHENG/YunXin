# 部署指南 (Deployment Guide)

本指南将帮助你将 AI 助教系统打包并部署到 Linux 服务器上。

## 1. 准备工作 (Prerequisites)

在目标服务器上，你需要安装以下软件：

*   **Docker**: 用于容器化运行应用。
*   **Docker Compose**: 用于编排前后端服务。

### 安装命令 (Ubuntu/Debian 示例)
```bash
# 安装 Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 安装 Docker Compose
sudo apt-get install -y docker-compose-plugin
```

## 2. 上传代码 (Upload Code)

由于项目包含大量小文件（如 node_modules），直接上传容易中断。**强烈建议**使用“压缩包”方式传输。

### 步骤 1: 本地压缩 (并排除不必要文件)
在你的**本地电脑终端**执行：

```bash
cd /Users/alex/Downloads/
# 压缩为 agent.zip，自动排除依赖包和模型缓存（大大减小体积）
zip -r agent.zip " Agent" -x "*/node_modules/*" -x "*/.venv/*" -x "*/.git/*" -x "*/model_cache/*" -x "*/modelscope_cache/*"
```

### 步骤 2: 上传压缩包
```bash
# 上传 agent.zip
scp -o PubkeyAuthentication=no agent.zip ubuntu@150.158.190.244:/home/ubuntu/
```

### 步骤 3: 服务器解压
登录服务器后执行：
```bash
ssh -o PubkeyAuthentication=no ubuntu@150.158.190.244

# 安装 unzip 并解压
sudo apt-get update && sudo apt-get install -y unzip
unzip agent.zip
mv " Agent" agent  # 去除空格
```

## 3. 启动服务 (Start Services)

进入项目目录并启动：

```bash
cd /home/ubuntu/agent

# 构建并后台启动所有服务
# 注意：如果报错 "docker: 'compose' is not a docker command"，请尝试使用 docker-compose (带横杠)
sudo docker-compose up -d --build
# 或者尝试新版命令: sudo docker compose up -d --build
```

系统会自动执行以下操作：
1.  构建前端 Vue 应用并生成静态文件。
2.  构建后端 Python 环境并安装依赖。
3.  启动 MySQL 数据库。
4.  启动 Nginx 服务反向代理前后端。

## 4. 验证部署 (Verify)

等待几分钟后，访问服务器 IP：

*   **前端页面**: `http://your-server-ip`
*   **后端 API**: `http://your-server-ip/api/docs` (Swagger 文档)

## 5. 常见问题 (FAQ)

### 模型加载慢？
项目配置了 `model_cache` 目录映射。第一次启动时，如果没有本地模型，容器会自动下载模型到 `model_cache` 目录。下载完成后，下次启动将直接加载本地模型。

### 端口冲突？
如果服务器的 80 或 8000 端口被占用，请修改 `docker-compose.yml` 中的 `ports` 映射，例如：
```yaml
ports:
  - "8080:80" # 将容器的 80 映射到宿主机的 8080
```

### 查看日志
```bash
# 查看所有日志
sudo docker compose logs -f

# 查看后端日志
sudo docker compose logs -f backend
```
