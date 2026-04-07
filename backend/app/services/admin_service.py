from typing import List, Dict, Optional
from app.repositories.user_repo import user_repo


class AdminService:
    """管理员业务服务"""
    
    def get_users(self) -> List[Dict]:
        """获取所有用户
        
        Returns:
            List[Dict]: 用户列表
        """
        return user_repo.get_all_users()
    
    def get_user_messages(self, username: str) -> List[Dict]:
        """获取用户的对话消息
        
        Args:
            username: 用户名
        
        Returns:
            List[Dict]: 消息列表
        """
        return user_repo.get_user_messages(username)
    
    def delete_user(self, username: str) -> bool:
        """删除用户及其所有消息
        
        Args:
            username: 用户名
        
        Returns:
            bool: 是否删除成功
        """
        return user_repo.delete_user(username)
    
    def delete_message(self, message_id: int) -> bool:
        """删除单条消息
        
        Args:
            message_id: 消息 ID
        
        Returns:
            bool: 是否删除成功
        """
        return user_repo.delete_message(message_id)
    
    def get_stats(self) -> Dict:
        """获取统计数据
        
        Returns:
            Dict: 统计数据
        """
        return user_repo.get_stats()
    
    def clean_all_data(self) -> bool:
        """清空所有数据
        
        Returns:
            bool: 是否清空成功
        """
        return user_repo.clean_all_data()


# 创建全局管理员服务实例
admin_service = AdminService()
