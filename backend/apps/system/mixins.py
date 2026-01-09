"""
Dynamic Fields Mixin - Universal Dynamic Form Management System

This module provides mixins for ViewSets to handle dynamic/custom fields
automatically. It integrates with the Module Registry and FieldDefinition
model to provide seamless custom field handling.

Usage:
    class AssetViewSet(DynamicFieldsMixin, viewsets.ModelViewSet):
        module_name = 'asset'
        queryset = Asset.objects.all()
        serializer_class = AssetSerializer
"""

from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction

from .form_models import FieldDefinition, ModuleFormConfig
from .module_registry import get_module_config


class DynamicFieldsSerializerMixin:
    """
    Serializer mixin to handle custom fields.
    
    Automatically adds custom_fields to serializer and handles
    validation and storage of custom field values.
    """
    
    def to_representation(self, instance):
        """Add custom fields to the output representation."""
        data = super().to_representation(instance)
        
        # Include custom fields in output
        if hasattr(instance, 'custom_fields') and instance.custom_fields:
            # Merge custom fields into main data
            for key, value in instance.custom_fields.items():
                if key not in data:
                    data[key] = value
        
        return data
    
    def to_internal_value(self, data):
        """Extract custom fields from input data."""
        # First, process standard fields
        validated_data = super().to_internal_value(data)
        
        # Then extract custom fields
        if hasattr(self, 'context') and 'module_name' in self.context:
            module_name = self.context['module_name']
            custom_field_keys = self._get_custom_field_keys(module_name)
            
            custom_fields = {}
            for key in custom_field_keys:
                if key in data and key not in validated_data:
                    custom_fields[key] = data[key]
            
            if custom_fields:
                # Get existing custom_fields or initialize empty dict
                existing = validated_data.get('custom_fields', {}) or {}
                existing.update(custom_fields)
                validated_data['custom_fields'] = existing
        
        return validated_data
    
    def _get_custom_field_keys(self, module_name):
        """Get list of custom field keys for the module."""
        try:
            fields = FieldDefinition.objects.filter(
                module=module_name,
                is_active=True,
                is_system=False
            ).values_list('field_key', flat=True)
            return list(fields)
        except Exception:
            return []


