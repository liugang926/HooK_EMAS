"""
资产管理模型 - 精臣云资产管理系统
"""
from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from decimal import Decimal


class AssetCategory(MPTTModel):
    """资产分类（树形结构）"""
    
    company = models.ForeignKey(
        'organizations.Company',
        on_delete=models.CASCADE,
        related_name='asset_categories',
        verbose_name='所属公司'
    )
    name = models.CharField('分类名称', max_length=100)
    code = models.CharField('分类代码', max_length=50)
    parent = TreeForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name='上级分类'
    )
    description = models.TextField('分类描述', blank=True, null=True)
    
    # 默认配置
    depreciation_method = models.CharField('折旧方式', max_length=50, blank=True, null=True)
    useful_life = models.IntegerField('使用年限(月)', null=True, blank=True)
    salvage_rate = models.DecimalField('残值率(%)', max_digits=5, decimal_places=2, null=True, blank=True)
    
    # 自定义字段配置
    custom_fields = models.JSONField('自定义字段', default=list)
    
    sort_order = models.IntegerField('排序', default=0)
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class MPTTMeta:
        order_insertion_by = ['sort_order', 'name']
    
    class Meta:
        verbose_name = '资产分类'
        verbose_name_plural = '资产分类'
        unique_together = ['company', 'code']
    
    def __str__(self):
        return self.name


