"""
角色权限管理服务 - 精臣云资产管理系统
"""
from django.db import transaction
from .models import Role, UserRole, User


class RoleService:
    """角色权限管理服务"""
    
    # 默认角色定义
    DEFAULT_ROLES = [
        {
            'name': '超级管理员',
            'code': 'super_admin',
            'description': '拥有所有权限',
            'is_system': True,
            'permissions': {
                'function_permissions': 'all',
                'data_scope': 'all'
            }
        },
        {
            'name': '资产管理员',
            'code': 'asset_admin',
            'description': '管理资产相关功能',
            'is_system': False,
            'permissions': {
                'function_permissions': [11, 12, 13, 14, 15, 16, 17, 18, 19, 21, 22, 23, 24, 41, 42, 43, 51, 52],
                'data_scope': 'all'
            }
        },
        {
            'name': '部门管理员',
            'code': 'dept_admin',
            'description': '管理本部门资产',
            'is_system': False,
            'permissions': {
                'function_permissions': [11, 12, 13, 16, 17, 18, 21, 22, 23, 41, 43, 51],
                'data_scope': 'dept_below'
            }
        },
        {
            'name': '普通员工',
            'code': 'employee',
            'description': '基础查看和申请权限',
            'is_system': False,
            'permissions': {
                'function_permissions': [11, 21, 51, 16],  # 资产查看、耗材查看、报表查看、资产领用
                'data_scope': 'self'
            }
        }
    ]
    
    @classmethod
    def ensure_default_roles(cls):
        """确保默认角色存在"""
        created_roles = []
        for role_data in cls.DEFAULT_ROLES:
            permissions = role_data.pop('permissions', {})
            role, created = Role.objects.get_or_create(
                code=role_data['code'],
                defaults={
                    'name': role_data['name'],
                    'description': role_data['description'],
                    'is_system': role_data.get('is_system', False),
                    'permissions': permissions
                }
            )
            if created:
                created_roles.append(role)
            # 恢复 permissions 用于下次循环
            role_data['permissions'] = permissions
        return created_roles
    
    @classmethod
    def get_role_by_code(cls, code):
        """根据代码获取角色"""
        return Role.objects.filter(code=code, is_active=True).first()
    
    @classmethod
    def assign_role_to_user(cls, user, role_code, department=None):
        """给用户分配角色"""
        role = cls.get_role_by_code(role_code)
        if not role:
            return None
        
        user_role, created = UserRole.objects.get_or_create(
            user=user,
            role=role,
            defaults={'department': department or user.department}
        )
        return user_role
    
    @classmethod
    def remove_role_from_user(cls, user, role_code):
        """移除用户的角色"""
        role = cls.get_role_by_code(role_code)
        if not role:
            return False
        
        deleted, _ = UserRole.objects.filter(user=user, role=role).delete()
        return deleted > 0
    
    @classmethod
    def get_user_roles(cls, user):
        """获取用户的所有角色"""
        return Role.objects.filter(user_roles__user=user, is_active=True)
    
    @classmethod
    def has_role(cls, user, role_code):
        """检查用户是否拥有指定角色"""
        return UserRole.objects.filter(
            user=user,
            role__code=role_code,
            role__is_active=True
        ).exists()
    
    @classmethod
    @transaction.atomic
    def auto_assign_roles_for_new_user(cls, user):
        """
        为新用户自动分配角色
        - 所有用户默认分配"普通员工"角色
        """
        # 确保默认角色存在
        cls.ensure_default_roles()
        
        # 分配普通员工角色
        cls.assign_role_to_user(user, 'employee')
        
        return user
    
    @classmethod
    @transaction.atomic
    def auto_assign_dept_manager_role(cls, user, department):
        """
        为部门负责人分配部门管理员角色
        """
        # 确保默认角色存在
        cls.ensure_default_roles()
        
        # 分配部门管理员角色
        cls.assign_role_to_user(user, 'dept_admin', department)
        
        return user
    
    @classmethod
    @transaction.atomic
    def remove_dept_manager_role(cls, user):
        """
        移除用户的部门管理员角色
        """
        cls.remove_role_from_user(user, 'dept_admin')
    
    @classmethod
    @transaction.atomic
    def sync_all_user_roles(cls):
        """
        同步所有用户的角色
        - 所有活跃用户分配普通员工角色
        - 部门负责人分配部门管理员角色
        - 超级用户分配超级管理员角色
        """
        from apps.organizations.models import Department
        
        # 确保默认角色存在
        cls.ensure_default_roles()
        
        employee_role = cls.get_role_by_code('employee')
        dept_admin_role = cls.get_role_by_code('dept_admin')
        super_admin_role = cls.get_role_by_code('super_admin')
        
        if not employee_role:
            return {'error': '普通员工角色不存在'}
        
        stats = {
            'total_users': 0,
            'employee_assigned': 0,
            'dept_admin_assigned': 0,
            'super_admin_assigned': 0
        }
        
        # 获取所有活跃用户
        active_users = User.objects.filter(is_active=True)
        stats['total_users'] = active_users.count()
        
        # 获取所有部门负责人
        dept_managers = set()
        for dept in Department.objects.filter(manager__isnull=False):
            if dept.manager:
                dept_managers.add(dept.manager.id)
        
        for user in active_users:
            # 所有用户分配普通员工角色
            _, created = UserRole.objects.get_or_create(
                user=user,
                role=employee_role,
                defaults={'department': user.department}
            )
            if created:
                stats['employee_assigned'] += 1
            
            # 部门负责人分配部门管理员角色
            if user.id in dept_managers and dept_admin_role:
                _, created = UserRole.objects.get_or_create(
                    user=user,
                    role=dept_admin_role,
                    defaults={'department': user.department}
                )
                if created:
                    stats['dept_admin_assigned'] += 1
            
            # 超级用户分配超级管理员角色
            if user.is_superuser and super_admin_role:
                _, created = UserRole.objects.get_or_create(
                    user=user,
                    role=super_admin_role,
                    defaults={'department': user.department}
                )
                if created:
                    stats['super_admin_assigned'] += 1
        
        return stats
    
    @classmethod
    def get_users_by_role(cls, role_code):
        """获取指定角色的所有用户"""
        role = cls.get_role_by_code(role_code)
        if not role:
            return User.objects.none()
        
        return User.objects.filter(
            user_roles__role=role,
            is_active=True
        ).distinct()
