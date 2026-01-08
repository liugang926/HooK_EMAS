"""
动态表单字段配置模型

此模块定义了动态表单系统的核心模型，支持：
- 动态字段定义
- 字段分组
- 字段权限控制
- 多种字段类型（文本、数字、日期、选择、引用等）
"""

from django.db import models


class FieldGroup(models.Model):
    """字段分组模型"""
    
    module = models.CharField('模块名称', max_length=50, db_index=True)
    group_key = models.CharField('分组键', max_length=50)
    group_name = models.CharField('分组名称', max_length=100)
    sort_order = models.IntegerField('排序', default=0)
    is_collapsible = models.BooleanField('可折叠', default=False)
    default_collapsed = models.BooleanField('默认折叠', default=False)
    is_active = models.BooleanField('是否启用', default=True)
    
    class Meta:
        verbose_name = '字段分组'
        verbose_name_plural = verbose_name
        unique_together = ['module', 'group_key']
        ordering = ['module', 'sort_order']
    
    def __str__(self):
        return f"{self.module} - {self.group_name}"


class FieldDefinition(models.Model):
    """字段定义模型"""
    
    class FieldType(models.TextChoices):
        TEXT = 'text', '单行文本'
        TEXTAREA = 'textarea', '多行文本'
        NUMBER = 'number', '数字'
        DECIMAL = 'decimal', '小数'
        DATE = 'date', '日期'
        DATETIME = 'datetime', '日期时间'
        SELECT = 'select', '下拉选择'
        MULTI_SELECT = 'multi_select', '多选'
        RADIO = 'radio', '单选框'
        CHECKBOX = 'checkbox', '复选框'
        SWITCH = 'switch', '开关'
        REFERENCE = 'reference', '引用查找'
        TREE_SELECT = 'tree_select', '树形选择'
        CASCADER = 'cascader', '级联选择'
        IMAGE = 'image', '图片上传'
        FILE = 'file', '文件上传'
        RICH_TEXT = 'rich_text', '富文本'
        CODE = 'code', '代码/编号'  # 自动生成的编号
    
    # 基本信息
    module = models.CharField(
        '模块名称', 
        max_length=50, 
        db_index=True,
        help_text='如：asset, consumable, procurement'
    )
    field_key = models.CharField(
        '字段键', 
        max_length=100,
        help_text='对应数据库字段名或自定义字段键'
    )
    field_name = models.CharField('字段名称', max_length=100)
    field_type = models.CharField(
        '字段类型', 
        max_length=20, 
        choices=FieldType.choices,
        default=FieldType.TEXT
    )
    
    # 分组
    group = models.ForeignKey(
        FieldGroup,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='fields',
        verbose_name='所属分组'
    )
    sort_order = models.IntegerField('排序', default=0)
    
    # 权限控制
    is_required = models.BooleanField('是否必填', default=False)
    is_readonly = models.BooleanField('始终只读', default=False)
    is_readonly_on_create = models.BooleanField('新增时只读', default=False)
    is_readonly_on_edit = models.BooleanField('编辑时只读', default=False)
    is_hidden = models.BooleanField('始终隐藏', default=False)
    is_hidden_on_create = models.BooleanField('新增时隐藏', default=False)
    is_hidden_on_edit = models.BooleanField('编辑时隐藏', default=False)
    
    # 下拉选项配置（用于 select/multi_select/radio 类型）
    options = models.JSONField(
        '选项列表', 
        default=list, 
        blank=True,
        help_text='格式：[{"label": "显示名", "value": "值"}, ...]'
    )
    
    # 引用配置（用于 reference/tree_select/cascader 类型）
    reference_config = models.JSONField(
        '引用配置',
        default=dict,
        blank=True,
        help_text='''格式：{
            "api": "/api/path",
            "labelField": "name",
            "valueField": "id",
            "searchField": "name",
            "multiple": false,
            "treeData": false,
            "parentField": "parent_id",
            "autoFillFields": {"department": "user.department"}
        }'''
    )
    
    # 数字配置（用于 number/decimal 类型）
    number_config = models.JSONField(
        '数字配置',
        default=dict,
        blank=True,
        help_text='格式：{"min": 0, "max": 999999, "precision": 2, "step": 1}'
    )
    
    # 自动生成编号配置（用于 code 类型）
    code_config = models.JSONField(
        '编号配置',
        default=dict,
        blank=True,
        help_text='格式：{"prefix": "ZC", "dateFormat": "YYYYMMDD", "length": 8}'
    )
    
    # 默认值
    default_value = models.JSONField('默认值', null=True, blank=True)
    
    # 验证规则
    validation_rules = models.JSONField(
        '验证规则',
        default=list,
        blank=True,
        help_text='''格式：[
            {"type": "length", "min": 1, "max": 100, "message": "长度必须在1-100之间"},
            {"type": "pattern", "pattern": "^[A-Z]+$", "message": "只能输入大写字母"},
            {"type": "custom", "validator": "validatePhone", "message": "手机号格式不正确"}
        ]'''
    )
    
    # 显示配置
    placeholder = models.CharField('占位符', max_length=200, blank=True)
    help_text = models.CharField('帮助文本', max_length=500, blank=True)
    width = models.IntegerField(
        '宽度', 
        default=8,
        help_text='栅格宽度，1-24，默认8表示一行3列'
    )
    
    # 列表显示配置
    show_in_list = models.BooleanField('列表中显示', default=False)
    list_width = models.IntegerField('列表列宽', default=150)
    list_sortable = models.BooleanField('列表可排序', default=False)
    list_searchable = models.BooleanField('列表可搜索', default=False)
    
    # 系统配置
    is_system = models.BooleanField(
        '系统字段', 
        default=False,
        help_text='系统字段不允许删除'
    )
    is_active = models.BooleanField('是否启用', default=True)
    
    # 扩展配置
    extra_config = models.JSONField(
        '扩展配置',
        default=dict,
        blank=True,
        help_text='其他自定义配置'
    )
    
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '字段定义'
        verbose_name_plural = verbose_name
        unique_together = ['module', 'field_key']
        ordering = ['module', 'group__sort_order', 'sort_order']
    
    def __str__(self):
        return f"{self.module}.{self.field_key} ({self.field_name})"
    
    def get_field_config(self, mode='create'):
        """
        获取字段配置（用于前端渲染）
        
        Args:
            mode: 'create' 或 'edit'
        
        Returns:
            dict: 字段配置字典
        """
        config = {
            'key': self.field_key,
            'label': self.field_name,
            'type': self.field_type,
            'required': self.is_required,
            'readonly': self._is_readonly(mode),
            'hidden': self._is_hidden(mode),
            'placeholder': self.placeholder,
            'helpText': self.help_text,
            'width': self.width,
            'defaultValue': self.default_value,
            'rules': self._build_validation_rules(),
        }
        
        # 根据字段类型添加特定配置
        if self.field_type in ['select', 'multi_select', 'radio']:
            config['options'] = self.options
        
        if self.field_type in ['reference', 'tree_select', 'cascader']:
            config['referenceConfig'] = self.reference_config
        
        if self.field_type in ['number', 'decimal']:
            config['numberConfig'] = self.number_config
        
        if self.field_type == 'code':
            config['codeConfig'] = self.code_config
        
        if self.extra_config:
            config['extra'] = self.extra_config
        
        return config
    
    def _is_readonly(self, mode):
        """判断字段是否只读"""
        if self.is_readonly:
            return True
        if mode == 'create' and self.is_readonly_on_create:
            return True
        if mode == 'edit' and self.is_readonly_on_edit:
            return True
        return False
    
    def _is_hidden(self, mode):
        """判断字段是否隐藏"""
        if self.is_hidden:
            return True
        if mode == 'create' and self.is_hidden_on_create:
            return True
        if mode == 'edit' and self.is_hidden_on_edit:
            return True
        return False
    
    def _build_validation_rules(self):
        """构建验证规则"""
        rules = []
        
        if self.is_required:
            rules.append({
                'required': True,
                'message': f'请输入{self.field_name}',
                'trigger': 'blur' if self.field_type in ['text', 'textarea', 'number', 'decimal'] else 'change'
            })
        
        # 添加自定义验证规则
        for rule in self.validation_rules:
            rules.append(rule)
        
        return rules


