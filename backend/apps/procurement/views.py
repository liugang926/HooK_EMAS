from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Supplier, PurchaseRequest, PurchaseOrder
from .serializers import (
    SupplierSerializer, PurchaseRequestSerializer, PurchaseOrderSerializer
)


class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['company', 'is_active']
    search_fields = ['name', 'code', 'contact']


class PurchaseRequestViewSet(viewsets.ModelViewSet):
    queryset = PurchaseRequest.objects.all()
    serializer_class = PurchaseRequestSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['company', 'status', 'applicant']
    search_fields = ['request_code', 'title']
    ordering = ['-created_at']
    
    def perform_create(self, serializer):
        serializer.save(applicant=self.request.user)
    
    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """提交审批"""
        obj = self.get_object()
        if obj.status != 'draft':
            return Response({'error': '只有草稿状态可以提交'}, status=status.HTTP_400_BAD_REQUEST)
        obj.status = 'pending'
        obj.save()
        return Response({'message': '提交成功'})
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """审批通过"""
        obj = self.get_object()
        obj.status = 'approved'
        obj.save()
        return Response({'message': '审批通过'})
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """审批拒绝"""
        obj = self.get_object()
        obj.status = 'rejected'
        obj.save()
        return Response({'message': '已拒绝'})


class PurchaseOrderViewSet(viewsets.ModelViewSet):
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['company', 'status', 'supplier']
    search_fields = ['order_code']
    ordering = ['-created_at']
    
    @action(detail=True, methods=['post'])
    def receive(self, request, pk=None):
        """验收入库"""
        obj = self.get_object()
        obj.status = 'received'
        obj.save()
        return Response({'message': '验收成功'})
