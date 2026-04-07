# 阶段一：核心功能修复计划

## 📋 修复范围

### 1. **核心问题分析**

| 问题类型 | 严重程度 | 影响范围 | 根本原因 |
|---------|----------|----------|----------|
| **数据库连接失败** | 🔴 严重 | 全局 | 密码配置错误 |
| **LLM API密钥未配置** | 🔴 严重 | 全局 | 密钥未设置 |
| **模型加载问题** | 🟡 中等 | 语音功能 | 依赖缺失 |
| **错误处理不完善** | 🟡 中等 | 全局 | 异常处理缺失 |

### 2. **修复优先级**

1. **优先级1** - 数据库配置与连接
2. **优先级2** - API密钥配置
3. **优先级3** - 核心功能修复
4. **优先级4** - 错误处理优化

## 🔧 详细修复计划

### 📁 **1. 配置文件修复**

#### **`backend/.env`文件修复**
```python
# 数据库配置
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_actual_password  # 修复：填入真实密码
DB_NAME=ai_assistant

# LLM 配置
LLM_API_KEY=your_actual_api_key    # 修复：填入真实密钥
DASHSCOPE_API_KEY=your_dashscope_key
OPENAI_API_KEY=your_openai_key
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_MODEL=qwen-plus
LLM_TEMPERATURE=0.7

# 应用配置
DEBUG=True
```

#### **`backend/app/config/settings.py`修复**
```python
class Settings(BaseSettings):
    """应用配置"""
    # 数据库配置
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = ""  # 修复：使用环境变量
    DB_NAME: str = "ai_assistant"
    
    # LLM 配置
    LLM_API_KEY: str = ""  # 修复：使用环境变量
    # ... 其他配置
    
    class Config:
        env_file = ".env"
        case_sensitive = True
```

### 📁 **2. 数据库连接修复**

#### **`backend/mysql_storage.py`修复**
```python
class MySQLStorage:
    def __init__(self, host=None, user=None, password=None, database=None, port=None):
        """初始化 MySQL 连接"""
        self.host = host or settings.DB_HOST
        self.port = port or settings.DB_PORT
        self.user = user or settings.DB_USER
        self.password = password or settings.DB_PASSWORD
        self.database = database or settings.DB_NAME
        self.connection_pool = None  # 修复：添加连接池
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
    def get_connection(self):
        """获取数据库连接"""
        try:
            if not self.connection_pool:
                # 修复：使用连接池
                self.connection_pool = pymysql.connect(
                    host=self.host,
                    port=self.port,
                    user=self.user,
                    password=self.password,
                    database=self.database,
                    charset='utf8mb4',
                    cursorclass=pymysql.cursors.DictCursor
                )
            return self.connection_pool
        except Exception as e:
            print(f"连接数据库失败: {e}")
            # 修复：返回None而不是抛出异常
            return None
```

### 📁 **3. LLM服务修复**

#### **`backend/app/services/llm_service.py`修复**
```python
class LLMService:
    """大语言模型服务"""
    
    def __init__(self):
        """初始化 LLM 服务"""
        # 优先使用环境变量中的API密钥
        api_key = os.getenv("LLM_API_KEY") or os.getenv("DASHSCOPE_API_KEY") or os.getenv("OPENAI_API_KEY") or settings.LLM_API_KEY
        
        # 修复：检查API密钥是否配置
        if not api_key or api_key in ["your_llm_api_key_here"]:
            raise ValueError("LLM API密钥未配置，请设置LLM_API_KEY环境变量")
        
        self.client = OpenAI(
            api_key=api_key,
            base_url=settings.LLM_BASE_URL,
        )
        self.model = settings.LLM_MODEL
        self.temperature = settings.LLM_TEMPERATURE
```

### 📁 **4. 模型加载优化**

#### **`backend/app/core/model_manager.py`修复**
```python
class ModelManager:
    """模型管理器"""
    
    async def preload_models(self):
        """预加载模型"""
        try:
            # 修复：添加异常处理
            print("正在预加载 SenseVoice 模型...")
            # 模型加载逻辑
            print("SenseVoice 模型加载成功")
        except Exception as e:
            print(f"模型加载失败: {e}")
            # 修复：记录错误但不终止服务
```

### 📁 **5. 错误处理优化**

#### **`backend/main.py`全局错误处理**
```python
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理"""
    logger.error(f"全局异常: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "内部服务器错误"}
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTP异常处理"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )
```

### 📁 **6. 前端错误处理**

#### **`frontend/src/utils/api.js`修复**
```javascript
class ApiClient {
    async request(endpoint, options = {}) {
        try {
            const response = await fetch(endpoint, {
                ...options,
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                }
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || '请求失败');
            }
            
            return await response.json();
        } catch (error) {
            console.error('API请求错误:', error);
            // 修复：抛出错误以便上层处理
            throw error;
        }
    }
}
```

## 📊 **修复验证计划**

### **1. 配置验证**
- [ ] 检查`.env`文件配置
- [ ] 验证数据库连接
- [ ] 测试LLM API密钥

### **2. 功能验证**
- [ ] 启动服务测试
- [ ] 数据库操作测试
- [ ] LLM服务测试
- [ ] 模型加载测试

### **3. 性能验证**
- [ ] 启动时间测量
- [ ] API响应时间测试
- [ ] 错误处理测试

## 🎯 **预期修复效果**

| 修复项 | 修复前 | 修复后 | 验证方法 |
|---------|--------|--------|----------|
| **数据库连接** | 失败 | 成功 | 服务启动无错误 |
| **LLM服务** | 模拟响应 | 真实AI | 聊天功能测试 |
| **模型加载** | 失败 | 成功 | 语音功能测试 |
| **错误处理** | 不完善 | 完善 | 异常场景测试 |

## 📋 **修复清单**

### **配置文件**
- [ ] `backend/.env` - 修复数据库密码和API密钥
- [ ] `backend/app/config/settings.py` - 完善配置管理

### **核心功能**
- [ ] `backend/mysql_storage.py` - 修复数据库连接
- [ ] `backend/app/services/llm_service.py` - 修复LLM服务
- [ ] `backend/app/core/model_manager.py` - 优化模型加载

### **错误处理**
- [ ] `backend/main.py` - 添加全局错误处理
- [ ] `backend/app/api/*.py` - 完善API错误处理
- [ ] `frontend/src/utils/api.js` - 前端错误处理

### **测试验证**
- [ ] 服务启动测试
- [ ] 功能测试
- [ ] 性能测试
- [ ] 安全测试

## 🚀 **修复交付标准**

1. **服务正常启动** - 无配置和连接错误
2. **核心功能可用** - 聊天、学习、数学功能正常
3. **错误处理完善** - 友好的错误提示
4. **性能符合预期** - 启动时间和响应速度合理
5. **代码质量良好** - 无语法错误和逻辑问题

通过以上修复计划，AI助教系统将解决当前的核心问题，为后续的功能完善和性能优化奠定基础。