class Asset(models.Model):
    """资产主模型"""
    
    class Status(models.TextChoices):
        IDLE = 'idle', '闲置'
        IN_USE = 'in_use', '在用'
        BORROWED = 'borrowed', '借用'
        MAINTENANCE = 'maintenance', '维修中'
        PENDING_MAINTENANCE = 'pending_maintenance', '待维修'
        DISPOSED = 'disposed', '已处置'
        PENDING_DISPOSAL = 'pending_disposal', '待处置'
        APPROVING = 'approving', '审批中'
    
    class AcquisitionMethod(models.TextChoices):
        PURCHASE = 'purchase', '采购'
        LEASE = 'lease', '租赁'
        GIFT = 'gift', '赠予'
        TRANSFER = 'transfer', '调入'
        SELF_BUILD = 'self_build', '自建'
        OTHER = 'other', '其他'
    
    # 基本信息
    company = models.ForeignKey(
        'organizations.Company',
        on_delete=models.CASCADE,
        related_name='assets',
        verbose_name='所属公司'
    )
    asset_code = models.CharField('资产编码', max_length=100)
    name = models.CharField('资产名称', max_length=200)
    category = models.ForeignKey(
        AssetCategory,
        on_delete=models.SET_NULL,
        null=True,
        related_name='assets',
        verbose_name='资产分类'
    )
    status = models.CharField('资产状态', max_length=30, choices=Status.choices, default=Status.IDLE)
    
    # 规格信息
    brand = models.CharField('品牌', max_length=100, blank=True, null=True)
    model = models.CharField('规格型号', max_length=200, blank=True, null=True)
    serial_number = models.CharField('序列号', max_length=200, blank=True, null=True)
    unit = models.CharField('计量单位', max_length=20, default='台')
    quantity = models.IntegerField('数量', default=1)
    
    # 图片和附件
    image = models.ImageField('资产图片', upload_to='assets/images/', blank=True, null=True)
    attachments = models.JSONField('附件列表', default=list)
    
    # 财务信息
    acquisition_method = models.CharField(
        '取得方式',
        max_length=20,
        choices=AcquisitionMethod.choices,
        default=AcquisitionMethod.PURCHASE
    )
    acquisition_date = models.DateField('取得日期', null=True, blank=True)
    original_value = models.DecimalField('原值', max_digits=15, decimal_places=2, default=0)
    current_value = models.DecimalField('净值', max_digits=15, decimal_places=2, default=0)
    accumulated_depreciation = models.DecimalField('累计折旧', max_digits=15, decimal_places=2, default=0)
    
    # 折旧信息
    depreciation_method = models.CharField('折旧方式', max_length=50, blank=True, null=True)
    useful_life = models.IntegerField('使用年限(月)', null=True, blank=True)
    salvage_rate = models.DecimalField('残值率(%)', max_digits=5, decimal_places=2, null=True, blank=True)
    depreciation_start_date = models.DateField('折旧开始日期', null=True, blank=True)
    
    # 使用信息
    using_department = models.ForeignKey(
        'organizations.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='using_assets',
        verbose_name='使用部门'
    )
    using_user = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='using_assets',
        verbose_name='使用人'
    )
    location = models.ForeignKey(
        'organizations.Location',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assets',
        verbose_name='存放区域'
    )
    
    # 管理信息
    manage_department = models.ForeignKey(
        'organizations.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_assets',
        verbose_name='管理部门'
    )
    manager = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_assets',
        verbose_name='资产管理员'
    )
    
    # 标签信息
    rfid_code = models.CharField('RFID编码', max_length=100, blank=True, null=True)
    barcode = models.CharField('条形码', max_length=100, blank=True, null=True)
    qrcode = models.CharField('二维码', max_length=200, blank=True, null=True)
    
    # 供应商信息
    supplier = models.ForeignKey(
        'procurement.Supplier',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assets',
        verbose_name='供应商'
    )
    warranty_expiry = models.DateField('保修到期日', null=True, blank=True)
    
    # 资产组合
    parent_asset = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='child_assets',
        verbose_name='主资产'
    )
    is_component = models.BooleanField('是否备件', default=False)
    
    # 自定义字段
    custom_data = models.JSONField('自定义字段数据', default=dict)
    
    # 备注
    remark = models.TextField('备注', blank=True, null=True)
    
    # 审计字段
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_assets',
        verbose_name='创建人'
    )
    is_deleted = models.BooleanField('是否删除', default=False)
    deleted_at = models.DateTimeField('删除时间', null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '资产'
        verbose_name_plural = '资产'
        ordering = ['-created_at']
        unique_together = ['company', 'asset_code']
    
    def __str__(self):
        return f"{self.asset_code} - {self.name}"
    
    @property
    def salvage_value(self):
        """残值"""
        if self.salvage_rate:
            return self.original_value * (self.salvage_rate / 100)
        return Decimal('0')


class AssetImage(models.Model):
    """资产图片"""
    
    asset = models.ForeignKey(
        Asset,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name='资产'
    )
    image = models.ImageField('图片', upload_to='assets/images/')
    is_primary = models.BooleanField('主图', default=False)
    sort_order = models.IntegerField('排序', default=0)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '资产图片'
        verbose_name_plural = '资产图片'
        ordering = ['sort_order', '-created_at']


class AssetOperation(models.Model):
    """资产操作记录"""
    
    class OperationType(models.TextChoices):
        CREATE = 'create', '录入'
        UPDATE = 'update', '编辑'
        RECEIVE = 'receive', '领用'
        RETURN = 'return', '退还'
        BORROW = 'borrow', '借用'
        GIVE_BACK = 'give_back', '归还'
        TRANSFER = 'transfer', '调拨'
        CHANGE = 'change', '变更'
        MAINTENANCE = 'maintenance', '维保'
        DISPOSE = 'dispose', '处置'
        INVENTORY = 'inventory', '盘点'
    
    asset = models.ForeignKey(
        Asset,
        on_delete=models.CASCADE,
        related_name='operations',
        verbose_name='资产'
    )
    operation_type = models.CharField('操作类型', max_length=30, choices=OperationType.choices)
    operation_no = models.CharField('操作单号', max_length=50, blank=True, null=True)
    description = models.TextField('操作描述', blank=True, null=True)
    old_data = models.JSONField('操作前数据', null=True, blank=True)
    new_data = models.JSONField('操作后数据', null=True, blank=True)
    operator = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='asset_operations',
        verbose_name='操作人'
    )
    created_at = models.DateTimeField('操作时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '资产操作记录'
        verbose_name_plural = '资产操作记录'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.asset.asset_code} - {self.get_operation_type_display()}"


