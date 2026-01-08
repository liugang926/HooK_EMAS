import requests
import json
from urllib.parse import urlencode
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from apps.accounts.models import User, UserDepartment
from apps.organizations.models import Department
from .models import SSOUserBinding


class BaseSSOService:
    """SSO服务基类"""
    
    def __init__(self, config):
        self.config = config
        self.company = config.company if config else None
    
    def get_auth_url(self, redirect_uri):
        raise NotImplementedError
    
    def get_user_info(self, code):
        raise NotImplementedError
    
    def get_or_create_user(self, user_info):
        raise NotImplementedError
    
    def sync_organization(self, options=None):
        """
        同步组织架构
        options: {
            'sync_type': 'full' | 'incremental',  # 同步类型
            'clear_existing': False,  # 是否清空现有数据
            'sync_departments': True,  # 是否同步部门
            'sync_users': True,  # 是否同步用户
            'sync_managers': True,  # 是否同步部门负责人
        }
        """
        raise NotImplementedError
    
    def clear_existing_data(self):
        """清空现有组织架构数据"""
        if not self.company:
            return
        
        with transaction.atomic():
            # 获取该公司下所有部门的ID
            dept_ids = list(Department.objects.filter(
                company=self.company
            ).values_list('id', flat=True))
            
            # 删除SSO用户绑定（只删除该公司部门下的用户绑定）
            SSOUserBinding.objects.filter(
                user__department_id__in=dept_ids
            ).delete()
            
            # 删除同步过来的用户（保留管理员和超级用户）
            User.objects.filter(
                department_id__in=dept_ids,
                is_superuser=False,
                is_staff=False
            ).exclude(
                username='admin'
            ).delete()
            
            # 删除部门
            Department.objects.filter(company=self.company).delete()


