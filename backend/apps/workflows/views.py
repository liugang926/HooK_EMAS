from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from .models import WorkflowTemplate, WorkflowInstance, WorkflowTask
from .serializers import (
    WorkflowTemplateSerializer, WorkflowInstanceSerializer, WorkflowTaskSerializer
)


class WorkflowTemplateViewSet(viewsets.ModelViewSet):
    queryset = WorkflowTemplate.objects.all()
    serializer_class = WorkflowTemplateSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['company', 'business_type', 'is_active']


class WorkflowInstanceViewSet(viewsets.ModelViewSet):
    queryset = WorkflowInstance.objects.all()
    serializer_class = WorkflowInstanceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['template', 'status', 'initiator']
    
    def perform_create(self, serializer):
        serializer.save(initiator=self.request.user)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """取消流程"""
        instance = self.get_object()
        if instance.status in ['completed', 'cancelled']:
            return Response({'error': '流程已结束，无法取消'}, status=status.HTTP_400_BAD_REQUEST)
        instance.status = 'cancelled'
        instance.save()
        return Response({'message': '流程已取消'})


class WorkflowTaskViewSet(viewsets.ModelViewSet):
    queryset = WorkflowTask.objects.all()
    serializer_class = WorkflowTaskSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['instance', 'assignee', 'status']
    
    @action(detail=False, methods=['get'])
    def my_tasks(self, request):
        """获取我的待办任务"""
        tasks = self.get_queryset().filter(
            assignee=request.user,
            status='pending'
        )
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """审批通过"""
        task = self.get_object()
        comment = request.data.get('comment', '')
        
        task.status = 'approved'
        task.comment = comment
        task.save()
        
        # 处理后续节点
        self._process_next_node(task.instance)
        
        return Response({'message': '审批通过'})
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """审批拒绝"""
        task = self.get_object()
        comment = request.data.get('comment', '')
        
        task.status = 'rejected'
        task.comment = comment
        task.save()
        
        # 更新流程状态
        task.instance.status = 'rejected'
        task.instance.save()
        
        return Response({'message': '已拒绝'})
    
    def _process_next_node(self, instance):
        """处理下一个节点"""
        current_node = instance.current_node
        if current_node:
            next_node = WorkflowNode.objects.filter(
                template=instance.template,
                order=current_node.order + 1
            ).first()
            
            if next_node:
                # 创建下一个任务
                instance.current_node = next_node
                instance.save()
                # 这里需要实现分配审批人的逻辑
            else:
                # 流程结束
                instance.status = 'completed'
                instance.save()
