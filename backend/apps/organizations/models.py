"""
组织架构模型 - 精臣云资产管理系统
"""
from django.db import models
from mptt.models import MPTTModel, TreeForeignKey


class Company(models.Model):
    """
    企业/公司模型 - Multi-company architecture support
    
    Supports:
    - Company hierarchy (parent/children for group structure)
    - Organization mode (independent/shared/inherit)
    - Financial settings per company
    
    Business Scenarios:
    1. Independent: Each company has completely separate org structure
    2. Shared: Multiple companies share organization structure  
    3. Inherit: Subsidiary inherits parent company's org structure
    """
    
    class CompanyType(models.TextChoices):
        GROUP = 'group', '集团总部'               # Group headquarters
        SUBSIDIARY = 'subsidiary', '子公司'       # Subsidiary
        BRANCH = 'branch', '分公司'              # Branch
        AFFILIATE = 'affiliate', '关联公司'      # Affiliated company
        DEPARTMENT_UNIT = 'dept_unit', '独立核算部门'  # Independent accounting unit
    
    class OrgMode(models.TextChoices):
        INDEPENDENT = 'independent', '独立组织架构'  # Own org structure
        SHARED = 'shared', '共享组织架构'           # Share with parent
        INHERIT = 'inherit', '继承上级架构'         # Inherit parent's structure
    
    # Company Hierarchy
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='children',
        verbose_name='上级公司',
        help_text='用于集团公司层级管理'
    )
    company_type = models.CharField(
        '公司类型',
        max_length=20,
        choices=CompanyType.choices,
        default=CompanyType.SUBSIDIARY
    )
    
    # Organization Mode
    org_mode = models.CharField(
        '组织架构模式',
        max_length=20,
        choices=OrgMode.choices,
        default=OrgMode.INDEPENDENT,
        help_text='决定部门和用户的数据隔离方式'
    )
    
    # Basic Info
    name = models.CharField('公司名称', max_length=200)
    code = models.CharField('公司代码', max_length=50, unique=True)
    short_name = models.CharField('简称', max_length=50, blank=True, null=True)
    logo = models.ImageField('公司Logo', upload_to='company_logos/', blank=True, null=True)
    address = models.CharField('公司地址', max_length=500, blank=True, null=True)
    phone = models.CharField('联系电话', max_length=50, blank=True, null=True)
    email = models.EmailField('邮箱', blank=True, null=True)
    website = models.URLField('网站', blank=True, null=True)
    description = models.TextField('公司简介', blank=True, null=True)
    
    # Financial Settings - For financial audit and reporting
    tax_id = models.CharField('税务登记号', max_length=50, blank=True, null=True)
    legal_representative = models.CharField('法人代表', max_length=100, blank=True, null=True)
    currency = models.CharField('核算货币', max_length=10, default='CNY')
    fiscal_year_start = models.IntegerField('财年起始月', default=1, help_text='1-12')
    
    # SSO 关联 - Deprecated, use SSOConfig table instead
    # 保留字段用于向后兼容，新项目应使用 sso.SSOConfig
    wework_corp_id = models.CharField(
        '企业微信CorpID', max_length=200, blank=True, null=True,
        help_text='[Deprecated] 请使用SSO配置管理'
    )
    dingtalk_corp_id = models.CharField(
        '钉钉CorpID', max_length=200, blank=True, null=True,
        help_text='[Deprecated] 请使用SSO配置管理'
    )
    feishu_corp_id = models.CharField(
        '飞书CorpID', max_length=200, blank=True, null=True,
        help_text='[Deprecated] 请使用SSO配置管理'
    )
    
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '公司'
        verbose_name_plural = '公司'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_all_children(self):
        """Get all descendant companies recursively"""
        children = list(self.children.filter(is_active=True))
        all_children = []
        for child in children:
            all_children.append(child)
            all_children.extend(child.get_all_children())
        return all_children
    
    def get_group_companies(self):
        """Get all companies in the same group (including self)"""
        if self.parent:
            # Find root company
            root = self
            while root.parent:
                root = root.parent
            return [root] + root.get_all_children()
        return [self] + self.get_all_children()
    
    @property
    def is_group_root(self):
        """Check if this is a group root company"""
        return self.parent is None and self.children.exists()


