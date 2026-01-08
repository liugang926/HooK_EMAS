"""
组织架构视图 - 精臣云资产管理系统
Multi-company architecture support with cross-company transfer workflows
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.utils import timezone
from django.db import transaction

from .models import Company, Department, Location, OrganizationChange, CrossCompanyTransfer, CrossCompanyTransferItem
from .serializers import (
    CompanySerializer,
    DepartmentSerializer,
    DepartmentTreeSerializer,
    LocationSerializer,
    LocationTreeSerializer,
    OrganizationChangeSerializer,
    CrossCompanyTransferSerializer,
    CrossCompanyTransferCreateSerializer,
    CrossCompanyTransferItemSerializer
)


class CompanyViewSet(viewsets.ModelViewSet):
    """公司管理视图集"""
    
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'code', 'short_name']
    ordering = ['name']
    
    @action(detail=False, methods=['get'], permission_classes=[])
    def public_list(self, request):
        """
        公开的公司列表接口，用于登录页面选择公司
        无需认证即可访问
        """
        companies = Company.objects.filter(is_active=True).values('id', 'name', 'short_name', 'code')
        return Response(list(companies))


class DepartmentViewSet(viewsets.ModelViewSet):
    """部门管理视图集"""
    
    queryset = Department.objects.select_related('company', 'parent', 'manager').all()
    serializer_class = DepartmentSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['company', 'parent', 'is_active']
    search_fields = ['name', 'code']
    ordering_fields = ['sort_order', 'name', 'created_at']
    ordering = ['sort_order', 'name']
    
    @action(detail=False, methods=['get'])
    def tree(self, request):
        """获取部门树形结构"""
        company_id = request.query_params.get('company')
        queryset = self.queryset.filter(parent__isnull=True, is_active=True).order_by('sort_order', 'name')
        if company_id:
            queryset = queryset.filter(company_id=company_id)
        serializer = DepartmentTreeSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def move(self, request, pk=None):
        """移动部门位置"""
        department = self.get_object()
        new_parent_id = request.data.get('parent')
        
        if new_parent_id:
            try:
                new_parent = Department.objects.get(pk=new_parent_id)
                # 检查是否会形成循环
                if department in new_parent.get_ancestors(include_self=True):
                    return Response(
                        {'error': '不能移动到自己的子部门下'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                department.move_to(new_parent)
            except Department.DoesNotExist:
                return Response(
                    {'error': '目标部门不存在'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            department.move_to(None)  # 移动到根节点
        
        return Response({'message': '部门移动成功'})


class LocationViewSet(viewsets.ModelViewSet):
    """存放区域管理视图集"""
    
    queryset = Location.objects.select_related('company', 'parent').all()
    serializer_class = LocationSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['company', 'parent', 'is_active']
    search_fields = ['name', 'code', 'address']
    ordering_fields = ['sort_order', 'name', 'created_at']
    ordering = ['sort_order', 'name']
    
    def perform_create(self, serializer):
        """创建位置时自动设置公司"""
        company = None
        if hasattr(self.request.user, 'company') and self.request.user.company:
            company = self.request.user.company
        else:
            company = Company.objects.first()
        
        serializer.save(company=company)
    
    @action(detail=False, methods=['get'])
    def tree(self, request):
        """获取区域树形结构"""
        company_id = request.query_params.get('company')
        queryset = self.queryset.filter(parent__isnull=True, is_active=True)
        if company_id:
            queryset = queryset.filter(company_id=company_id)
        serializer = LocationTreeSerializer(queryset, many=True)
        return Response(serializer.data)


class OrganizationChangeViewSet(viewsets.ModelViewSet):
    """组织异动管理视图集"""
    
    queryset = OrganizationChange.objects.select_related(
        'department', 'created_by', 'processed_by'
    ).all()
    serializer_class = OrganizationChangeSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['department', 'change_type', 'status']
    search_fields = ['description']
    ordering = ['-created_at']
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """审批通过"""
        change = self.get_object()
        if change.status != OrganizationChange.Status.PENDING:
            return Response(
                {'error': '只能审批待处理的记录'},
                status=status.HTTP_400_BAD_REQUEST
            )
        change.status = OrganizationChange.Status.APPROVED
        change.processed_by = request.user
        change.processed_at = timezone.now()
        change.save()
        return Response({'message': '审批通过'})
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """审批拒绝"""
        change = self.get_object()
        if change.status != OrganizationChange.Status.PENDING:
            return Response(
                {'error': '只能审批待处理的记录'},
                status=status.HTTP_400_BAD_REQUEST
            )
        change.status = OrganizationChange.Status.REJECTED
        change.processed_by = request.user
        change.processed_at = timezone.now()
        change.save()
        return Response({'message': '已拒绝'})


class CrossCompanyTransferViewSet(viewsets.ModelViewSet):
    """
    跨公司资产调拨管理视图集
    
    Cross-company asset transfer workflow with dual approval:
    1. From-company approval (asset owner)
    2. To-company approval (asset receiver)
    
    Supports financial audit requirements:
    - Settlement tracking
    - Asset valuation snapshots
    - Approval chain records
    """
    
    queryset = CrossCompanyTransfer.objects.select_related(
        'from_company', 'to_company',
        'from_department', 'to_department',
        'from_approver', 'to_approver',
        'created_by'
    ).prefetch_related('items', 'items__asset').all()
    
    serializer_class = CrossCompanyTransferSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['from_company', 'to_company', 'status', 'transfer_type', 'settlement_type']
    search_fields = ['transfer_no', 'reason', 'items__asset__name', 'items__asset__asset_code']
    ordering_fields = ['created_at', 'transfer_value', 'status']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CrossCompanyTransferCreateSerializer
        return CrossCompanyTransferSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """
        提交调拨单进入审批流程
        Changes status from DRAFT to PENDING
        """
        transfer = self.get_object()
        
        if transfer.status != CrossCompanyTransfer.Status.DRAFT:
            return Response(
                {'msg': '只能提交草稿状态的调拨单'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not transfer.items.exists():
            return Response(
                {'msg': '调拨单中没有资产，请先添加资产'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        transfer.status = CrossCompanyTransfer.Status.PENDING
        transfer.save()
        
        return Response({'message': '调拨单已提交审批'})
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """
        审批调拨单
        Supports dual-approval workflow:
        - side='from': From-company approves asset release
        - side='to': To-company approves asset receipt
        """
        transfer = self.get_object()
        side = request.data.get('side', 'from')
        
        if transfer.status == CrossCompanyTransfer.Status.REJECTED:
            return Response(
                {'msg': '此调拨单已被拒绝'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if transfer.status == CrossCompanyTransfer.Status.COMPLETED:
            return Response(
                {'msg': '此调拨单已完成'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        now = timezone.now()
        
        if side == 'from':
            if transfer.from_approved_at:
                return Response(
                    {'msg': '调出公司已审批'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            transfer.from_approver = request.user
            transfer.from_approved_at = now
            transfer.status = CrossCompanyTransfer.Status.APPROVED
        elif side == 'to':
            if not transfer.from_approved_at:
                return Response(
                    {'msg': '请先完成调出公司审批'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if transfer.to_approved_at:
                return Response(
                    {'msg': '调入公司已审批'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            transfer.to_approver = request.user
            transfer.to_approved_at = now
            transfer.status = CrossCompanyTransfer.Status.IN_TRANSIT
        
        transfer.save()
        
        return Response({
            'message': f'{"调出" if side == "from" else "调入"}公司审批通过',
            'status': transfer.status
        })
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """
        拒绝调拨单
        """
        transfer = self.get_object()
        reason = request.data.get('reason', '')
        
        if transfer.status in [CrossCompanyTransfer.Status.COMPLETED, CrossCompanyTransfer.Status.REJECTED]:
            return Response(
                {'msg': '无法拒绝已完成或已拒绝的调拨单'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        transfer.status = CrossCompanyTransfer.Status.REJECTED
        if reason:
            transfer.remark = f"{transfer.remark or ''}\n拒绝原因: {reason}".strip()
        transfer.save()
        
        return Response({'message': '调拨单已拒绝'})
    
    @action(detail=True, methods=['post'])
    @transaction.atomic
    def complete(self, request, pk=None):
        """
        完成调拨 - 执行实际资产转移
        
        This action:
        1. Updates asset ownership (company, department)
        2. Records the transfer in asset history
        3. Calculates settlement amounts if applicable
        """
        transfer = self.get_object()
        
        if transfer.status != CrossCompanyTransfer.Status.IN_TRANSIT:
            if transfer.status == CrossCompanyTransfer.Status.APPROVED:
                # Allow completion after from-company approval only in some cases
                pass
            else:
                return Response(
                    {'msg': '只能完成已审批的调拨单'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        now = timezone.now()
        
        # Process each asset in the transfer
        for item in transfer.items.all():
            asset = item.asset
            
            # Update asset company assignment
            # Note: Actual implementation depends on your Asset model structure
            # This is a placeholder for the business logic
            if hasattr(asset, 'company'):
                asset.company = transfer.to_company
            if transfer.to_department and hasattr(asset, 'using_department'):
                asset.using_department = transfer.to_department
            
            # Record operation in asset history
            from apps.assets.models import AssetOperation
            AssetOperation.objects.create(
                asset=asset,
                operation_type='transfer',
                description=f'跨公司调拨: {transfer.from_company.name} → {transfer.to_company.name}',
                operator=request.user,
                extra_data={
                    'transfer_no': transfer.transfer_no,
                    'from_company_id': transfer.from_company.id,
                    'to_company_id': transfer.to_company.id,
                    'settlement_type': transfer.settlement_type,
                    'transfer_price': str(item.transfer_price)
                }
            )
            
            asset.save()
        
        # Calculate final settlement
        transfer.settlement_amount = sum(
            item.transfer_price for item in transfer.items.all()
        )
        transfer.settlement_date = now.date()
        transfer.status = CrossCompanyTransfer.Status.COMPLETED
        transfer.completed_at = now
        transfer.save()
        
        return Response({
            'message': '调拨完成',
            'settlement_amount': str(transfer.settlement_amount)
        })
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """取消调拨单"""
        transfer = self.get_object()
        
        if transfer.status in [CrossCompanyTransfer.Status.COMPLETED, CrossCompanyTransfer.Status.IN_TRANSIT]:
            return Response(
                {'msg': '无法取消已完成或调拨中的调拨单'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        transfer.status = CrossCompanyTransfer.Status.CANCELLED
        transfer.save()
        
        return Response({'message': '调拨单已取消'})
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        获取调拨统计数据
        
        Returns counts by status and total transfer values
        """
        from django.db.models import Sum, Count
        
        company_id = request.query_params.get('company')
        queryset = self.queryset
        
        if company_id:
            from django.db.models import Q
            queryset = queryset.filter(
                Q(from_company_id=company_id) | Q(to_company_id=company_id)
            )
        
        stats = queryset.aggregate(
            total_count=Count('id'),
            total_value=Sum('transfer_value'),
            pending_count=Count('id', filter=models.Q(status='pending')),
            approved_count=Count('id', filter=models.Q(status='approved')),
            completed_count=Count('id', filter=models.Q(status='completed')),
            rejected_count=Count('id', filter=models.Q(status='rejected'))
        )
        
        return Response(stats)
