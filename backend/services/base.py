"""
服务层基类

提供统一的服务层模式和工具方法
"""
from django.db import transaction
from typing import Any, Dict, Optional
import uuid
from django.utils import timezone


class BaseService:
    """
    服务层基类
    
    所有业务服务应继承此类，获得：
    - 事务管理装饰器
    - 通用工具方法
    - 统一的错误处理
    """
    
    @staticmethod
    def generate_order_no(prefix: str) -> str:
        """
        生成业务单号
        
        格式: 前缀 + 日期 + 8位UUID
        例: LY20260108ABCD1234
        
        Args:
            prefix: 单号前缀 (LY=领用, JY=借用, DB=调拨, CZ=处置, WB=维保)
        
        Returns:
            生成的单号
        """
        return f"{prefix}{timezone.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:8].upper()}"
    
    @staticmethod
    def get_user_company(user, company_id=None):
        """
        获取用户所属公司
        
        Args:
            user: 用户对象
            company_id: 显式指定的公司ID (可选)
            
        Returns:
            公司对象，优先级: 
            1. company_id (如果存在且有效)
            2. user.current_company_id (当前会话公司)
            3. user.company (用户归属公司)
            4. Company.objects.first() (默认公司)
        """
        from apps.organizations.models import Company
        
        # 1. 尝试使用显式指定的 company_id
        if company_id:
            try:
                company = Company.objects.get(id=company_id)
                if company:
                    return company
            except Company.DoesNotExist:
                pass
                
        # 2. 尝试使用当前会话公司 (current_company_id)
        current_company_id = getattr(user, 'current_company_id', None)
        if current_company_id:
            try:
                company = Company.objects.get(id=current_company_id)
                if company:
                    return company
            except Company.DoesNotExist:
                pass
        
        # 3. 尝试使用用户归属公司
        if hasattr(user, 'company') and user.company:
            return user.company
            
        # 4. 默认返回第一个公司
        return Company.objects.first()
    
    @classmethod
    def with_transaction(cls, func):
        """
        事务装饰器 - 包装方法使用数据库事务
        
        遵循 .cursorrules: 涉及多表更新的操作必须包裹在 @transaction.atomic 装饰器中
        """
        def wrapper(*args, **kwargs):
            with transaction.atomic():
                return func(*args, **kwargs)
        return wrapper
