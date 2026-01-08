"""
消息通知模型 - 精臣云资产管理系统
"""
from django.db import models


class Notification(models.Model):
    """通知消息"""
    
    class NotificationType(models.TextChoices):
        SYSTEM = 'system', '系统通知'
        WORKFLOW = 'workflow', '审批通知'
        ALERT = 'alert', '预警提醒'
        ANNOUNCEMENT = 'announcement', '公告'
    
    company = models.ForeignKey(
        'organizations.Company',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications',
        verbose_name='所属公司'
    )
    notification_type = models.CharField('通知类型', max_length=20, choices=NotificationType.choices)
    title = models.CharField('标题', max_length=200)
    content = models.TextField('内容')
    
    # 关联业务
    business_type = models.CharField('业务类型', max_length=50, blank=True, null=True)
    business_id = models.IntegerField('业务ID', null=True, blank=True)
    
    # 接收者
    recipients = models.ManyToManyField(
        'accounts.User',
        through='NotificationRecipient',
        related_name='received_notifications',
        verbose_name='接收者'
    )
    
    is_global = models.BooleanField('全局通知', default=False)
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_notifications',
        verbose_name='创建人'
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '通知'
        verbose_name_plural = '通知'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title


class NotificationRecipient(models.Model):
    """通知接收记录"""
    
    notification = models.ForeignKey(
        Notification,
        on_delete=models.CASCADE,
        related_name='recipient_records',
        verbose_name='通知'
    )
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='notification_records',
        verbose_name='用户'
    )
    is_read = models.BooleanField('是否已读', default=False)
    read_at = models.DateTimeField('阅读时间', null=True, blank=True)
    
    class Meta:
        verbose_name = '通知接收记录'
        verbose_name_plural = '通知接收记录'
        unique_together = ['notification', 'user']


class Announcement(models.Model):
    """公告"""
    
    company = models.ForeignKey(
        'organizations.Company',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='announcements',
        verbose_name='所属公司'
    )
    title = models.CharField('标题', max_length=200)
    content = models.TextField('内容')
    is_top = models.BooleanField('置顶', default=False)
    is_published = models.BooleanField('已发布', default=False)
    publish_time = models.DateTimeField('发布时间', null=True, blank=True)
    expire_time = models.DateTimeField('过期时间', null=True, blank=True)
    
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='创建人'
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '公告'
        verbose_name_plural = '公告'
        ordering = ['-is_top', '-publish_time']
    
    def __str__(self):
        return self.title


class AlertRule(models.Model):
    """预警规则"""
    
    class AlertType(models.TextChoices):
        WARRANTY_EXPIRY = 'warranty_expiry', '保修到期'
        CONTRACT_EXPIRY = 'contract_expiry', '合同到期'
        STOCK_LOW = 'stock_low', '库存不足'
        MAINTENANCE_DUE = 'maintenance_due', '维保到期'
        RETURN_DUE = 'return_due', '借用归还'
    
    company = models.ForeignKey(
        'organizations.Company',
        on_delete=models.CASCADE,
        related_name='alert_rules',
        verbose_name='所属公司'
    )
    name = models.CharField('规则名称', max_length=100)
    alert_type = models.CharField('预警类型', max_length=30, choices=AlertType.choices)
    description = models.TextField('描述', blank=True, null=True)
    
    # 提醒配置
    advance_days = models.IntegerField('提前天数', default=7)
    repeat_interval = models.IntegerField('重复间隔(天)', default=1)
    
    # 接收者
    recipients = models.ManyToManyField(
        'accounts.User',
        blank=True,
        related_name='alert_rules',
        verbose_name='接收者'
    )
    
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '预警规则'
        verbose_name_plural = '预警规则'
    
    def __str__(self):
        return self.name
