"""
平台适配器基类

遵循 .cursorrules 规约:
- 新增集成平台时，必须继承 BasePlatformAdapter 类
- 必须实现 get_user_info 和 send_notification 方法
- 第三方系统的 AccessToken 必须存储在 Redis 中并设置过期时间
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)


class BasePlatformAdapter(ABC):
    """
    平台适配器基类
    
    所有第三方平台集成必须继承此类并实现抽象方法
    
    遵循 .cursorrules:
    - AccessToken 必须存储在 Redis 中并设置过期时间
    - 统一接口规范
    """
    
    # 平台标识，子类必须重写
    PLATFORM_NAME: str = ''
    
    # Token 缓存前缀
    TOKEN_CACHE_PREFIX: str = 'platform_token:'
    
    # Token 默认过期时间（秒），预留5分钟缓冲
    TOKEN_EXPIRE_BUFFER: int = 300
    
    def __init__(self, corp_id: str = None, app_key: str = None, app_secret: str = None):
        """
        初始化适配器
        
        Args:
            corp_id: 企业ID
            app_key: 应用Key
            app_secret: 应用密钥
        """
        self.corp_id = corp_id
        self.app_key = app_key
        self.app_secret = app_secret
    
    @property
    def token_cache_key(self) -> str:
        """生成 Token 缓存 Key"""
        return f"{self.TOKEN_CACHE_PREFIX}{self.PLATFORM_NAME}:{self.corp_id}"
    
    def get_access_token(self) -> str:
        """
        获取 AccessToken（带缓存）
        
        遵循 .cursorrules: 第三方系统的 AccessToken 必须存储在 Redis 中并设置过期时间
        
        Returns:
            AccessToken 字符串
        """
        # 先从缓存获取
        cached_token = cache.get(self.token_cache_key)
        if cached_token:
            return cached_token
        
        # 缓存未命中，获取新 Token
        token_data = self._fetch_access_token()
        token = token_data.get('access_token', '')
        expires_in = token_data.get('expires_in', 7200)
        
        # 存入 Redis，预留缓冲时间
        cache_timeout = max(expires_in - self.TOKEN_EXPIRE_BUFFER, 60)
        cache.set(self.token_cache_key, token, timeout=cache_timeout)
        
        logger.info(f"[{self.PLATFORM_NAME}] AccessToken 已刷新, 有效期: {cache_timeout}s")
        return token
    
    def clear_token_cache(self) -> None:
        """清除 Token 缓存"""
        cache.delete(self.token_cache_key)
        logger.info(f"[{self.PLATFORM_NAME}] AccessToken 缓存已清除")
    
    @abstractmethod
    def _fetch_access_token(self) -> Dict[str, Any]:
        """
        从平台 API 获取 AccessToken
        
        子类必须实现此方法
        
        Returns:
            {'access_token': str, 'expires_in': int}
        """
        pass
    
    @abstractmethod
    def get_user_info(self, user_id: str) -> Dict[str, Any]:
        """
        获取用户信息
        
        遵循 .cursorrules: 必须实现此方法
        
        Args:
            user_id: 用户ID
            
        Returns:
            用户信息字典
        """
        pass
    
    @abstractmethod
    def send_notification(self, user_ids: List[str], message: Dict) -> Dict[str, Any]:
        """
        发送通知消息
        
        遵循 .cursorrules: 必须实现此方法
        
        Args:
            user_ids: 用户ID列表
            message: 消息内容
            
        Returns:
            发送结果
        """
        pass
    
    def get_department_list(self) -> List[Dict]:
        """
        获取部门列表（可选实现）
        
        Returns:
            部门列表
        """
        raise NotImplementedError(f"{self.PLATFORM_NAME} 未实现部门列表获取")
    
    def get_user_list(self, department_id: str = None) -> List[Dict]:
        """
        获取用户列表（可选实现）
        
        Args:
            department_id: 部门ID（可选）
            
        Returns:
            用户列表
        """
        raise NotImplementedError(f"{self.PLATFORM_NAME} 未实现用户列表获取")
    
    def sync_organization(self) -> Dict[str, Any]:
        """
        同步组织架构（可选实现）
        
        Returns:
            同步结果
        """
        raise NotImplementedError(f"{self.PLATFORM_NAME} 未实现组织架构同步")
