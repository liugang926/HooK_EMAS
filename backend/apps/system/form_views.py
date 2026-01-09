"""
Dynamic Form Configuration Views

This module provides API endpoints for:
- Field groups management
- Field definitions management
- Module form configurations
- Module registry access (centralized config)

Following .cursorrules:
- Service Layer pattern for business logic
- Consistent API responses
"""

from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .form_models import FieldGroup, FieldDefinition, ModuleFormConfig
from .form_serializers import (
    FieldGroupSerializer,
    FieldDefinitionSerializer,
    FieldDefinitionCreateSerializer,
    ModuleFormConfigSerializer,
    BulkFieldUpdateSerializer
)
from .module_registry import (
    MODULE_REGISTRY,
    get_module_config,
    get_all_modules,
    get_module_system_fields,
    get_modules_with_feature,
    get_module_code_rule_config
)


class FieldGroupViewSet(viewsets.ModelViewSet):
    """字段分组视图集"""
    
    queryset = FieldGroup.objects.all()
    serializer_class = FieldGroupSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['module', 'is_active']
    search_fields = ['group_name', 'group_key']
    ordering_fields = ['sort_order', 'created_at']
    ordering = ['module', 'sort_order']
    
    @action(detail=False, methods=['get'])
    def by_module(self, request):
        """按模块获取分组"""
        module = request.query_params.get('module')
        if not module:
            return Response(
                {'error': '请提供 module 参数'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        groups = self.queryset.filter(module=module, is_active=True)
        serializer = self.get_serializer(groups, many=True)
        return Response(serializer.data)


class FieldDefinitionViewSet(viewsets.ModelViewSet):
    """字段定义视图集"""
    
    queryset = FieldDefinition.objects.select_related('group').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['module', 'field_type', 'group', 'is_active', 'is_system', 'show_in_list']
    search_fields = ['field_key', 'field_name']
    ordering_fields = ['sort_order', 'created_at']
    ordering = ['group__sort_order', 'sort_order']
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return FieldDefinitionCreateSerializer
        return FieldDefinitionSerializer
    
    @action(detail=False, methods=['get'])
    def by_module(self, request):
        """按模块获取字段定义"""
        module = request.query_params.get('module')
        mode = request.query_params.get('mode', 'create')  # create 或 edit
        
        if not module:
            return Response(
                {'error': '请提供 module 参数'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        fields = self.queryset.filter(module=module, is_active=True)
        
        # 构建字段配置
        field_configs = []
        for field in fields:
            config = field.get_field_config(mode)
            if not config['hidden']:
                field_configs.append(config)
        
        return Response(field_configs)
    
    @action(detail=False, methods=['get'])
    def list_fields(self, request):
        """获取列表显示字段"""
        module = request.query_params.get('module')
        
        if not module:
            return Response(
                {'error': '请提供 module 参数'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        fields = self.queryset.filter(
            module=module, 
            is_active=True, 
            show_in_list=True
        ).order_by('sort_order')
        
        list_columns = []
        for field in fields:
            list_columns.append({
                'prop': field.field_key,
                'label': field.field_name,
                'width': field.list_width,
                'sortable': field.list_sortable,
                'searchable': field.list_searchable,
                'type': field.field_type,
            })
        
        return Response(list_columns)
    
    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        """批量更新字段配置"""
        serializer = BulkFieldUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        module = request.data.get('module')
        fields_data = serializer.validated_data['fields']
        
        updated = []
        errors = []
        
        for field_data in fields_data:
            field_key = field_data.pop('field_key')
            try:
                field = FieldDefinition.objects.get(module=module, field_key=field_key)
                for key, value in field_data.items():
                    setattr(field, key, value)
                field.save()
                updated.append(field_key)
            except FieldDefinition.DoesNotExist:
                errors.append(f"字段 {field_key} 不存在")
            except Exception as e:
                errors.append(f"更新 {field_key} 失败: {str(e)}")
        
        return Response({
            'updated': updated,
            'errors': errors
        })
    
    @action(detail=False, methods=['post'])
    def reorder(self, request):
        """重新排序字段"""
        module = request.data.get('module')
        order_data = request.data.get('order', [])  # [{'field_key': 'name', 'sort_order': 1}, ...]
        
        if not module or not order_data:
            return Response(
                {'error': '请提供 module 和 order 参数'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        for item in order_data:
            FieldDefinition.objects.filter(
                module=module,
                field_key=item['field_key']
            ).update(sort_order=item['sort_order'])
        
        return Response({'message': '排序更新成功'})


class ModuleFormConfigViewSet(viewsets.ModelViewSet):
    """模块表单配置视图集"""
    
    queryset = ModuleFormConfig.objects.all()
    serializer_class = ModuleFormConfigSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['module', 'is_active']
    search_fields = ['module', 'module_label']
    
    @action(detail=False, methods=['get'])
    def form_config(self, request):
        """获取完整表单配置（用于前端渲染）"""
        module = request.query_params.get('module')
        mode = request.query_params.get('mode', 'create')
        
        if not module:
            return Response(
                {'error': '请提供 module 参数'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            config = ModuleFormConfig.objects.get(module=module, is_active=True)
            form_config = config.get_form_config(mode)
            return Response(form_config)
        except ModuleFormConfig.DoesNotExist:
            # 如果没有配置，返回默认配置
            return self._get_default_config(module, mode)
    
    def _get_default_config(self, module, mode):
        """获取默认表单配置"""
        groups = FieldGroup.objects.filter(
            module=module,
            is_active=True
        ).order_by('sort_order')
        
        fields = FieldDefinition.objects.filter(
            module=module,
            is_active=True
        ).select_related('group').order_by('group__sort_order', 'sort_order')
        
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
        
        return Response({
            'module': module,
            'moduleLabel': module,
            'apiBase': f'/api/{module}/',
            'dialogWidth': '900px',
            'labelWidth': '100px',
            'permissions': {
                'create': True,
                'edit': True,
                'delete': True,
                'import': True,
                'export': True,
            },
            'groups': list(grouped_fields.values()),
            'ungroupedFields': ungrouped_fields,
            'extra': {},
        })
    
    @action(detail=False, methods=['get'])
    def modules(self, request):
        """获取所有已配置的模块列表"""
        modules = ModuleFormConfig.objects.filter(is_active=True).values(
            'module', 'module_label', 'api_base'
        )
        return Response(list(modules))


# =============================================================================
# Module Registry API Views
# =============================================================================

class ModuleRegistryView(APIView):
    """
    Module Registry API - Serves centralized module configurations
    
    This provides direct access to MODULE_REGISTRY without database queries,
    useful for initial configuration and frontend schema generation.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Get all modules or a specific module configuration
        
        Query params:
            module: (optional) specific module name to retrieve
            include_fields: (optional) whether to include system fields (default: true)
        
        Returns:
            - Single module config if 'module' param provided
            - List of all modules otherwise
        """
        module_name = request.query_params.get('module')
        include_fields = request.query_params.get('include_fields', 'true').lower() == 'true'
        
        if module_name:
            config = get_module_config(module_name)
            if not config:
                return Response(
                    {'error': f'Module "{module_name}" not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            result = self._format_module_config(module_name, config, include_fields)
            return Response(result)
        
        # Return all modules
        modules = []
        for name, config in MODULE_REGISTRY.items():
            modules.append(self._format_module_config(name, config, include_fields))
        
        return Response(modules)
    
    def _format_module_config(self, name, config, include_fields=True):
        """Format module config for API response"""
        result = {
            'name': name,
            'label': config.get('label'),
            'label_en': config.get('label_en'),
            'api_base': config.get('api_base'),
            'icon': config.get('icon'),
            'code_rule': config.get('code_rule'),
            'features': config.get('features'),
        }
        
        if include_fields:
            # Convert system fields to serializable format
            system_fields = config.get('system_fields', [])
            result['system_fields'] = [
                self._format_field(field) for field in system_fields
            ]
        
        return result
    
    def _format_field(self, field):
        """Format field config, converting enums to strings"""
        formatted = {}
        for key, value in field.items():
            if hasattr(value, 'value'):
                # Convert enum to string
                formatted[key] = value.value
            else:
                formatted[key] = value
        return formatted


class ModuleRegistryFieldsView(APIView):
    """
    Module Fields API - Get system fields for a module
    
    Provides field configurations for frontend form rendering.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, module_name):
        """
        Get system fields for a specific module
        
        Path params:
            module_name: The module identifier
            
        Query params:
            mode: 'create' or 'edit' - affects readonly/hidden fields
        
        Returns:
            List of field configurations
        """
        fields = get_module_system_fields(module_name)
        
        if not fields:
            return Response(
                {'error': f'Module "{module_name}" not found or has no fields'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        mode = request.query_params.get('mode', 'create')
        
        # Format fields for response
        formatted_fields = []
        for field in fields:
            field_config = self._format_field_for_form(field, mode)
            formatted_fields.append(field_config)
        
        return Response(formatted_fields)
    
    def _format_field_for_form(self, field, mode='create'):
        """Format field config for form rendering"""
        field_type = field.get('field_type')
        if hasattr(field_type, 'value'):
            field_type = field_type.value
        
        # Determine readonly based on mode
        is_readonly = field.get('is_readonly', False)
        if mode == 'edit' and field.get('is_readonly_on_edit', False):
            is_readonly = True
        
        config = {
            'key': field.get('field_key'),
            'label': field.get('field_name'),
            'type': field_type,
            'required': field.get('is_required', False),
            'readonly': is_readonly,
            'width': field.get('width', 8),
            'sortOrder': field.get('sort_order', 0),
            'showInList': field.get('show_in_list', False),
            'listSortable': field.get('list_sortable', False),
            'listSearchable': field.get('list_searchable', False),
        }
        
        # Add type-specific configurations
        if 'options' in field:
            config['options'] = field['options']
        
        if 'default_value' in field:
            config['defaultValue'] = field['default_value']
        
        if 'reference_config' in field:
            config['referenceConfig'] = field['reference_config']
        
        if 'number_config' in field:
            config['numberConfig'] = field['number_config']
        
        return config


class ModuleCodeRuleView(APIView):
    """
    Module Code Rule API - Get code generation rules for a module
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, module_name):
        """Get code rule configuration for a module"""
        code_rule = get_module_code_rule_config(module_name)
        
        if not code_rule:
            return Response(
                {'error': f'Module "{module_name}" has no code rule configured'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response(code_rule)


class ModuleFeatureView(APIView):
    """
    Module Features API - Query modules by feature
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Get modules that have a specific feature enabled
        
        Query params:
            feature: Feature name (e.g., 'custom_fields', 'workflow', 'batch_operations')
        
        Returns:
            List of module names with the feature enabled
        """
        feature = request.query_params.get('feature')
        
        if not feature:
            return Response(
                {'error': 'Please provide "feature" parameter'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        modules = get_modules_with_feature(feature)
        
        return Response({
            'feature': feature,
            'modules': modules
        })
