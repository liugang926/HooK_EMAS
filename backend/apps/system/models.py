"""
系统管理模型 - 钩子资产管理系统
"""
from django.db import models

# 导入动态表单模型
from .form_models import FieldGroup, FieldDefinition, ModuleFormConfig, FormLayout

__all__ = [
    'SystemConfig', 'OperationLog', 'CodeRule', 'DataDictionary',
    'FieldGroup', 'FieldDefinition', 'ModuleFormConfig', 'FormLayout'
]


class SystemConfig(models.Model):
    """系统配置"""
    
    company = models.ForeignKey(
        'organizations.Company',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='system_configs',
        verbose_name='所属公司'
    )
    config_key = models.CharField('配置键', max_length=100)
    config_value = models.TextField('配置值')
    description = models.CharField('描述', max_length=200, blank=True, null=True)
    is_system = models.BooleanField('系统配置', default=False)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '系统配置'
        verbose_name_plural = '系统配置'
        unique_together = ['company', 'config_key']
    
    def __str__(self):
        return f"{self.config_key}: {self.config_value[:50]}"


class OperationLog(models.Model):
    """操作日志"""
    
    company = models.ForeignKey(
        'organizations.Company',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='sys_operation_logs',
        verbose_name='所属公司'
    )
    module = models.CharField('模块', max_length=50)
    action = models.CharField('操作', max_length=50)
    content = models.TextField('操作内容')
    
    operator = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='sys_operation_logs',
        verbose_name='操作人'
    )
    ip_address = models.GenericIPAddressField('IP地址', null=True, blank=True)
    user_agent = models.TextField('User Agent', blank=True, null=True)
    
    created_at = models.DateTimeField('操作时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '操作日志'
        verbose_name_plural = '操作日志'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.module} - {self.action} - {self.created_at}"


class CodeRule(models.Model):
    """编码规则"""
    
    company = models.ForeignKey(
        'organizations.Company',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='code_rules',
        verbose_name='所属公司',
        help_text='为空表示系统级规则'
    )
    name = models.CharField('规则名称', max_length=100)
    code = models.CharField('规则代码', max_length=50)
    
    prefix = models.CharField('前缀', max_length=20, blank=True, null=True)
    date_format = models.CharField('日期格式', max_length=20, blank=True, null=True)
    serial_length = models.IntegerField('流水号长度', default=4)
    separator = models.CharField('分隔符', max_length=5, blank=True, null=True)
    
    current_serial = models.IntegerField('当前流水号', default=0)
    reset_cycle = models.CharField('重置周期', max_length=20, default='never')
    last_reset_date = models.DateField('最后重置日期', null=True, blank=True)
    
    description = models.TextField('描述', blank=True, null=True)
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '编码规则'
        verbose_name_plural = '编码规则'
        unique_together = ['company', 'code']
    
    def __str__(self):
        return self.name


class DataDictionary(models.Model):
    """数据字典"""
    
    company = models.ForeignKey(
        'organizations.Company',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='data_dictionaries',
        verbose_name='所属公司'
    )
    category = models.CharField('分类', max_length=50)
    code = models.CharField('代码', max_length=50)
    name = models.CharField('名称', max_length=100)
    value = models.CharField('值', max_length=200, blank=True, null=True)
    sort_order = models.IntegerField('排序', default=0)
    description = models.CharField('描述', max_length=200, blank=True, null=True)
    is_system = models.BooleanField('系统字典', default=False)
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '数据字典'
        verbose_name_plural = '数据字典'
        unique_together = ['company', 'category', 'code']
        ordering = ['category', 'sort_order']
    
    def __str__(self):
        return f"{self.category} - {self.name}"