class WeWorkService(BaseSSOService):
    """企业微信服务"""
    
    BASE_URL = 'https://qyapi.weixin.qq.com/cgi-bin'
    
    def get_access_token(self):
        """获取access_token"""
        url = f"{self.BASE_URL}/gettoken"
        params = {
            'corpid': self.config.app_id,
            'corpsecret': self.config.app_secret
        }
        response = requests.get(url, params=params, timeout=30)
        data = response.json()
        if data.get('errcode') == 0:
            return data.get('access_token')
        raise Exception(f"获取access_token失败: {data.get('errmsg')} (错误码: {data.get('errcode')})")
    
    def get_auth_url(self, redirect_uri):
        """获取企业微信授权URL"""
        params = {
            'appid': self.config.app_id,
            'agentid': self.config.extra_config.get('agent_id', ''),
            'redirect_uri': redirect_uri,
            'response_type': 'code',
            'scope': 'snsapi_privateinfo',
            'state': 'wework'
        }
        return f"https://open.work.weixin.qq.com/wwopen/sso/3rd_qrConnect?{urlencode(params)}"
    
    def get_user_info(self, code):
        """通过code获取用户信息"""
        access_token = self.get_access_token()
        
        # 获取用户ID
        url = f"{self.BASE_URL}/auth/getuserinfo"
        params = {'access_token': access_token, 'code': code}
        response = requests.get(url, params=params, timeout=30)
        data = response.json()
        
        if data.get('errcode') != 0:
            raise Exception(f"获取用户信息失败: {data.get('errmsg')}")
        
        user_id = data.get('userid') or data.get('UserId')
        
        # 获取用户详情
        url = f"{self.BASE_URL}/user/get"
        params = {'access_token': access_token, 'userid': user_id}
        response = requests.get(url, params=params, timeout=30)
        user_data = response.json()
        
        return {
            'user_id': user_id,
            'name': user_data.get('name'),
            'mobile': user_data.get('mobile'),
            'email': user_data.get('email'),
            'avatar': user_data.get('avatar'),
            'department': user_data.get('department', []),
            'position': user_data.get('position', ''),
            'is_leader_in_dept': user_data.get('is_leader_in_dept', [])
        }
    
    def get_or_create_user(self, user_info):
        """获取或创建用户"""
        try:
            binding = SSOUserBinding.objects.get(
                provider='wework',
                provider_user_id=user_info['user_id']
            )
            return binding.user
        except SSOUserBinding.DoesNotExist:
            # 创建新用户
            user = User.objects.create(
                username=f"wework_{user_info['user_id']}",
                display_name=user_info.get('name', ''),
                phone=user_info.get('mobile', ''),
                email=user_info.get('email', ''),
                avatar=user_info.get('avatar', '')
            )
            
            # 创建绑定关系
            SSOUserBinding.objects.create(
                user=user,
                provider='wework',
                provider_user_id=user_info['user_id']
            )
            
            return user
    
    def sync_organization(self, options=None):
        """同步组织架构"""
        options = options or {}
        sync_type = options.get('sync_type', 'full')
        clear_existing = options.get('clear_existing', False)
        sync_departments = options.get('sync_departments', True)
        sync_users = options.get('sync_users', True)
        sync_managers = options.get('sync_managers', True)
        
        # 清空现有数据
        if clear_existing:
            self.clear_existing_data()
        
        access_token = self.get_access_token()
        dept_count = 0
        user_count = 0
        manager_count = 0
        dept_id_map = {}  # 企业微信部门ID -> 本地部门对象
        user_dept_relations = []  # 用户部门关系
        
        # 同步部门
        if sync_departments:
            url = f"{self.BASE_URL}/department/list"
            params = {'access_token': access_token}
            response = requests.get(url, params=params, timeout=30)
            data = response.json()
            
            if data.get('errcode') == 0:
                departments = data.get('department', [])
                
                # 构建部门ID到数据的映射
                dept_data_map = {str(d['id']): d for d in departments}
                wework_dept_ids = set(dept_data_map.keys())
                
                # 第一步：先创建或更新所有部门（不设置父部门）
                for dept_data in departments:
                    wework_dept_id = str(dept_data['id'])
                    wework_order = dept_data.get('order', 0)
                    
                    dept, created = Department.objects.update_or_create(
                        company=self.company,
                        wework_dept_id=wework_dept_id,
                        defaults={
                            'name': dept_data['name'],
                            'code': f"ww_{dept_data['id']}",
                            'sort_order': wework_order,
                        }
                    )
                    dept_id_map[wework_dept_id] = dept
                    dept_count += 1
                
                # 第二步：更新所有部门的父部门关系
                for dept_data in departments:
                    wework_dept_id = str(dept_data['id'])
                    parent_id = str(dept_data.get('parentid', 0))
                    
                    dept = dept_id_map.get(wework_dept_id)
                    if not dept:
                        continue
                    
                    # 查找父部门
                    parent_dept = None
                    if parent_id and parent_id != '0':
                        # 优先从映射中查找
                        parent_dept = dept_id_map.get(parent_id)
                        # 如果不在映射中，从数据库查找
                        if not parent_dept:
                            parent_dept = Department.objects.filter(
                                company=self.company,
                                wework_dept_id=parent_id
                            ).first()
                    
                    # 更新父部门关系（如果有变化）
                    if dept.parent != parent_dept:
                        dept.parent = parent_dept
                        dept.save()
                
                # 第三步：处理已删除的部门（在企业微信中不存在但数据库中存在的）
                if sync_type == 'full':
                    deleted_depts = Department.objects.filter(
                        company=self.company,
                        wework_dept_id__isnull=False
                    ).exclude(wework_dept_id__in=wework_dept_ids)
                    
                    for deleted_dept in deleted_depts:
                        # 将该部门下的员工移到父部门或设为空
                        from apps.accounts.models import User
                        User.objects.filter(department=deleted_dept).update(
                            department=deleted_dept.parent
                        )
                        # 将子部门移到父部门
                        Department.objects.filter(parent=deleted_dept).update(
                            parent=deleted_dept.parent
                        )
                        # 删除部门
                        deleted_dept.delete()
                
                # 修复MPTT树结构
                try:
                    Department.objects.rebuild()
                except Exception:
                    pass
        
        # 同步用户
        if sync_users:
            processed_users = set()  # 记录已处理的用户ID，避免重复
            
            # 获取所有部门的用户
            for wework_dept_id, dept in dept_id_map.items():
                url = f"{self.BASE_URL}/user/list"
                params = {
                    'access_token': access_token,
                    'department_id': int(wework_dept_id),
                    'fetch_child': 0  # 不获取子部门用户，避免重复
                }
                response = requests.get(url, params=params, timeout=30)
                data = response.json()
                
                if data.get('errcode') == 0:
                    for user_data in data.get('userlist', []):
                        userid = user_data['userid']
                        
                        # 检查是否已绑定
                        binding = SSOUserBinding.objects.filter(
                            provider='wework',
                            provider_user_id=userid
                        ).first()
                        
                        # 获取用户的主部门（取企业微信返回的第一个部门）
                        user_depts = user_data.get('department', [])
                        main_dept = None
                        if user_depts:
                            main_dept_id = str(user_depts[0])
                            main_dept = dept_id_map.get(main_dept_id)
                        
                        if binding:
                            # 增量同步时只更新
                            user = binding.user
                            user.display_name = user_data.get('name', '')
                            user.phone = user_data.get('mobile', '')
                            user.email = user_data.get('email', '')
                            if user_data.get('avatar'):
                                user.avatar = user_data.get('avatar', '')
                            user.position = user_data.get('position', '')
                            user.department = main_dept
                            user.wework_user_id = userid
                            user.sso_type = 'wework'
                            user.save()
                        else:
                            # 创建用户
                            user = User.objects.create(
                                username=f"wework_{userid}",
                                display_name=user_data.get('name', ''),
                                phone=user_data.get('mobile', ''),
                                email=user_data.get('email', ''),
                                avatar=user_data.get('avatar', ''),
                                position=user_data.get('position', ''),
                                department=main_dept,
                                wework_user_id=userid,
                                sso_type='wework'
                            )
                            SSOUserBinding.objects.create(
                                user=user,
                                provider='wework',
                                provider_user_id=userid,
                                provider_user_info=user_data
                            )
                        
                        # 只统计新用户
                        if userid not in processed_users:
                            user_count += 1
                            processed_users.add(userid)
                        
                        # 记录用户部门关系和负责人信息（支持一人多部门）
                        # Record user-department relations with multi-department support
                        is_leader_in_dept = user_data.get('is_leader_in_dept', [])
                        
                        for i, dept_id in enumerate(user_depts):
                            is_leader = False
                            if i < len(is_leader_in_dept):
                                is_leader = is_leader_in_dept[i] == 1
                            
                            user_dept_relations.append({
                                'user': user,
                                'dept_id': str(dept_id),
                                'is_leader': is_leader,
                                'position': user_data.get('position', ''),
                                'sso_order': i  # 0 = primary department, 1+ = secondary departments
                            })
            
            # 处理离职用户（全量同步时）
            if sync_type == 'full':
                # 获取所有通过企业微信同步的用户
                synced_bindings = SSOUserBinding.objects.filter(provider='wework')
                for binding in synced_bindings:
                    if binding.provider_user_id not in processed_users:
                        # 该用户在企业微信中已不存在（离职）
                        user = binding.user
                        # 保护admin和超级管理员用户
                        if user.is_superuser or user.username == 'admin':
                            continue
                        # 标记为离职/非活跃状态
                        user.is_active = False
                        user.department = None  # 移除部门关联
                        user.save()
                        # 如果是部门负责人，移除负责人关系
                        Department.objects.filter(manager=user).update(manager=None)
        
        # 同步用户部门关联（多部门支持）和部门负责人
        if sync_users and user_dept_relations:
            for relation in user_dept_relations:
                dept = dept_id_map.get(relation['dept_id'])
                user = relation['user']
                if not dept or not user:
                    continue
                
                # Create or update UserDepartment record
                user_dept, created = UserDepartment.objects.update_or_create(
                    user=user,
                    department=dept,
                    defaults={
                        'is_primary': relation.get('sso_order', 0) == 0,
                        'is_leader': relation.get('is_leader', False),
                        'position': relation.get('position', ''),
                        'sso_order': relation.get('sso_order', 0)
                    }
                )
                
                # Set department manager if is_leader
                if sync_managers and relation.get('is_leader'):
                    dept.manager = user
                    dept.save()
                    manager_count += 1
            
            # Set asset_department to main department if not set
            # 如果用户没有设置资产归属部门，默认设置为主部门
            for user_id in processed_users:
                try:
                    binding = SSOUserBinding.objects.get(provider='wework', provider_user_id=user_id)
                    user = binding.user
                    if user.department and not user.asset_department:
                        user.asset_department = user.department
                        user.save()
                except SSOUserBinding.DoesNotExist:
                    pass
        
        # 自动同步用户角色
        from apps.accounts.services import RoleService
        role_stats = RoleService.sync_all_user_roles()
        
        return {
            'departments': dept_count,
            'users': user_count,
            'managers': manager_count,
            'user_dept_relations': len(user_dept_relations),
            'role_sync': role_stats
        }


