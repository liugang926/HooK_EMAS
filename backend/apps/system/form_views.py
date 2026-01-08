"""
动态表单配置视图
"""

from rest_framework import viewsets, status
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
