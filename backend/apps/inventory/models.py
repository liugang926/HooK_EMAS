"""
盘点管理模型 - 精臣云资产管理系统
"""
from django.db import models


class InventoryTask(models.Model):
    """盘点任务"""
    
    class Status(models.TextChoices):
        DRAFT = 'draft', '草稿'
        IN_PROGRESS = 'in_progress', '进行中'
        COMPLETED = 'completed', '已完成'
        CANCELLED = 'cancelled', '已取消'
    
    class InventoryType(models.TextChoices):
        FULL = 'full', '全盘'
        SPOT = 'spot', '抽盘'
        DEPARTMENT = 'department', '部门盘点'
        LOCATION = 'location', '区域盘点'
    
    task_no = models.CharField('任务编号', max_length=50, unique=True)
    company = models.ForeignKey(
        'organizations.Company',
        on_delete=models.CASCADE,
        related_name='inventory_tasks',
        verbose_name='所属公司'
    )
    name = models.CharField('任务名称', max_length=200)
    inventory_type = models.CharField('盘点类型', max_length=20, choices=InventoryType.choices)
    status = models.CharField('状态', max_length=20, choices=Status.choices, default=Status.DRAFT)
    
    # 盘点范围
    departments = models.ManyToManyField(
        'organizations.Department',
        blank=True,
        related_name='inventory_tasks',
        verbose_name='盘点部门'
    )
    locations = models.ManyToManyField(
        'organizations.Location',
        blank=True,
        related_name='inventory_tasks',
        verbose_name='盘点区域'
    )
    categories = models.ManyToManyField(
        'assets.AssetCategory',
        blank=True,
        related_name='inventory_tasks',
        verbose_name='盘点分类'
    )
    
    start_date = models.DateField('开始日期')
    end_date = models.DateField('截止日期')
    actual_start_date = models.DateField('实际开始日期', null=True, blank=True)
    actual_end_date = models.DateField('实际完成日期', null=True, blank=True)
    
    # 统计
    total_assets = models.IntegerField('应盘数量', default=0)
    checked_assets = models.IntegerField('已盘数量', default=0)
    normal_count = models.IntegerField('盘盈数量', default=0)
    loss_count = models.IntegerField('盘亏数量', default=0)
    surplus_count = models.IntegerField('盘盈数量', default=0)
    
    description = models.TextField('描述', blank=True, null=True)
    
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_inventory_tasks',
        verbose_name='创建人'
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '盘点任务'
        verbose_name_plural = '盘点任务'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.task_no} - {self.name}"


class InventoryRecord(models.Model):
    """盘点记录"""
    
    class Result(models.TextChoices):
        NORMAL = 'normal', '正常'
        LOSS = 'loss', '盘亏'
        SURPLUS = 'surplus', '盘盈'
        UNCHECKED = 'unchecked', '未盘'
    
    task = models.ForeignKey(
        InventoryTask,
        on_delete=models.CASCADE,
        related_name='records',
        verbose_name='盘点任务'
    )
    asset = models.ForeignKey(
        'assets.Asset',
        on_delete=models.CASCADE,
        related_name='inventory_records',
        verbose_name='资产'
    )
    result = models.CharField('盘点结果', max_length=20, choices=Result.choices, default=Result.UNCHECKED)
    
    # 账面信息
    book_department = models.ForeignKey(
        'organizations.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='book_inventory_records',
        verbose_name='账面部门'
    )
    book_location = models.ForeignKey(
        'organizations.Location',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='book_inventory_records',
        verbose_name='账面位置'
    )
    book_user = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='book_inventory_records',
        verbose_name='账面使用人'
    )
    
    # 实际信息
    actual_department = models.ForeignKey(
        'organizations.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='actual_inventory_records',
        verbose_name='实际部门'
    )
    actual_location = models.ForeignKey(
        'organizations.Location',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='actual_inventory_records',
        verbose_name='实际位置'
    )
    actual_user = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='actual_inventory_records',
        verbose_name='实际使用人'
    )
    
    check_time = models.DateTimeField('盘点时间', null=True, blank=True)
    checker = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='checked_inventory_records',
        verbose_name='盘点人'
    )
    images = models.JSONField('盘点照片', default=list)
    remark = models.TextField('备注', blank=True, null=True)
    
    class Meta:
        verbose_name = '盘点记录'
        verbose_name_plural = '盘点记录'
        unique_together = ['task', 'asset']
    
    def __str__(self):
        return f"{self.task.task_no} - {self.asset.asset_code}"
