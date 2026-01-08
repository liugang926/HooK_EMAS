from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from django.db.models import Sum

from .models import DepreciationScheme, DepreciationRecord
from .serializers import DepreciationSchemeSerializer, DepreciationRecordSerializer


class DepreciationSchemeViewSet(viewsets.ModelViewSet):
    queryset = DepreciationScheme.objects.all()
    serializer_class = DepreciationSchemeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['company', 'is_active']


class DepreciationRecordViewSet(viewsets.ModelViewSet):
    queryset = DepreciationRecord.objects.all()
    serializer_class = DepreciationRecordSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['asset', 'depreciation_year', 'depreciation_month']
    ordering = ['-depreciation_year', '-depreciation_month']
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """获取折旧汇总数据"""
        queryset = self.get_queryset()
        company_id = request.query_params.get('company')
        year = request.query_params.get('year')
        month = request.query_params.get('month')
        
        if company_id:
            queryset = queryset.filter(asset__company_id=company_id)
        if year:
            queryset = queryset.filter(depreciation_year=year)
        if month:
            queryset = queryset.filter(depreciation_month=month)
        
        summary = queryset.aggregate(
            total_depreciation=Sum('depreciation_amount'),
            total_accumulated=Sum('accumulated_depreciation'),
            total_net_value=Sum('net_value')
        )
        
        return Response(summary)
    
    @action(detail=False, methods=['post'])
    def calculate(self, request):
        """计算折旧"""
        year = request.data.get('year')
        month = request.data.get('month')
        company_id = request.data.get('company')
        
        # 这里实现折旧计算逻辑
        # ...
        
        return Response({'message': '折旧计算完成'})