class Department(MPTTModel):
    """部门模型（树形结构）"""
    
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='departments',
        verbose_name='所属公司'
    )
    name = models.CharField('部门名称', max_length=255)
    code = models.CharField('部门代码', max_length=100)
    parent = TreeForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name='上级部门'
    )
    manager = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_departments',
        verbose_name='部门负责人'
    )
    description = models.TextField('部门描述', blank=True, null=True)
    sort_order = models.IntegerField('排序', default=0)
    
    # SSO 关联
    wework_dept_id = models.CharField('企业微信部门ID', max_length=50, blank=True, null=True)
    dingtalk_dept_id = models.CharField('钉钉部门ID', max_length=50, blank=True, null=True)
    feishu_dept_id = models.CharField('飞书部门ID', max_length=50, blank=True, null=True)
    
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class MPTTMeta:
        order_insertion_by = ['sort_order', 'name']
    
    class Meta:
        verbose_name = '部门'
        verbose_name_plural = '部门'
        unique_together = ['company', 'code']
    
    def __str__(self):
        return f"{self.company.short_name or self.company.name} - {self.name}"
    
    @property
    def full_name(self):
        """获取完整部门路径名称"""
        ancestors = self.get_ancestors(include_self=True)
        return ' / '.join([a.name for a in ancestors])


class Location(MPTTModel):
    """存放区域/位置模型（树形结构）"""
    
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='locations',
        verbose_name='所属公司'
    )
    name = models.CharField('区域名称', max_length=100)
    code = models.CharField('区域代码', max_length=50)
    parent = TreeForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name='上级区域'
    )
    address = models.CharField('详细地址', max_length=500, blank=True, null=True)
    description = models.TextField('区域描述', blank=True, null=True)
    sort_order = models.IntegerField('排序', default=0)
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class MPTTMeta:
        order_insertion_by = ['sort_order', 'name']
    
    class Meta:
        verbose_name = '存放区域'
        verbose_name_plural = '存放区域'
        unique_together = ['company', 'code']
    
    def __str__(self):
        return self.name
    
    @property
    def full_name(self):
        """获取完整区域路径名称"""
        ancestors = self.get_ancestors(include_self=True)
        return ' / '.join([a.name for a in ancestors])


class OrganizationChange(models.Model):
    """组织异动记录"""
    
    class ChangeType(models.TextChoices):
        CREATE = 'create', '新建'
        UPDATE = 'update', '修改'
        DELETE = 'delete', '删除'
        MOVE = 'move', '移动'
        MERGE = 'merge', '合并'
    
    class Status(models.TextChoices):
        PENDING = 'pending', '待处理'
        APPROVED = 'approved', '已通过'
        REJECTED = 'rejected', '已拒绝'
        PROCESSED = 'processed', '已处理'
    
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        related_name='changes',
        verbose_name='部门'
    )
    change_type = models.CharField('变更类型', max_length=20, choices=ChangeType.choices)
    status = models.CharField('状态', max_length=20, choices=Status.choices, default=Status.PENDING)
    old_data = models.JSONField('原数据', null=True, blank=True)
    new_data = models.JSONField('新数据', null=True, blank=True)
    description = models.TextField('变更说明', blank=True, null=True)
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='org_changes_created',
        verbose_name='创建人'
    )
    processed_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='org_changes_processed',
        verbose_name='处理人'
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    processed_at = models.DateTimeField('处理时间', null=True, blank=True)
    
    class Meta:
        verbose_name = '组织异动'
        verbose_name_plural = '组织异动'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.department.name if self.department else '未知'} - {self.get_change_type_display()}"


