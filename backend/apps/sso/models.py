"""
SSO单点登录模型 - 精臣云资产管理系统

Multi-company SSO Architecture:
- Each company can have separate SSO configurations
- SSO bindings are company-aware for multi-company users
- Sync settings are per-company for isolated sync operations
"""
from django.db import models


class SSOConfig(models.Model):
    """
    SSO配置 - Enhanced for multi-company support
    
    Each company can configure its own SSO provider settings.
    This is the authoritative source for SSO credentials 
    (replaces Company.wework_corp_id, etc.)
    """
    
    class Provider(models.TextChoices):
        WEWORK = 'wework', '企业微信'
        DINGTALK = 'dingtalk', '钉钉'
        FEISHU = 'feishu', '飞书'
    
    company = models.ForeignKey(
        'organizations.Company',
        on_delete=models.CASCADE,
        related_name='sso_configs',
        verbose_name='所属公司'
    )
    provider = models.CharField('SSO平台', max_length=20, choices=Provider.choices)
    
    # Corp Level Settings - Primary identification
    corp_id = models.CharField(
        '企业ID',
        max_length=200,
        blank=True,
        null=True,
        help_text='企业微信CorpID / 钉钉CorpID / 飞书CorpID'
    )
    
    # Agent/App Settings
    agent_id = models.CharField(
        '应用AgentID',
        max_length=200,
        blank=True,
        null=True,
        help_text='自建应用AgentID'
    )
    app_id = models.CharField('应用ID', max_length=200, blank=True, null=True)
    app_secret = models.CharField(
        '应用密钥',
        max_length=500,
        blank=True,
        null=True,
        help_text='应用密钥，建议加密存储'
    )
    
    # OAuth Settings
    oauth_enabled = models.BooleanField('启用OAuth登录', default=True)
    callback_url = models.URLField(
        '回调地址',
        blank=True,
        null=True,
        help_text='OAuth回调地址'
    )
    
    # Sync Settings
    sync_enabled = models.BooleanField('启用数据同步', default=True)
    sync_departments = models.BooleanField('同步部门', default=True)
    sync_users = models.BooleanField('同步用户', default=True)
    sync_interval = models.IntegerField(
        '同步间隔(分钟)',
        default=60,
        help_text='自动同步间隔，0表示禁用自动同步'
    )
    root_department_id = models.CharField(
        '同步根部门ID',
        max_length=50,
        blank=True,
        null=True,
        help_text='只同步该部门及其子部门，为空则同步全部'
    )
    
    # User Auto Creation Settings
    auto_create_user = models.BooleanField(
        '自动创建用户',
        default=True,
        help_text='SSO登录时自动创建用户'
    )
    auto_create_department = models.BooleanField(
        '自动创建部门',
        default=True,
        help_text='同步时自动创建缺失的部门'
    )
    default_role_id = models.IntegerField(
        '新用户默认角色ID',
        null=True,
        blank=True,
        help_text='SSO创建的用户默认分配的角色'
    )
    
    # Encrypted extra config for provider-specific settings
    extra_config = models.JSONField(
        '扩展配置',
        default=dict,
        blank=True,
        help_text='存储特定平台的额外配置'
    )
    
    is_enabled = models.BooleanField('是否启用', default=True)
    auto_sync = models.BooleanField('自动同步', default=True)
    last_sync_at = models.DateTimeField('最后同步时间', null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = 'SSO配置'
        verbose_name_plural = 'SSO配置'
        unique_together = ['company', 'provider']
    
    def __str__(self):
        return f"{self.company.name} - {self.get_provider_display()}"
    
    def get_corp_id(self):
        """Get CorpID, checking deprecated Company fields as fallback"""
        if self.corp_id:
            return self.corp_id
        # Fallback to deprecated Company fields for backwards compatibility
        if self.provider == self.Provider.WEWORK:
            return self.company.wework_corp_id
        elif self.provider == self.Provider.DINGTALK:
            return self.company.dingtalk_corp_id
        elif self.provider == self.Provider.FEISHU:
            return self.company.feishu_corp_id
        return None


class SSOUserBinding(models.Model):
    """
    SSO用户绑定 - Enhanced for multi-company support
    
    Links a local user to an SSO provider account.
    Company-aware for users working across multiple companies.
    """
    
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='sso_bindings',
        verbose_name='用户'
    )
    
    # Company context - A user might have different SSO bindings per company
    # (e.g., different WeWork accounts for different legal entities)
    company = models.ForeignKey(
        'organizations.Company',
        on_delete=models.CASCADE,
        related_name='sso_user_bindings',
        verbose_name='公司',
        null=True,
        blank=True,
        help_text='关联的公司，支持多公司用户'
    )
    
    provider = models.CharField('SSO平台', max_length=20, choices=SSOConfig.Provider.choices)
    provider_user_id = models.CharField('平台用户ID', max_length=200)
    provider_user_info = models.JSONField(
        '平台用户信息',
        default=dict,
        blank=True,
        help_text='存储从SSO平台获取的用户原始信息'
    )
    
    # Status tracking
    is_active = models.BooleanField('是否有效', default=True)
    last_login_at = models.DateTimeField('最后登录时间', null=True, blank=True)
    
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = 'SSO用户绑定'
        verbose_name_plural = 'SSO用户绑定'
        # A provider user ID should be unique within a company
        unique_together = ['company', 'provider', 'provider_user_id']
    
    def __str__(self):
        company_name = self.company.short_name if self.company else '全局'
        return f"{self.user.username} - {self.provider} ({company_name})"


class SSOSyncLog(models.Model):
    """SSO同步日志"""
    
    class SyncType(models.TextChoices):
        DEPARTMENT = 'department', '部门同步'
        USER = 'user', '用户同步'
        FULL = 'full', '全量同步'
    
    class Status(models.TextChoices):
        RUNNING = 'running', '同步中'
        SUCCESS = 'success', '成功'
        FAILED = 'failed', '失败'
    
    sso_config = models.ForeignKey(
        SSOConfig,
        on_delete=models.CASCADE,
        related_name='sync_logs',
        verbose_name='SSO配置'
    )
    sync_type = models.CharField('同步类型', max_length=20, choices=SyncType.choices)
    status = models.CharField('状态', max_length=20, choices=Status.choices, default=Status.RUNNING)
    
    # 同步统计
    total_count = models.IntegerField('总数', default=0)
    success_count = models.IntegerField('成功数', default=0)
    failed_count = models.IntegerField('失败数', default=0)
    
    error_message = models.TextField('错误信息', blank=True, null=True)
    detail = models.JSONField('详细信息', default=dict)
    
    started_at = models.DateTimeField('开始时间', auto_now_add=True)
    completed_at = models.DateTimeField('完成时间', null=True, blank=True)
    
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='操作人'
    )
    
    class Meta:
        verbose_name = 'SSO同步日志'
        verbose_name_plural = 'SSO同步日志'
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.sso_config} - {self.get_sync_type_display()} - {self.started_at}"
