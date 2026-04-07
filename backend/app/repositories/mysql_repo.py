import pymysql
from typing import Optional, List, Dict, Any
from app.config.settings import settings


class MySQLRepository:
    """MySQL 数据访问仓库"""
    
    def __init__(self):
        """初始化 MySQL 仓库"""
        self.host = settings.DB_HOST
        self.port = settings.DB_PORT
        self.user = settings.DB_USER
        self.password = settings.DB_PASSWORD
        self.database = settings.DB_NAME
        self.connection = None
    
    def get_connection(self) -> Optional[pymysql.Connection]:
        """获取数据库连接
        
        Returns:
            pymysql.Connection: 数据库连接对象
        """
        try:
            if not self.connection or not self.connection.open:
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
            return self.connection
        except Exception as e:
            print(f"⚠️ 数据库连接失败: {str(e)}")
            raise e # Raise exception to crash if real DB fails, as requested "Remove mock data"
    
    def close_connection(self):
        """关闭数据库连接"""
        if self.connection and self.connection.open:
            self.connection.close()
    
    def execute(self, sql: str, params: tuple = ()) -> Optional[List[Dict[str, Any]]]:
        """执行SQL语句
        
        Args:
            sql: SQL语句
            params: SQL参数
        
        Returns:
            Optional[List[Dict[str, Any]]]: 查询结果
        """
        connection = self.get_connection()
        if not connection:
            return None
            
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                if sql.strip().upper().startswith('SELECT'):
                    return cursor.fetchall()
                else:
                    connection.commit()
                    return None
        except Exception as e:
            print(f"执行SQL失败: {str(e)}")
            connection.rollback()
            return None
    
    def fetch_one(self, sql: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
        """执行SQL语句并返回单行结果
        
        Args:
            sql: SQL语句
            params: SQL参数
        
        Returns:
            Optional[Dict[str, Any]]: 单行查询结果
        """
        results = self.execute(sql, params)
        return results[0] if results else None
    
    def fetch_all(self, sql: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """执行SQL语句并返回所有结果
        
        Args:
            sql: SQL语句
            params: SQL参数
        
        Returns:
            List[Dict[str, Any]]: 查询结果列表
        """
        results = self.execute(sql, params)
        return results or []
    
    def execute_many(self, sql: str, params_list: list) -> bool:
        """批量执行SQL语句
        
        Args:
            sql: SQL语句
            params_list: 参数列表
        
        Returns:
            bool: 是否执行成功
        """
        connection = self.get_connection()
        if not connection:
            return False
            
        try:
            with connection.cursor() as cursor:
                cursor.executemany(sql, params_list)
                connection.commit()
                return True
        except Exception as e:
            print(f"批量执行SQL失败: {str(e)}")
            connection.rollback()
            return False


# 创建全局MySQL仓库实例
mysql_repo = MySQLRepository()
