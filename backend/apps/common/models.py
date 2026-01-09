"""
通用模型基类 - 钩子资产管理系统

遵循 .cursorrules 规约:
- 所有 Model 必须继承 BaseModel (包含 created_at, updated_at, is_deleted, created_by)
- 禁止物理删除，必须实现 soft_delete 逻辑
"""
from django.db import models
from django.conf import settings
from django.utils import timezone


class SoftDeleteManager(models.Manager):
    """
    软删除管理器
    
    默认过滤已删除的记录，提供 all_with_deleted() 查询所有记录
    """
    
    def get_queryset(self):
        """默认只返回未删除的记录"""
        return super().get_queryset().filter(is_deleted=False)
    
    def all_with_deleted(self):
        """返回包含已删除记录的查询集"""
        return super().get_queryset()
    
    def deleted_only(self):
        """只返回已删除的记录"""
        return super().get_queryset().filter(is_deleted=True)


class BaseModel(models.Model):
    """
    模型基类
    
    遵循 .cursorrules 规约:
    - 包含 created_at, updated_at, is_deleted, created_by 字段
    - 实现软删除逻辑
    
    所有业务模型都应继承此类
    
    动态表单支持:
    - custom_fields: JSONField 存储自定义字段值
    """
    
    created_at = models.DateTimeField(
        '创建时间',
        auto_now_add=True,
        db_index=True
    )
    updated_at = models.DateTimeField(
        '更新时间',
        auto_now=True
    )
    is_deleted = models.BooleanField(
        '是否删除',
        default=False,
        db_index=True
    )
    deleted_at = models.DateTimeField(
        '删除时间',
        null=True,
        blank=True
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_created',
        verbose_name='创建人'
    )
    
    # Dynamic form custom fields storage
    # Stores values for user-defined custom fields as JSON
    # Format: {"field_key": value, "another_field": value}
    custom_fields = models.JSONField(
        '自定义字段',
        default=dict,
        blank=True,
        help_text='存储动态表单系统中的自定义字段值'
    )
    
    # 使用软删除管理器
    objects = SoftDeleteManager()
    all_objects = models.Manager()  # 包含已删除记录的管理器
    
    class Meta:
        abstract = True
    
    def soft_delete(self, user=None):
        """
        软删除
        
        遵循 .cursorrules: 禁止物理删除，必须实现 soft_delete 逻辑
        
        Args:
            user: 执行删除操作的用户（可选）
        """
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=['is_deleted', 'deleted_at', 'updated_at'])
    
    def restore(self):
        """恢复已删除的记录"""
        self.is_deleted = False
        self.deleted_at = None
        self.save(update_fields=['is_deleted', 'deleted_at', 'updated_at'])
    
    def hard_delete(self):
        """
        物理删除（仅在特殊情况下使用）
        
        警告: 仅应在数据清理或维护时使用
        """
        super().delete()
    
    # =====================================================
    # Custom Fields Methods (Dynamic Form Support)
    # =====================================================
    
    def get_custom_field(self, field_key, default=None):
        """
        Get a custom field value.
        
        Args:
            field_key: The field key to retrieve
            default: Default value if field not found
            
        Returns:
            The field value or default
        """
        if not self.custom_fields:
            return default
        return self.custom_fields.get(field_key, default)
    
    def set_custom_field(self, field_key, value):
        """
        Set a custom field value.
        
        Args:
            field_key: The field key to set
            value: The value to store
        """
        if self.custom_fields is None:
            self.custom_fields = {}
        self.custom_fields[field_key] = value
    
    def set_custom_fields(self, fields_dict):
        """
        Set multiple custom field values at once.
        
        Args:
            fields_dict: Dictionary of field_key: value pairs
        """
        if self.custom_fields is None:
            self.custom_fields = {}
        self.custom_fields.update(fields_dict)
    
    def remove_custom_field(self, field_key):
        """
        Remove a custom field.
        
        Args:
            field_key: The field key to remove
        """
        if self.custom_fields and field_key in self.custom_fields:
            del self.custom_fields[field_key]
    
    def get_all_custom_fields(self):
        """
        Get all custom fields.
        
        Returns:
            dict: All custom field values
        """
        return self.custom_fields or {}


class TimeStampedModel(models.Model):
    """
    时间戳模型
    
    简化版本，仅包含创建和更新时间
    用于不需要软删除的辅助表
    """
    
    created_at = models.DateTimeField(
        '创建时间',
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        '更新时间',
        auto_now=True
    )
    
    class Meta:
        abstract = True


# =====================================================
# 金额字段规范
# 遵循 .cursorrules: 金额字段必须使用 DecimalField(max_digits=19, decimal_places=4)
# =====================================================

def MoneyField(verbose_name, **kwargs):
    """
    金额字段工厂函数
    
    遵循 .cursorrules 规约:
    金额字段必须使用 DecimalField(max_digits=19, decimal_places=4)
    
    Args:
        verbose_name: 字段名称
        **kwargs: 其他 DecimalField 参数
        
    Returns:
        DecimalField 实例
        
    Example:
        original_value = MoneyField('原值')
        current_value = MoneyField('净值', null=True, blank=True)
    """
    defaults = {
        'max_digits': 19,
        'decimal_places': 4,
        'default': 0,
    }
    defaults.update(kwargs)
    return models.DecimalField(verbose_name, **defaults)
