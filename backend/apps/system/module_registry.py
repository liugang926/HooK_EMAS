"""
Module Registry - Universal Dynamic Form Management System

This module defines all system modules with their default system fields,
API configurations, and code rule settings.

Each module registration includes:
- label: Display name for the module
- api_base: Base API endpoint for CRUD operations
- code_rule_prefix: Prefix for auto-generated codes (optional)
- code_rule_type: Code rule type identifier
- enable_custom_fields: Whether custom fields are supported
- system_fields: List of default system fields

Usage:
    from apps.system.module_registry import MODULE_REGISTRY, get_module_config
    
    config = get_module_config('asset')
    fields = config['system_fields']
"""

# Field type constants (matching FieldDefinition.FieldType)
FIELD_TYPE_TEXT = 'text'
FIELD_TYPE_TEXTAREA = 'textarea'
FIELD_TYPE_NUMBER = 'number'
FIELD_TYPE_DECIMAL = 'decimal'
FIELD_TYPE_DATE = 'date'
FIELD_TYPE_DATETIME = 'datetime'
FIELD_TYPE_SELECT = 'select'
FIELD_TYPE_MULTI_SELECT = 'multi_select'
FIELD_TYPE_RADIO = 'radio'
FIELD_TYPE_SWITCH = 'switch'
FIELD_TYPE_REFERENCE = 'reference'
FIELD_TYPE_TREE_SELECT = 'tree_select'
FIELD_TYPE_CASCADER = 'cascader'
FIELD_TYPE_IMAGE = 'image'
FIELD_TYPE_FILE = 'file'
FIELD_TYPE_CODE = 'code'