class AssetReceive(models.Model):
    """资产领用单"""
    
    class Status(models.TextChoices):
        DRAFT = 'draft', '草稿'
        PENDING = 'pending', '待审批'
        APPROVED = 'approved', '已通过'
        REJECTED = 'rejected', '已拒绝'
        COMPLETED = 'completed', '已完成'
        CANCELLED = 'cancelled', '已取消'
    
    receive_no = models.CharField('领用单号', max_length=50, unique=True)
    company = models.ForeignKey(
        'organizations.Company',
        on_delete=models.CASCADE,
        related_name='asset_receives',
        verbose_name='所属公司'
    )
    status = models.CharField('状态', max_length=20, choices=Status.choices, default=Status.DRAFT)
    
    # 领用信息
    receive_user = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='asset_receives',
        verbose_name='领用人'
    )
    receive_department = models.ForeignKey(
        'organizations.Department',
        on_delete=models.SET_NULL,
        null=True,
        related_name='asset_receives',
        verbose_name='领用部门'
    )
    receive_date = models.DateField('领用日期')
    expected_return_date = models.DateField('预计归还日期', null=True, blank=True)
    reason = models.TextField('领用原因', blank=True, null=True)
    remark = models.TextField('备注', blank=True, null=True)
    
    # 审批信息
    workflow_instance = models.ForeignKey(
        'workflows.WorkflowInstance',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='审批流程'
    )
    
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_asset_receives',
        verbose_name='创建人'
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '资产领用单'
        verbose_name_plural = '资产领用单'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.receive_no


class AssetReceiveItem(models.Model):
    """资产领用单明细"""
    
    receive = models.ForeignKey(
        AssetReceive,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='领用单'
    )
    asset = models.ForeignKey(
        Asset,
        on_delete=models.CASCADE,
        related_name='receive_items',
        verbose_name='资产'
    )
    quantity = models.IntegerField('数量', default=1)
    is_returned = models.BooleanField('是否退还', default=False)
    return_date = models.DateField('退还日期', null=True, blank=True)
    remark = models.TextField('备注', blank=True, null=True)
    
    class Meta:
        verbose_name = '资产领用明细'
        verbose_name_plural = '资产领用明细'


class AssetBorrow(models.Model):
    """资产借用单"""
    
    class Status(models.TextChoices):
        DRAFT = 'draft', '草稿'
        PENDING = 'pending', '待审批'
        APPROVED = 'approved', '已通过'
        REJECTED = 'rejected', '已拒绝'
        BORROWED = 'borrowed', '借用中'
        RETURNED = 'returned', '已归还'
        CANCELLED = 'cancelled', '已取消'
    
    borrow_no = models.CharField('借用单号', max_length=50, unique=True)
    company = models.ForeignKey(
        'organizations.Company',
        on_delete=models.CASCADE,
        related_name='asset_borrows',
        verbose_name='所属公司'
    )
    status = models.CharField('状态', max_length=20, choices=Status.choices, default=Status.DRAFT)
    
    # 借用信息
    borrower = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='asset_borrows',
        verbose_name='借用人'
    )
    borrow_department = models.ForeignKey(
        'organizations.Department',
        on_delete=models.SET_NULL,
        null=True,
        related_name='asset_borrows',
        verbose_name='借用部门'
    )
    borrow_date = models.DateField('借用日期')
    expected_return_date = models.DateField('预计归还日期')
    actual_return_date = models.DateField('实际归还日期', null=True, blank=True)
    reason = models.TextField('借用原因', blank=True, null=True)
    remark = models.TextField('备注', blank=True, null=True)
    
    # 审批信息
    workflow_instance = models.ForeignKey(
        'workflows.WorkflowInstance',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='审批流程'
    )
    
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_asset_borrows',
        verbose_name='创建人'
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '资产借用单'
        verbose_name_plural = '资产借用单'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.borrow_no