class DingTalkService(BaseSSOService):
    """钉钉服务"""
    
    def get_access_token(self):
        url = "https://oapi.dingtalk.com/gettoken"
        params = {
            'appkey': self.config.app_id,
            'appsecret': self.config.app_secret
        }
        response = requests.get(url, params=params, timeout=30)
        data = response.json()
        if data.get('errcode') == 0:
            return data.get('access_token')
        raise Exception(f"获取access_token失败: {data.get('errmsg')}")
    
    def get_auth_url(self, redirect_uri):
        params = {
            'appid': self.config.app_id,
            'response_type': 'code',
            'scope': 'openid',
            'redirect_uri': redirect_uri,
            'state': 'dingtalk',
            'prompt': 'consent'
        }
        return f"https://login.dingtalk.com/oauth2/auth?{urlencode(params)}"
    
    def get_user_info(self, auth_code):
        # 获取用户token
        url = "https://api.dingtalk.com/v1.0/oauth2/userAccessToken"
        data = {
            'clientId': self.config.app_id,
            'clientSecret': self.config.app_secret,
            'code': auth_code,
            'grantType': 'authorization_code'
        }
        response = requests.post(url, json=data, timeout=30)
        token_data = response.json()
        
        access_token = token_data.get('accessToken')
        
        # 获取用户信息
        url = "https://api.dingtalk.com/v1.0/contact/users/me"
        headers = {'x-acs-dingtalk-access-token': access_token}
        response = requests.get(url, headers=headers, timeout=30)
        user_data = response.json()
        
        return {
            'user_id': user_data.get('unionId'),
            'name': user_data.get('nick'),
            'mobile': user_data.get('mobile'),
            'email': user_data.get('email'),
            'avatar': user_data.get('avatarUrl')
        }
    
    def get_or_create_user(self, user_info):
        try:
            binding = SSOUserBinding.objects.get(
                provider='dingtalk',
                provider_user_id=user_info['user_id']
            )
            return binding.user
        except SSOUserBinding.DoesNotExist:
            user = User.objects.create(
                username=f"dingtalk_{user_info['user_id'][:20]}",
                display_name=user_info.get('name', ''),
                phone=user_info.get('mobile', ''),
                email=user_info.get('email', ''),
                avatar=user_info.get('avatar', '')
            )
            
            SSOUserBinding.objects.create(
                user=user,
                provider='dingtalk',
                provider_user_id=user_info['user_id']
            )
            
            return user
    
    def sync_organization(self, options=None):
        """同步钉钉组织架构"""
        options = options or {}
        sync_type = options.get('sync_type', 'full')
        clear_existing = options.get('clear_existing', False)
        sync_departments = options.get('sync_departments', True)
        sync_users = options.get('sync_users', True)
        sync_managers = options.get('sync_managers', True)
        
        if clear_existing:
            self.clear_existing_data()
        
        access_token = self.get_access_token()
        dept_count = 0
        user_count = 0
        manager_count = 0
        dept_id_map = {}
        
        # 同步部门
        if sync_departments:
            url = "https://oapi.dingtalk.com/topapi/v2/department/listsub"
            
            def sync_dept(parent_id=1, parent_dept=None):
                nonlocal dept_count
                params = {'access_token': access_token}
                data = {'dept_id': parent_id}
                response = requests.post(url, params=params, json=data, timeout=30)
                result = response.json()
                
                if result.get('errcode') == 0:
                    for dept_data in result.get('result', []):
                        dingtalk_dept_id = str(dept_data['dept_id'])
                        
                        dept, created = Department.objects.update_or_create(
                            company=self.company,
                            dingtalk_dept_id=dingtalk_dept_id,
                            defaults={
                                'name': dept_data['name'],
                                'code': f"dd_{dept_data['dept_id']}",
                                'sort_order': dept_data.get('order', 0),
                                'parent': parent_dept
                            }
                        )
                        dept_id_map[dingtalk_dept_id] = dept
                        dept_count += 1
                        
                        # 递归同步子部门
                        sync_dept(dept_data['dept_id'], dept)
            
            sync_dept(1)
        
        # 同步用户
        if sync_users:
            user_url = "https://oapi.dingtalk.com/topapi/v2/user/list"
            
            for dingtalk_dept_id, dept in dept_id_map.items():
                cursor = 0
                while True:
                    params = {'access_token': access_token}
                    data = {'dept_id': int(dingtalk_dept_id), 'cursor': cursor, 'size': 100}
                    response = requests.post(user_url, params=params, json=data, timeout=30)
                    result = response.json()
                    
                    if result.get('errcode') != 0:
                        break
                    
                    user_list = result.get('result', {}).get('list', [])
                    for user_data in user_list:
                        userid = user_data['userid']
                        
                        binding = SSOUserBinding.objects.filter(
                            provider='dingtalk',
                            provider_user_id=userid
                        ).first()
                        
                        if binding:
                            user = binding.user
                            user.display_name = user_data.get('name', '')
                            user.phone = user_data.get('mobile', '')
                            user.email = user_data.get('email', '')
                            user.save()
                        else:
                            user = User.objects.create(
                                username=f"dingtalk_{userid[:20]}",
                                display_name=user_data.get('name', ''),
                                phone=user_data.get('mobile', ''),
                                email=user_data.get('email', '')
                            )
                            SSOUserBinding.objects.create(
                                user=user,
                                provider='dingtalk',
                                provider_user_id=userid,
                                provider_user_info=user_data
                            )
                            user_count += 1
                        
                        # 同步部门负责人
                        if sync_managers and user_data.get('leader'):
                            dept.manager = user
                            dept.save()
                            manager_count += 1
                    
                    if not result.get('result', {}).get('has_more'):
                        break
                    cursor = result.get('result', {}).get('next_cursor', 0)
        
        return {
            'departments': dept_count,
            'users': user_count,
            'managers': manager_count
        }


