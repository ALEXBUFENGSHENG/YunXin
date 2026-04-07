import os
import pymysql
import json
from datetime import datetime
from passlib.context import CryptContext
from app.config.settings import settings

class MySQLStorage:
    """MySQL 存储模块"""
    
    def __init__(self, host=None, user=None, password=None, database=None, port=None):
        """初始化 MySQL 连接
        
        Args:
            host: MySQL 主机地址
            user: MySQL 用户名
            password: MySQL 密码
            database: 数据库名称
            port: MySQL 端口
        """
        self.host = host or settings.DB_HOST
        self.port = port or settings.DB_PORT
        self.user = user or settings.DB_USER
        self.password = password or settings.DB_PASSWORD
        self.database = database or settings.DB_NAME
        self.connection = None
        self.pwd_context = CryptContext(schemes=["pbkdf2_sha256", "bcrypt"], deprecated="auto")
        
        # 尝试初始化数据库表结构
        self._init_db_schema()
    
    def _init_db_schema(self):
        """初始化数据库表结构 (如果不存在)"""
        conn = self.get_connection()
        if not conn:
            return
        try:
            with conn.cursor() as cursor:
                # 0. 基础用户与会话表
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        username VARCHAR(50) UNIQUE NOT NULL,
                        password_hash VARCHAR(255),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS sessions (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        user_id INT,
                        name VARCHAR(100),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(id)
                    )
                """)
                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS messages (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        user_id INT,
                        session_id INT,
                        message_type VARCHAR(20),
                        content TEXT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(id),
                        FOREIGN KEY (session_id) REFERENCES sessions(id)
                    )
                """)

                # 检查 users 表是否有 password_hash 字段 (兼容旧表)
                cursor.execute("SHOW COLUMNS FROM users LIKE 'password_hash'")
                if not cursor.fetchone():
                    print("正在为 users 表添加 password_hash 字段...")
                    cursor.execute("ALTER TABLE users ADD COLUMN password_hash VARCHAR(255) DEFAULT NULL")
                    conn.commit()
                
                # 初始化数学学习相关表
                self._init_math_tables(cursor)
                
                # 初始化通用学习相关表 (云心大脑)
                self._init_learning_tables(cursor)
                
                # 强制修复并重新注入题目
                cursor.execute("DELETE FROM math_problems")
                real_problems = [
                    (r"（2023数一）求极限 $\lim_{n \to \infty} \sum_{k=1}^n \frac{k}{n^2 + k^2}$.", 
                     r"利用定积分定义：$\int_0^1 \frac{x}{1+x^2} dx$. 结果为 $\frac{1}{2}\ln 2$.", 
                     json.dumps(["定积分定义", "极限计算", "高数"]), 4),
                    (r"（2022数一）设 $z = z(x, y)$ 由方程 $x^2 + y^2 + z^2 = 3xyz$ 确定，求 $\frac{\partial z}{\partial x}$.",
                     r"隐函数求导法则。两边对 x 求导，将 z 视作 x, y 的函数。",
                     json.dumps(["隐函数求导", "多元函数微分", "高数"]), 3),
                    (r"（2021数一）已知矩阵 $A$ 的特征值为 1, 2, 3，求 $A^2 - 3A + 2E$ 的特征值。",
                     r"特征值映射定理。结果为 0, 0, 2。",
                     json.dumps(["特征值", "矩阵运算", "线代"]), 3),
                    (r"（2019数一）设 $X \sim U(0, 1)$，$Y = -\ln X$，求 $E(Y)$ 和 $D(Y)$.",
                     r"Y 服从指数分布 E(1)。E(Y)=1，D(Y)=1。",
                     json.dumps(["均匀分布", "指数分布", "期望方差", "概率"]), 4),
                    (r"（2020数一）求幂级数 $\sum_{n=1}^\infty \frac{x^n}{n(n+1)}$ 的收敛域及和函数。",
                     r"收敛半径 R=1。和函数通过逐项求导或积分还原。",
                     json.dumps(["幂级数", "和函数", "收敛域"]), 5),
                    (r"（2022数一）设 $A$ 为 3 阶矩阵，其特征值为 1, -1, 0，则 $A^2 + A$ 的特征值为？",
                     r"根据特征值性质，分别为 $1^2+1=2, (-1)^2-1=0, 0^2+0=0$。",
                     json.dumps(["特征值", "线代"]), 3),
                    (r"（2018数一）求由方程 $y - x = \ln(x+y)$ 确定的隐函数在 $(0, 1)$ 处的导数 $y'$.",
                     r"两边对 x 求导：$y' - 1 = \frac{1+y'}{x+y}$，代入 (0, 1) 解得 $y'=3$。",
                     json.dumps(["隐函数求导", "高数"]), 3),
                    (r"（2023数一）设 $f(x) = \int_0^{x^2} \sin(t^2) dt$，求 $f'(x)$.",
                     r"变限积分求导：$f'(x) = \sin((x^2)^2) \cdot (x^2)' = 2x \sin(x^4)$。",
                     json.dumps(["变限积分", "高数"]), 4)
                ]
                cursor.executemany(
                    "INSERT INTO math_problems (stem, answer_outline, tags, difficulty) VALUES (%s, %s, %s, %s)",
                    real_problems
                )
                
                conn.commit()
                print("数据库初始化与数学题库强制修复完成")
        except Exception as e:
            print(f"初始化数据库 Schema 失败: {e}")

    def _init_math_tables(self, cursor):
        """初始化数学学习相关表"""
        # 1. 考研画像
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS math_exam_profiles (
                user_id INT PRIMARY KEY,
                exam_name VARCHAR(50),
                target_score INT,
                exam_date DATE,
                daily_hours INT,
                resources_config JSON,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

        # 2. 题目库 (math_problems)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS math_problems (
                id INT AUTO_INCREMENT PRIMARY KEY,
                stem TEXT NOT NULL,
                answer_outline TEXT,
                tags JSON,
                difficulty INT DEFAULT 3,
                source VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 3. 知识点库 (math_knowledge_points)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS math_knowledge_points (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) UNIQUE NOT NULL,
                category VARCHAR(50),
                chapter VARCHAR(50),
                importance INT DEFAULT 3
            )
        """)

        # 4. 用户知识点掌握度 (math_user_kp_mastery)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS math_user_kp_mastery (
                user_id INT,
                kp_id INT,
                mastery FLOAT DEFAULT 0.0,
                last_practiced_at TIMESTAMP,
                PRIMARY KEY (user_id, kp_id),
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (kp_id) REFERENCES math_knowledge_points(id)
            )
        """)

        # 5. 做题记录 (math_problem_attempts)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS math_problem_attempts (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                problem_id INT,
                self_score INT,
                time_spent_sec INT,
                user_steps TEXT,
                key_check_result JSON,
                error_tags JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (problem_id) REFERENCES math_problems(id)
            )
        """)

        # 6. 复习条目 (math_study_items) - SM-2
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS math_study_items (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                content TEXT,
                item_type VARCHAR(20), -- problem, concept, mistake
                source_id INT, -- problem_id or other
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

        # 7. 复习进度 (math_item_progress)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS math_item_progress (
                item_id INT PRIMARY KEY,
                user_id INT,
                ease_factor FLOAT DEFAULT 2.5,
                interval_days INT DEFAULT 0,
                repetition INT DEFAULT 0,
                next_review TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_score INT,
                FOREIGN KEY (item_id) REFERENCES math_study_items(id),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        # 8. 注入初始真实题库
        cursor.execute("SELECT COUNT(*) as count FROM math_problems")
        if cursor.fetchone()['count'] == 0:
            real_problems = [
                (r"（2023数一）求极限 $\lim_{n \to \infty} \sum_{k=1}^n \frac{k}{n^2 + k^2}$.", 
                 r"利用定积分定义：$\int_0^1 \frac{x}{1+x^2} dx$. 结果为 $\frac{1}{2}\ln 2$.", 
                 json.dumps(["定积分定义", "极限计算", "高数"]), 4),
                (r"（2022数一）设 $z = z(x, y)$ 由方程 $x^2 + y^2 + z^2 = 3xyz$ 确定，求 $\frac{\partial z}{\partial x}$.",
                 r"隐函数求导法则。两边对 x 求导，将 z 视作 x, y 的函数。",
                 json.dumps(["隐函数求导", "多元函数微分", "高数"]), 3),
                (r"（2021数一）已知矩阵 $A$ 的特征值为 1, 2, 3，求 $A^2 - 3A + 2E$ 的特征值。",
                 r"特征值映射定理。结果为 0, 0, 2。",
                 json.dumps(["特征值", "矩阵运算", "线代"]), 3),
                (r"（2019数一）设 $X \sim U(0, 1)$，$Y = -\ln X$，求 $E(Y)$ 和 $D(Y)$.",
                 r"Y 服从指数分布 E(1)。E(Y)=1，D(Y)=1。",
                 json.dumps(["均匀分布", "指数分布", "期望方差", "概率"]), 4),
                (r"（2020数一）求幂级数 $\sum_{n=1}^\infty \frac{x^n}{n(n+1)}$ 的收敛域及和函数。",
                 r"收敛半径 R=1。和函数通过逐项求导或积分还原。",
                 json.dumps(["幂级数", "和函数", "收敛域"]), 5),
                (r"（2022数一）设 $A$ 为 3 阶矩阵，其特征值为 1, -1, 0，则 $A^2 + A$ 的特征值为？",
                 r"根据特征值性质，分别为 $1^2+1=2, (-1)^2-1=0, 0^2+0=0$。",
                 json.dumps(["特征值", "线代"]), 3),
                (r"（2018数一）求由方程 $y - x = \ln(x+y)$ 确定的隐函数在 $(0, 1)$ 处的导数 $y'$.",
                 r"两边对 x 求导：$y' - 1 = \frac{1+y'}{x+y}$，代入 (0, 1) 解得 $y'=3$。",
                 json.dumps(["隐函数求导", "高数"]), 3),
                (r"（2023数一）设 $f(x) = \int_0^{x^2} \sin(t^2) dt$，求 $f'(x)$.",
                 r"变限积分求导：$f'(x) = \sin((x^2)^2) \cdot (x^2)' = 2x \sin(x^4)$。",
                 json.dumps(["变限积分", "高数"]), 4)
            ]
            cursor.executemany(
                "INSERT INTO math_problems (stem, answer_outline, tags, difficulty) VALUES (%s, %s, %s, %s)",
                real_problems
            )

    def _init_learning_tables(self, cursor):
        """初始化通用学习相关表 (云心大脑)"""
        # 1. 学习画像
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS learning_profiles (
                user_id INT PRIMARY KEY,
                default_session_min INT DEFAULT 30,
                preferred_style VARCHAR(50) DEFAULT 'socratic',
                domain_focus JSON,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

        # 2. 知识点字典 (KP)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS knowledge_points (
                kp_key VARCHAR(100) PRIMARY KEY,
                label_cn VARCHAR(100),
                domain VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 3. 用户 KP 掌握度 (Mastery)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_kp_mastery (
                user_id INT,
                kp_key VARCHAR(100),
                mastery FLOAT DEFAULT 0.0,
                evidence TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, kp_key),
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (kp_key) REFERENCES knowledge_points(kp_key)
            )
        """)

        # 4. 学习产物 (Artifacts)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS learning_artifacts (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                session_id INT,
                topic VARCHAR(255),
                artifacts JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

        # 5. 通用复习卡片 (SM-2 调度)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS general_study_items (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                content TEXT NOT NULL,
                item_type VARCHAR(50),
                source_topic VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS general_item_progress (
                item_id INT PRIMARY KEY,
                user_id INT,
                ease_factor FLOAT DEFAULT 2.5,
                interval_days INT DEFAULT 0,
                repetition INT DEFAULT 0,
                next_review TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_score INT DEFAULT 0,
                FOREIGN KEY (item_id) REFERENCES general_study_items(id),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

    def save_learning_artifacts(self, user_id, session_id, topic, artifacts):
        """保存会话产物、更新掌握度并进入 SM-2 复习队列"""
        connection = self.get_connection()
        if not connection: return False
        try:
            with connection.cursor() as cursor:
                # 1. 保存 Artifacts
                sql_art = "INSERT INTO learning_artifacts (user_id, session_id, topic, artifacts) VALUES (%s, %s, %s, %s)"
                cursor.execute(sql_art, (user_id, session_id, topic, json.dumps(artifacts)))
                
                # 2. 处理 KP 更新
                for kp in artifacts.get("kp_updates", []):
                    key = kp["kp_key"]
                    delta = kp["delta"]
                    evidence = kp.get("evidence", "")
                    cursor.execute("INSERT IGNORE INTO knowledge_points (kp_key, domain) VALUES (%s, %s)", 
                                 (key, key.split('.')[0] if '.' in key else 'general'))
                    cursor.execute("SELECT mastery FROM user_kp_mastery WHERE user_id = %s AND kp_key = %s", (user_id, key))
                    row = cursor.fetchone()
                    curr = row['mastery'] if row else 0.0
                    new_m = max(0.0, min(1.0, curr + delta))
                    cursor.execute("""
                        INSERT INTO user_kp_mastery (user_id, kp_key, mastery, evidence)
                        VALUES (%s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE mastery = %s, evidence = %s
                    """, (user_id, key, new_m, evidence, new_m, evidence))
                
                # 3. 处理复习卡片 (SM-2 队列)
                for card in artifacts.get("review_cards", []):
                    cursor.execute("""
                        INSERT INTO general_study_items (user_id, content, item_type, source_topic)
                        VALUES (%s, %s, %s, %s)
                    """, (user_id, card.get("content", ""), card.get("type", "general"), topic))
                    item_id = cursor.lastrowid
                    cursor.execute("""
                        INSERT INTO general_item_progress (item_id, user_id, next_review)
                        VALUES (%s, %s, CURRENT_TIMESTAMP)
                    """, (item_id, user_id))
                
                connection.commit()
                return True
        except Exception as e:
            print(f"保存学习产物失败: {e}")
            connection.rollback()
            return False

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password):
        return self.pwd_context.hash(password, scheme="pbkdf2_sha256")

    def get_connection(self):
        """获取数据库连接
        
        Returns:
            pymysql.Connection: 数据库连接对象
        """
        # 检查连接是否有效，如果无效则重连
        try:
            if self.connection:
                self.connection.ping(reconnect=True)
                return self.connection
        except Exception:
            self.connection = None

        try:
            self.connection = pymysql.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor,
                connect_timeout=5
            )
        except Exception as e:
            print(f"连接数据库失败: {str(e)}")
            print("⚠️  数据库连接失败，启用演示模式（使用内存存储）")
            self.connection = None
        return self.connection
    
    def close_connection(self):
        """关闭数据库连接"""
        if self.connection and self.connection.open:
            self.connection.close()
    
    def create_user(self, username, password):
        """创建新用户 (带密码)"""
        connection = self.get_connection()
        if not connection:
            return None
        try:
            with connection.cursor() as cursor:
                # 检查用户是否存在
                sql = "SELECT id, password_hash FROM users WHERE username = %s"
                cursor.execute(sql, (username,))
                existing_user = cursor.fetchone()
                if existing_user:
                    # 兼容旧数据：历史上可能存在“仅用户名、无密码”的用户
                    if not existing_user.get('password_hash'):
                        password_hash = self.get_password_hash(password)
                        sql = "UPDATE users SET password_hash = %s WHERE id = %s"
                        cursor.execute(sql, (password_hash, existing_user['id']))
                        connection.commit()
                        return True
                    return False # 用户已存在且已有密码

                password_hash = self.get_password_hash(password)
                sql = "INSERT INTO users (username, password_hash) VALUES (%s, %s)"
                cursor.execute(sql, (username, password_hash))
                connection.commit()
                return True
        except Exception as e:
            print(f"创建用户失败: {str(e)}")
            if connection:
                connection.rollback()
            return False

    def authenticate_user(self, username, password):
        """验证用户登录"""
        connection = self.get_connection()
        if not connection:
            return None
        try:
            with connection.cursor() as cursor:
                sql = "SELECT id, password_hash FROM users WHERE username = %s"
                cursor.execute(sql, (username,))
                user = cursor.fetchone()
                
                if not user:
                    return False
                
                if not user['password_hash']:
                    # 如果用户存在但没有密码 (旧用户)，可以策略性处理，这里暂时拒绝
                    return False
                    
                if self.verify_password(password, user['password_hash']):
                    return user
                return False
        except Exception as e:
            print(f"验证用户失败: {str(e)}")
            return None

    def get_user_id(self, username):
        """获取用户 ID，如果用户不存在则创建
        
        Args:
            username: 用户名
        
        Returns:
            int: 用户 ID
        """
        connection = self.get_connection()
        if not connection:
            return None
        try:
            with connection.cursor() as cursor:
                # 检查用户是否存在
                sql = "SELECT id FROM users WHERE username = %s"
                cursor.execute(sql, (username,))
                result = cursor.fetchone()
                
                if result:
                    return result['id']
                else:
                    # 创建新用户
                    sql = "INSERT INTO users (username) VALUES (%s)"
                    cursor.execute(sql, (username,))
                    connection.commit()
                    return cursor.lastrowid
        except Exception as e:
            print(f"获取用户 ID 失败: {str(e)}")
            if connection:
                connection.rollback()
            return None
    
    def create_session(self, username, name=None):
        """创建新会话
        
        Args:
            username: 用户名
            name: 会话名称，如果为空则默认为"新会话"
            
        Returns:
            int: 会话 ID
        """
        connection = self.get_connection()
        if not connection:
            return None
        try:
            user_id = self.get_user_id(username)
            if not user_id:
                return None
            
            if not name:
                name = f"会话 {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                
            with connection.cursor() as cursor:
                sql = "INSERT INTO sessions (user_id, name) VALUES (%s, %s)"
                cursor.execute(sql, (user_id, name))
                connection.commit()
                return cursor.lastrowid
        except Exception as e:
            print(f"创建会话失败: {str(e)}")
            if connection:
                connection.rollback()
            return None

    def get_user_sessions(self, username):
        """获取用户的所有会话
        
        Args:
            username: 用户名
            
        Returns:
            list: 会话列表 [{'id': 1, 'name': '...', 'created_at': ...}]
        """
        connection = self.get_connection()
        if not connection:
            return []
        try:
            user_id = self.get_user_id(username)
            if not user_id:
                return []
            
            with connection.cursor() as cursor:
                sql = "SELECT id, name, created_at FROM sessions WHERE user_id = %s ORDER BY created_at DESC"
                cursor.execute(sql, (user_id,))
                return cursor.fetchall()
        except Exception as e:
            print(f"获取会话列表失败: {str(e)}")
            return []

    def save_chat(self, username, messages, session_id=None):
        """保存对话历史
        
        Args:
            username: 用户名
            messages: 消息列表
            session_id: 会话 ID，如果为空则尝试保存到最近的会话或新建会话
        
        Returns:
            bool: 是否保存成功
        """
        connection = self.get_connection()
        if not connection:
            return False
        try:
            # 获取用户 ID
            user_id = self.get_user_id(username)
            if not user_id:
                return False
            
            # 如果没有提供 session_id，尝试查找最近的会话
            if not session_id:
                sessions = self.get_user_sessions(username)
                if sessions:
                    session_id = sessions[0]['id']
                else:
                    # 如果没有会话，创建一个新的
                    session_id = self.create_session(username)
                    if not session_id:
                        return False

            with connection.cursor() as cursor:
                # 只有当确实需要覆盖整个会话历史时才删除（通常我们是追加消息，这里保留原有逻辑但也支持 session_id）
                # 注意：原逻辑是 DELETE FROM messages WHERE user_id = %s，这会删除用户的所有消息！
                # 修改为只删除当前 session 的消息
                sql = "DELETE FROM messages WHERE session_id = %s"
                cursor.execute(sql, (session_id,))
                
                # 插入新消息
                for msg in messages:
                    sql = "INSERT INTO messages (user_id, session_id, message_type, content, timestamp) VALUES (%s, %s, %s, %s, %s)"
                    timestamp = msg.get('timestamp', datetime.now().isoformat())
                    cursor.execute(sql, (user_id, session_id, msg['type'], msg['content'], timestamp))
                
                connection.commit()
            
            return True
        except Exception as e:
            print(f"保存对话失败: {str(e)}")
            if connection:
                connection.rollback()
            return False
    
    def load_chat(self, username, session_id=None):
        """加载对话历史
        
        Args:
            username: 用户名
            session_id: 会话 ID，如果为空则加载最近的会话
        
        Returns:
            list: 消息列表
        """
        connection = self.get_connection()
        if not connection:
            return []
        try:
            # 获取用户 ID
            user_id = self.get_user_id(username)
            if not user_id:
                return []
            
            if not session_id:
                sessions = self.get_user_sessions(username)
                if sessions:
                    session_id = sessions[0]['id']
                else:
                    return [] # 没有会话，也就没有消息
            
            with connection.cursor() as cursor:
                # 查询消息
                sql = "SELECT message_type as type, content, timestamp FROM messages WHERE session_id = %s ORDER BY timestamp ASC"
                cursor.execute(sql, (session_id,))
                messages = cursor.fetchall()
            
            return messages
        except Exception as e:
            print(f"加载对话失败: {str(e)}")
            return []
    
    def add_message(self, username, message_type, content, session_id=None):
        """添加单条消息
        
        Args:
            username: 用户名
            message_type: 消息类型
            content: 消息内容
            session_id: 会话 ID
        
        Returns:
            bool: 是否添加成功
        """
        connection = self.get_connection()
        if not connection:
            return False
        try:
            # 获取用户 ID
            user_id = self.get_user_id(username)
            if not user_id:
                return False
            
            if not session_id:
                sessions = self.get_user_sessions(username)
                if sessions:
                    session_id = sessions[0]['id']
                else:
                    session_id = self.create_session(username)
            
            with connection.cursor() as cursor:
                # 插入消息
                sql = "INSERT INTO messages (user_id, session_id, message_type, content) VALUES (%s, %s, %s, %s)"
                cursor.execute(sql, (user_id, session_id, message_type, content))
                connection.commit()
            
            return True
        except Exception as e:
            print(f"添加消息失败: {str(e)}")
            if connection:
                connection.rollback()
            return False
    
    def clear_chat(self, username):
        """清空对话历史
        
        Args:
            username: 用户名
        
        Returns:
            bool: 是否清空成功
        """
        connection = self.get_connection()
        if not connection:
            return False
        try:
            # 获取用户 ID
            user_id = self.get_user_id(username)
            if not user_id:
                return False
            
            with connection.cursor() as cursor:
                # 删除消息
                sql = "DELETE FROM messages WHERE user_id = %s"
                cursor.execute(sql, (user_id,))
                connection.commit()
            
            return True
        except Exception as e:
            print(f"清空对话失败: {str(e)}")
            if connection:
                connection.rollback()
            return False
    
    def list_users(self):
        """列出所有用户
        
        Returns:
            list: 用户名列表
        """
        connection = self.get_connection()
        if not connection:
            return []
        try:
            with connection.cursor() as cursor:
                sql = "SELECT username FROM users"
                cursor.execute(sql)
                users = cursor.fetchall()
            
            return [user['username'] for user in users]
        except Exception as e:
            print(f"列出用户失败: {str(e)}")
            return []

    # --- 数学学习相关方法 ---

    def get_math_profile(self, user_id):
        """获取数学学习画像"""
        connection = self.get_connection()
        if not connection:
            return None
        try:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM math_exam_profiles WHERE user_id = %s"
                cursor.execute(sql, (user_id,))
                return cursor.fetchone()
        except Exception as e:
            print(f"获取数学画像失败: {str(e)}")
            return None

    def save_math_profile(self, user_id, exam_name, target_score, exam_date, daily_hours, resources_config):
        """保存数学学习画像"""
        connection = self.get_connection()
        if not connection:
            return False
        try:
            with connection.cursor() as cursor:
                sql = """
                    INSERT INTO math_exam_profiles (user_id, exam_name, target_score, exam_date, daily_hours, resources_config)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                    exam_name = VALUES(exam_name), target_score = VALUES(target_score),
                    exam_date = VALUES(exam_date), daily_hours = VALUES(daily_hours),
                    resources_config = VALUES(resources_config)
                """
                cursor.execute(sql, (user_id, exam_name, target_score, exam_date, daily_hours, json.dumps(resources_config)))
                connection.commit()
                return True
        except Exception as e:
            print(f"保存数学画像失败: {str(e)}")
            if connection:
                connection.rollback()
            return False

    def get_math_kp_mastery(self, user_id):
        """获取用户知识点掌握度"""
        connection = self.get_connection()
        if not connection:
            return []
        try:
            with connection.cursor() as cursor:
                sql = """
                    SELECT kp.id, kp.category, kp.chapter, kp.name, kp.importance, m.mastery, m.last_practiced_at
                    FROM math_knowledge_points kp
                    LEFT JOIN math_user_kp_mastery m ON kp.id = m.kp_id AND m.user_id = %s
                """
                cursor.execute(sql, (user_id,))
                return cursor.fetchall()
        except Exception as e:
            print(f"获取掌握度失败: {str(e)}")
            return []

    def update_kp_mastery(self, user_id, kp_id, mastery_delta):
        """更新知识点掌握度"""
        connection = self.get_connection()
        if not connection:
            return False
        try:
            with connection.cursor() as cursor:
                # 获取当前掌握度
                cursor.execute("SELECT mastery FROM math_user_kp_mastery WHERE user_id = %s AND kp_id = %s", (user_id, kp_id))
                row = cursor.fetchone()
                current_mastery = row['mastery'] if row else 0
                new_mastery = max(0, min(1.0, current_mastery + mastery_delta))
                
                sql = """
                    INSERT INTO math_user_kp_mastery (user_id, kp_id, mastery, last_practiced_at)
                    VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
                    ON DUPLICATE KEY UPDATE
                    mastery = VALUES(mastery), last_practiced_at = CURRENT_TIMESTAMP
                """
                cursor.execute(sql, (user_id, kp_id, new_mastery))
                connection.commit()
                return True
        except Exception as e:
            print(f"更新掌握度失败: {str(e)}")
            if connection:
                connection.rollback()
            return False

    def save_math_attempt(self, user_id, problem_id, self_score, time_spent_sec, user_steps, key_check_result, error_tags):
        """保存作答记录"""
        connection = self.get_connection()
        if not connection:
            return False
        try:
            with connection.cursor() as cursor:
                sql = """
                    INSERT INTO math_problem_attempts (user_id, problem_id, self_score, time_spent_sec, user_steps, key_check_result, error_tags)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (user_id, problem_id, self_score, time_spent_sec, user_steps, 
                                     json.dumps(key_check_result), json.dumps(error_tags)))
                connection.commit()
                return True
        except Exception as e:
            print(f"保存作答记录失败: {str(e)}")
            if connection:
                connection.rollback()
            return False

    def get_due_study_items(self, user_id, limit=20):
        """获取到期需复习的条目 (SM-2)"""
        connection = self.get_connection()
        if not connection:
            return []
        try:
            with connection.cursor() as cursor:
                sql = """
                    SELECT i.*, p.ease_factor, p.interval_days, p.repetition, p.next_review
                    FROM math_study_items i
                    JOIN math_item_progress p ON i.id = p.item_id
                    WHERE i.user_id = %s AND (p.next_review <= CURRENT_TIMESTAMP OR p.next_review IS NULL)
                    ORDER BY p.next_review ASC
                    LIMIT %s
                """
                cursor.execute(sql, (user_id, limit))
                return cursor.fetchall()
        except Exception as e:
            print(f"获取复习条目失败: {str(e)}")
            return []

# 全局存储实例
mysql_storage = MySQLStorage()

if __name__ == "__main__":
    # 测试代码
    storage = MySQLStorage()
    
    # 测试保存对话
    test_messages = [
        {"type": "user", "content": "你好", "timestamp": datetime.now().isoformat()},
        {"type": "ai", "content": "你好，我是 AI 助教", "timestamp": datetime.now().isoformat()}
    ]
    
    print("测试保存对话:")
    result = storage.save_chat("测试用户", test_messages)
    print(f"保存结果: {result}")
    
    print("\n测试加载对话:")
    loaded_messages = storage.load_chat("测试用户")
    print(f"加载的消息数: {len(loaded_messages)}")
    for msg in loaded_messages:
        print(f"{msg['type']}: {msg['content']}")
    
    print("\n测试添加消息:")
    add_result = storage.add_message("测试用户", "user", "如何使用 AI 助教？")
    print(f"添加结果: {add_result}")
    
    print("\n测试列出用户:")
    users = storage.list_users()
    print(f"用户列表: {users}")
    
    print("\n测试清空对话:")
    clear_result = storage.clear_chat("测试用户")
    print(f"清空结果: {clear_result}")
    
    # 关闭连接
    storage.close_connection()
