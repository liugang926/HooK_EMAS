from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db import transaction
from django.utils import timezone

from .models import ConsumableCategory, Consumable, ConsumableStock, ConsumableInbound, ConsumableInboundItem, ConsumableOutbound, ConsumableOutboundItem
from .serializers import (
    ConsumableCategorySerializer, ConsumableSerializer,
    ConsumableStockSerializer, ConsumableInboundSerializer, ConsumableOutboundSerializer
)


class ConsumableCategoryViewSet(viewsets.ModelViewSet):
    queryset = ConsumableCategory.objects.all()
    serializer_class = ConsumableCategorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['company', 'parent']
    search_fields = ['name', 'code']
    
    @action(detail=False, methods=['get'])
    def tree(self, request):
        """获取分类树形结构"""
        company_id = request.query_params.get('company')
        queryset = self.get_queryset().filter(parent__isnull=True)
        if company_id:
            queryset = queryset.filter(company_id=company_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ConsumableViewSet(viewsets.ModelViewSet):
    queryset = Consumable.objects.all()
    serializer_class = ConsumableSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['company', 'category', 'is_active']
    search_fields = ['name', 'code', 'brand', 'model', 'category__name']
    ordering_fields = ['created_at', 'name']
    ordering = ['-created_at']


class ConsumableStockViewSet(viewsets.ModelViewSet):
    queryset = ConsumableStock.objects.select_related('consumable', 'consumable__category', 'warehouse').all()
    serializer_class = ConsumableStockSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['consumable', 'warehouse']
    search_fields = ['consumable__name', 'consumable__code', 'consumable__category__name', 'warehouse__name']
    
    @action(detail=False, methods=['get'])
    def warning(self, request):
        """获取库存预警列表"""
        from django.db.models import F
        queryset = self.get_queryset().filter(quantity__lte=F('consumable__min_stock'))
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


def generate_document_code(code_type, company_id=None):
    """Generate document code using the code rule system"""
    from apps.system.models import CodeRule
    import os, json, traceback
    
    now = timezone.now()
    
    # #region agent log
    try:
        log_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), '.cursor', 'debug.log')
        open(log_path, 'a').write(json.dumps({'location': 'views.py:generate_document_code', 'message': 'Code generation started', 'data': {'code_type': code_type, 'company_id': company_id}, 'timestamp': __import__('time').time(), 'sessionId': 'debug-session', 'hypothesisId': 'H1'}) + '\n')
    except:
        pass
    # #endregion
    
    # Get or create default rule
    try:
        if company_id:
            rule = CodeRule.objects.get(company_id=company_id, code=code_type)
        else:
            rule = CodeRule.objects.get(company__isnull=True, code=code_type)
        # #region agent log
        try:
            log_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), '.cursor', 'debug.log')
            open(log_path, 'a').write(json.dumps({'location': 'views.py:generate_document_code', 'message': 'Rule found', 'data': {'rule_id': rule.id, 'prefix': rule.prefix, 'current_serial': rule.current_serial}, 'timestamp': __import__('time').time(), 'sessionId': 'debug-session', 'hypothesisId': 'H1'}) + '\n')
        except:
            pass
        # #endregion
    except CodeRule.DoesNotExist:
        # Default rules for different types
        defaults = {
            'inbound_code': {'prefix': 'RK', 'name': '入库单编号规则'},
            'outbound_code': {'prefix': 'LY', 'name': '领用单编号规则'},
        }
        default = defaults.get(code_type, {'prefix': 'DOC', 'name': '单据编号规则'})
        rule = CodeRule.objects.create(
            company_id=company_id,
            code=code_type,
            name=default['name'],
            prefix=default['prefix'],
            date_format='YYYYMMDD',
            serial_length=4,
            reset_cycle='daily',
            is_active=True
        )
        # #region agent log
        try:
            log_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), '.cursor', 'debug.log')
            open(log_path, 'a').write(json.dumps({'location': 'views.py:generate_document_code', 'message': 'Rule created', 'data': {'rule_id': rule.id, 'prefix': rule.prefix}, 'timestamp': __import__('time').time(), 'sessionId': 'debug-session', 'hypothesisId': 'H1'}) + '\n')
        except:
            pass
        # #endregion
    
    # Generate date string
    date_str = ''
    if rule.date_format == 'YYYY':
        date_str = now.strftime('%Y')
    elif rule.date_format == 'YYYYMM':
        date_str = now.strftime('%Y%m')
    elif rule.date_format == 'YYYYMMDD':
        date_str = now.strftime('%Y%m%d')
    
    # Check if reset is needed
    should_reset = False
    if rule.reset_cycle == 'daily' and rule.last_reset_date != now.date():
        should_reset = True
    elif rule.reset_cycle == 'monthly' and (rule.last_reset_date is None or rule.last_reset_date.month != now.month):
        should_reset = True
    elif rule.reset_cycle == 'yearly' and (rule.last_reset_date is None or rule.last_reset_date.year != now.year):
        should_reset = True
    
    if should_reset:
        rule.current_serial = 0
        rule.last_reset_date = now.date()
    
    # Increment serial
    rule.current_serial += 1
    rule.save()
    
    # Format serial number
    serial = str(rule.current_serial).zfill(rule.serial_length)
    sep = rule.separator or ''
    generated_code = f"{rule.prefix or ''}{sep}{date_str}{sep}{serial}"
    
    # #region agent log
    try:
        log_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), '.cursor', 'debug.log')
        open(log_path, 'a').write(json.dumps({'location': 'views.py:generate_document_code', 'message': 'Code generated', 'data': {'generated_code': generated_code, 'prefix': rule.prefix, 'date_str': date_str, 'serial': serial}, 'timestamp': __import__('time').time(), 'sessionId': 'debug-session', 'hypothesisId': 'H1'}) + '\n')
    except:
        pass
    # #endregion
    
    return generated_code