class ModuleFormConfig(models.Model):
    """模块表单配置"""
    
    module = models.CharField('模块名称', max_length=50, unique=True)
    module_label = models.CharField('模块显示名', max_length=100)
    
    # API配置
    api_base = models.CharField(
        'API基础路径',
        max_length=200,
        help_text='如：/api/assets/list/'
    )
    
    # 表单配置
    dialog_width = models.CharField('弹窗宽度', max_length=20, default='900px')
    label_width = models.CharField('标签宽度', max_length=20, default='100px')
    
    # 功能开关
    enable_create = models.BooleanField('允许新增', default=True)
    enable_edit = models.BooleanField('允许编辑', default=True)
    enable_delete = models.BooleanField('允许删除', default=True)
    enable_import = models.BooleanField('允许导入', default=True)
    enable_export = models.BooleanField('允许导出', default=True)
    
    # 扩展配置
    extra_config = models.JSONField('扩展配置', default=dict, blank=True)
    
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '模块表单配置'
        verbose_name_plural = verbose_name
    
    def __str__(self):
        return f"{self.module} ({self.module_label})"
    
    def get_form_config(self, mode='create'):
        """获取完整的表单配置"""
        groups = FieldGroup.objects.filter(
            module=self.module, 
            is_active=True
        ).order_by('sort_order')
        
        fields = FieldDefinition.objects.filter(
            module=self.module, 
            is_active=True
        ).select_related('group').order_by('group__sort_order', 'sort_order')
        
        # 按分组组织字段
        grouped_fields = {}
        ungrouped_fields = []
        
        for field in fields:
            field_config = field.get_field_config(mode)
            if field_config['hidden']:
                continue
            
            if field.group:
                group_key = field.group.group_key
                if group_key not in grouped_fields:
                    grouped_fields[group_key] = {
                        'key': group_key,
                        'name': field.group.group_name,
                        'collapsible': field.group.is_collapsible,
                        'collapsed': field.group.default_collapsed,
                        'sortOrder': field.group.sort_order,
                        'fields': []
                    }
                grouped_fields[group_key]['fields'].append(field_config)
            else:
                ungrouped_fields.append(field_config)
        
        # 构建最终配置
        return {
            'module': self.module,
            'moduleLabel': self.module_label,
            'apiBase': self.api_base,
            'dialogWidth': self.dialog_width,
            'labelWidth': self.label_width,
            'permissions': {
                'create': self.enable_create,
                'edit': self.enable_edit,
                'delete': self.enable_delete,
                'import': self.enable_import,
                'export': self.enable_export,
            },
            'groups': list(grouped_fields.values()),
            'ungroupedFields': ungrouped_fields,
            'extra': self.extra_config,
        }
