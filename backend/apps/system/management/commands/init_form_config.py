"""
初始化动态表单配置的管理命令

Usage:
    python manage.py init_form_config
    python manage.py init_form_config --module asset
    python manage.py init_form_config --reset  # 重置所有配置
"""

from django.core.management.base import BaseCommand
from apps.system.form_models import FieldGroup, FieldDefinition, ModuleFormConfig


class Command(BaseCommand):
    help = '初始化动态表单字段配置'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--module',
            type=str,
            help='指定要初始化的模块，不指定则初始化所有'
        )
        parser.add_argument(
            '--reset',
            action='store_true',
            help='重置配置（删除现有配置后重新创建）'
        )
    
    def handle(self, *args, **options):
        module = options.get('module')
        reset = options.get('reset', False)
        
        if reset:
            self.stdout.write(self.style.WARNING('正在重置配置...'))
            if module:
                FieldGroup.objects.filter(module=module).delete()
                FieldDefinition.objects.filter(module=module).delete()
                ModuleFormConfig.objects.filter(module=module).delete()
            else:
                FieldGroup.objects.all().delete()
                FieldDefinition.objects.all().delete()
                ModuleFormConfig.objects.all().delete()
        
        if not module or module == 'asset':
            self.init_asset_config()
        
        if not module or module == 'consumable':
            self.init_consumable_config()
        
        self.stdout.write(self.style.SUCCESS('表单配置初始化完成！'))
    
    def init_asset_config(self):
        """初始化资产模块配置"""
        self.stdout.write('初始化资产模块配置...')
        
        # 创建模块配置
        module_config, _ = ModuleFormConfig.objects.update_or_create(
            module='asset',
            defaults={
                'module_label': '资产',
                'api_base': '/api/assets/list/',
                'dialog_width': '900px',
                'label_width': '100px',
                'enable_create': True,
                'enable_edit': True,
                'enable_delete': True,
                'enable_import': True,
                'enable_export': True,
            }
        )
        
        # 创建字段分组
        groups = {
            'basic': self.create_group('asset', 'basic', '基本信息', 1),
            'finance': self.create_group('asset', 'finance', '财务信息', 2),
            'usage': self.create_group('asset', 'usage', '使用信息', 3),
            'management': self.create_group('asset', 'management', '管理信息', 4),
            'tags': self.create_group('asset', 'tags', '标签信息', 5),
            'image': self.create_group('asset', 'image', '资产图片', 6),
            'other': self.create_group('asset', 'other', '其他信息', 7),
        }
        
        # 创建字段定义
        fields = [
            # 基本信息
            {
                'module': 'asset',
                'field_key': 'asset_code',
                'field_name': '资产编号',
                'field_type': 'code',
                'group': groups['basic'],
                'sort_order': 1,
                'is_readonly': True,
                'is_system': True,
                'width': 8,
                'placeholder': '系统自动生成',
                'show_in_list': True,
                'list_width': 180,
                'list_sortable': True,
                'list_searchable': True,
                'code_config': {
                    'prefix': 'ZC',
                    'dateFormat': 'YYYYMMDD',
                    'length': 8
                }
            },
            {
                'module': 'asset',
                'field_key': 'name',
                'field_name': '资产名称',
                'field_type': 'text',
                'group': groups['basic'],
                'sort_order': 2,
                'is_required': True,
                'is_system': True,
                'width': 8,
                'placeholder': '请输入资产名称',
                'show_in_list': True,
                'list_width': 150,
                'list_searchable': True,
            },
            {
                'module': 'asset',
                'field_key': 'category',
                'field_name': '资产分类',
                'field_type': 'cascader',
                'group': groups['basic'],
                'sort_order': 3,
                'width': 8,
                'placeholder': '请选择分类',
                'show_in_list': True,
                'list_width': 120,
                'reference_config': {
                    'api': '/api/assets/categories/',
                    'labelField': 'name',
                    'valueField': 'id',
                }
            },
            {
                'module': 'asset',
                'field_key': 'brand',
                'field_name': '品牌',
                'field_type': 'text',
                'group': groups['basic'],
                'sort_order': 4,
                'width': 8,
                'placeholder': '请输入品牌',
                'show_in_list': True,
                'list_width': 100,
            },
            {
                'module': 'asset',
                'field_key': 'model',
                'field_name': '型号',
                'field_type': 'text',
                'group': groups['basic'],
                'sort_order': 5,
                'width': 8,
                'placeholder': '请输入型号',
                'show_in_list': True,
                'list_width': 100,
            },
            {
                'module': 'asset',
                'field_key': 'serial_number',
                'field_name': '序列号',
                'field_type': 'text',
                'group': groups['basic'],
                'sort_order': 6,
                'width': 8,
                'placeholder': '请输入序列号',
            },
            {
                'module': 'asset',
                'field_key': 'unit',
                'field_name': '计量单位',
                'field_type': 'select',
                'group': groups['basic'],
                'sort_order': 7,
                'width': 8,
                'default_value': '台',
                'options': [
                    {'label': '台', 'value': '台'},
                    {'label': '个', 'value': '个'},
                    {'label': '套', 'value': '套'},
                    {'label': '件', 'value': '件'},
                    {'label': '张', 'value': '张'},
                    {'label': '把', 'value': '把'},
                    {'label': '辆', 'value': '辆'},
                    {'label': '其他', 'value': '其他'},
                ]
            },
            {
                'module': 'asset',
                'field_key': 'quantity',
                'field_name': '数量',
                'field_type': 'number',
                'group': groups['basic'],
                'sort_order': 8,
                'width': 8,
                'default_value': 1,
                'number_config': {'min': 1, 'max': 999999}
            },
            {
                'module': 'asset',
                'field_key': 'status',
                'field_name': '资产状态',
                'field_type': 'select',
                'group': groups['basic'],
                'sort_order': 9,
                'width': 8,
                'default_value': 'idle',
                'show_in_list': True,
                'list_width': 80,
                'options': [
                    {'label': '闲置', 'value': 'idle'},
                    {'label': '在用', 'value': 'in_use'},
                    {'label': '借用', 'value': 'borrowed'},
                    {'label': '维修中', 'value': 'maintenance'},
                    {'label': '待维修', 'value': 'pending_maintenance'},
                    {'label': '待处置', 'value': 'pending_disposal'},
                    {'label': '已处置', 'value': 'disposed'},
                ]
            },
            
            # 财务信息
            {
                'module': 'asset',
                'field_key': 'original_value',
                'field_name': '原值(元)',
                'field_type': 'decimal',
                'group': groups['finance'],
                'sort_order': 1,
                'is_required': True,
                'width': 8,
                'default_value': 0,
                'show_in_list': True,
                'list_width': 100,
                'number_config': {'min': 0, 'precision': 2}
            },
            {
                'module': 'asset',
                'field_key': 'current_value',
                'field_name': '净值(元)',
                'field_type': 'decimal',
                'group': groups['finance'],
                'sort_order': 2,
                'is_readonly': True,
                'width': 8,
                'default_value': 0,
                'number_config': {'min': 0, 'precision': 2}
            },
            {
                'module': 'asset',
                'field_key': 'accumulated_depreciation',
                'field_name': '累计折旧',
                'field_type': 'decimal',
                'group': groups['finance'],
                'sort_order': 3,
                'is_readonly': True,
                'width': 8,
                'default_value': 0,
                'number_config': {'min': 0, 'precision': 2}
            },
            {
                'module': 'asset',
                'field_key': 'acquisition_method',
                'field_name': '取得方式',
                'field_type': 'select',
                'group': groups['finance'],
                'sort_order': 4,
                'width': 8,
                'default_value': 'purchase',
                'options': [
                    {'label': '采购', 'value': 'purchase'},
                    {'label': '租赁', 'value': 'lease'},
                    {'label': '赠予', 'value': 'gift'},
                    {'label': '调入', 'value': 'transfer'},
                    {'label': '自建', 'value': 'self_build'},
                    {'label': '其他', 'value': 'other'},
                ]
            },
            {
                'module': 'asset',
                'field_key': 'acquisition_date',
                'field_name': '取得日期',
                'field_type': 'date',
                'group': groups['finance'],
                'sort_order': 5,
                'width': 8,
                'placeholder': '请选择取得日期',
            },
            {
                'module': 'asset',
                'field_key': 'warranty_expiry',
                'field_name': '保修到期',
                'field_type': 'date',
                'group': groups['finance'],
                'sort_order': 6,
                'width': 8,
                'placeholder': '请选择保修到期日期',
            },
            
            # 使用信息
            {
                'module': 'asset',
                'field_key': 'using_user',
                'field_name': '使用人',
                'field_type': 'reference',
                'group': groups['usage'],
                'sort_order': 1,
                'width': 8,
                'placeholder': '请选择使用人',
                'show_in_list': True,
                'list_width': 80,
                'reference_config': {
                    'api': '/api/auth/users/',
                    'labelField': 'display_name',
                    'valueField': 'id',
                    'searchField': 'display_name',
                    'autoFillFields': {
                        'using_department': 'department'
                    }
                }
            },
            {
                'module': 'asset',
                'field_key': 'using_department',
                'field_name': '使用部门',
                'field_type': 'tree_select',
                'group': groups['usage'],
                'sort_order': 2,
                'width': 8,
                'placeholder': '请选择使用部门',
                'show_in_list': True,
                'list_width': 100,
                'reference_config': {
                    'api': '/api/organizations/departments/',
                    'labelField': 'name',
                    'valueField': 'id',
                    'treeData': True,
                    'parentField': 'parent'
                }
            },
            {
                'module': 'asset',
                'field_key': 'location',
                'field_name': '存放位置',
                'field_type': 'tree_select',
                'group': groups['usage'],
                'sort_order': 3,
                'width': 8,
                'placeholder': '请选择存放位置',
                'show_in_list': True,
                'list_width': 100,
                'reference_config': {
                    'api': '/api/organizations/locations/',
                    'labelField': 'name',
                    'valueField': 'id',
                    'treeData': True,
                    'parentField': 'parent'
                }
            },
            
            # 管理信息
            {
                'module': 'asset',
                'field_key': 'manage_department',
                'field_name': '管理部门',
                'field_type': 'tree_select',
                'group': groups['management'],
                'sort_order': 1,
                'width': 8,
                'placeholder': '请选择管理部门',
                'reference_config': {
                    'api': '/api/organizations/departments/',
                    'labelField': 'name',
                    'valueField': 'id',
                    'treeData': True,
                    'parentField': 'parent'
                }
            },
            {
                'module': 'asset',
                'field_key': 'manager',
                'field_name': '资产管理员',
                'field_type': 'reference',
                'group': groups['management'],
                'sort_order': 2,
                'width': 8,
                'placeholder': '请选择资产管理员',
                'reference_config': {
                    'api': '/api/auth/users/',
                    'labelField': 'display_name',
                    'valueField': 'id',
                    'searchField': 'display_name'
                }
            },
            
            # 标签信息
            {
                'module': 'asset',
                'field_key': 'rfid_code',
                'field_name': 'RFID编码',
                'field_type': 'text',
                'group': groups['tags'],
                'sort_order': 1,
                'width': 8,
                'placeholder': '请输入RFID编码',
            },
            {
                'module': 'asset',
                'field_key': 'barcode',
                'field_name': '条形码',
                'field_type': 'text',
                'group': groups['tags'],
                'sort_order': 2,
                'width': 8,
                'placeholder': '请输入条形码',
            },
            
            # 资产图片
            {
                'module': 'asset',
                'field_key': 'image',
                'field_name': '资产图片',
                'field_type': 'image',
                'group': groups['image'],
                'sort_order': 1,
                'width': 24,
                'help_text': '支持 jpg、png 格式，文件大小不超过 5MB',
            },
            
            # 其他信息
            {
                'module': 'asset',
                'field_key': 'remark',
                'field_name': '备注',
                'field_type': 'textarea',
                'group': groups['other'],
                'sort_order': 1,
                'width': 24,
                'placeholder': '请输入备注',
            },
        ]
        
        for field_data in fields:
            FieldDefinition.objects.update_or_create(
                module=field_data['module'],
                field_key=field_data['field_key'],
                defaults=field_data
            )
        
        self.stdout.write(f'  - 创建了 {len(fields)} 个字段配置')
    
    def init_consumable_config(self):
        """初始化耗材模块配置"""
        self.stdout.write('初始化耗材模块配置...')
        
        # 创建模块配置
        module_config, _ = ModuleFormConfig.objects.update_or_create(
            module='consumable',
            defaults={
                'module_label': '耗材',
                'api_base': '/api/consumables/list/',
                'dialog_width': '800px',
                'label_width': '100px',
            }
        )
        
        # 创建字段分组
        groups = {
            'basic': self.create_group('consumable', 'basic', '基本信息', 1),
            'stock': self.create_group('consumable', 'stock', '库存信息', 2),
            'other': self.create_group('consumable', 'other', '其他信息', 3),
        }
        
        # 创建字段定义
        fields = [
            {
                'module': 'consumable',
                'field_key': 'code',
                'field_name': '耗材编号',
                'field_type': 'code',
                'group': groups['basic'],
                'sort_order': 1,
                'is_readonly': True,
                'is_system': True,
                'width': 8,
                'placeholder': '系统自动生成',
                'show_in_list': True,
                'list_width': 150,
            },
            {
                'module': 'consumable',
                'field_key': 'name',
                'field_name': '耗材名称',
                'field_type': 'text',
                'group': groups['basic'],
                'sort_order': 2,
                'is_required': True,
                'width': 8,
                'placeholder': '请输入耗材名称',
                'show_in_list': True,
                'list_width': 150,
            },
            {
                'module': 'consumable',
                'field_key': 'category',
                'field_name': '耗材分类',
                'field_type': 'select',
                'group': groups['basic'],
                'sort_order': 3,
                'width': 8,
                'placeholder': '请选择分类',
                'show_in_list': True,
                'list_width': 100,
            },
            {
                'module': 'consumable',
                'field_key': 'specification',
                'field_name': '规格型号',
                'field_type': 'text',
                'group': groups['basic'],
                'sort_order': 4,
                'width': 8,
                'placeholder': '请输入规格型号',
                'show_in_list': True,
                'list_width': 100,
            },
            {
                'module': 'consumable',
                'field_key': 'unit',
                'field_name': '计量单位',
                'field_type': 'select',
                'group': groups['basic'],
                'sort_order': 5,
                'width': 8,
                'default_value': '个',
                'options': [
                    {'label': '个', 'value': '个'},
                    {'label': '件', 'value': '件'},
                    {'label': '箱', 'value': '箱'},
                    {'label': '盒', 'value': '盒'},
                    {'label': '包', 'value': '包'},
                    {'label': '卷', 'value': '卷'},
                ]
            },
            {
                'module': 'consumable',
                'field_key': 'unit_price',
                'field_name': '单价(元)',
                'field_type': 'decimal',
                'group': groups['basic'],
                'sort_order': 6,
                'width': 8,
                'default_value': 0,
                'show_in_list': True,
                'list_width': 80,
                'number_config': {'min': 0, 'precision': 2}
            },
            {
                'module': 'consumable',
                'field_key': 'current_stock',
                'field_name': '当前库存',
                'field_type': 'number',
                'group': groups['stock'],
                'sort_order': 1,
                'is_readonly': True,
                'width': 8,
                'default_value': 0,
                'show_in_list': True,
                'list_width': 80,
            },
            {
                'module': 'consumable',
                'field_key': 'min_stock',
                'field_name': '最低库存',
                'field_type': 'number',
                'group': groups['stock'],
                'sort_order': 2,
                'width': 8,
                'default_value': 0,
                'number_config': {'min': 0}
            },
            {
                'module': 'consumable',
                'field_key': 'max_stock',
                'field_name': '最高库存',
                'field_type': 'number',
                'group': groups['stock'],
                'sort_order': 3,
                'width': 8,
                'default_value': 0,
                'number_config': {'min': 0}
            },
            {
                'module': 'consumable',
                'field_key': 'remark',
                'field_name': '备注',
                'field_type': 'textarea',
                'group': groups['other'],
                'sort_order': 1,
                'width': 24,
                'placeholder': '请输入备注',
            },
        ]
        
        for field_data in fields:
            FieldDefinition.objects.update_or_create(
                module=field_data['module'],
                field_key=field_data['field_key'],
                defaults=field_data
            )
        
        self.stdout.write(f'  - 创建了 {len(fields)} 个字段配置')
    
    def create_group(self, module, group_key, group_name, sort_order):
        """创建或获取字段分组"""
        group, _ = FieldGroup.objects.update_or_create(
            module=module,
            group_key=group_key,
            defaults={
                'group_name': group_name,
                'sort_order': sort_order,
                'is_active': True,
            }
        )
        return group