class ConsumableInboundViewSet(viewsets.ModelViewSet):
    queryset = ConsumableInbound.objects.select_related('warehouse', 'supplier', 'created_by').prefetch_related('items').all()
    serializer_class = ConsumableInboundSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ['company', 'status', 'warehouse']
    search_fields = ['inbound_no', 'warehouse__name', 'supplier__name', 'created_by__username', 'created_by__nickname']
    ordering = ['-created_at']
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """Create inbound with items"""
        try:
            # #region agent log
            try:
                import json, os; log_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), '.cursor', 'debug.log'); open(log_path, 'a').write(json.dumps({'location': 'views.py:inbound_create', 'message': 'Inbound create called', 'data': {'request_data': str(dict(request.data))[:500], 'user_id': request.user.id if request.user else None}, 'timestamp': __import__('time').time(), 'sessionId': 'debug-session', 'hypothesisId': 'H1'}) + '\n')
            except Exception as e:
                pass
            # #endregion
            
            # Convert request.data to dict and extract items
            if hasattr(request.data, 'get'):
                data = {k: v for k, v in request.data.items()}
            else:
                data = dict(request.data)
            items_data = data.pop('items', []) if 'items' in data else []
            
            # Auto-generate inbound_no
            company_id = data.get('company') or getattr(request.user, 'current_company_id', None)
            if not company_id:
                return Response({'detail': '公司ID不能为空'}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                data['inbound_no'] = generate_document_code('inbound_code', company_id)
            except Exception as e:
                # #region agent log
                try:
                    import json, os; log_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), '.cursor', 'debug.log'); open(log_path, 'a').write(json.dumps({'location': 'views.py:inbound_code_gen_error', 'message': 'Code generation failed', 'data': {'error': str(e)}, 'timestamp': __import__('time').time(), 'sessionId': 'debug-session', 'hypothesisId': 'H1'}) + '\n')
                except:
                    pass
                # #endregion
                return Response({'detail': f'生成编号失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            data['company'] = company_id
            data['created_by'] = request.user.id
            
            # #region agent log
            try:
                import json, os; log_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), '.cursor', 'debug.log'); open(log_path, 'a').write(json.dumps({'location': 'views.py:inbound_before_save', 'message': 'Before save inbound', 'data': {'inbound_no': data.get('inbound_no'), 'company': str(company_id), 'items_count': len(items_data)}, 'timestamp': __import__('time').time(), 'sessionId': 'debug-session', 'hypothesisId': 'H1'}) + '\n')
            except:
                pass
            # #endregion
            
            # Create inbound record
            serializer = self.get_serializer(data=data)
            if not serializer.is_valid():
                # #region agent log
                try:
                    import json, os; log_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), '.cursor', 'debug.log'); open(log_path, 'a').write(json.dumps({'location': 'views.py:inbound_serializer_invalid', 'message': 'Serializer validation failed', 'data': {'errors': str(serializer.errors)}, 'timestamp': __import__('time').time(), 'sessionId': 'debug-session', 'hypothesisId': 'H1'}) + '\n')
                except:
                    pass
                # #endregion
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            inbound = serializer.save()
            
            # #region agent log
            try:
                import json, os; log_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), '.cursor', 'debug.log'); open(log_path, 'a').write(json.dumps({'location': 'views.py:inbound_after_save', 'message': 'Inbound created', 'data': {'id': inbound.id, 'inbound_no': inbound.inbound_no}, 'timestamp': __import__('time').time(), 'sessionId': 'debug-session', 'hypothesisId': 'H1'}) + '\n')
            except:
                pass
            # #endregion
            
            # Create items
            for item_data in items_data:
                quantity = item_data.get('quantity', 0)
                price = item_data.get('price', 0)
                amount = item_data.get('amount', quantity * price)
                ConsumableInboundItem.objects.create(
                    inbound=inbound,
                    consumable_id=item_data['consumable'],
                    quantity=quantity,
                    price=price,
                    amount=amount
                )
            
            return Response(self.get_serializer(inbound).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            # #region agent log
            try:
                import json, os, traceback; log_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), '.cursor', 'debug.log'); open(log_path, 'a').write(json.dumps({'location': 'views.py:inbound_create_exception', 'message': 'Unexpected error in create', 'data': {'error': str(e), 'traceback': traceback.format_exc()[:1000]}, 'timestamp': __import__('time').time(), 'sessionId': 'debug-session', 'hypothesisId': 'H1'}) + '\n')
            except:
                pass
            # #endregion
            return Response({'detail': f'创建失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @transaction.atomic
    def update(self, request, *args, **kwargs):
        """Update inbound with items"""
        instance = self.get_object()
        
        if instance.status != 'draft':
            return Response({'detail': '只能编辑草稿状态的入库单'}, status=status.HTTP_400_BAD_REQUEST)
        
        data = request.data.copy()
        items_data = data.pop('items', [])
        
        # Update inbound record
        serializer = self.get_serializer(instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        inbound = serializer.save()
        
        # Replace items
        instance.items.all().delete()
        for item_data in items_data:
            quantity = item_data.get('quantity', 0)
            price = item_data.get('price', 0)
            amount = item_data.get('amount', quantity * price)
            ConsumableInboundItem.objects.create(
                inbound=inbound,
                consumable_id=item_data['consumable'],
                quantity=quantity,
                price=price,
                amount=amount
            )
        
        return Response(self.get_serializer(inbound).data)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve inbound and update stock"""
        inbound = self.get_object()
        
        if inbound.status != 'draft':
            return Response({'detail': '只能确认草稿状态的入库单'}, status=status.HTTP_400_BAD_REQUEST)
        
        with transaction.atomic():
            # Update stock for each item
            for item in inbound.items.all():
                stock, created = ConsumableStock.objects.get_or_create(
                    consumable=item.consumable,
                    warehouse=inbound.warehouse,
                    defaults={'quantity': 0}
                )
                stock.quantity += item.quantity
                stock.save()
            
            # Update status
            inbound.status = 'approved'
            inbound.save()
        
        return Response({'detail': '入库确认成功'})


class ConsumableOutboundViewSet(viewsets.ModelViewSet):
    queryset = ConsumableOutbound.objects.select_related('warehouse', 'receive_user', 'receive_department', 'created_by').prefetch_related('items').all()
    serializer_class = ConsumableOutboundSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ['company', 'status', 'outbound_type']
    search_fields = ['outbound_no', 'warehouse__name', 'receive_user__username', 'receive_user__nickname', 'receive_department__name', 'created_by__username', 'created_by__nickname']
    ordering = ['-created_at']
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """Create outbound with items"""
        try:
            # #region agent log
            try:
                import json, os; log_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), '.cursor', 'debug.log'); open(log_path, 'a').write(json.dumps({'location': 'views.py:outbound_create', 'message': 'Outbound create called', 'data': {'request_data': str(dict(request.data))[:500], 'user_id': request.user.id if request.user else None}, 'timestamp': __import__('time').time(), 'sessionId': 'debug-session', 'hypothesisId': 'H1'}) + '\n')
            except:
                pass
            # #endregion
            
            # Convert request.data to dict and extract items
            if hasattr(request.data, 'get'):
                data = {k: v for k, v in request.data.items()}
            else:
                data = dict(request.data)
            items_data = data.pop('items', []) if 'items' in data else []
            
            # Auto-generate outbound_no
            company_id = data.get('company') or getattr(request.user, 'current_company_id', None)
            if not company_id:
                return Response({'detail': '公司ID不能为空'}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                data['outbound_no'] = generate_document_code('outbound_code', company_id)
            except Exception as e:
                # #region agent log
                try:
                    import json, os; log_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), '.cursor', 'debug.log'); open(log_path, 'a').write(json.dumps({'location': 'views.py:outbound_code_gen_error', 'message': 'Code generation failed', 'data': {'error': str(e)}, 'timestamp': __import__('time').time(), 'sessionId': 'debug-session', 'hypothesisId': 'H1'}) + '\n')
                except:
                    pass
                # #endregion
                return Response({'detail': f'生成编号失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            data['company'] = company_id
            data['created_by'] = request.user.id
            data['outbound_type'] = data.get('outbound_type', 'receive')
            
            # Create outbound record
            serializer = self.get_serializer(data=data)
            if not serializer.is_valid():
                # #region agent log
                try:
                    import json, os; log_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), '.cursor', 'debug.log'); open(log_path, 'a').write(json.dumps({'location': 'views.py:outbound_serializer_invalid', 'message': 'Serializer validation failed', 'data': {'errors': str(serializer.errors)}, 'timestamp': __import__('time').time(), 'sessionId': 'debug-session', 'hypothesisId': 'H1'}) + '\n')
                except:
                    pass
                # #endregion
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            outbound = serializer.save()
            
            # Create items
            for item_data in items_data:
                ConsumableOutboundItem.objects.create(
                    outbound=outbound,
                    consumable_id=item_data['consumable'],
                    quantity=item_data['quantity']
                )
            
            return Response(self.get_serializer(outbound).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            # #region agent log
            try:
                import json, os, traceback; log_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), '.cursor', 'debug.log'); open(log_path, 'a').write(json.dumps({'location': 'views.py:outbound_create_exception', 'message': 'Unexpected error in create', 'data': {'error': str(e), 'traceback': traceback.format_exc()[:1000]}, 'timestamp': __import__('time').time(), 'sessionId': 'debug-session', 'hypothesisId': 'H1'}) + '\n')
            except:
                pass
            # #endregion
            return Response({'detail': f'创建失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @transaction.atomic
    def update(self, request, *args, **kwargs):
        """Update outbound with items"""
        instance = self.get_object()
        
        if instance.status != 'draft':
            return Response({'detail': '只能编辑草稿状态的领用单'}, status=status.HTTP_400_BAD_REQUEST)
        
        data = request.data.copy()
        items_data = data.pop('items', [])
        
        # Update outbound record
        serializer = self.get_serializer(instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        outbound = serializer.save()
        
        # Replace items
        instance.items.all().delete()
        for item_data in items_data:
            ConsumableOutboundItem.objects.create(
                outbound=outbound,
                consumable_id=item_data['consumable'],
                quantity=item_data['quantity']
            )
        
        return Response(self.get_serializer(outbound).data)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve outbound and deduct stock"""
        outbound = self.get_object()
        
        if outbound.status != 'draft':
            return Response({'detail': '只能确认草稿状态的领用单'}, status=status.HTTP_400_BAD_REQUEST)
        
        with transaction.atomic():
            # Check and deduct stock for each item
            for item in outbound.items.all():
                try:
                    stock = ConsumableStock.objects.get(
                        consumable=item.consumable,
                        warehouse=outbound.warehouse
                    )
                    if stock.quantity < item.quantity:
                        return Response({
                            'detail': f'{item.consumable.name} 库存不足，当前库存: {stock.quantity}'
                        }, status=status.HTTP_400_BAD_REQUEST)
                    stock.quantity -= item.quantity
                    stock.save()
                except ConsumableStock.DoesNotExist:
                    return Response({
                        'detail': f'{item.consumable.name} 在该仓库无库存'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # Update status
            outbound.status = 'approved'
            outbound.save()
        
        return Response({'detail': '领用确认成功'})
