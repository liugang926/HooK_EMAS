"""
动态表单配置序列化器
"""

from rest_framework import serializers
from .form_models import FieldGroup, FieldDefinition, ModuleFormConfig, FormLayout


class FieldGroupSerializer(serializers.ModelSerializer):
    """字段分组序列化器"""
    
    class Meta:
        model = FieldGroup
        fields = [
            'id', 'module', 'group_key', 'group_name', 'sort_order',
            'is_collapsible', 'default_collapsed', 'is_active'
        ]


class FieldDefinitionSerializer(serializers.ModelSerializer):
    """字段定义序列化器"""
    
    group_name = serializers.CharField(source='group.group_name', read_only=True, default='')
    
    class Meta:
        model = FieldDefinition
        fields = [
            'id', 'module', 'field_key', 'field_name', 'field_type',
            'group', 'group_name', 'sort_order',
            'is_required', 'is_readonly', 'is_readonly_on_create', 'is_readonly_on_edit',
            'is_hidden', 'is_hidden_on_create', 'is_hidden_on_edit',
            'options', 'reference_config', 'number_config', 'code_config',
            'default_value', 'validation_rules',
            'placeholder', 'help_text', 'width',
            'show_in_list', 'list_width', 'list_sortable', 'list_searchable',
            'is_system', 'is_active', 'extra_config',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class FieldDefinitionCreateSerializer(serializers.ModelSerializer):
    """字段定义创建序列化器"""
    
    class Meta:
        model = FieldDefinition
        fields = [
            'module', 'field_key', 'field_name', 'field_type',
            'group', 'sort_order',
            'is_required', 'is_readonly', 'is_readonly_on_create', 'is_readonly_on_edit',
            'is_hidden', 'is_hidden_on_create', 'is_hidden_on_edit',
            'options', 'reference_config', 'number_config', 'code_config',
            'default_value', 'validation_rules',
            'placeholder', 'help_text', 'width',
            'show_in_list', 'list_width', 'list_sortable', 'list_searchable',
            'is_system', 'is_active', 'extra_config'
        ]


class ModuleFormConfigSerializer(serializers.ModelSerializer):
    """模块表单配置序列化器"""
    
    class Meta:
        model = ModuleFormConfig
        fields = [
            'id', 'module', 'module_label', 'api_base',
            'dialog_width', 'label_width',
            'enable_create', 'enable_edit', 'enable_delete',
            'enable_import', 'enable_export',
            'extra_config', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class FormConfigResponseSerializer(serializers.Serializer):
    """表单配置响应序列化器（用于前端渲染）"""
    
    module = serializers.CharField()
    moduleLabel = serializers.CharField()
    apiBase = serializers.CharField()
    dialogWidth = serializers.CharField()
    labelWidth = serializers.CharField()
    permissions = serializers.DictField()
    groups = serializers.ListField()
    ungroupedFields = serializers.ListField()
    extra = serializers.DictField()


class FieldConfigSerializer(serializers.Serializer):
    """单个字段配置序列化器（用于前端渲染）"""
    
    key = serializers.CharField()
    label = serializers.CharField()
    type = serializers.CharField()
    required = serializers.BooleanField()
    readonly = serializers.BooleanField()
    hidden = serializers.BooleanField()
    placeholder = serializers.CharField(allow_blank=True)
    helpText = serializers.CharField(allow_blank=True)
    width = serializers.IntegerField()
    defaultValue = serializers.JSONField(allow_null=True)
    rules = serializers.ListField()
    options = serializers.ListField(required=False)
    referenceConfig = serializers.DictField(required=False)
    numberConfig = serializers.DictField(required=False)
    codeConfig = serializers.DictField(required=False)
    extra = serializers.DictField(required=False)


class BulkFieldUpdateSerializer(serializers.Serializer):
    """批量更新字段序列化器"""
    
    fields = serializers.ListField(
        child=serializers.DictField(),
        help_text='字段配置列表'
    )
    
    def validate_fields(self, value):
        for field_data in value:
            if 'field_key' not in field_data:
                raise serializers.ValidationError('每个字段必须包含 field_key')
        return value


class FormLayoutSerializer(serializers.ModelSerializer):
    """表单布局序列化器"""
    
    company_name = serializers.CharField(source='company.name', read_only=True, default='全局')
    created_by_name = serializers.CharField(source='created_by.display_name', read_only=True, default='')
    
    class Meta:
        model = FormLayout
        fields = [
            'id', 'module', 'layout_type', 'layout_name', 'layout_config',
            'company', 'company_name', 'is_default', 'is_active',
            'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'created_by']


class FormLayoutCreateSerializer(serializers.ModelSerializer):
    """表单布局创建序列化器"""
    
    class Meta:
        model = FormLayout
        fields = [
            'module', 'layout_type', 'layout_name', 'layout_config',
            'company', 'is_default', 'is_active'
        ]
    
    def create(self, validated_data):
        # 如果设置为默认布局，先取消同类型其他默认布局
        if validated_data.get('is_default'):
            FormLayout.objects.filter(
                module=validated_data['module'],
                layout_type=validated_data['layout_type'],
                company=validated_data.get('company'),
                is_default=True
            ).update(is_default=False)
        
        return super().create(validated_data)

