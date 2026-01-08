"""
采购管理模型 - 精臣云资产管理系统
"""
from django.db import models


class Supplier(models.Model):
    """供应商"""
    
    company = models.ForeignKey(
        'organizations.Company',
        on_delete=models.CASCADE,
        related_name='suppliers',
        verbose_name='所属公司'
    )
    code = models.CharField('供应商编码', max_length=50)
    name = models.CharField('供应商名称', max_length=200)
    short_name = models.CharField('简称', max_length=50, blank=True, null=True)
    contact = models.CharField('联系人', max_length=50, blank=True, null=True)
    phone = models.CharField('联系电话', max_length=50, blank=True, null=True)
    email = models.EmailField('邮箱', blank=True, null=True)
    address = models.CharField('地址', max_length=500, blank=True, null=True)
    bank_name = models.CharField('开户银行', max_length=100, blank=True, null=True)
    bank_account = models.CharField('银行账号', max_length=100, blank=True, null=True)
    tax_number = models.CharField('税号', max_length=50, blank=True, null=True)
    description = models.TextField('描述', blank=True, null=True)
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '供应商'
        verbose_name_plural = '供应商'
        unique_together = ['company', 'code']
    
    def __str__(self):
        return self.name


class PurchaseRequest(models.Model):
    """采购申请"""
    
    class Status(models.TextChoices):
        DRAFT = 'draft', '草稿'
        PENDING = 'pending', '待审批'
        APPROVED = 'approved', '已通过'
        REJECTED = 'rejected', '已拒绝'
        CANCELLED = 'cancelled', '已取消'
    
    request_no = models.CharField('申请单号', max_length=50, unique=True)
    company = models.ForeignKey(
        'organizations.Company',
        on_delete=models.CASCADE,
        related_name='purchase_requests',
        verbose_name='所属公司'
    )
    status = models.CharField('状态', max_length=20, choices=Status.choices, default=Status.DRAFT)
    request_date = models.DateField('申请日期')
    expected_date = models.DateField('期望到货日期', null=True, blank=True)
    department = models.ForeignKey(
        'organizations.Department',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='申请部门'
    )
    reason = models.TextField('申请原因', blank=True, null=True)
    total_amount = models.DecimalField('总金额', max_digits=15, decimal_places=2, default=0)
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
        verbose_name='创建人'
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '采购申请'
        verbose_name_plural = '采购申请'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.request_no


class PurchaseRequestItem(models.Model):
    """采购申请明细"""
    
    class ItemType(models.TextChoices):
        ASSET = 'asset', '资产'
        CONSUMABLE = 'consumable', '耗材'
    
    request = models.ForeignKey(
        PurchaseRequest,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='采购申请'
    )
    item_type = models.CharField('物品类型', max_length=20, choices=ItemType.choices)
    name = models.CharField('物品名称', max_length=200)
    model = models.CharField('规格型号', max_length=200, blank=True, null=True)
    unit = models.CharField('单位', max_length=20, default='个')
    quantity = models.IntegerField('数量')
    estimated_price = models.DecimalField('预估单价', max_digits=15, decimal_places=2, default=0)
    estimated_amount = models.DecimalField('预估金额', max_digits=15, decimal_places=2, default=0)
    remark = models.TextField('备注', blank=True, null=True)
    
    class Meta:
        verbose_name = '采购申请明细'
        verbose_name_plural = '采购申请明细'


class PurchaseOrder(models.Model):
    """采购订单"""
    
    class Status(models.TextChoices):
        DRAFT = 'draft', '草稿'
        PENDING = 'pending', '待审批'
        APPROVED = 'approved', '已通过'
        PARTIAL = 'partial', '部分入库'
        COMPLETED = 'completed', '已完成'
        CANCELLED = 'cancelled', '已取消'
    
    order_no = models.CharField('订单编号', max_length=50, unique=True)
    company = models.ForeignKey(
        'organizations.Company',
        on_delete=models.CASCADE,
        related_name='purchase_orders',
        verbose_name='所属公司'
    )
    purchase_request = models.ForeignKey(
        PurchaseRequest,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='采购申请'
    )
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='供应商'
    )
    status = models.CharField('状态', max_length=20, choices=Status.choices, default=Status.DRAFT)
    order_date = models.DateField('订单日期')
    expected_date = models.DateField('预计到货日期', null=True, blank=True)
    total_amount = models.DecimalField('总金额', max_digits=15, decimal_places=2, default=0)
    paid_amount = models.DecimalField('已付金额', max_digits=15, decimal_places=2, default=0)
    remark = models.TextField('备注', blank=True, null=True)
    
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='创建人'
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '采购订单'
        verbose_name_plural = '采购订单'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.order_no


class PurchaseOrderItem(models.Model):
    """采购订单明细"""
    
    order = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='采购订单'
    )
    name = models.CharField('物品名称', max_length=200)
    model = models.CharField('规格型号', max_length=200, blank=True, null=True)
    unit = models.CharField('单位', max_length=20)
    quantity = models.IntegerField('数量')
    price = models.DecimalField('单价', max_digits=15, decimal_places=2)
    amount = models.DecimalField('金额', max_digits=15, decimal_places=2)
    received_quantity = models.IntegerField('已入库数量', default=0)
    
    class Meta:
        verbose_name = '采购订单明细'
        verbose_name_plural = '采购订单明细'