class CrossCompanyTransfer(models.Model):
    """
    Cross-company asset transfer record for financial audit
    跨公司资产调拨记录 - 用于财务审计
    
    This model tracks asset transfers between different legal entities,
    supporting various settlement types for proper financial accounting.
    
    Financial Impact Calculation:
    - Internal Transfer: No monetary exchange, book value transfer
    - Cost Allocation: Charge based on depreciation or usage
    - Market Price: Transfer at current fair market value
    """
    
    class TransferType(models.TextChoices):
        TRANSFER = 'transfer', '调拨'           # Permanent transfer
        LEASE = 'lease', '租借'                 # Temporary lease between companies
        ALLOCATION = 'allocation', '划拨'       # Administrative allocation
        SALE = 'sale', '销售'                   # Internal sale
    
    class SettlementType(models.TextChoices):
        INTERNAL = 'internal', '内部划转'              # No cash exchange
        COST_ALLOCATION = 'cost_allocation', '费用分摊'  # Based on depreciation
        MARKET_PRICE = 'market_price', '市场定价'       # Fair market value
        BOOK_VALUE = 'book_value', '账面价值'           # Transfer at book value
    
    class Status(models.TextChoices):
        DRAFT = 'draft', '草稿'
        PENDING = 'pending', '待审批'
        APPROVED = 'approved', '已审批'
        IN_TRANSIT = 'in_transit', '调拨中'
        COMPLETED = 'completed', '已完成'
        REJECTED = 'rejected', '已拒绝'
        CANCELLED = 'cancelled', '已取消'
    
    # Transfer identification
    transfer_no = models.CharField('调拨单号', max_length=50, unique=True)
    transfer_type = models.CharField(
        '调拨类型',
        max_length=20,
        choices=TransferType.choices,
        default=TransferType.TRANSFER
    )
    
    # Source company info
    from_company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='outgoing_transfers',
        verbose_name='调出公司'
    )
    from_department = models.ForeignKey(
        'organizations.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='outgoing_cross_transfers',
        verbose_name='调出部门'
    )
    
    # Destination company info
    to_company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='incoming_transfers',
        verbose_name='调入公司'
    )
    to_department = models.ForeignKey(
        'organizations.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='incoming_cross_transfers',
        verbose_name='调入部门'
    )
    
    # Financial information
    transfer_value = models.DecimalField(
        '调拨价值',
        max_digits=19,
        decimal_places=4,
        default=0,
        help_text='调拨资产的总价值'
    )
    settlement_type = models.CharField(
        '结算方式',
        max_length=20,
        choices=SettlementType.choices,
        default=SettlementType.INTERNAL
    )
    settlement_amount = models.DecimalField(
        '结算金额',
        max_digits=19,
        decimal_places=4,
        default=0,
        help_text='实际结算金额，可能与调拨价值不同'
    )
    settlement_date = models.DateField('结算日期', null=True, blank=True)
    
    # Business context
    reason = models.TextField('调拨原因', blank=True, null=True)
    remark = models.TextField('备注', blank=True, null=True)
    
    # Workflow status
    status = models.CharField(
        '状态',
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT
    )
    
    # Approval chain
    from_approver = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='from_company_approvals',
        verbose_name='调出审批人'
    )
    from_approved_at = models.DateTimeField('调出审批时间', null=True, blank=True)
    
    to_approver = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='to_company_approvals',
        verbose_name='调入审批人'
    )
    to_approved_at = models.DateTimeField('调入审批时间', null=True, blank=True)
    
    # Audit trail
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='cross_transfers_created',
        verbose_name='创建人'
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    completed_at = models.DateTimeField('完成时间', null=True, blank=True)
    
    class Meta:
        verbose_name = '跨公司调拨'
        verbose_name_plural = '跨公司调拨'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.transfer_no}: {self.from_company.short_name or self.from_company.name} → {self.to_company.short_name or self.to_company.name}"
    
    def save(self, *args, **kwargs):
        # Auto-generate transfer number if not set
        if not self.transfer_no:
            from django.utils import timezone
            import uuid
            date_str = timezone.now().strftime('%Y%m%d')
            short_uuid = str(uuid.uuid4())[:8].upper()
            self.transfer_no = f"CCT{date_str}{short_uuid}"
        super().save(*args, **kwargs)


class CrossCompanyTransferItem(models.Model):
    """
    Cross-company transfer item - Links assets to transfer records
    跨公司调拨明细
    """
    
    transfer = models.ForeignKey(
        CrossCompanyTransfer,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='调拨单'
    )
    asset = models.ForeignKey(
        'assets.Asset',
        on_delete=models.CASCADE,
        related_name='cross_company_transfers',
        verbose_name='资产'
    )
    
    # Snapshot of asset value at transfer time for audit
    original_value = models.DecimalField(
        '原值',
        max_digits=19,
        decimal_places=4,
        null=True,
        blank=True
    )
    book_value = models.DecimalField(
        '账面净值',
        max_digits=19,
        decimal_places=4,
        null=True,
        blank=True
    )
    transfer_price = models.DecimalField(
        '调拨价格',
        max_digits=19,
        decimal_places=4,
        default=0
    )
    
    # Asset state snapshot
    asset_snapshot = models.JSONField(
        '资产快照',
        default=dict,
        help_text='资产在调拨时的完整信息快照'
    )
    
    remark = models.TextField('备注', blank=True, null=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '跨公司调拨明细'
        verbose_name_plural = '跨公司调拨明细'
        unique_together = ['transfer', 'asset']
    
    def __str__(self):
        return f"{self.transfer.transfer_no} - {self.asset.name}"
