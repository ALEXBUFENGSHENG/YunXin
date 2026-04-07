import pymysql
import os

# 配置
host = os.getenv('MYSQL_HOST', 'localhost')
user = os.getenv('MYSQL_USER', 'root')
password = os.getenv('MYSQL_PASSWORD', '@wqng15390441586')
database = os.getenv('MYSQL_DATABASE', 'ai_assistant')

def update_database():
    try:
        connection = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        with connection.cursor() as cursor:
            # 1. 创建 sessions 表
            print("正在创建 sessions 表...")
            sql_create_sessions = """
            CREATE TABLE IF NOT EXISTS sessions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                name VARCHAR(255) NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
            cursor.execute(sql_create_sessions)
            
            # 2. 检查 messages 表是否有 session_id 列
            cursor.execute("SHOW COLUMNS FROM messages LIKE 'session_id'")
            result = cursor.fetchone()
            
            if not result:
                print("正在向 messages 表添加 session_id 列...")
                # 先添加列，允许为空
                sql_alter_messages = """
                ALTER TABLE messages ADD COLUMN session_id INT
                """
                cursor.execute(sql_alter_messages)
                
                # 添加外键约束
                # 注意：现有数据 session_id 为 NULL，这没问题
                sql_add_fk = """
                ALTER TABLE messages ADD CONSTRAINT fk_messages_session 
                FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
                """
                cursor.execute(sql_add_fk)
            else:
                print("messages 表已包含 session_id 列。")

        connection.commit()
        print("数据库更新成功！")
        
    except Exception as e:
        print(f"数据库更新失败: {e}")
    finally:
        if 'connection' in locals() and connection:
            connection.close()

if __name__ == "__main__":
    update_database()
