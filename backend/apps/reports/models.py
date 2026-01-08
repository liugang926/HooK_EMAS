"""
报表管理模型 - 精臣云资产管理系统
"""
from django.db import models


class ReportTemplate(models.Model):
    """报表模板"""
    
    class ReportType(models.TextChoices):
        ASSET = 'asset', '资产报表'
        CONSUMABLE = 'consumable', '耗材报表'
        FINANCE = 'finance', '财务报表'
        INVENTORY = 'inventory', '盘点报表'
    
    company = models.ForeignKey(
        'organizations.Company',
        on_delete=models.CASCADE,
        related_name='report_templates',
        verbose_name='所属公司'
    )
    name = models.CharField('报表名称', max_length=100)
    code = models.CharField('报表代码', max_length=50)
    report_type = models.CharField('报表类型', max_length=20, choices=ReportType.choices)
    description = models.TextField('描述', blank=True, null=True)
    
    # 报表配置
    columns = models.JSONField('列配置', default=list)
    filters = models.JSONField('筛选条件', default=list)
    grouping = models.JSONField('分组配置', default=list)
    sorting = models.JSONField('排序配置', default=list)
    
    is_system = models.BooleanField('系统报表', default=False)
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '报表模板'
        verbose_name_plural = '报表模板'
        unique_together = ['company', 'code']
    
    def __str__(self):
        return self.name


class ReportExportLog(models.Model):
    """报表导出日志"""
    
    company = models.ForeignKey(
        'organizations.Company',
        on_delete=models.CASCADE,
        related_name='report_exports',
        verbose_name='所属公司'
    )
    report_template = models.ForeignKey(
        ReportTemplate,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='报表模板'
    )
    report_name = models.CharField('报表名称', max_length=200)
    file_path = models.CharField('文件路径', max_length=500, blank=True, null=True)
    file_size = models.IntegerField('文件大小', default=0)
    export_params = models.JSONField('导出参数', default=dict)
    
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='导出人'
    )
    created_at = models.DateTimeField('导出时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '报表导出日志'
        verbose_name_plural = '报表导出日志'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.report_name} - {self.created_at}"
