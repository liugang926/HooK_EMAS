from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Sum, Q
from django.db.models.functions import TruncMonth

from apps.assets.models import Asset
from apps.consumables.models import Consumable, ConsumableStock
from apps.organizations.models import Department


class AssetSummaryReportView(APIView):
    """资产汇总报表"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        company_id = request.query_params.get('company')
        
        queryset = Asset.objects.filter(is_deleted=False)
        if company_id:
            queryset = queryset.filter(company_id=company_id)
        
        # 总资产数量和价值
        summary = queryset.aggregate(
            total_count=Count('id'),
            total_value=Sum('original_value'),
            total_net_value=Sum('net_value')
        )
        
        # 按状态统计
        by_status = queryset.values('status').annotate(
            count=Count('id'),
            value=Sum('original_value')
        )
        
        # 按分类统计
        by_category = queryset.values('category__name').annotate(
            count=Count('id'),
            value=Sum('original_value')
        )
        
        return Response({
            'summary': summary,
            'by_status': list(by_status),
            'by_category': list(by_category)
        })


class AssetTrendReportView(APIView):
    """资产趋势报表"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        company_id = request.query_params.get('company')
        
        queryset = Asset.objects.filter(is_deleted=False)
        if company_id:
            queryset = queryset.filter(company_id=company_id)
        
        # 按月统计新增资产
        monthly_trend = queryset.annotate(
            month=TruncMonth('created_at')
        ).values('month').annotate(
            count=Count('id'),
            value=Sum('original_value')
        ).order_by('month')
        
        return Response(list(monthly_trend))


class DepartmentAssetReportView(APIView):
    """部门资产报表"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        company_id = request.query_params.get('company')
        
        queryset = Asset.objects.filter(is_deleted=False)
        if company_id:
            queryset = queryset.filter(company_id=company_id)
        
        # 按部门统计
        by_department = queryset.values('department__name').annotate(
            count=Count('id'),
            value=Sum('original_value')
        ).order_by('-count')
        
        return Response(list(by_department))


class ConsumableSummaryReportView(APIView):
    """耗材汇总报表"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        company_id = request.query_params.get('company')
        
        stock_queryset = ConsumableStock.objects.all()
        if company_id:
            stock_queryset = stock_queryset.filter(consumable__company_id=company_id)
        
        # 库存汇总
        summary = stock_queryset.aggregate(
            total_types=Count('consumable', distinct=True),
            total_quantity=Sum('quantity')
        )
        
        # 库存预警
        from django.db.models import F
        warning_count = stock_queryset.filter(
            quantity__lte=F('consumable__min_stock')
        ).count()
        
        summary['warning_count'] = warning_count
        
        return Response(summary)