class DynamicFieldsMixin:
    """
    ViewSet mixin to handle dynamic/custom fields for any model.
    
    Features:
    - Automatic custom field extraction and storage
    - Form configuration endpoint
    - Field definition retrieval
    - Code generation support
    
    Usage:
        class AssetViewSet(DynamicFieldsMixin, viewsets.ModelViewSet):
            module_name = 'asset'
            queryset = Asset.objects.all()
            serializer_class = AssetSerializer
    """
    
    module_name = None  # Override in subclass
    
    def get_serializer_context(self):
        """Add module_name to serializer context."""
        context = super().get_serializer_context()
        context['module_name'] = self.module_name
        return context
    
    def perform_create(self, serializer):
        """Extract and save custom field values on create."""
        # Get custom fields from request data
        custom_fields = self._extract_custom_fields(self.request.data)
        
        # Save with custom fields
        instance = serializer.save()
        
        if custom_fields and hasattr(instance, 'set_custom_fields'):
            instance.set_custom_fields(custom_fields)
            instance.save(update_fields=['custom_fields'])
    
    def perform_update(self, serializer):
        """Extract and update custom field values on update."""
        # Get custom fields from request data
        custom_fields = self._extract_custom_fields(self.request.data)
        
        # Update with custom fields
        instance = serializer.save()
        
        if custom_fields and hasattr(instance, 'set_custom_fields'):
            instance.set_custom_fields(custom_fields)
            instance.save(update_fields=['custom_fields'])
    
    def _extract_custom_fields(self, data):
        """
        Extract custom field values from request data.
        
        Args:
            data: Request data dictionary
            
        Returns:
            dict: Custom field values
        """
        if not self.module_name:
            return {}
        
        # Get field definitions for this module
        try:
            custom_field_defs = FieldDefinition.objects.filter(
                module=self.module_name,
                is_active=True,
                is_system=False
            )
            
            custom_fields = {}
            for field_def in custom_field_defs:
                if field_def.field_key in data:
                    custom_fields[field_def.field_key] = data[field_def.field_key]
            
            return custom_fields
        except Exception:
            return {}
    
    @action(detail=False, methods=['get'])
    def form_config(self, request):
        """
        Get form configuration for this module.
        
        Query Parameters:
            mode: 'create' or 'edit' (default: 'create')
            
        Returns:
            Form configuration including fields, groups, and permissions
        """
        mode = request.query_params.get('mode', 'create')
        
        try:
            # Try to get module form config from database
            config = ModuleFormConfig.objects.get(
                module=self.module_name,
                is_active=True
            )
            return Response(config.get_form_config(mode))
        except ModuleFormConfig.DoesNotExist:
            # Fall back to module registry
            module_config = get_module_config(self.module_name)
            if module_config:
                return Response(self._build_form_config_from_registry(module_config, mode))
            
            return Response({'error': 'Module configuration not found'}, status=404)
    
    @action(detail=False, methods=['get'])
    def list_fields(self, request):
        """
        Get list display fields for this module.
        
        Returns:
            List of fields configured for list display
        """
        fields = FieldDefinition.objects.filter(
            module=self.module_name,
            is_active=True,
            show_in_list=True
        ).order_by('sort_order')
        
        return Response([
            {
                'key': f.field_key,
                'label': f.field_name,
                'type': f.field_type,
                'width': f.list_width,
                'sortable': f.list_sortable,
                'searchable': f.list_searchable,
            }
            for f in fields
        ])
    
    @action(detail=False, methods=['get'])
    def field_definitions(self, request):
        """
        Get all field definitions for this module.
        
        Returns:
            List of all field configurations
        """
        fields = FieldDefinition.objects.filter(
            module=self.module_name,
            is_active=True
        ).order_by('sort_order')
        
        return Response([
            f.get_field_config(request.query_params.get('mode', 'create'))
            for f in fields
        ])
    
    def _build_form_config_from_registry(self, module_config, mode='create'):
        """
        Build form configuration from module registry.
        
        Args:
            module_config: Module configuration from registry
            mode: 'create' or 'edit'
            
        Returns:
            dict: Form configuration
        """
        system_fields = module_config.get('system_fields', [])
        
        # Build field configs
        fields = []
        for field in system_fields:
            field_config = {
                'key': field['field_key'],
                'label': field['field_name'],
                'type': field['field_type'],
                'required': field.get('is_required', False),
                'readonly': self._is_field_readonly(field, mode),
                'hidden': self._is_field_hidden(field, mode),
                'placeholder': field.get('placeholder', ''),
                'helpText': field.get('help_text', ''),
                'width': field.get('width', 8),
                'defaultValue': field.get('default_value'),
            }
            
            # Add type-specific configs
            if field['field_type'] in ['select', 'multi_select', 'radio']:
                field_config['options'] = field.get('options', [])
            
            if field['field_type'] in ['reference', 'tree_select', 'cascader']:
                field_config['referenceConfig'] = field.get('reference_config', {})
            
            if field['field_type'] in ['number', 'decimal']:
                field_config['numberConfig'] = field.get('number_config', {})
            
            fields.append(field_config)
        
        return {
            'module': self.module_name,
            'moduleLabel': module_config['label'],
            'apiBase': module_config['api_base'],
            'dialogWidth': '900px',
            'labelWidth': '100px',
            'permissions': {
                'create': True,
                'edit': True,
                'delete': True,
                'import': True,
                'export': True,
            },
            'groups': [],
            'ungroupedFields': fields,
        }
    
    def _is_field_readonly(self, field, mode):
        """Check if field is readonly in the given mode."""
        if field.get('is_readonly', False):
            return True
        if mode == 'create' and field.get('is_readonly_on_create', False):
            return True
        if mode == 'edit' and field.get('is_readonly_on_edit', False):
            return True
        return False
    
    def _is_field_hidden(self, field, mode):
        """Check if field is hidden in the given mode."""
        if field.get('is_hidden', False):
            return True
        if mode == 'create' and field.get('is_hidden_on_create', False):
            return True
        if mode == 'edit' and field.get('is_hidden_on_edit', False):
            return True
        return False


