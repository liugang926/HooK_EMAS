"""
企业微信适配器 - WeWork Adapter

企业微信平台集成实现
"""
import requests
import logging
from typing import Dict, List, Any

from .base import BasePlatformAdapter

logger = logging.getLogger(__name__)


class WeWorkAdapter(BasePlatformAdapter):
    """
    企业微信适配器
    
    实现企业微信相关的API集成:
    - 获取用户信息
    - 发送应用消息
    - 获取部门/用户列表
    - 同步组织架构
    """
    
    PLATFORM_NAME = 'wework'
    BASE_URL = 'https://qyapi.weixin.qq.com/cgi-bin'
    
    def __init__(self, corp_id: str, agent_id: str, secret: str):
        """
        初始化企业微信适配器
        
        Args:
            corp_id: 企业ID
            agent_id: 应用ID
            secret: 应用密钥
        """
        super().__init__(corp_id=corp_id, app_secret=secret)
        self.agent_id = agent_id
    
    def _fetch_access_token(self) -> Dict[str, Any]:
        """获取企业微信 AccessToken"""
        url = f"{self.BASE_URL}/gettoken"
        params = {
            'corpid': self.corp_id,
            'corpsecret': self.app_secret
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if data.get('errcode', 0) != 0:
                logger.error(f"[WeWork] 获取Token失败: {data}")
                raise Exception(f"获取Token失败: {data.get('errmsg')}")
            
            return {
                'access_token': data.get('access_token', ''),
                'expires_in': data.get('expires_in', 7200)
            }
        except Exception as e:
            logger.error(f"[WeWork] 获取Token异常: {str(e)}")
            raise
    
    def get_user_info(self, user_id: str) -> Dict[str, Any]:
        """
        获取企业微信用户信息
        
        Args:
            user_id: 企业微信用户ID
            
        Returns:
            用户信息
        """
        token = self.get_access_token()
        url = f"{self.BASE_URL}/user/get"
        params = {
            'access_token': token,
            'userid': user_id
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if data.get('errcode', 0) != 0:
                logger.error(f"[WeWork] 获取用户信息失败: {data}")
                return {}
            
            return {
                'user_id': data.get('userid'),
                'name': data.get('name'),
                'email': data.get('email'),
                'mobile': data.get('mobile'),
                'department': data.get('department', []),
                'position': data.get('position'),
                'avatar': data.get('avatar'),
                'status': data.get('status')
            }
        except Exception as e:
            logger.error(f"[WeWork] 获取用户信息异常: {str(e)}")
            return {}
    
    def send_notification(self, user_ids: List[str], message: Dict) -> Dict[str, Any]:
        """
        发送企业微信应用消息
        
        Args:
            user_ids: 用户ID列表
            message: 消息内容 {'type': 'text/markdown/...', 'content': '...'}
            
        Returns:
            发送结果
        """
        token = self.get_access_token()
        url = f"{self.BASE_URL}/message/send"
        
        msg_type = message.get('type', 'text')
        content = message.get('content', '')
        
        payload = {
            'touser': '|'.join(user_ids),
            'agentid': self.agent_id,
            'msgtype': msg_type,
        }
        
        if msg_type == 'text':
            payload['text'] = {'content': content}
        elif msg_type == 'markdown':
            payload['markdown'] = {'content': content}
        elif msg_type == 'textcard':
            payload['textcard'] = message.get('textcard', {})
        
        try:
            response = requests.post(
                f"{url}?access_token={token}",
                json=payload,
                timeout=10
            )
            data = response.json()
            
            if data.get('errcode', 0) != 0:
                logger.error(f"[WeWork] 发送消息失败: {data}")
                return {'success': False, 'error': data.get('errmsg')}
            
            return {'success': True, 'invaliduser': data.get('invaliduser', '')}
        except Exception as e:
            logger.error(f"[WeWork] 发送消息异常: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_department_list(self, parent_id: int = None) -> List[Dict]:
        """
        获取部门列表
        
        Args:
            parent_id: 父部门ID（可选）
            
        Returns:
            部门列表
        """
        token = self.get_access_token()
        url = f"{self.BASE_URL}/department/list"
        params = {'access_token': token}
        if parent_id is not None:
            params['id'] = parent_id
        
        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if data.get('errcode', 0) != 0:
                logger.error(f"[WeWork] 获取部门列表失败: {data}")
                return []
            
            return [
                {
                    'id': dept.get('id'),
                    'name': dept.get('name'),
                    'parentid': dept.get('parentid'),
                    'order': dept.get('order')
                }
                for dept in data.get('department', [])
            ]
        except Exception as e:
            logger.error(f"[WeWork] 获取部门列表异常: {str(e)}")
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
        url = f"{self.BASE_URL}/user/list"
        params = {
            'access_token': token,
            'department_id': department_id,
            'fetch_child': 1
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            data = response.json()
            
            if data.get('errcode', 0) != 0:
                logger.error(f"[WeWork] 获取用户列表失败: {data}")
                return []
            
            return [
                {
                    'user_id': user.get('userid'),
                    'name': user.get('name'),
                    'email': user.get('email'),
                    'mobile': user.get('mobile'),
                    'department': user.get('department', []),
                    'position': user.get('position'),
                    'status': user.get('status')
                }
                for user in data.get('userlist', [])
            ]
        except Exception as e:
            logger.error(f"[WeWork] 获取用户列表异常: {str(e)}")
            return []
