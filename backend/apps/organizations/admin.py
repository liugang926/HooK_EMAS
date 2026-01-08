"""
组织架构 Admin 配置
"""
from django.contrib import admin
from mptt.admin import MPTTModelAdmin
from .models import Company, Department, Location, OrganizationChange


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'short_name', 'phone', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'code', 'short_name']


@admin.register(Department)
class DepartmentAdmin(MPTTModelAdmin):
    list_display = ['name', 'code', 'company', 'parent', 'manager', 'is_active']
    list_filter = ['company', 'is_active']
    search_fields = ['name', 'code']


@admin.register(Location)
class LocationAdmin(MPTTModelAdmin):
    list_display = ['name', 'code', 'company', 'parent', 'is_active']
    list_filter = ['company', 'is_active']
    search_fields = ['name', 'code', 'address']


@admin.register(OrganizationChange)
class OrganizationChangeAdmin(admin.ModelAdmin):
    list_display = ['department', 'change_type', 'status', 'created_by', 'created_at']
    list_filter = ['change_type', 'status']
    search_fields = ['description']