class AssetBorrowItem(models.Model):
    """资产借用单明细"""
    
    borrow = models.ForeignKey(
        AssetBorrow,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='借用单'
    )
    asset = models.ForeignKey(
        Asset,
        on_delete=models.CASCADE,
        related_name='borrow_items',
        verbose_name='资产'
    )
    quantity = models.IntegerField('数量', default=1)
    is_returned = models.BooleanField('是否归还', default=False)
    return_date = models.DateField('归还日期', null=True, blank=True)
    remark = models.TextField('备注', blank=True, null=True)
    
    class Meta:
        verbose_name = '资产借用明细'
        verbose_name_plural = '资产借用明细'


class AssetTransfer(models.Model):
    """资产调拨单"""
    
    class Status(models.TextChoices):
        DRAFT = 'draft', '草稿'
        PENDING = 'pending', '待审批'
        APPROVED = 'approved', '已通过'
        REJECTED = 'rejected', '已拒绝'
        COMPLETED = 'completed', '已完成'
        CANCELLED = 'cancelled', '已取消'
    
    transfer_no = models.CharField('调拨单号', max_length=50, unique=True)
    company = models.ForeignKey(
        'organizations.Company',
        on_delete=models.CASCADE,
        related_name='asset_transfers',
        verbose_name='所属公司'
    )
    status = models.CharField('状态', max_length=20, choices=Status.choices, default=Status.DRAFT)
    
    # 调出方
    from_department = models.ForeignKey(
        'organizations.Department',
        on_delete=models.SET_NULL,
        null=True,
        related_name='asset_transfers_out',
        verbose_name='调出部门'
    )
    from_user = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='asset_transfers_out',
        verbose_name='调出人'
    )
    from_location = models.ForeignKey(
        'organizations.Location',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='asset_transfers_out',
        verbose_name='调出位置'
    )
    
    # 调入方
    to_department = models.ForeignKey(
        'organizations.Department',
        on_delete=models.SET_NULL,
        null=True,
        related_name='asset_transfers_in',
        verbose_name='调入部门'
    )
    to_user = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='asset_transfers_in',
        verbose_name='调入人'
    )
    to_location = models.ForeignKey(
        'organizations.Location',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='asset_transfers_in',
        verbose_name='调入位置'
    )
    
    transfer_date = models.DateField('调拨日期')
    reason = models.TextField('调拨原因', blank=True, null=True)
    remark = models.TextField('备注', blank=True, null=True)
    
    workflow_instance = models.ForeignKey(
        'workflows.WorkflowInstance',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='审批流程'
    )
    
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_asset_transfers',
        verbose_name='创建人'
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '资产调拨单'
        verbose_name_plural = '资产调拨单'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.transfer_no


class AssetTransferItem(models.Model):
    """资产调拨单明细"""
    
    transfer = models.ForeignKey(
        AssetTransfer,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='调拨单'
    )
    asset = models.ForeignKey(
        Asset,
        on_delete=models.CASCADE,
        related_name='transfer_items',
        verbose_name='资产'
    )
    quantity = models.IntegerField('数量', default=1)
    
    # 调拨前的原始信息
    from_user = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transfer_items_from',
        verbose_name='原使用人'
    )
    from_department = models.ForeignKey(
        'organizations.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transfer_items_from',
        verbose_name='原部门'
    )
    from_location = models.ForeignKey(
        'organizations.Location',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transfer_items_from',
        verbose_name='原位置'
    )
    
    remark = models.TextField('备注', blank=True, null=True)
    
    class Meta:
        verbose_name = '资产调拨明细'
        verbose_name_plural = '资产调拨明细'