MODULE_REGISTRY = {
    # ==================== Asset Module ====================
    'asset': {
        'label': '资产',
        'api_base': '/api/assets/list/',
        'code_rule_prefix': 'ZC',
        'code_rule_type': 'asset_code',
        'enable_custom_fields': True,
        'system_fields': [
            {
                'field_key': 'asset_code',
                'field_name': '资产编号',
                'field_type': FIELD_TYPE_CODE,
                'is_required': True,
                'is_system': True,
                'show_in_list': True,
                'list_sortable': True,
                'sort_order': 1,
                'width': 8,
            },
            {
                'field_key': 'name',
                'field_name': '资产名称',
                'field_type': FIELD_TYPE_TEXT,
                'is_required': True,
                'is_system': True,
                'show_in_list': True,
                'list_searchable': True,
                'sort_order': 2,
                'width': 8,
            },
            {
                'field_key': 'category',
                'field_name': '资产分类',
                'field_type': FIELD_TYPE_TREE_SELECT,
                'is_required': True,
                'is_system': True,
                'show_in_list': True,
                'sort_order': 3,
                'width': 8,
                'reference_config': {
                    'api': '/api/assets/categories/',
                    'labelField': 'name',
                    'valueField': 'id',
                    'treeData': True,
                },
            },
            {
                'field_key': 'model',
                'field_name': '规格型号',
                'field_type': FIELD_TYPE_TEXT,
                'is_required': False,
                'is_system': True,
                'show_in_list': True,
                'sort_order': 4,
                'width': 8,
            },
            {
                'field_key': 'brand',
                'field_name': '品牌',
                'field_type': FIELD_TYPE_TEXT,
                'is_required': False,
                'is_system': True,
                'show_in_list': True,
                'sort_order': 5,
                'width': 8,
            },
            {
                'field_key': 'serial_number',
                'field_name': '序列号',
                'field_type': FIELD_TYPE_TEXT,
                'is_required': False,
                'is_system': True,
                'show_in_list': False,
                'sort_order': 6,
                'width': 8,
            },
            {
                'field_key': 'original_value',
                'field_name': '原值',
                'field_type': FIELD_TYPE_DECIMAL,
                'is_required': False,
                'is_system': True,
                'show_in_list': True,
                'sort_order': 7,
                'width': 8,
                'number_config': {'min': 0, 'precision': 2},
            },
            {
                'field_key': 'purchase_date',
                'field_name': '购置日期',
                'field_type': FIELD_TYPE_DATE,
                'is_required': False,
                'is_system': True,
                'show_in_list': True,
                'sort_order': 8,
                'width': 8,
            },
            {
                'field_key': 'location',
                'field_name': '存放位置',
                'field_type': FIELD_TYPE_TREE_SELECT,
                'is_required': False,
                'is_system': True,
                'show_in_list': True,
                'sort_order': 9,
                'width': 8,
                'reference_config': {
                    'api': '/api/organizations/locations/',
                    'labelField': 'name',
                    'valueField': 'id',
                    'treeData': True,
                },
            },
            {
                'field_key': 'department',
                'field_name': '使用部门',
                'field_type': FIELD_TYPE_TREE_SELECT,
                'is_required': False,
                'is_system': True,
                'show_in_list': True,
                'sort_order': 10,
                'width': 8,
                'reference_config': {
                    'api': '/api/organizations/departments/',
                    'labelField': 'name',
                    'valueField': 'id',
                    'treeData': True,
                },
            },
            {
                'field_key': 'user',
                'field_name': '使用人',
                'field_type': FIELD_TYPE_REFERENCE,
                'is_required': False,
                'is_system': True,
                'show_in_list': True,
                'sort_order': 11,
                'width': 8,
                'reference_config': {
                    'api': '/api/auth/users/',
                    'labelField': 'display_name',
                    'valueField': 'id',
                },
            },
            {
                'field_key': 'status',
                'field_name': '状态',
                'field_type': FIELD_TYPE_SELECT,
                'is_required': True,
                'is_system': True,
                'show_in_list': True,
                'sort_order': 12,
                'width': 8,
                'options': [
                    {'label': '闲置', 'value': 'idle'},
                    {'label': '在用', 'value': 'in_use'},
                    {'label': '维修', 'value': 'repair'},
                    {'label': '报废', 'value': 'scrapped'},
                ],
                'default_value': 'idle',
            },
            {
                'field_key': 'description',
                'field_name': '描述',
                'field_type': FIELD_TYPE_TEXTAREA,
                'is_required': False,
                'is_system': True,
                'show_in_list': False,
                'sort_order': 13,
                'width': 24,
            },
        ],
    },
    
    # ==================== Supply (Office Supplies) Module ====================
    'supply': {
        'label': '办公用品',
        'api_base': '/api/consumables/list/',
        'code_rule_prefix': 'BG',
        'code_rule_type': 'supply_code',
        'enable_custom_fields': True,
        'system_fields': [
            {
                'field_key': 'code',
                'field_name': '用品编号',
                'field_type': FIELD_TYPE_CODE,
                'is_required': True,
                'is_system': True,
                'show_in_list': True,
                'list_sortable': True,
                'sort_order': 1,
                'width': 8,
            },
            {
                'field_key': 'name',
                'field_name': '用品名称',
                'field_type': FIELD_TYPE_TEXT,
                'is_required': True,
                'is_system': True,
                'show_in_list': True,
                'list_searchable': True,
                'sort_order': 2,
                'width': 8,
            },
            {
                'field_key': 'category',
                'field_name': '用品分类',
                'field_type': FIELD_TYPE_TREE_SELECT,
                'is_required': True,
                'is_system': True,
                'show_in_list': True,
                'sort_order': 3,
                'width': 8,
                'reference_config': {
                    'api': '/api/consumables/categories/',
                    'labelField': 'name',
                    'valueField': 'id',
                    'treeData': True,
                },
            },
            {
                'field_key': 'model',
                'field_name': '规格型号',
                'field_type': FIELD_TYPE_TEXT,
                'is_required': False,
                'is_system': True,
                'show_in_list': True,
                'sort_order': 4,
                'width': 8,
            },
            {
                'field_key': 'unit',
                'field_name': '单位',
                'field_type': FIELD_TYPE_TEXT,
                'is_required': True,
                'is_system': True,
                'show_in_list': True,
                'sort_order': 5,
                'width': 8,
            },
            {
                'field_key': 'price',
                'field_name': '单价',
                'field_type': FIELD_TYPE_DECIMAL,
                'is_required': False,
                'is_system': True,
                'show_in_list': True,
                'sort_order': 6,
                'width': 8,
                'number_config': {'min': 0, 'precision': 2},
            },
            {
                'field_key': 'min_stock',
                'field_name': '库存预警',
                'field_type': FIELD_TYPE_NUMBER,
                'is_required': False,
                'is_system': True,
                'show_in_list': False,
                'sort_order': 7,
                'width': 8,
                'number_config': {'min': 0},
            },
            {
                'field_key': 'description',
                'field_name': '描述',
                'field_type': FIELD_TYPE_TEXTAREA,
                'is_required': False,
                'is_system': True,
                'show_in_list': False,
                'sort_order': 8,
                'width': 24,
            },
            {
                'field_key': 'is_active',
                'field_name': '是否启用',
                'field_type': FIELD_TYPE_SWITCH,
                'is_required': False,
                'is_system': True,
                'show_in_list': True,
                'sort_order': 9,
                'width': 8,
                'default_value': True,
            },
        ],
    },
    
    # ==================== User Module ====================
    'user': {
        'label': '用户',
        'api_base': '/api/auth/users/',
        'enable_custom_fields': True,
        'system_fields': [
            {
                'field_key': 'username',
                'field_name': '用户名',
                'field_type': FIELD_TYPE_TEXT,
                'is_required': True,
                'is_system': True,
                'show_in_list': True,
                'is_readonly_on_edit': True,
                'sort_order': 1,
                'width': 8,
            },
            {
                'field_key': 'display_name',
                'field_name': '显示名称',
                'field_type': FIELD_TYPE_TEXT,
                'is_required': False,
                'is_system': True,
                'show_in_list': True,
                'sort_order': 2,
                'width': 8,
            },
            {
                'field_key': 'email',
                'field_name': '邮箱',
                'field_type': FIELD_TYPE_TEXT,
                'is_required': False,
                'is_system': True,
                'show_in_list': True,
                'sort_order': 3,
                'width': 8,
            },
            {
                'field_key': 'phone',
                'field_name': '手机号',
                'field_type': FIELD_TYPE_TEXT,
                'is_required': False,
                'is_system': True,
                'show_in_list': True,
                'sort_order': 4,
                'width': 8,
            },
            {
                'field_key': 'department',
                'field_name': '所属部门',
                'field_type': FIELD_TYPE_TREE_SELECT,
                'is_required': False,
                'is_system': True,
                'show_in_list': True,
                'sort_order': 5,
                'width': 8,
                'reference_config': {
                    'api': '/api/organizations/departments/',
                    'labelField': 'name',
                    'valueField': 'id',
                    'treeData': True,
                },
            },
            {
                'field_key': 'position',
                'field_name': '职位',
                'field_type': FIELD_TYPE_TEXT,
                'is_required': False,
                'is_system': True,
                'show_in_list': True,
                'sort_order': 6,
                'width': 8,
            },
            {
                'field_key': 'is_active',
                'field_name': '是否启用',
                'field_type': FIELD_TYPE_SWITCH,
                'is_required': False,
                'is_system': True,
                'show_in_list': True,
                'sort_order': 7,
                'width': 8,
                'default_value': True,
            },
        ],
    },
    
    # ==================== Department Module ====================
    'department': {
        'label': '部门',
        'api_base': '/api/organizations/departments/',
        'enable_custom_fields': True,
        'tree_mode': True,
        'system_fields': [
            {
                'field_key': 'name',
                'field_name': '部门名称',
                'field_type': FIELD_TYPE_TEXT,
                'is_required': True,
                'is_system': True,
                'show_in_list': True,
                'sort_order': 1,
                'width': 8,
            },
            {
                'field_key': 'code',
                'field_name': '部门编码',
                'field_type': FIELD_TYPE_TEXT,
                'is_required': False,
                'is_system': True,
                'show_in_list': True,
                'sort_order': 2,
                'width': 8,
            },
            {
                'field_key': 'parent',
                'field_name': '上级部门',
                'field_type': FIELD_TYPE_TREE_SELECT,
                'is_required': False,
                'is_system': True,
                'show_in_list': False,
                'sort_order': 3,
                'width': 8,
                'reference_config': {
                    'api': '/api/organizations/departments/',
                    'labelField': 'name',
                    'valueField': 'id',
                    'treeData': True,
                },
            },
            {
                'field_key': 'manager',
                'field_name': '部门负责人',
                'field_type': FIELD_TYPE_REFERENCE,
                'is_required': False,
                'is_system': True,
                'show_in_list': True,
                'sort_order': 4,
                'width': 8,
                'reference_config': {
                    'api': '/api/auth/users/',
                    'labelField': 'display_name',
                    'valueField': 'id',
                },
            },
            {
                'field_key': 'sort_order',
                'field_name': '排序',
                'field_type': FIELD_TYPE_NUMBER,
                'is_required': False,
                'is_system': True,
                'show_in_list': False,
                'sort_order': 5,
                'width': 8,
                'default_value': 0,
            },
            {
                'field_key': 'is_active',
                'field_name': '是否启用',
                'field_type': FIELD_TYPE_SWITCH,
                'is_required': False,
                'is_system': True,
                'show_in_list': True,
                'sort_order': 6,
                'width': 8,
                'default_value': True,
            },
        ],
    },
    
    # ==================== Purchase Order Module ====================
    'purchase_order': {
        'label': '采购订单',
        'api_base': '/api/procurement/orders/',
        'code_rule_prefix': 'PO',
        'code_rule_type': 'purchase_order_code',
        'enable_custom_fields': True,
        'workflow': True,
        'system_fields': [
            {
                'field_key': 'order_no',
                'field_name': '订单编号',
                'field_type': FIELD_TYPE_CODE,
                'is_required': True,
                'is_system': True,
                'show_in_list': True,
                'list_sortable': True,
                'is_readonly_on_edit': True,
                'sort_order': 1,
                'width': 8,
            },
            {
                'field_key': 'title',
                'field_name': '订单标题',
                'field_type': FIELD_TYPE_TEXT,
                'is_required': True,
                'is_system': True,
                'show_in_list': True,
                'list_searchable': True,
                'sort_order': 2,
                'width': 16,
            },
            {
                'field_key': 'supplier',
                'field_name': '供应商',
                'field_type': FIELD_TYPE_REFERENCE,
                'is_required': True,
                'is_system': True,
                'show_in_list': True,
                'sort_order': 3,
                'width': 8,
                'reference_config': {
                    'api': '/api/procurement/suppliers/',
                    'labelField': 'name',
                    'valueField': 'id',
                },
            },
            {
                'field_key': 'order_date',
                'field_name': '订单日期',
                'field_type': FIELD_TYPE_DATE,
                'is_required': True,
                'is_system': True,
                'show_in_list': True,
                'list_sortable': True,
                'sort_order': 4,
                'width': 8,
            },
            {
                'field_key': 'total_amount',
                'field_name': '订单金额',
                'field_type': FIELD_TYPE_DECIMAL,
                'is_required': False,
                'is_system': True,
                'show_in_list': True,
                'is_readonly': True,
                'sort_order': 5,
                'width': 8,
                'number_config': {'min': 0, 'precision': 2},
            },
            {
                'field_key': 'status',
                'field_name': '状态',
                'field_type': FIELD_TYPE_SELECT,
                'is_required': True,
                'is_system': True,
                'show_in_list': True,
                'sort_order': 6,
                'width': 8,
                'options': [
                    {'label': '草稿', 'value': 'draft'},
                    {'label': '待审批', 'value': 'pending'},
                    {'label': '已批准', 'value': 'approved'},
                    {'label': '已拒绝', 'value': 'rejected'},
                    {'label': '已完成', 'value': 'completed'},
                    {'label': '已取消', 'value': 'cancelled'},
                ],
                'default_value': 'draft',
            },
            {
                'field_key': 'remark',
                'field_name': '备注',
                'field_type': FIELD_TYPE_TEXTAREA,
                'is_required': False,
                'is_system': True,
                'show_in_list': False,
                'sort_order': 7,
                'width': 24,
            },
        ],
    },
    
    # ==================== Supplier Module ====================
    'supplier': {
        'label': '供应商',
        'api_base': '/api/procurement/suppliers/',
        'enable_custom_fields': True,
        'system_fields': [
            {
                'field_key': 'code',
                'field_name': '供应商编码',
                'field_type': FIELD_TYPE_TEXT,
                'is_required': False,
                'is_system': True,
                'show_in_list': True,
                'sort_order': 1,
                'width': 8,
            },
            {
                'field_key': 'name',
                'field_name': '供应商名称',
                'field_type': FIELD_TYPE_TEXT,
                'is_required': True,
                'is_system': True,
                'show_in_list': True,
                'list_searchable': True,
                'sort_order': 2,
                'width': 8,
            },
            {
                'field_key': 'contact',
                'field_name': '联系人',
                'field_type': FIELD_TYPE_TEXT,
                'is_required': False,
                'is_system': True,
                'show_in_list': True,
                'sort_order': 3,
                'width': 8,
            },
            {
                'field_key': 'phone',
                'field_name': '联系电话',
                'field_type': FIELD_TYPE_TEXT,
                'is_required': False,
                'is_system': True,
                'show_in_list': True,
                'sort_order': 4,
                'width': 8,
            },
            {
                'field_key': 'email',
                'field_name': '邮箱',
                'field_type': FIELD_TYPE_TEXT,
                'is_required': False,
                'is_system': True,
                'show_in_list': False,
                'sort_order': 5,
                'width': 8,
            },
            {
                'field_key': 'address',
                'field_name': '地址',
                'field_type': FIELD_TYPE_TEXT,
                'is_required': False,
                'is_system': True,
                'show_in_list': False,
                'sort_order': 6,
                'width': 16,
            },
            {
                'field_key': 'is_active',
                'field_name': '是否启用',
                'field_type': FIELD_TYPE_SWITCH,
                'is_required': False,
                'is_system': True,
                'show_in_list': True,
                'sort_order': 7,
                'width': 8,
                'default_value': True,
            },
        ],
    },
    
    # ==================== Location Module ====================
    'location': {
        'label': '存放位置',
        'api_base': '/api/organizations/locations/',
        'enable_custom_fields': True,
        'tree_mode': True,
        'system_fields': [
            {
                'field_key': 'name',
                'field_name': '位置名称',
                'field_type': FIELD_TYPE_TEXT,
                'is_required': True,
                'is_system': True,
                'show_in_list': True,
                'sort_order': 1,
                'width': 8,
            },
            {
                'field_key': 'code',
                'field_name': '位置编码',
                'field_type': FIELD_TYPE_TEXT,
                'is_required': False,
                'is_system': True,
                'show_in_list': True,
                'sort_order': 2,
                'width': 8,
            },
            {
                'field_key': 'parent',
                'field_name': '上级位置',
                'field_type': FIELD_TYPE_TREE_SELECT,
                'is_required': False,
                'is_system': True,
                'show_in_list': False,
                'sort_order': 3,
                'width': 8,
                'reference_config': {
                    'api': '/api/organizations/locations/',
                    'labelField': 'name',
                    'valueField': 'id',
                    'treeData': True,
                },
            },
            {
                'field_key': 'address',
                'field_name': '详细地址',
                'field_type': FIELD_TYPE_TEXT,
                'is_required': False,
                'is_system': True,
                'show_in_list': False,
                'sort_order': 4,
                'width': 16,
            },
            {
                'field_key': 'type',
                'field_name': '位置类型',
                'field_type': FIELD_TYPE_SELECT,
                'is_required': False,
                'is_system': True,
                'show_in_list': True,
                'sort_order': 5,
                'width': 8,
                'options': [
                    {'label': '办公区', 'value': 'office'},
                    {'label': '仓库', 'value': 'warehouse'},
                    {'label': '其他', 'value': 'other'},
                ],
            },
        ],
    },
    
    # ==================== Company Module ====================
    'company': {
        'label': '公司',
        'api_base': '/api/organizations/companies/',
        'enable_custom_fields': True,
        'system_fields': [
            {
                'field_key': 'name',
                'field_name': '公司名称',
                'field_type': FIELD_TYPE_TEXT,
                'is_required': True,
                'is_system': True,
                'show_in_list': True,
                'sort_order': 1,
                'width': 8,
            },
            {
                'field_key': 'code',
                'field_name': '公司编码',
                'field_type': FIELD_TYPE_TEXT,
                'is_required': False,
                'is_system': True,
                'show_in_list': True,
                'sort_order': 2,
                'width': 8,
            },
            {
                'field_key': 'address',
                'field_name': '地址',
                'field_type': FIELD_TYPE_TEXT,
                'is_required': False,
                'is_system': True,
                'show_in_list': False,
                'sort_order': 3,
                'width': 16,
            },
            {
                'field_key': 'contact',
                'field_name': '联系人',
                'field_type': FIELD_TYPE_TEXT,
                'is_required': False,
                'is_system': True,
                'show_in_list': True,
                'sort_order': 4,
                'width': 8,
            },
            {
                'field_key': 'phone',
                'field_name': '联系电话',
                'field_type': FIELD_TYPE_TEXT,
                'is_required': False,
                'is_system': True,
                'show_in_list': True,
                'sort_order': 5,
                'width': 8,
            },
            {
                'field_key': 'is_active',
                'field_name': '是否启用',
                'field_type': FIELD_TYPE_SWITCH,
                'is_required': False,
                'is_system': True,
                'show_in_list': True,
                'sort_order': 6,
                'width': 8,
                'default_value': True,
            },
        ],
    },
}


