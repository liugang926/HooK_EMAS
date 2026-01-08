from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter

from .models import InventoryTask, InventoryRecord
from .serializers import InventoryTaskSerializer, InventoryRecordSerializer


class InventoryTaskViewSet(viewsets.ModelViewSet):
    queryset = InventoryTask.objects.all()
    serializer_class = InventoryTaskSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['company', 'status', 'executor']
    ordering = ['-created_at']
    
    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """开始盘点"""
        task = self.get_object()
        if task.status != 'pending':
            return Response({'error': '任务状态不正确'}, status=status.HTTP_400_BAD_REQUEST)
        task.status = 'in_progress'
        task.save()
        return Response({'message': '盘点已开始'})
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """完成盘点"""
        task = self.get_object()
        task.status = 'completed'
        task.save()
        return Response({'message': '盘点已完成'})
    
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """获取盘点统计"""
        task = self.get_object()
        records = task.records.all()
        total = records.count()
        normal = records.filter(result='normal').count()
        abnormal = total - normal
        return Response({
            'total': total,
            'completed': records.filter(status='completed').count(),
            'normal': normal,
            'abnormal': abnormal
        })


class InventoryRecordViewSet(viewsets.ModelViewSet):
    queryset = InventoryRecord.objects.all()
    serializer_class = InventoryRecordSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['task', 'asset', 'status', 'result']
    
    @action(detail=True, methods=['post'])
    def check(self, request, pk=None):
        """提交盘点结果"""
        record = self.get_object()
        result = request.data.get('result')
        remark = request.data.get('remark', '')
        
        record.result = result
        record.remark = remark
        record.status = 'completed'
        record.checked_by = request.user
        record.save()
        
        return Response({'message': '提交成功'})
