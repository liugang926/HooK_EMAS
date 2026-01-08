from django.contrib import admin
from .models import SystemConfig, OperationLog
from .form_models import FieldGroup, FieldDefinition, ModuleFormConfig


@admin.register(SystemConfig)
class SystemConfigAdmin(admin.ModelAdmin):
    list_display = ['config_key', 'company', 'updated_at']
    list_filter = ['company']
    search_fields = ['config_key']


@admin.register(OperationLog)
class OperationLogAdmin(admin.ModelAdmin):
    list_display = ['module', 'action', 'content', 'operator', 'ip_address', 'created_at']
    list_filter = ['module', 'action', 'created_at']
    search_fields = ['content', 'operator__username']
    readonly_fields = ['module', 'action', 'content', 'operator', 'ip_address', 'user_agent', 'created_at']


@admin.register(FieldGroup)
class FieldGroupAdmin(admin.ModelAdmin):
    list_display = ['module', 'group_key', 'group_name', 'sort_order', 'is_active']
    list_filter = ['module', 'is_active']
    search_fields = ['group_key', 'group_name']
    ordering = ['module', 'sort_order']


@admin.register(FieldDefinition)
class FieldDefinitionAdmin(admin.ModelAdmin):
    list_display = ['module', 'field_key', 'field_name', 'field_type', 'group', 'is_required', 'is_active']
    list_filter = ['module', 'field_type', 'is_required', 'is_system', 'is_active']
    search_fields = ['field_key', 'field_name']
    ordering = ['module', 'group__sort_order', 'sort_order']
    list_editable = ['is_required', 'is_active']


@admin.register(ModuleFormConfig)
class ModuleFormConfigAdmin(admin.ModelAdmin):
    list_display = ['module', 'module_label', 'api_base', 'is_active']
    list_filter = ['is_active']
    search_fields = ['module', 'module_label']
