"""
钉钉适配器 - DingTalk Adapter

钉钉平台集成实现
"""
import requests
import logging
from typing import Dict, List, Any

from .base import BasePlatformAdapter

logger = logging.getLogger(__name__)


class DingTalkAdapter(BasePlatformAdapter):
    """
    钉钉适配器
    
    实现钉钉相关的API集成:
    - 获取用户信息
    - 发送工作通知
    - 获取部门/用户列表
    """
    
    PLATFORM_NAME = 'dingtalk'
    BASE_URL = 'https://oapi.dingtalk.com'
    
    def __init__(self, app_key: str, app_secret: str, agent_id: str = None):
        """
        初始化钉钉适配器
        
        Args:
            app_key: 应用AppKey
            app_secret: 应用AppSecret
            agent_id: 应用AgentId（发送消息时需要）
        """
        super().__init__(app_key=app_key, app_secret=app_secret)
        self.agent_id = agent_id
    
    def _fetch_access_token(self) -> Dict[str, Any]:
        """获取钉钉 AccessToken"""
        url = f"{self.BASE_URL}/gettoken"
        params = {
            'appkey': self.app_key,
            'appsecret': self.app_secret
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if data.get('errcode', 0) != 0:
                logger.error(f"[DingTalk] 获取Token失败: {data}")
                raise Exception(f"获取Token失败: {data.get('errmsg')}")
            
            return {
                'access_token': data.get('access_token', ''),
                'expires_in': data.get('expires_in', 7200)
            }
        except Exception as e:
            logger.error(f"[DingTalk] 获取Token异常: {str(e)}")
            raise
    
    def get_user_info(self, user_id: str) -> Dict[str, Any]:
        """
        获取钉钉用户信息
        
        Args:
            user_id: 钉钉用户ID
            
        Returns:
            用户信息
        """
        token = self.get_access_token()
        url = f"{self.BASE_URL}/topapi/v2/user/get"
        
        try:
            response = requests.post(
                f"{url}?access_token={token}",
                json={'userid': user_id},
                timeout=10
            )
            data = response.json()
            
            if data.get('errcode', 0) != 0:
                logger.error(f"[DingTalk] 获取用户信息失败: {data}")
                return {}
            
            result = data.get('result', {})
            return {
                'user_id': result.get('userid'),
                'name': result.get('name'),
                'email': result.get('email'),
                'mobile': result.get('mobile'),
                'department': result.get('dept_id_list', []),
                'title': result.get('title'),
                'avatar': result.get('avatar'),
                'active': result.get('active', True)
            }
        except Exception as e:
            logger.error(f"[DingTalk] 获取用户信息异常: {str(e)}")
            return {}
    
    def send_notification(self, user_ids: List[str], message: Dict) -> Dict[str, Any]:
        """
        发送钉钉工作通知
        
        Args:
            user_ids: 用户ID列表
            message: 消息内容 {'type': 'text/markdown/...', 'content': '...'}
            
        Returns:
            发送结果
        """
        token = self.get_access_token()
        url = f"{self.BASE_URL}/topapi/message/corpconversation/asyncsend_v2"
        
        msg_type = message.get('type', 'text')
        content = message.get('content', '')
        
        msg = {}
        if msg_type == 'text':
            msg = {'msgtype': 'text', 'text': {'content': content}}
        elif msg_type == 'markdown':
            msg = {
                'msgtype': 'markdown',
                'markdown': {
                    'title': message.get('title', '通知'),
                    'text': content
                }
            }
        
        payload = {
            'agent_id': self.agent_id,
            'userid_list': ','.join(user_ids),
            'msg': msg
        }
        
        try:
            response = requests.post(
                f"{url}?access_token={token}",
                json=payload,
                timeout=10
            )
            data = response.json()
            
            if data.get('errcode', 0) != 0:
                logger.error(f"[DingTalk] 发送消息失败: {data}")
                return {'success': False, 'error': data.get('errmsg')}
            
            return {'success': True, 'task_id': data.get('task_id')}
        except Exception as e:
            logger.error(f"[DingTalk] 发送消息异常: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_department_list(self, parent_id: int = 1) -> List[Dict]:
        """
        获取部门列表
        
        Args:
            parent_id: 父部门ID
            
        Returns:
            部门列表
        """
        token = self.get_access_token()
        url = f"{self.BASE_URL}/topapi/v2/department/listsub"
        
        try:
            response = requests.post(
                f"{url}?access_token={token}",
                json={'dept_id': parent_id},
                timeout=10
            )
            data = response.json()
            
            if data.get('errcode', 0) != 0:
                logger.error(f"[DingTalk] 获取部门列表失败: {data}")
                return []
            
            return [
                {
                    'id': dept.get('dept_id'),
                    'name': dept.get('name'),
                    'parentid': dept.get('parent_id'),
                    'order': dept.get('order', 0)
                }
                for dept in data.get('result', [])
            ]
        except Exception as e:
            logger.error(f"[DingTalk] 获取部门列表异常: {str(e)}")
            return []
    
    def get_user_list(self, department_id: int = 1) -> List[Dict]:
        """
        获取部门用户列表
        
        Args:
            department_id: 部门ID
            
        Returns:
            用户列表
        """
        token = self.get_access_token()
        url = f"{self.BASE_URL}/topapi/v2/user/list"
        
        try:
            response = requests.post(
                f"{url}?access_token={token}",
                json={
                    'dept_id': department_id,
                    'cursor': 0,
                    'size': 100
                },
                timeout=30
            )
            data = response.json()
            
            if data.get('errcode', 0) != 0:
                logger.error(f"[DingTalk] 获取用户列表失败: {data}")
                return []
            
            result = data.get('result', {})
            return [
                {
                    'user_id': user.get('userid'),
                    'name': user.get('name'),
                    'email': user.get('email'),
                    'mobile': user.get('mobile'),
                    'department': user.get('dept_id_list', []),
                    'title': user.get('title'),
                    'active': user.get('active', True)
                }
                for user in result.get('list', [])
            ]
        except Exception as e:
            logger.error(f"[DingTalk] 获取用户列表异常: {str(e)}")
            return []