class AssetDisposal(models.Model):
    """资产处置单"""
    
    class Status(models.TextChoices):
        DRAFT = 'draft', '草稿'
        PENDING = 'pending', '待审批'
        APPROVED = 'approved', '已通过'
        REJECTED = 'rejected', '已拒绝'
        COMPLETED = 'completed', '已完成'
        CANCELLED = 'cancelled', '已取消'
    
    class DisposalMethod(models.TextChoices):
        SCRAP = 'scrap', '报废'
        SELL = 'sell', '出售'
        DONATE = 'donate', '捐赠'
        TRANSFER_OUT = 'transfer_out', '调出'
        OTHER = 'other', '其他'
    
    disposal_no = models.CharField('处置单号', max_length=50, unique=True)
    company = models.ForeignKey(
        'organizations.Company',
        on_delete=models.CASCADE,
        related_name='asset_disposals',
        verbose_name='所属公司'
    )
    status = models.CharField('状态', max_length=20, choices=Status.choices, default=Status.DRAFT)
    disposal_method = models.CharField('处置方式', max_length=20, choices=DisposalMethod.choices)
    disposal_date = models.DateField('处置日期')
    disposal_amount = models.DecimalField('处置金额', max_digits=15, decimal_places=2, default=0)
    reason = models.TextField('处置原因', blank=True, null=True)
    remark = models.TextField('备注', blank=True, null=True)
    
    workflow_instance = models.ForeignKey(
        'workflows.WorkflowInstance',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='审批流程'
    )
    
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_asset_disposals',
        verbose_name='创建人'
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '资产处置单'
        verbose_name_plural = '资产处置单'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.disposal_no


class AssetDisposalItem(models.Model):
    """资产处置单明细"""
    
    disposal = models.ForeignKey(
        AssetDisposal,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='处置单'
    )
    asset = models.ForeignKey(
        Asset,
        on_delete=models.CASCADE,
        related_name='disposal_items',
        verbose_name='资产'
    )
    original_value = models.DecimalField('原值', max_digits=15, decimal_places=2)
    current_value = models.DecimalField('净值', max_digits=15, decimal_places=2)
    disposal_value = models.DecimalField('处置价值', max_digits=15, decimal_places=2, default=0)
    quantity = models.IntegerField('数量', default=1)
    remark = models.TextField('备注', blank=True, null=True)
    
    class Meta:
        verbose_name = '资产处置明细'
        verbose_name_plural = '资产处置明细'


class AssetMaintenance(models.Model):
    """资产维保记录"""
    
    class MaintenanceType(models.TextChoices):
        REPAIR = 'repair', '维修'
        MAINTAIN = 'maintain', '保养'
        UPGRADE = 'upgrade', '升级'
        OTHER = 'other', '其他'
    
    class Status(models.TextChoices):
        PENDING = 'pending', '待处理'
        IN_PROGRESS = 'in_progress', '处理中'
        COMPLETED = 'completed', '已完成'
        CANCELLED = 'cancelled', '已取消'
    
    maintenance_no = models.CharField('维保单号', max_length=50, unique=True)
    asset = models.ForeignKey(
        Asset,
        on_delete=models.CASCADE,
        related_name='maintenances',
        verbose_name='资产'
    )
    maintenance_type = models.CharField('维保类型', max_length=20, choices=MaintenanceType.choices)
    status = models.CharField('状态', max_length=20, choices=Status.choices, default=Status.PENDING)
    
    description = models.TextField('问题描述')
    start_date = models.DateField('开始日期', null=True, blank=True)
    end_date = models.DateField('完成日期', null=True, blank=True)
    cost = models.DecimalField('维保费用', max_digits=15, decimal_places=2, default=0)
    service_provider = models.CharField('服务商', max_length=200, blank=True, null=True)
    result = models.TextField('维保结果', blank=True, null=True)
    
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_maintenances',
        verbose_name='创建人'
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '资产维保'
        verbose_name_plural = '资产维保'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.maintenance_no


class AssetLabel(models.Model):
    """资产标签模板"""
    
    company = models.ForeignKey(
        'organizations.Company',
        on_delete=models.CASCADE,
        related_name='asset_labels',
        verbose_name='所属公司'
    )
    name = models.CharField('模板名称', max_length=100)
    width = models.IntegerField('宽度(mm)')
    height = models.IntegerField('高度(mm)')
    template_config = models.JSONField('模板配置', default=dict)
    is_default = models.BooleanField('默认模板', default=False)
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '资产标签模板'
        verbose_name_plural = '资产标签模板'
    
    def __str__(self):
        return self.name