class FeishuService(BaseSSOService):
    """飞书服务"""
    
    def get_access_token(self):
        url = "https://open.feishu.cn/open-apis/auth/v3/app_access_token/internal"
        data = {
            'app_id': self.config.app_id,
            'app_secret': self.config.app_secret
        }
        response = requests.post(url, json=data, timeout=30)
        result = response.json()
        if result.get('code') == 0:
            return result.get('app_access_token')
        raise Exception(f"获取access_token失败: {result.get('msg')}")
    
    def get_auth_url(self, redirect_uri):
        params = {
            'app_id': self.config.app_id,
            'redirect_uri': redirect_uri,
            'state': 'feishu'
        }
        return f"https://open.feishu.cn/open-apis/authen/v1/index?{urlencode(params)}"
    
    def get_user_info(self, code):
        app_access_token = self.get_access_token()
        
        url = "https://open.feishu.cn/open-apis/authen/v1/access_token"
        headers = {'Authorization': f'Bearer {app_access_token}'}
        data = {
            'grant_type': 'authorization_code',
            'code': code
        }
        response = requests.post(url, headers=headers, json=data, timeout=30)
        result = response.json()
        
        user_access_token = result.get('data', {}).get('access_token')
        
        url = "https://open.feishu.cn/open-apis/authen/v1/user_info"
        headers = {'Authorization': f'Bearer {user_access_token}'}
        response = requests.get(url, headers=headers, timeout=30)
        user_data = response.json().get('data', {})
        
        return {
            'user_id': user_data.get('union_id'),
            'name': user_data.get('name'),
            'mobile': user_data.get('mobile'),
            'email': user_data.get('email'),
            'avatar': user_data.get('avatar_url')
        }
    
    def get_or_create_user(self, user_info):
        try:
            binding = SSOUserBinding.objects.get(
                provider='feishu',
                provider_user_id=user_info['user_id']
            )
            return binding.user
        except SSOUserBinding.DoesNotExist:
            user = User.objects.create(
                username=f"feishu_{user_info['user_id'][:20]}",
                display_name=user_info.get('name', ''),
                phone=user_info.get('mobile', ''),
                email=user_info.get('email', ''),
                avatar=user_info.get('avatar', '')
            )
            
            SSOUserBinding.objects.create(
                user=user,
                provider='feishu',
                provider_user_id=user_info['user_id']
            )
            
            return user
    
    def sync_organization(self, options=None):
        """同步飞书组织架构"""
        options = options or {}
        sync_type = options.get('sync_type', 'full')
        clear_existing = options.get('clear_existing', False)
        sync_departments = options.get('sync_departments', True)
        sync_users = options.get('sync_users', True)
        sync_managers = options.get('sync_managers', True)
        
        if clear_existing:
            self.clear_existing_data()
        
        access_token = self.get_access_token()
        dept_count = 0
        user_count = 0
        manager_count = 0
        dept_id_map = {}
        
        headers = {'Authorization': f'Bearer {access_token}'}
        
        # 同步部门
        if sync_departments:
            def sync_dept(parent_id='0', parent_dept=None):
                nonlocal dept_count
                url = f"https://open.feishu.cn/open-apis/contact/v3/departments/{parent_id}/children"
                params = {'page_size': 50}
                
                while True:
                    response = requests.get(url, headers=headers, params=params, timeout=30)
                    result = response.json()
                    
                    if result.get('code') != 0:
                        break
                    
                    for dept_data in result.get('data', {}).get('items', []):
                        feishu_dept_id = dept_data['open_department_id']
                        
                        dept, created = Department.objects.update_or_create(
                            company=self.company,
                            feishu_dept_id=feishu_dept_id,
                            defaults={
                                'name': dept_data['name'],
                                'code': f"fs_{feishu_dept_id[:20]}",
                                'sort_order': dept_data.get('order', 0),
                                'parent': parent_dept
                            }
                        )
                        dept_id_map[feishu_dept_id] = dept
                        dept_count += 1
                        
                        # 同步部门负责人
                        if sync_managers and dept_data.get('leader_user_id'):
                            # 稍后处理
                            pass
                        
                        sync_dept(feishu_dept_id, dept)
                    
                    if not result.get('data', {}).get('has_more'):
                        break
                    params['page_token'] = result.get('data', {}).get('page_token')
            
            sync_dept('0')
        
        # 同步用户
        if sync_users:
            for feishu_dept_id, dept in dept_id_map.items():
                url = "https://open.feishu.cn/open-apis/contact/v3/users/find_by_department"
                params = {'department_id': feishu_dept_id, 'page_size': 50}
                
                while True:
                    response = requests.get(url, headers=headers, params=params, timeout=30)
                    result = response.json()
                    
                    if result.get('code') != 0:
                        break
                    
                    for user_data in result.get('data', {}).get('items', []):
                        union_id = user_data.get('union_id', user_data.get('user_id', ''))
                        
                        binding = SSOUserBinding.objects.filter(
                            provider='feishu',
                            provider_user_id=union_id
                        ).first()
                        
                        if binding:
                            user = binding.user
                            user.display_name = user_data.get('name', '')
                            user.phone = user_data.get('mobile', '')
                            user.email = user_data.get('email', '')
                            user.save()
                        else:
                            user = User.objects.create(
                                username=f"feishu_{union_id[:20]}",
                                display_name=user_data.get('name', ''),
                                phone=user_data.get('mobile', ''),
                                email=user_data.get('email', '')
                            )
                            SSOUserBinding.objects.create(
                                user=user,
                                provider='feishu',
                                provider_user_id=union_id,
                                provider_user_info=user_data
                            )
                            user_count += 1
                        
                        # 同步部门负责人
                        if sync_managers and user_data.get('is_tenant_manager'):
                            dept.manager = user
                            dept.save()
                            manager_count += 1
                    
                    if not result.get('data', {}).get('has_more'):
                        break
                    params['page_token'] = result.get('data', {}).get('page_token')
        
        return {
            'departments': dept_count,
            'users': user_count,
            'managers': manager_count
        }
