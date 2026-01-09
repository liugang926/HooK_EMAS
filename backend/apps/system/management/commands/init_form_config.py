"""
Initialize Dynamic Form Configuration from Module Registry

This management command synchronizes the centralized MODULE_REGISTRY
configuration to the database tables (ModuleFormConfig, FieldGroup, FieldDefinition).

Usage:
    python manage.py init_form_config              # Initialize all modules
    python manage.py init_form_config --module asset  # Initialize specific module
    python manage.py init_form_config --reset      # Reset all configurations
    python manage.py init_form_config --list       # List available modules

Following .cursorrules:
- Uses centralized MODULE_REGISTRY for all configurations
- Service Layer pattern for business logic
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from apps.system.form_models import FieldGroup, FieldDefinition, ModuleFormConfig
from apps.system.module_registry import MODULE_REGISTRY, get_module_config, get_all_modules


class Command(BaseCommand):
    help = 'Initialize dynamic form field configurations from MODULE_REGISTRY'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--module',
            type=str,
            help='Specify module to initialize (e.g., asset, supply, user)'
        )
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Reset configurations (delete existing before recreating)'
        )
        parser.add_argument(
            '--list',
            action='store_true',
            help='List all available modules in registry'
        )
    
    def handle(self, *args, **options):
        # List modules mode
        if options.get('list'):
            self._list_modules()
            return
        
        module = options.get('module')
        reset = options.get('reset', False)
        
        # Reset mode
        if reset:
            self._reset_configs(module)
        
        # Initialize configurations
        if module:
            if module not in MODULE_REGISTRY:
                self.stdout.write(
                    self.style.ERROR(f'Module "{module}" not found in registry.')
                )
                self.stdout.write('Available modules: ' + ', '.join(MODULE_REGISTRY.keys()))
                return
            self._init_module(module)
        else:
            # Initialize all modules
            for module_name in MODULE_REGISTRY.keys():
                self._init_module(module_name)
        
        self.stdout.write(self.style.SUCCESS('\nForm configuration initialization completed!'))
    
    def _list_modules(self):
        """List all available modules in the registry"""
        self.stdout.write(self.style.MIGRATE_HEADING('\nAvailable Modules in Registry:'))
        self.stdout.write('-' * 60)
        
        for name, config in MODULE_REGISTRY.items():
            label = config.get('label', name)
            label_en = config.get('label_en', '')
            fields_count = len(config.get('system_fields', []))
            features = config.get('features', {})
            
            self.stdout.write(f"\n  {self.style.SUCCESS(name)}")
            self.stdout.write(f"    Label: {label} ({label_en})")
            self.stdout.write(f"    API: {config.get('api_base', 'N/A')}")
            self.stdout.write(f"    Fields: {fields_count}")
            self.stdout.write(f"    Features: {', '.join(k for k, v in features.items() if v)}")
        
        self.stdout.write('\n')
    
    def _reset_configs(self, module=None):
        """Reset configurations for specified module or all modules"""
        self.stdout.write(self.style.WARNING('\nResetting configurations...'))
        
        with transaction.atomic():
            if module:
                FieldDefinition.objects.filter(module=module).delete()
                FieldGroup.objects.filter(module=module).delete()
                ModuleFormConfig.objects.filter(module=module).delete()
                self.stdout.write(f'  - Reset module: {module}')
            else:
                FieldDefinition.objects.all().delete()
                FieldGroup.objects.all().delete()
                ModuleFormConfig.objects.all().delete()
                self.stdout.write('  - Reset all modules')
    
    @transaction.atomic
    def _init_module(self, module_name):
        """Initialize a single module from registry"""
        config = MODULE_REGISTRY.get(module_name)
        if not config:
            return
        
        self.stdout.write(f"\nInitializing module: {self.style.SUCCESS(module_name)}")
        
        # Create ModuleFormConfig
        module_config, created = ModuleFormConfig.objects.update_or_create(
            module=module_name,
            defaults={
                'module_label': config.get('label', module_name),
                'api_base': config.get('api_base', f'/api/{module_name}/'),
                'dialog_width': '900px',
                'label_width': '100px',
                'enable_create': config.get('features', {}).get('create', True),
                'enable_edit': config.get('features', {}).get('edit', True),
                'enable_delete': config.get('features', {}).get('delete', True),
                'enable_import': config.get('features', {}).get('import', True),
                'enable_export': config.get('features', {}).get('export', True),
                'extra_config': {
                    'icon': config.get('icon'),
                    'label_en': config.get('label_en'),
                    'code_rule': config.get('code_rule'),
                    'features': config.get('features'),
                },
                'is_active': True,
            }
        )
        status = 'created' if created else 'updated'
        self.stdout.write(f"  - Module config {status}")
        
        # Create field groups based on system fields
        groups = self._create_groups_from_fields(module_name, config)
        
        # Create field definitions
        system_fields = config.get('system_fields', [])
        fields_created = 0
        fields_updated = 0
        
        for field_config in system_fields:
            field_data = self._convert_field_config(module_name, field_config, groups)
            
            field, created = FieldDefinition.objects.update_or_create(
                module=module_name,
                field_key=field_config['field_key'],
                defaults=field_data
            )
            
            if created:
                fields_created += 1
            else:
                fields_updated += 1
        
        self.stdout.write(f"  - Fields: {fields_created} created, {fields_updated} updated")
    
    def _create_groups_from_fields(self, module_name, config):
        """Create field groups based on field types and categories"""
        groups = {}
        
        # Define standard groups for all modules
        standard_groups = [
            ('basic', '基本信息', 1),
            ('finance', '财务信息', 2),
            ('usage', '使用信息', 3),
            ('management', '管理信息', 4),
            ('other', '其他信息', 5),
        ]
        
        # Create groups
        for group_key, group_name, sort_order in standard_groups:
            group, _ = FieldGroup.objects.update_or_create(
                module=module_name,
                group_key=group_key,
                defaults={
                    'group_name': group_name,
                    'sort_order': sort_order,
                    'is_active': True,
                }
            )
            groups[group_key] = group
        
        return groups
    
    def _convert_field_config(self, module_name, field_config, groups):
        """Convert MODULE_REGISTRY field config to FieldDefinition format"""
        field_type = field_config.get('field_type')
        if hasattr(field_type, 'value'):
            field_type = field_type.value
        
        # Determine group based on field type/key
        group = self._determine_field_group(field_config, groups)
        
        # Build field definition data
        data = {
            'field_name': field_config.get('field_name', ''),
            'field_type': field_type,
            'group': group,
            'sort_order': field_config.get('sort_order', 0),
            'is_required': field_config.get('is_required', False),
            'is_readonly': field_config.get('is_readonly', False),
            'is_readonly_on_edit': field_config.get('is_readonly_on_edit', False),
            'is_system': True,  # All registry fields are system fields
            'width': field_config.get('width', 8),
            'show_in_list': field_config.get('show_in_list', False),
            'list_width': field_config.get('list_width', 150),
            'list_sortable': field_config.get('list_sortable', False),
            'list_searchable': field_config.get('list_searchable', False),
            'is_active': True,
        }
        
        # Handle options for select fields
        if 'options' in field_config:
            data['options'] = field_config['options']
        
        # Handle default value
        if 'default_value' in field_config:
            data['default_value'] = field_config['default_value']
        
        # Handle reference config
        if 'reference_config' in field_config:
            data['reference_config'] = field_config['reference_config']
        
        # Handle number config
        if 'number_config' in field_config:
            data['number_config'] = field_config['number_config']
        
        # Handle code config (for auto-generated codes)
        if field_type == 'code':
            code_rule = field_config.get('code_rule', {})
            data['code_config'] = {
                'prefix': code_rule.get('default_prefix', ''),
                'dateFormat': code_rule.get('default_date_format', 'YYYYMMDD'),
                'length': code_rule.get('default_serial_length', 4),
            }
        
        return data
    
    def _determine_field_group(self, field_config, groups):
        """Determine which group a field belongs to based on its key and type"""
        field_key = field_config.get('field_key', '')
        field_type = field_config.get('field_type')
        if hasattr(field_type, 'value'):
            field_type = field_type.value
        
        # Financial fields
        if any(k in field_key for k in ['value', 'price', 'cost', 'amount', 'depreciation']):
            return groups.get('finance')
        
        # Usage fields
        if any(k in field_key for k in ['user', 'department', 'location', 'position']):
            return groups.get('usage')
        
        # Management fields
        if any(k in field_key for k in ['manager', 'manage', 'admin']):
            return groups.get('management')
        
        # Description/remark fields
        if any(k in field_key for k in ['remark', 'description', 'note']):
            return groups.get('other')
        
        # Default to basic
        return groups.get('basic')