class CodeGenerationMixin:
    """
    Mixin to add code generation support to ViewSets.
    
    Usage:
        class AssetViewSet(CodeGenerationMixin, DynamicFieldsMixin, viewsets.ModelViewSet):
            module_name = 'asset'
    """
    
    @action(detail=False, methods=['post'])
    def generate_code(self, request):
        """
        Generate a new code based on module's code rule.
        
        Request body:
            company: Company ID (optional)
            
        Returns:
            code: The generated code
        """
        from .models import CodeRule
        from django.utils import timezone
        
        if not self.module_name:
            return Response({'error': 'Module name not configured'}, status=400)
        
        module_config = get_module_config(self.module_name)
        if not module_config:
            return Response({'error': 'Module not found'}, status=404)
        
        code_rule_type = module_config.get('code_rule_type')
        if not code_rule_type:
            return Response({'error': 'Module does not support code generation'}, status=400)
        
        company_id = request.data.get('company')
        
        try:
            # Try to get code rule from database
            rule = CodeRule.objects.get(
                company_id=company_id,
                code=code_rule_type
            )
            
            # Generate code based on rule
            now = timezone.now()
            
            # Check if we need to reset serial number
            should_reset = False
            if rule.reset_cycle == 'daily':
                should_reset = rule.last_reset_date != now.date()
            elif rule.reset_cycle == 'monthly':
                should_reset = (
                    not rule.last_reset_date or
                    rule.last_reset_date.month != now.month or
                    rule.last_reset_date.year != now.year
                )
            elif rule.reset_cycle == 'yearly':
                should_reset = (
                    not rule.last_reset_date or
                    rule.last_reset_date.year != now.year
                )
            
            if should_reset:
                rule.current_serial = 0
                rule.last_reset_date = now.date()
            
            # Increment serial
            rule.current_serial += 1
            rule.save()
            
            # Build code
            date_str = ''
            if rule.date_format == 'YYYY':
                date_str = now.strftime('%Y')
            elif rule.date_format == 'YYYYMM':
                date_str = now.strftime('%Y%m')
            elif rule.date_format == 'YYYYMMDD':
                date_str = now.strftime('%Y%m%d')
            
            serial = str(rule.current_serial).zfill(rule.serial_length)
            sep = rule.separator or ''
            
            code = f"{rule.prefix or ''}{sep}{date_str}{sep}{serial}"
            
            return Response({'code': code})
            
        except CodeRule.DoesNotExist:
            # Generate code using default prefix
            prefix = module_config.get('code_rule_prefix', 'CODE')
            now = timezone.now()
            date_str = now.strftime('%Y%m%d')
            serial = str(int(now.timestamp() * 1000) % 10000).zfill(4)
            
            return Response({'code': f"{prefix}{date_str}{serial}"})


class BulkOperationsMixin:
    """
    Mixin to add bulk operations support to ViewSets.
    
    Provides bulk create, update, and delete operations.
    """
    
    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """
        Create multiple records at once.
        
        Request body:
            items: List of record data
            
        Returns:
            List of created records
        """
        items = request.data.get('items', [])
        if not items:
            return Response({'error': 'No items provided'}, status=400)
        
        serializer = self.get_serializer(data=items, many=True)
        serializer.is_valid(raise_exception=True)
        
        with transaction.atomic():
            instances = serializer.save()
        
        return Response(
            self.get_serializer(instances, many=True).data,
            status=201
        )
    
    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        """
        Update multiple records at once.
        
        Request body:
            items: List of {id: ..., data: {...}}
            
        Returns:
            List of updated records
        """
        items = request.data.get('items', [])
        if not items:
            return Response({'error': 'No items provided'}, status=400)
        
        updated = []
        with transaction.atomic():
            for item in items:
                item_id = item.get('id')
                data = item.get('data', {})
                
                if not item_id:
                    continue
                
                try:
                    instance = self.get_queryset().get(pk=item_id)
                    serializer = self.get_serializer(instance, data=data, partial=True)
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                    updated.append(serializer.data)
                except self.get_queryset().model.DoesNotExist:
                    pass
        
        return Response(updated)
    
    @action(detail=False, methods=['post'])
    def bulk_delete(self, request):
        """
        Delete multiple records at once (soft delete).
        
        Request body:
            ids: List of record IDs
            
        Returns:
            Number of deleted records
        """
        ids = request.data.get('ids', [])
        if not ids:
            return Response({'error': 'No IDs provided'}, status=400)
        
        queryset = self.get_queryset().filter(pk__in=ids)
        count = queryset.count()
        
        # Use soft delete if available
        with transaction.atomic():
            for instance in queryset:
                if hasattr(instance, 'soft_delete'):
                    instance.soft_delete()
                else:
                    instance.delete()
        
        return Response({'deleted': count})