def get_module_config(module_name):
    """
    Get configuration for a specific module.
    
    Args:
        module_name: Module identifier (e.g., 'asset', 'supply', 'user')
        
    Returns:
        dict: Module configuration or None if not found
    """
    return MODULE_REGISTRY.get(module_name)


def get_all_modules():
    """
    Get all registered modules.
    
    Returns:
        dict: All module configurations
    """
    return MODULE_REGISTRY


def get_module_choices():
    """
    Get module choices for form select fields.
    
    Returns:
        list: List of (value, label) tuples
    """
    return [(key, config['label']) for key, config in MODULE_REGISTRY.items()]


def get_modules_with_custom_fields():
    """
    Get modules that support custom fields.
    
    Returns:
        list: List of module names
    """
    return [
        key for key, config in MODULE_REGISTRY.items()
        if config.get('enable_custom_fields', False)
    ]


def get_modules_with_code_rules():
    """
    Get modules that have code rule configuration.
    
    Returns:
        list: List of module names
    """
    return [
        key for key, config in MODULE_REGISTRY.items()
        if config.get('code_rule_type')
    ]


def get_module_system_fields(module_name):
    """
    Get system fields for a specific module.
    
    Args:
        module_name: The module identifier
        
    Returns:
        list: List of system field configurations
    """
    config = get_module_config(module_name)
    if config:
        return config.get('system_fields', [])
    return []


