"""
Management command to initialize module field definitions.

This command creates or updates the system fields for all registered modules
in the MODULE_REGISTRY. It ensures that all default system fields are
properly configured in the database.

Usage:
    python manage.py init_module_fields                    # Initialize all modules
    python manage.py init_module_fields --module=asset    # Initialize specific module
    python manage.py init_module_fields --module=asset --force  # Force overwrite
    python manage.py init_module_fields --list             # List available modules
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.system.form_models import FieldDefinition, FieldGroup, ModuleFormConfig
from apps.system.module_registry import (
    MODULE_REGISTRY, 
    get_module_config, 
    get_all_modules
)


class Command(BaseCommand):
    help = 'Initialize module field definitions from MODULE_REGISTRY'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--module',
            type=str,
            default='all',
            help='Module name to initialize (default: all)'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force overwrite existing field definitions'
        )
        parser.add_argument(
            '--list',
            action='store_true',
            dest='list_modules',
            help='List available modules'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes'
        )
    
    def handle(self, *args, **options):
        if options['list_modules']:
            self.list_modules()
            return
        
        module_name = options['module']
        force = options['force']
        dry_run = options['dry_run']
        
        if module_name == 'all':
            modules = get_all_modules()
        else:
            module_config = get_module_config(module_name)
            if not module_config:
                raise CommandError(f"Module '{module_name}' not found in registry")
            modules = {module_name: module_config}
        
        total_created = 0
        total_updated = 0
        total_skipped = 0
        
        for name, config in modules.items():
            self.stdout.write(f"\nProcessing module: {name} ({config['label']})")
            
            created, updated, skipped = self.process_module(
                name, config, force, dry_run
            )
            
            total_created += created
            total_updated += updated
            total_skipped += skipped
        
        self.stdout.write(self.style.SUCCESS(
            f"\nSummary: {total_created} created, {total_updated} updated, {total_skipped} skipped"
        ))
        
        if dry_run:
            self.stdout.write(self.style.WARNING(
                "Dry run - no changes were made"
            ))
    
    def list_modules(self):
        """List all available modules."""
        self.stdout.write("Available modules:")
        for name, config in MODULE_REGISTRY.items():
            field_count = len(config.get('system_fields', []))
            self.stdout.write(
                f"  - {name}: {config['label']} ({field_count} fields)"
            )
    
    @transaction.atomic
    def process_module(self, module_name, config, force=False, dry_run=False):
        """
        Process a single module's field definitions.
        
        Args:
            module_name: Module identifier
            config: Module configuration from registry
            force: Whether to force overwrite existing fields
            dry_run: Whether to perform a dry run
            
        Returns:
            tuple: (created_count, updated_count, skipped_count)
        """
        created = 0
        updated = 0
        skipped = 0
        
        system_fields = config.get('system_fields', [])
        
        for field_def in system_fields:
            field_key = field_def['field_key']
            
            # Check if field already exists
            existing = FieldDefinition.objects.filter(
                module=module_name,
                field_key=field_key
            ).first()
            
            if existing:
                if force:
                    if not dry_run:
                        self._update_field(existing, field_def)
                    self.stdout.write(f"  Updated: {field_key}")
                    updated += 1
                else:
                    self.stdout.write(f"  Skipped: {field_key} (already exists)")
                    skipped += 1
            else:
                if not dry_run:
                    self._create_field(module_name, field_def)
                self.stdout.write(f"  Created: {field_key}")
                created += 1
        
        # Create or update ModuleFormConfig if not dry run
        if not dry_run:
            self._ensure_module_config(module_name, config)
        
        return created, updated, skipped
    
    def _create_field(self, module_name, field_def):
        """Create a new field definition."""
        FieldDefinition.objects.create(
            module=module_name,
            field_key=field_def['field_key'],
            field_name=field_def['field_name'],
            field_type=field_def['field_type'],
            is_required=field_def.get('is_required', False),
            is_system=field_def.get('is_system', True),
            is_readonly=field_def.get('is_readonly', False),
            is_readonly_on_create=field_def.get('is_readonly_on_create', False),
            is_readonly_on_edit=field_def.get('is_readonly_on_edit', False),
            is_hidden=field_def.get('is_hidden', False),
            is_hidden_on_create=field_def.get('is_hidden_on_create', False),
            is_hidden_on_edit=field_def.get('is_hidden_on_edit', False),
            sort_order=field_def.get('sort_order', 0),
            width=field_def.get('width', 8),
            placeholder=field_def.get('placeholder', ''),
            help_text=field_def.get('help_text', ''),
            options=field_def.get('options', []),
            reference_config=field_def.get('reference_config', {}),
            number_config=field_def.get('number_config', {}),
            default_value=field_def.get('default_value'),
            show_in_list=field_def.get('show_in_list', False),
            list_width=field_def.get('list_width', 150),
            list_sortable=field_def.get('list_sortable', False),
            list_searchable=field_def.get('list_searchable', False),
            is_active=True,
        )
    
    def _update_field(self, field, field_def):
        """Update an existing field definition."""
        field.field_name = field_def['field_name']
        field.field_type = field_def['field_type']
        field.is_required = field_def.get('is_required', False)
        field.is_system = field_def.get('is_system', True)
        field.is_readonly = field_def.get('is_readonly', False)
        field.is_readonly_on_create = field_def.get('is_readonly_on_create', False)
        field.is_readonly_on_edit = field_def.get('is_readonly_on_edit', False)
        field.is_hidden = field_def.get('is_hidden', False)
        field.is_hidden_on_create = field_def.get('is_hidden_on_create', False)
        field.is_hidden_on_edit = field_def.get('is_hidden_on_edit', False)
        field.sort_order = field_def.get('sort_order', 0)
        field.width = field_def.get('width', 8)
        field.placeholder = field_def.get('placeholder', '')
        field.help_text = field_def.get('help_text', '')
        field.options = field_def.get('options', [])
        field.reference_config = field_def.get('reference_config', {})
        field.number_config = field_def.get('number_config', {})
        field.default_value = field_def.get('default_value')
        field.show_in_list = field_def.get('show_in_list', False)
        field.list_width = field_def.get('list_width', 150)
        field.list_sortable = field_def.get('list_sortable', False)
        field.list_searchable = field_def.get('list_searchable', False)
        field.save()
    
    def _ensure_module_config(self, module_name, config):
        """Create or update ModuleFormConfig for the module."""
        ModuleFormConfig.objects.update_or_create(
            module=module_name,
            defaults={
                'module_label': config['label'],
                'api_base': config['api_base'],
                'dialog_width': '900px',
                'label_width': '100px',
                'enable_create': True,
                'enable_edit': True,
                'enable_delete': True,
                'enable_import': config.get('enable_import', True),
                'enable_export': config.get('enable_export', True),
                'extra_config': {
                    'tree_mode': config.get('tree_mode', False),
                    'workflow': config.get('workflow', False),
                    'code_rule_type': config.get('code_rule_type'),
                    'code_rule_prefix': config.get('code_rule_prefix'),
                },
                'is_active': True,
            }
        )
        self.stdout.write(f"  Module config updated for: {module_name}")
