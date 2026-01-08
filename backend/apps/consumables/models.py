"""
办公用品管理模型 - 钩子资产管理系统
Office Supplies Management Models

Note: The internal model names remain as 'Consumable' for backward compatibility,
but display names (verbose_name) have been updated to '办公用品' (Office Supplies).
"""
from django.db import models
from mptt.models import MPTTModel, TreeForeignKey


class ConsumableCategory(MPTTModel):
    """办公用品分类 (Office Supplies Category)"""
    
    company = models.ForeignKey(
        'organizations.Company',
        on_delete=models.CASCADE,
        related_name='consumable_categories',
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
    description = models.TextField('描述', blank=True, null=True)
    sort_order = models.IntegerField('排序', default=0)
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '用品分类'
        verbose_name_plural = '用品分类'
        unique_together = ['company', 'code']
    
    def __str__(self):
        return self.name


class Consumable(models.Model):
    """办公用品档案 (Office Supplies)"""
    
    company = models.ForeignKey(
        'organizations.Company',
        on_delete=models.CASCADE,
        related_name='consumables',
        verbose_name='所属公司'
    )
    code = models.CharField('用品编码', max_length=100)
    name = models.CharField('用品名称', max_length=200)
    category = models.ForeignKey(
        ConsumableCategory,
        on_delete=models.SET_NULL,
        null=True,
        related_name='consumables',
        verbose_name='用品分类'
    )
    brand = models.CharField('品牌', max_length=100, blank=True, null=True)
    model = models.CharField('规格型号', max_length=200, blank=True, null=True)
    unit = models.CharField('计量单位', max_length=20, default='个')
    price = models.DecimalField('单价', max_digits=15, decimal_places=2, default=0)
    image = models.ImageField('图片', upload_to='supplies/', blank=True, null=True)
    
    # 库存预警
    min_stock = models.IntegerField('安全库存', default=0)
    max_stock = models.IntegerField('最高库存', default=0)
    
    description = models.TextField('描述', blank=True, null=True)
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '办公用品'
        verbose_name_plural = '办公用品'
        unique_together = ['company', 'code']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class ConsumableStock(models.Model):
    """办公用品库存 (Office Supplies Stock)"""
    
    consumable = models.ForeignKey(
        Consumable,
        on_delete=models.CASCADE,
        related_name='stocks',
        verbose_name='用品'
    )
    warehouse = models.ForeignKey(
        'organizations.Location',
        on_delete=models.CASCADE,
        related_name='consumable_stocks',
        verbose_name='仓库'
    )
    quantity = models.IntegerField('库存数量', default=0)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '用品库存'
        verbose_name_plural = '用品库存'
        unique_together = ['consumable', 'warehouse']
    
    def __str__(self):
        return f"{self.consumable.name} - {self.warehouse.name}: {self.quantity}"


class ConsumableInbound(models.Model):
    """办公用品入库单 (Office Supplies Inbound)"""
    
    class Status(models.TextChoices):
        DRAFT = 'draft', '草稿'
        PENDING = 'pending', '待审批'
        APPROVED = 'approved', '已入库'
        CANCELLED = 'cancelled', '已取消'
    
    inbound_no = models.CharField('入库单号', max_length=50, unique=True)
    company = models.ForeignKey(
        'organizations.Company',
        on_delete=models.CASCADE,
        related_name='consumable_inbounds',
        verbose_name='所属公司'
    )
    warehouse = models.ForeignKey(
        'organizations.Location',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='入库仓库'
    )
    status = models.CharField('状态', max_length=20, choices=Status.choices, default=Status.DRAFT)
    inbound_date = models.DateField('入库日期')
    supplier = models.ForeignKey(
        'procurement.Supplier',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='供应商'
    )
    total_amount = models.DecimalField('总金额', max_digits=15, decimal_places=2, default=0)
    remark = models.TextField('备注', blank=True, null=True)
    
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='创建人'
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '用品入库单'
        verbose_name_plural = '用品入库单'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.inbound_no


class ConsumableInboundItem(models.Model):
    """办公用品入库明细 (Office Supplies Inbound Item)"""
    
    inbound = models.ForeignKey(
        ConsumableInbound,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='入库单'
    )
    consumable = models.ForeignKey(
        Consumable,
        on_delete=models.CASCADE,
        verbose_name='用品'
    )
    quantity = models.IntegerField('数量')
    price = models.DecimalField('单价', max_digits=15, decimal_places=2)
    amount = models.DecimalField('金额', max_digits=15, decimal_places=2)
    
    class Meta:
        verbose_name = '用品入库明细'
        verbose_name_plural = '用品入库明细'


class ConsumableOutbound(models.Model):
    """办公用品出库单 (Office Supplies Outbound / Requisition)"""
    
    class Status(models.TextChoices):
        DRAFT = 'draft', '草稿'
        PENDING = 'pending', '待审批'
        APPROVED = 'approved', '已出库'
        CANCELLED = 'cancelled', '已取消'
    
    class OutboundType(models.TextChoices):
        RECEIVE = 'receive', '领用'
        RETURN = 'return', '退库'
    
    outbound_no = models.CharField('出库单号', max_length=50, unique=True)
    company = models.ForeignKey(
        'organizations.Company',
        on_delete=models.CASCADE,
        related_name='consumable_outbounds',
        verbose_name='所属公司'
    )
    warehouse = models.ForeignKey(
        'organizations.Location',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='出库仓库'
    )
    outbound_type = models.CharField('出库类型', max_length=20, choices=OutboundType.choices)
    status = models.CharField('状态', max_length=20, choices=Status.choices, default=Status.DRAFT)
    outbound_date = models.DateField('出库日期')
    
    receive_user = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='consumable_receives',
        verbose_name='领用人'
    )
    receive_department = models.ForeignKey(
        'organizations.Department',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='领用部门'
    )
    reason = models.TextField('领用原因', blank=True, null=True)
    remark = models.TextField('备注', blank=True, null=True)
    
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_consumable_outbounds',
        verbose_name='创建人'
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '用品出库单'
        verbose_name_plural = '用品出库单'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.outbound_no


class ConsumableOutboundItem(models.Model):
    """办公用品出库明细 (Office Supplies Outbound Item)"""
    
    outbound = models.ForeignKey(
        ConsumableOutbound,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='出库单'
    )
    consumable = models.ForeignKey(
        Consumable,
        on_delete=models.CASCADE,
        verbose_name='用品'
    )
    quantity = models.IntegerField('数量')
    
    class Meta:
        verbose_name = '用品出库明细'
        verbose_name_plural = '用品出库明细'
