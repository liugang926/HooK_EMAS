"""
用户账户 Admin 配置
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Role, UserRole, OperationLog


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'employee_no', 'department', 'is_active', 'created_at']
    list_filter = ['is_active', 'is_staff', 'sso_type', 'department']
    search_fields = ['username', 'email', 'employee_no', 'first_name', 'last_name']
    ordering = ['-created_at']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('扩展信息', {
            'fields': ('employee_no', 'phone', 'gender', 'avatar', 'department', 'position')
        }),
        ('SSO 信息', {
            'fields': ('sso_type', 'sso_user_id', 'wework_user_id', 'dingtalk_user_id', 'feishu_user_id')
        }),
    )


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'is_system', 'is_active', 'created_at']
    list_filter = ['is_system', 'is_active']
    search_fields = ['name', 'code']


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'department', 'created_at']
    list_filter = ['role', 'department']
    search_fields = ['user__username', 'role__name']


@admin.register(OperationLog)
class OperationLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'operation_type', 'module', 'description', 'ip_address', 'created_at']
    list_filter = ['operation_type', 'module']
    search_fields = ['description', 'user__username']
    readonly_fields = ['user', 'operation_type', 'module', 'description', 'request_path',
                       'request_method', 'request_body', 'response_status', 'ip_address',
                       'user_agent', 'created_at']
