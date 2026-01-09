from rest_framework import viewsets, serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.utils import timezone

from .models import SystemConfig, OperationLog, CodeRule


class CodeRuleSerializer(serializers.ModelSerializer):
    """编码规则序列化器"""
    example = serializers.SerializerMethodField()
    
    class Meta:
        model = CodeRule
        fields = [
            'id', 'company', 'name', 'code', 'prefix', 'date_format',
            'serial_length', 'separator', 'current_serial', 'reset_cycle',
            'last_reset_date', 'description', 'is_active', 'example',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['current_serial', 'last_reset_date', 'created_at', 'updated_at']
    
    def get_example(self, obj):
        """Generate example code"""
        now = timezone.now()
        date_str = ''
        if obj.date_format == 'YYYY':
            date_str = now.strftime('%Y')
        elif obj.date_format == 'YYYYMM':
            date_str = now.strftime('%Y%m')
        elif obj.date_format == 'YYYYMMDD':
            date_str = now.strftime('%Y%m%d')
        
        serial = str(1).zfill(obj.serial_length)
        sep = obj.separator or ''
        
        return f"{obj.prefix or ''}{sep}{date_str}{sep}{serial}"


class CodeRuleViewSet(viewsets.ModelViewSet):
    """编码规则视图集"""
    queryset = CodeRule.objects.all()
    serializer_class = CodeRuleSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['company', 'code', 'is_active']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        company_id = self.request.query_params.get('company')
        if company_id:
            queryset = queryset.filter(company_id=company_id)
        return queryset
    
    @action(detail=False, methods=['get', 'post'])
    def asset_code(self, request):
        """Get or update asset code rule for a company"""
        company_id = request.query_params.get('company') or request.data.get('company')
        
        if request.method == 'GET':
            try:
                rule = CodeRule.objects.get(company_id=company_id, code='asset_code')
                return Response(self.get_serializer(rule).data)
            except CodeRule.DoesNotExist:
                # Return default rule
                return Response({
                    'prefix': 'ZC',
                    'date_format': 'YYYYMMDD',
                    'serial_length': 4,
                    'separator': '',
                    'reset_cycle': 'daily',
                    'example': f"ZC{timezone.now().strftime('%Y%m%d')}0001"
                })
        
        elif request.method == 'POST':
            from apps.organizations.models import Company
            
            try:
                company = Company.objects.get(id=company_id)
            except Company.DoesNotExist:
                return Response({'error': '公司不存在'}, status=400)
            
            rule_data = {
                'name': '资产编号规则',
                'prefix': request.data.get('prefix', 'ZC'),
                'date_format': request.data.get('date_format', 'YYYYMMDD'),
                'serial_length': request.data.get('serial_length', 4),
                'separator': request.data.get('separator', ''),
                'reset_cycle': request.data.get('reset_cycle', 'daily'),
                'is_active': True
            }
            
            rule, created = CodeRule.objects.update_or_create(
                company=company,
                code='asset_code',
                defaults=rule_data
            )
            
            return Response({
                'message': '编号规则保存成功',
                'data': self.get_serializer(rule).data
            })
    
    @action(detail=False, methods=['post'])
    def generate_code(self, request):
        """
        Generate a new code based on the company's code rule for any module.
        
        Request body:
            company: Company ID (optional for some modules)
            code_type: Code rule type (e.g., 'asset_code', 'supply_code', 'purchase_order_code')
            
        Returns:
            code: The generated code
        """
        from apps.organizations.models import Company
        from .module_registry import get_module_code_rule_config
        
        company_id = request.data.get('company')
        code_type = request.data.get('code_type', 'asset_code')
        
        # Try to get existing rule from database
        try:
            if company_id:
                rule = CodeRule.objects.get(company_id=company_id, code=code_type)
            else:
                rule = CodeRule.objects.filter(code=code_type).first()
            
            if rule:
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
            pass
        
        # Fallback: generate code using default prefix from module registry
        default_prefixes = {
            'asset_code': 'ZC',
            'supply_code': 'BG',
            'purchase_order_code': 'PO',
        }
        prefix = default_prefixes.get(code_type, 'CODE')
        now = timezone.now()
        date_str = now.strftime('%Y%m%d')
        serial = str(int(now.timestamp() * 1000) % 10000).zfill(4)
        
        return Response({'code': f"{prefix}{date_str}{serial}"})
    
    @action(detail=False, methods=['get', 'post'], url_path='by-code/(?P<code_type>[^/.]+)')
    def by_code(self, request, code_type=None):
        """
        Get or update a code rule by its code type.
        
        Path params:
            code_type: The code type (e.g., 'asset_code', 'supply_code')
            
        Query/Body params:
            company: Company ID (optional)
        """
        company_id = request.query_params.get('company') or request.data.get('company')
        
        if request.method == 'GET':
            try:
                filters = {'code': code_type}
                if company_id:
                    filters['company_id'] = company_id
                
                rule = CodeRule.objects.filter(**filters).first()
                
                if rule:
                    return Response(self.get_serializer(rule).data)
                else:
                    # Return default configuration
                    default_prefixes = {
                        'asset_code': 'ZC',
                        'supply_code': 'BG',
                        'purchase_order_code': 'PO',
                    }
                    return Response({
                        'prefix': default_prefixes.get(code_type, 'CODE'),
                        'date_format': 'YYYYMMDD',
                        'serial_length': 4,
                        'separator': '',
                        'reset_cycle': 'daily',
                        'example': f"{default_prefixes.get(code_type, 'CODE')}{timezone.now().strftime('%Y%m%d')}0001"
                    })
                    
            except Exception as e:
                return Response({'error': str(e)}, status=400)
        
        elif request.method == 'POST':
            from apps.organizations.models import Company
            
            # Get or create company reference
            company = None
            if company_id:
                try:
                    company = Company.objects.get(id=company_id)
                except Company.DoesNotExist:
                    return Response({'error': '公司不存在'}, status=400)
            
            # Default names based on code type
            default_names = {
                'asset_code': '资产编号规则',
                'supply_code': '用品编号规则',
                'purchase_order_code': '采购订单编号规则',
            }
            
            rule_data = {
                'name': request.data.get('name', default_names.get(code_type, f'{code_type}编号规则')),
                'prefix': request.data.get('prefix', 'CODE'),
                'date_format': request.data.get('date_format', 'YYYYMMDD'),
                'serial_length': request.data.get('serial_length', 4),
                'separator': request.data.get('separator', ''),
                'reset_cycle': request.data.get('reset_cycle', 'daily'),
                'is_active': True
            }
            
            if company:
                rule, created = CodeRule.objects.update_or_create(
                    company=company,
                    code=code_type,
                    defaults=rule_data
                )
            else:
                # For system-wide rules without company
                rule, created = CodeRule.objects.update_or_create(
                    company__isnull=True,
                    code=code_type,
                    defaults={**rule_data, 'company': None}
                )
            
            return Response({
                'message': '编号规则保存成功',
                'data': self.get_serializer(rule).data
            })


class SystemConfigViewSet(viewsets.ModelViewSet):
    queryset = SystemConfig.objects.all()
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['company', 'config_key']
    
    def get_serializer_class(self):
        from rest_framework import serializers
        
        class SystemConfigSerializer(serializers.ModelSerializer):
            class Meta:
                model = SystemConfig
                fields = '__all__'
        
        return SystemConfigSerializer


class OperationLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = OperationLog.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['company', 'module', 'action']
    search_fields = ['content', 'operator__username', 'operator__display_name']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # 日期范围过滤
        created_at_gte = self.request.query_params.get('created_at__gte')
        created_at_lte = self.request.query_params.get('created_at__lte')
        
        if created_at_gte:
            queryset = queryset.filter(created_at__gte=created_at_gte)
        if created_at_lte:
            queryset = queryset.filter(created_at__lte=created_at_lte)
        
        return queryset
    
    def get_serializer_class(self):
        from rest_framework import serializers
        
        class OperationLogSerializer(serializers.ModelSerializer):
            operator_name = serializers.SerializerMethodField()
            
            class Meta:
                model = OperationLog
                fields = '__all__'
            
            def get_operator_name(self, obj):
                if obj.operator:
                    return obj.operator.display_name or obj.operator.username
                return None
        
        return OperationLogSerializer


class SystemInfoView(APIView):
    """系统信息"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        from django.conf import settings
        import platform
        import django
        
        return Response({
            'version': '1.0.0',
            'python_version': platform.python_version(),
            'django_version': django.__version__,
            'debug': settings.DEBUG
        })


class GlobalConfigView(APIView):
    """全局系统配置（名称、Logo、主题等）"""
    permission_classes = [IsAuthenticated]
    
    CONFIG_KEY = 'global_system_config'
    
    def get(self, request):
        """获取全局配置"""
        import json
        
        try:
            config_obj = SystemConfig.objects.filter(
                config_key=self.CONFIG_KEY,
                company__isnull=True
            ).first()
            
            if config_obj:
                config = json.loads(config_obj.config_value)
            else:
                config = self.get_default_config()
            
            return Response({'config': config})
        except Exception as e:
            return Response({'config': self.get_default_config()})
    
    def post(self, request):
        """保存全局配置"""
        import json
        
        config = request.data.get('config', {})
        
        try:
            config_obj, created = SystemConfig.objects.update_or_create(
                config_key=self.CONFIG_KEY,
                company__isnull=True,
                defaults={
                    'config_value': json.dumps(config, ensure_ascii=False),
                    'description': '全局系统配置',
                    'is_system': True
                }
            )
            
            return Response({
                'message': '配置保存成功',
                'config': config
            })
        except Exception as e:
            return Response(
                {'error': f'保存配置失败: {str(e)}'},
                status=400
            )
    
    def get_default_config(self):
        """默认配置"""
        return {
            'name': '钩子资产',
            'logo': '',
            'favicon': '',
            'primaryColor': '#3b82f6',
            'theme': 'light',
            'copyright': '© 2024 钩子资产 版权所有'
        }