def get_modules_with_feature(feature):
    """
    Get all modules that have a specific feature enabled.
    
    Args:
        feature: Feature name (e.g., 'custom_fields', 'workflow')
        
    Returns:
        list: List of module names with the feature enabled
    """
    return [
        name
        for name, config in MODULE_REGISTRY.items()
        if config.get('features', {}).get(feature, False)
    ]


def get_module_code_rule_config(module_name):
    """
    Get code rule configuration for a specific module.
    
    Args:
        module_name: The module identifier
        
    Returns:
        dict: Code rule configuration or None
    """
    config = get_module_config(module_name)
    if config:
        return config.get('code_rule')
    return None


def get_module_system_fields(module_name):
    """
    Get system fields for a specific module.
    
    Args:
        module_name: Module identifier
        
    Returns:
        list: System field definitions or empty list
    """
    config = get_module_config(module_name)
    if config:
        return config.get('system_fields', [])
    return []


def get_modules_with_feature(feature_name):
    """
    Get modules that have a specific feature enabled.
    
    Args:
        feature_name: Feature to check (e.g., 'enable_custom_fields', 'workflow', 'tree_mode')
        
    Returns:
        list: List of module names with the feature enabled
    """
    return [
        key for key, config in MODULE_REGISTRY.items()
        if config.get(feature_name, False)
    ]


def get_module_code_rule_config(module_name):
    """
    Get code rule configuration for a module.
    
    Args:
        module_name: Module identifier
        
    Returns:
        dict: Code rule config or None if not configured
    """
    config = get_module_config(module_name)
    if config and config.get('code_rule_type'):
        return {
            'code_rule_type': config.get('code_rule_type'),
            'code_rule_prefix': config.get('code_rule_prefix'),
        }
    return None
