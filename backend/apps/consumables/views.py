from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import ConsumableCategory, Consumable, ConsumableStock, ConsumableInbound, ConsumableOutbound
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
    search_fields = ['name', 'code', 'brand', 'model']
    ordering_fields = ['created_at', 'name']
    ordering = ['-created_at']


class ConsumableStockViewSet(viewsets.ModelViewSet):
    queryset = ConsumableStock.objects.all()
    serializer_class = ConsumableStockSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['consumable', 'warehouse']
    
    @action(detail=False, methods=['get'])
    def warning(self, request):
        """获取库存预警列表"""
        from django.db.models import F
        queryset = self.get_queryset().filter(quantity__lte=F('consumable__min_stock'))
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ConsumableInboundViewSet(viewsets.ModelViewSet):
    queryset = ConsumableInbound.objects.all()
    serializer_class = ConsumableInboundSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['company', 'status', 'warehouse']
    ordering = ['-created_at']


class ConsumableOutboundViewSet(viewsets.ModelViewSet):
    queryset = ConsumableOutbound.objects.all()
    serializer_class = ConsumableOutboundSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['company', 'status', 'outbound_type']
    ordering = ['-created_at']
