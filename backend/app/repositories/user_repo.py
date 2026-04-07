from typing import List, Dict, Optional, Any
from datetime import datetime
from app.repositories.mysql_repo import mysql_repo


class UserRepository:
    """用户数据访问仓库"""
    
    def get_user_id(self, username: str) -> Optional[int]:
        """获取用户 ID，如果用户不存在则创建
        
        Args:
            username: 用户名
        
        Returns:
            Optional[int]: 用户 ID
        """
        # 检查用户是否存在
        sql = "SELECT id FROM users WHERE username = %s"
        user = mysql_repo.fetch_one(sql, (username,))
        
        if user:
            return user['id']
        else:
            # 创建新用户
            sql = "INSERT INTO users (username) VALUES (%s)"
            mysql_repo.execute(sql, (username,))
            # 获取新创建的用户 ID
            sql = "SELECT id FROM users WHERE username = %s"
            user = mysql_repo.fetch_one(sql, (username,))
            return user['id'] if user else None

    def _create_session(self, user_id: int, name: Optional[str] = None) -> Optional[int]:
        """为用户创建新会话"""
        if not name:
            name = f"会话 {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        sql = "INSERT INTO sessions (user_id, name) VALUES (%s, %s)"
        mysql_repo.execute(sql, (user_id, name))
        # 返回新会话 ID
        sql = "SELECT LAST_INSERT_ID() as id"
        result = mysql_repo.fetch_one(sql)
        return result['id'] if result else None

    def _resolve_session_id(self, user_id: int, session_id: Optional[int], create_if_missing: bool = True) -> Optional[int]:
        """确保会话 ID 可用并属于当前用户"""
        if session_id:
            sql = "SELECT id FROM sessions WHERE id = %s AND user_id = %s"
            exists = mysql_repo.fetch_one(sql, (session_id, user_id))
            if exists:
                return session_id
        # 找最近会话
        sql = "SELECT id FROM sessions WHERE user_id = %s ORDER BY created_at DESC LIMIT 1"
        latest = mysql_repo.fetch_one(sql, (user_id,))
        if latest:
            return latest['id']
        # 如果允许则创建新会话
        if create_if_missing:
            return self._create_session(user_id)
        return None

    def get_user_sessions(self, username: str) -> List[Dict[str, Any]]:
        """获取用户的会话列表"""
        user_id = self.get_user_id(username)
        if not user_id:
            return []
        sql = "SELECT id, name, created_at FROM sessions WHERE user_id = %s ORDER BY created_at DESC"
        return mysql_repo.fetch_all(sql, (user_id,))

    def create_session(self, username: str, name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """创建新会话"""
        user_id = self.get_user_id(username)
        if not user_id:
            return None
        session_id = self._create_session(user_id, name)
        if not session_id:
            return None
        sql = "SELECT id, name, created_at FROM sessions WHERE id = %s AND user_id = %s"
        return mysql_repo.fetch_one(sql, (session_id, user_id))

    def delete_session(self, username: str, session_id: int) -> bool:
        """删除指定会话及其消息"""
        user_id = self.get_user_id(username)
        if not user_id:
            return False
        sql = "SELECT id FROM sessions WHERE id = %s AND user_id = %s"
        exists = mysql_repo.fetch_one(sql, (session_id, user_id))
        if not exists:
            return False
        mysql_repo.execute("DELETE FROM messages WHERE session_id = %s", (session_id,))
        mysql_repo.execute("DELETE FROM sessions WHERE id = %s AND user_id = %s", (session_id, user_id))
        return True

    def get_session_messages(self, username: str, session_id: int) -> List[Dict[str, Any]]:
        """获取指定会话的消息列表"""
        user_id = self.get_user_id(username)
        if not user_id:
            return []
        sql = "SELECT id FROM sessions WHERE id = %s AND user_id = %s"
        exists = mysql_repo.fetch_one(sql, (session_id, user_id))
        if not exists:
            return []
        sql = "SELECT message_type as type, content, timestamp FROM messages WHERE session_id = %s ORDER BY timestamp ASC"
        return mysql_repo.fetch_all(sql, (session_id,))
    
    def save_chat(self, username: str, messages: List[Dict[str, Any]], session_id: Optional[int] = None, session_name: Optional[str] = None) -> bool:
        """保存对话历史
        
        Args:
            username: 用户名
            messages: 消息列表
            session_id: 会话 ID
            session_name: 会话名称，可选
        
        Returns:
            bool: 是否保存成功
        """
        user_id = self.get_user_id(username)
        if not user_id:
            return False
        
        # 确认会话 ID
        session_id = self._resolve_session_id(user_id, session_id)
        if not session_id:
            session_id = self._create_session(user_id, session_name)
        if not session_id:
            return False
        
        # 只清空当前会话的消息
        sql = "DELETE FROM messages WHERE session_id = %s"
        mysql_repo.execute(sql, (session_id,))
        
        # 批量插入新消息
        if messages:
            sql = "INSERT INTO messages (user_id, session_id, message_type, content, timestamp) VALUES (%s, %s, %s, %s, %s)"
            params_list = []
            for msg in messages:
                timestamp = msg.get('timestamp', datetime.now().isoformat())
                params_list.append((user_id, session_id, msg['type'], msg['content'], timestamp))
            return mysql_repo.execute_many(sql, params_list)
        
        return True
    
    def load_chat(self, username: str, session_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """按会话加载对话历史
        
        Args:
            username: 用户名
            session_id: 会话 ID，可为空则取最近会话
        
        Returns:
            List[Dict[str, Any]]: 消息列表
        """
        user_id = self.get_user_id(username)
        if not user_id:
            return []
        
        session_id = self._resolve_session_id(user_id, session_id, create_if_missing=False)
        if not session_id:
            return []
        
        # 查询消息
        sql = "SELECT message_type as type, content, timestamp FROM messages WHERE session_id = %s ORDER BY timestamp ASC"
        return mysql_repo.fetch_all(sql, (session_id,))
    
    def add_message(self, username: str, message_type: str, content: str, session_id: Optional[int] = None) -> bool:
        """添加单条消息
        
        Args:
            username: 用户名
            message_type: 消息类型
            content: 消息内容
            session_id: 会话 ID
        
        Returns:
            bool: 是否添加成功
        """
        user_id = self.get_user_id(username)
        if not user_id:
            return False
        
        session_id = self._resolve_session_id(user_id, session_id)
        if not session_id:
            return False
        
        # 插入消息
        sql = "INSERT INTO messages (user_id, session_id, message_type, content) VALUES (%s, %s, %s, %s)"
        mysql_repo.execute(sql, (user_id, session_id, message_type, content))
        return True
    
    def clear_chat(self, username: str) -> bool:
        """清空对话历史
        
        Args:
            username: 用户名
        
        Returns:
            bool: 是否清空成功
        """
        user_id = self.get_user_id(username)
        if not user_id:
            return False
        
        # 删除消息
        sql = "DELETE FROM messages WHERE user_id = %s"
        mysql_repo.execute(sql, (user_id,))
        return True
    
    def get_all_users(self) -> List[Dict[str, Any]]:
        """获取所有用户
        
        Returns:
            List[Dict[str, Any]]: 用户列表
        """
        sql = "SELECT * FROM users ORDER BY created_at DESC"
        return mysql_repo.fetch_all(sql)
    
    def get_user_messages(self, username: str) -> List[Dict[str, Any]]:
        """获取用户的对话消息
        
        Args:
            username: 用户名
        
        Returns:
            List[Dict[str, Any]]: 消息列表
        """
        user_id = self.get_user_id(username)
        if not user_id:
            return []
        
        # 获取用户消息
        sql = "SELECT * FROM messages WHERE user_id = %s ORDER BY timestamp ASC"
        return mysql_repo.fetch_all(sql, (user_id,))
    
    def delete_user(self, username: str) -> bool:
        """删除用户及其所有消息
        
        Args:
            username: 用户名
        
        Returns:
            bool: 是否删除成功
        """
        user_id = self.get_user_id(username)
        if not user_id:
            return False
        
        # 删除用户（级联删除会自动删除相关消息）
        sql = "DELETE FROM users WHERE id = %s"
        mysql_repo.execute(sql, (user_id,))
        return True
    
    def delete_message(self, message_id: int) -> bool:
        """删除单条消息
        
        Args:
            message_id: 消息 ID
        
        Returns:
            bool: 是否删除成功
        """
        sql = "DELETE FROM messages WHERE id = %s"
        mysql_repo.execute(sql, (message_id,))
        return True
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计数据
        
        Returns:
            Dict[str, Any]: 统计数据
        """
        stats = {}
        
        # 总用户数
        sql = "SELECT COUNT(*) as count FROM users"
        result = mysql_repo.fetch_one(sql)
        stats['total_users'] = result['count'] if result else 0
        
        # 总消息数
        sql = "SELECT COUNT(*) as count FROM messages"
        result = mysql_repo.fetch_one(sql)
        stats['total_messages'] = result['count'] if result else 0
        
        # 活跃用户数（最近7天有消息的用户）
        sql = """
        SELECT COUNT(DISTINCT user_id) as count 
        FROM messages 
        WHERE timestamp >= NOW() - INTERVAL 7 DAY
        """
        result = mysql_repo.fetch_one(sql)
        stats['active_users'] = result['count'] if result else 0
        
        # 消息类型分布
        sql = """
        SELECT 
            message_type, 
            COUNT(*) as count 
        FROM messages 
        GROUP BY message_type
        """
        message_types = mysql_repo.fetch_all(sql)
        stats['message_types'] = {}
        for item in message_types:
            stats['message_types'][item['message_type']] = item['count']
        
        # 今日消息数
        sql = """
        SELECT COUNT(*) as count 
        FROM messages 
        WHERE DATE(timestamp) = DATE(NOW())
        """
        result = mysql_repo.fetch_one(sql)
        stats['today_messages'] = result['count'] if result else 0
        
        return stats
    
    def clean_all_data(self) -> bool:
        """清空所有数据
        
        Returns:
            bool: 是否清空成功
        """
        # 删除所有消息
        sql = "DELETE FROM messages"
        mysql_repo.execute(sql)
        
        # 删除所有用户
        sql = "DELETE FROM users"
        mysql_repo.execute(sql)
        
        return True


# 创建全局用户仓库实例
user_repo = UserRepository()
