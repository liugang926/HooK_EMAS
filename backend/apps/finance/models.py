"""
财务管理模型 - 精臣云资产管理系统
"""
from django.db import models


class DepreciationScheme(models.Model):
    """折旧方案"""
    
    class Method(models.TextChoices):
        STRAIGHT_LINE = 'straight_line', '直线法'
        DECLINING_BALANCE = 'declining_balance', '双倍余额递减法'
        SUM_OF_YEARS = 'sum_of_years', '年数总和法'
        UNITS_OF_PRODUCTION = 'units_of_production', '工作量法'
    
    company = models.ForeignKey(
        'organizations.Company',
        on_delete=models.CASCADE,
        related_name='depreciation_schemes',
        verbose_name='所属公司'
    )
    name = models.CharField('方案名称', max_length=100)
    method = models.CharField('折旧方法', max_length=30, choices=Method.choices)
    useful_life = models.IntegerField('使用年限(月)')
    salvage_rate = models.DecimalField('残值率(%)', max_digits=5, decimal_places=2, default=5)
    description = models.TextField('描述', blank=True, null=True)
    is_default = models.BooleanField('默认方案', default=False)
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '折旧方案'
        verbose_name_plural = '折旧方案'
    
    def __str__(self):
        return self.name


class AssetAccounting(models.Model):
    """资产入账记录"""
    
    class Status(models.TextChoices):
        PENDING = 'pending', '待入账'
        ACCOUNTED = 'accounted', '已入账'
        CANCELLED = 'cancelled', '已取消'
    
    accounting_no = models.CharField('入账单号', max_length=50, unique=True)
    company = models.ForeignKey(
        'organizations.Company',
        on_delete=models.CASCADE,
        related_name='asset_accountings',
        verbose_name='所属公司'
    )
    status = models.CharField('状态', max_length=20, choices=Status.choices, default=Status.PENDING)
    accounting_date = models.DateField('入账日期')
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
        verbose_name = '资产入账'
        verbose_name_plural = '资产入账'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.accounting_no


class AssetAccountingItem(models.Model):
    """资产入账明细"""
    
    accounting = models.ForeignKey(
        AssetAccounting,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='入账单'
    )
    asset = models.ForeignKey(
        'assets.Asset',
        on_delete=models.CASCADE,
        verbose_name='资产'
    )
    original_value = models.DecimalField('原值', max_digits=15, decimal_places=2)
    depreciation_scheme = models.ForeignKey(
        DepreciationScheme,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='折旧方案'
    )
    
    class Meta:
        verbose_name = '资产入账明细'
        verbose_name_plural = '资产入账明细'


class DepreciationRecord(models.Model):
    """折旧记录"""
    
    company = models.ForeignKey(
        'organizations.Company',
        on_delete=models.CASCADE,
        related_name='depreciation_records',
        verbose_name='所属公司'
    )
    asset = models.ForeignKey(
        'assets.Asset',
        on_delete=models.CASCADE,
        related_name='depreciation_records',
        verbose_name='资产'
    )
    period = models.CharField('折旧期间', max_length=10)  # 格式: YYYY-MM
    depreciation_amount = models.DecimalField('本期折旧额', max_digits=15, decimal_places=2)
    accumulated_depreciation = models.DecimalField('累计折旧', max_digits=15, decimal_places=2)
    current_value = models.DecimalField('当前净值', max_digits=15, decimal_places=2)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '折旧记录'
        verbose_name_plural = '折旧记录'
        unique_together = ['asset', 'period']
        ordering = ['-period']
    
    def __str__(self):
        return f"{self.asset.asset_code} - {self.period}"


class AssetLedger(models.Model):
    """资产财务台账"""
    
    asset = models.OneToOneField(
        'assets.Asset',
        on_delete=models.CASCADE,
        related_name='ledger',
        verbose_name='资产'
    )
    original_value = models.DecimalField('原值', max_digits=15, decimal_places=2, default=0)
    accumulated_depreciation = models.DecimalField('累计折旧', max_digits=15, decimal_places=2, default=0)
    current_value = models.DecimalField('净值', max_digits=15, decimal_places=2, default=0)
    impairment = models.DecimalField('减值准备', max_digits=15, decimal_places=2, default=0)
    
    depreciation_scheme = models.ForeignKey(
        DepreciationScheme,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='折旧方案'
    )
    depreciation_start_date = models.DateField('折旧开始日期', null=True, blank=True)
    remaining_months = models.IntegerField('剩余折旧月数', default=0)
    
    last_depreciation_date = models.DateField('最后折旧日期', null=True, blank=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '资产财务台账'
        verbose_name_plural = '资产财务台账'
    
    def __str__(self):
        return f"{self.asset.asset_code} - 台账"
