"""
飞书适配器 - Feishu Adapter

飞书平台集成实现
"""
import requests
import logging
from typing import Dict, List, Any

from .base import BasePlatformAdapter

logger = logging.getLogger(__name__)


class FeishuAdapter(BasePlatformAdapter):
    """
    飞书适配器
    
    实现飞书相关的API集成:
    - 获取用户信息
    - 发送消息
    - 获取部门/用户列表
    """
    
    PLATFORM_NAME = 'feishu'
    BASE_URL = 'https://open.feishu.cn/open-apis'
    
    def __init__(self, app_id: str, app_secret: str):
        """
        初始化飞书适配器
        
        Args:
            app_id: 应用ID
            app_secret: 应用密钥
        """
        super().__init__(app_key=app_id, app_secret=app_secret)
        self.app_id = app_id
    
    def _fetch_access_token(self) -> Dict[str, Any]:
        """获取飞书 tenant_access_token"""
        url = f"{self.BASE_URL}/auth/v3/tenant_access_token/internal"
        payload = {
            'app_id': self.app_id,
            'app_secret': self.app_secret
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            data = response.json()
            
            if data.get('code', 0) != 0:
                logger.error(f"[Feishu] 获取Token失败: {data}")
                raise Exception(f"获取Token失败: {data.get('msg')}")
            
            return {
                'access_token': data.get('tenant_access_token', ''),
                'expires_in': data.get('expire', 7200)
            }
        except Exception as e:
            logger.error(f"[Feishu] 获取Token异常: {str(e)}")
            raise
    
    def _get_auth_header(self) -> Dict:
        """获取认证头"""
        token = self.get_access_token()
        return {'Authorization': f'Bearer {token}'}
    
    def get_user_info(self, user_id: str) -> Dict[str, Any]:
        """
        获取飞书用户信息
        
        Args:
            user_id: 飞书用户ID (open_id 或 user_id)
            
        Returns:
            用户信息
        """
        url = f"{self.BASE_URL}/contact/v3/users/{user_id}"
        
        try:
            response = requests.get(
                url,
                headers=self._get_auth_header(),
                params={'user_id_type': 'open_id'},
                timeout=10
            )
            data = response.json()
            
            if data.get('code', 0) != 0:
                logger.error(f"[Feishu] 获取用户信息失败: {data}")
                return {}
            
            user = data.get('data', {}).get('user', {})
            return {
                'user_id': user.get('user_id'),
                'open_id': user.get('open_id'),
                'name': user.get('name'),
                'email': user.get('email'),
                'mobile': user.get('mobile'),
                'department': user.get('department_ids', []),
                'job_title': user.get('job_title'),
                'avatar': user.get('avatar', {}).get('avatar_origin'),
                'status': user.get('status', {})
            }
        except Exception as e:
            logger.error(f"[Feishu] 获取用户信息异常: {str(e)}")
            return {}
    
    def send_notification(self, user_ids: List[str], message: Dict) -> Dict[str, Any]:
        """
        发送飞书消息
        
        Args:
            user_ids: 用户ID列表 (open_id)
            message: 消息内容 {'type': 'text/post/...', 'content': '...'}
            
        Returns:
            发送结果
        """
        url = f"{self.BASE_URL}/im/v1/messages"
        
        msg_type = message.get('type', 'text')
        content = message.get('content', '')
        
        results = []
        for user_id in user_ids:
            payload = {
                'receive_id': user_id,
                'msg_type': msg_type,
            }
            
            if msg_type == 'text':
                payload['content'] = f'{{"text": "{content}"}}'
            elif msg_type == 'post':
                payload['content'] = content  # 应该是富文本JSON
            
            try:
                response = requests.post(
                    url,
                    headers=self._get_auth_header(),
                    params={'receive_id_type': 'open_id'},
                    json=payload,
                    timeout=10
                )
                data = response.json()
                
                if data.get('code', 0) != 0:
                    results.append({'user_id': user_id, 'success': False, 'error': data.get('msg')})
                else:
                    results.append({'user_id': user_id, 'success': True})
            except Exception as e:
                results.append({'user_id': user_id, 'success': False, 'error': str(e)})
        
        success_count = sum(1 for r in results if r['success'])
        return {
            'success': success_count == len(user_ids),
            'total': len(user_ids),
            'success_count': success_count,
            'results': results
        }
    
    def get_department_list(self, parent_id: str = '0') -> List[Dict]:
        """
        获取部门列表
        
        Args:
            parent_id: 父部门ID ('0' 表示根部门)
            
        Returns:
            部门列表
        """
        url = f"{self.BASE_URL}/contact/v3/departments/{parent_id}/children"
        
        try:
            response = requests.get(
                url,
                headers=self._get_auth_header(),
                params={'department_id_type': 'department_id'},
                timeout=10
            )
            data = response.json()
            
            if data.get('code', 0) != 0:
                logger.error(f"[Feishu] 获取部门列表失败: {data}")
                return []
            
            items = data.get('data', {}).get('items', [])
            return [
                {
                    'id': dept.get('department_id'),
                    'name': dept.get('name'),
                    'parentid': dept.get('parent_department_id'),
                    'order': dept.get('order', 0)
                }
                for dept in items
            ]
        except Exception as e:
            logger.error(f"[Feishu] 获取部门列表异常: {str(e)}")
            return []
    
    def get_user_list(self, department_id: str = '0') -> List[Dict]:
        """
        获取部门用户列表
        
        Args:
            department_id: 部门ID
            
        Returns:
            用户列表
        """
        url = f"{self.BASE_URL}/contact/v3/users/find_by_department"
        
        try:
            response = requests.get(
                url,
                headers=self._get_auth_header(),
                params={
                    'department_id': department_id,
                    'department_id_type': 'department_id',
                    'page_size': 50
                },
                timeout=30
            )
            data = response.json()
            
            if data.get('code', 0) != 0:
                logger.error(f"[Feishu] 获取用户列表失败: {data}")
                return []
            
            items = data.get('data', {}).get('items', [])
            return [
                {
                    'user_id': user.get('user_id'),
                    'open_id': user.get('open_id'),
                    'name': user.get('name'),
                    'email': user.get('email'),
                    'mobile': user.get('mobile'),
                    'department': user.get('department_ids', []),
                    'job_title': user.get('job_title'),
                    'status': user.get('status', {})
                }
                for user in items
            ]
        except Exception as e:
            logger.error(f"[Feishu] 获取用户列表异常: {str(e)}")
            return []
