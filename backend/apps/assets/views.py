"""
资产管理视图 - 精臣云资产管理系统

遵循 .cursorrules 规约:
- 禁止在 Django View 中编写业务逻辑
- 所有业务逻辑封装在 services/ 目录下
- 列表查询使用 select_related 或 prefetch_related 优化 N+1 问题
"""
from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.utils import timezone

from .models import (
    AssetCategory, Asset, AssetImage, AssetOperation,
    AssetReceive, AssetReceiveItem,
    AssetBorrow, AssetBorrowItem,
    AssetTransfer, AssetTransferItem,
    AssetDisposal, AssetDisposalItem,
    AssetMaintenance, AssetLabel
)
from .serializers import (
    AssetCategorySerializer, AssetCategoryTreeSerializer,
    AssetSerializer, AssetListSerializer, AssetImageSerializer,
    AssetOperationSerializer,
    AssetReceiveSerializer, AssetReceiveItemSerializer,
    AssetBorrowSerializer, AssetBorrowItemSerializer,
    AssetTransferSerializer, AssetTransferItemSerializer,
    AssetDisposalSerializer, AssetDisposalItemSerializer,
    AssetMaintenanceSerializer, AssetLabelSerializer
)

# 导入服务层
from services import (
    AssetService, ReceiveService, BorrowService,
    TransferService, DisposalService, MaintenanceService,
    BatchImportExportService, BatchOperationService
)


class AssetCategoryViewSet(viewsets.ModelViewSet):
    """资产分类视图集"""
    
    queryset = AssetCategory.objects.select_related('parent').all()
    serializer_class = AssetCategorySerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['company', 'parent', 'is_active']
    search_fields = ['name', 'code']
    ordering = ['sort_order', 'name']
    
    def perform_create(self, serializer):
        """创建分类时自动设置公司"""
        from apps.organizations.models import Company
        
        company = None
        if hasattr(self.request.user, 'company') and self.request.user.company:
            company = self.request.user.company
        else:
            company = Company.objects.first()
        
        serializer.save(company=company)
    
    @action(detail=False, methods=['get'])
    def tree(self, request):
        """获取分类树形结构"""
        company_id = request.query_params.get('company')
        queryset = self.queryset.filter(parent__isnull=True, is_active=True)
        if company_id:
            queryset = queryset.filter(company_id=company_id)
        serializer = AssetCategoryTreeSerializer(queryset, many=True)
        return Response(serializer.data)


class AssetViewSet(viewsets.ModelViewSet):
    """
    资产视图集
    
    遵循 .cursorrules: 业务逻辑委托给 AssetService
    """
    
    queryset = Asset.objects.select_related(
        'category', 'using_department', 'using_user', 'location',
        'manage_department', 'manager', 'supplier', 'created_by'
    ).filter(is_deleted=False)
    serializer_class = AssetSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = [
        'company', 'category', 'status', 'using_department',
        'using_user', 'location', 'manage_department', 'manager'
    ]
    search_fields = ['asset_code', 'name', 'brand', 'model', 'serial_number']
    ordering_fields = ['asset_code', 'name', 'original_value', 'created_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return AssetListSerializer
        return AssetSerializer
    
    def perform_create(self, serializer):
        """创建资产 - 委托给 AssetService"""
        asset = AssetService.create_asset(
            validated_data=serializer.validated_data,
            user=self.request.user
        )
        # 更新 serializer.instance 以便返回正确的响应
        serializer.instance = asset
    
    def perform_update(self, serializer):
        """更新资产 - 委托给 AssetService"""
        asset = self.get_object()
        updated_asset = AssetService.update_asset(
            asset=asset,
            validated_data=serializer.validated_data,
            user=self.request.user
        )
        serializer.instance = updated_asset
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """资产统计 - 委托给 AssetService"""
        company_id = request.query_params.get('company')
        stats = AssetService.get_statistics(company_id=company_id)
        return Response(stats)
    
    @action(detail=True, methods=['post'])
    def soft_delete(self, request, pk=None):
        """软删除资产 - 委托给 AssetService"""
        asset = self.get_object()
        AssetService.soft_delete(asset=asset, user=request.user)
        return Response({'message': '资产已移入回收站'})
    
    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        """恢复已删除资产 - 委托给 AssetService"""
        AssetService.restore(asset_id=pk)
        return Response({'message': '资产已恢复'})
    
    @action(detail=False, methods=['get'])
    def recycle_bin(self, request):
        """回收站列表"""
        queryset = Asset.objects.filter(is_deleted=True)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = AssetListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = AssetListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    # ========== Batch Import/Export Operations ==========
    
    @action(detail=False, methods=['get'])
    def import_template(self, request):
        """Download import template - 下载导入模板"""
        return BatchImportExportService.generate_import_template()
    
    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def import_assets(self, request):
        """
        Batch import assets from Excel file - 批量导入资产
        
        Accepts an Excel file and creates assets based on the data.
        Returns a summary of successful imports and any errors.
        """
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response(
                {'success': False, 'message': '请上传Excel文件'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate file extension
        if not file_obj.name.endswith(('.xlsx', '.xls')):
            return Response(
                {'success': False, 'message': '请上传Excel文件（.xlsx或.xls格式）'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        result = BatchImportExportService.import_assets(file_obj, request.user)
        return Response(result)
    
    @action(detail=False, methods=['get'])
    def export(self, request):
        """
        Export assets to Excel file - 导出资产
        
        Supports filtering by same parameters as list endpoint.
        Optional 'fields' query param to specify which columns to export.
        Optional 'ids' query param to export specific assets.
        """
        # Get asset IDs if specified
        ids = request.query_params.get('ids')
        if ids:
            asset_ids = [int(id) for id in ids.split(',') if id.isdigit()]
            queryset = self.queryset.filter(id__in=asset_ids)
        else:
            # Apply same filters as list view
            queryset = self.filter_queryset(self.queryset)
        
        # Get export fields if specified
        fields = request.query_params.get('fields')
        export_fields = fields.split(',') if fields else None
        
        return BatchImportExportService.export_assets(queryset, export_fields)
    
    # ========== Batch Operations ==========
    
    @action(detail=False, methods=['post'])
    def batch_receive(self, request):
        """
        Batch receive assets - 批量领用
        
        Request body:
        {
            "asset_ids": [1, 2, 3],
            "receive_user": 1,
            "receive_department": 1,
            "receive_location": 1,
            "receive_date": "2024-01-15",
            "reason": "领用原因"
        }
        """
        asset_ids = request.data.get('asset_ids', [])
        receive_user = request.data.get('receive_user')
        receive_department = request.data.get('receive_department')
        receive_location = request.data.get('receive_location')
        receive_date = request.data.get('receive_date', timezone.now().date().isoformat())
        reason = request.data.get('reason', '')
        
        if not asset_ids:
            return Response(
                {'success': False, 'message': '请选择要领用的资产'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not receive_user:
            return Response(
                {'success': False, 'message': '请选择领用人'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get company from request body (POST) or query params (GET)
        # Frontend interceptor adds company to request.data for POST requests
        company_id = request.data.get('company') or request.query_params.get('company')
        
        result = BatchOperationService.batch_receive(
            asset_ids=asset_ids,
            receive_user_id=receive_user,
            receive_department_id=receive_department,
            receive_location_id=receive_location,
            receive_date=receive_date,
            reason=reason,
            user=request.user,
            company_id=company_id
        )
        
        if result['success']:
            return Response(result)
        return Response(result, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def batch_return(self, request):
        """
        Batch return assets - 批量退还
        
        Request body:
        {
            "asset_ids": [1, 2, 3],
            "return_date": "2024-01-15",
            "reason": "退还原因"
        }
        """
        asset_ids = request.data.get('asset_ids', [])
        return_date = request.data.get('return_date', timezone.now().date().isoformat())
        reason = request.data.get('reason', '')
        
        if not asset_ids:
            return Response(
                {'success': False, 'message': '请选择要退还的资产'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        result = BatchOperationService.batch_return(
            asset_ids=asset_ids,
            return_date=return_date,
            reason=reason,
            user=request.user
        )
        
        if result['success']:
            return Response(result)
        return Response(result, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def batch_transfer(self, request):
        """
        Batch transfer assets - 批量调拨
        
        Request body:
        {
            "asset_ids": [1, 2, 3],
            "to_department": 1,
            "to_user": 1,
            "to_location": 1,
            "transfer_date": "2024-01-15",
            "reason": "调拨原因"
        }
        """
        asset_ids = request.data.get('asset_ids', [])
        to_department = request.data.get('to_department')
        to_user = request.data.get('to_user')
        to_location = request.data.get('to_location')
        transfer_date = request.data.get('transfer_date', timezone.now().date().isoformat())
        reason = request.data.get('reason', '')
        
        if not asset_ids:
            return Response(
                {'success': False, 'message': '请选择要调拨的资产'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not any([to_department, to_user, to_location]):
            return Response(
                {'success': False, 'message': '请至少选择一个调拨目标（部门、人员或位置）'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get company from request body (POST) or query params (GET)
        # Frontend interceptor adds company to request.data for POST requests
        company_id = request.data.get('company') or request.query_params.get('company')
        
        result = BatchOperationService.batch_transfer(
            asset_ids=asset_ids,
            to_department_id=to_department,
            to_user_id=to_user,
            to_location_id=to_location,
            transfer_date=transfer_date,
            reason=reason,
            user=request.user,
            company_id=company_id
        )
        
        if result['success']:
            return Response(result)
        return Response(result, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def batch_delete(self, request):
        """
        Batch soft delete assets - 批量删除
        
        Request body:
        {
            "asset_ids": [1, 2, 3]
        }
        """
        asset_ids = request.data.get('asset_ids', [])
        
        if not asset_ids:
            return Response(
                {'success': False, 'message': '请选择要删除的资产'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        result = BatchOperationService.batch_delete(
            asset_ids=asset_ids,
            user=request.user
        )
        
        if result['success']:
            return Response(result)
        return Response(result, status=status.HTTP_400_BAD_REQUEST)


class AssetOperationViewSet(viewsets.ReadOnlyModelViewSet):
    """资产操作记录视图集（只读）"""
    
    queryset = AssetOperation.objects.select_related('asset', 'operator').all()
    serializer_class = AssetOperationSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['asset', 'operation_type', 'operator']
    search_fields = ['description', 'operation_no']
    ordering = ['-created_at']


class AssetReceiveViewSet(viewsets.ModelViewSet):
    """
    资产领用视图集
    
    遵循 .cursorrules: 业务逻辑委托给 ReceiveService
    """
    
    queryset = AssetReceive.objects.select_related(
        'company', 'receive_user', 'receive_department', 'created_by'
    ).prefetch_related('items').all()
    serializer_class = AssetReceiveSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['company', 'status', 'receive_user', 'receive_department']
    search_fields = ['receive_no', 'receive_user__nickname', 'receive_user__username', 
                     'receive_department__name', 'items__asset__name', 'items__asset__asset_code']
    ordering = ['-created_at']
    
    def perform_create(self, serializer):
        """创建领用单 - 委托给 ReceiveService"""
        import uuid
        from apps.organizations.models import Company
        
        # 自动设置公司
        company = None
        if hasattr(self.request.user, 'company') and self.request.user.company:
            company = self.request.user.company
        else:
            company = Company.objects.first()
        
        # 生成单号
        receive_no = f"LY{timezone.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:8].upper()}"
        receive = serializer.save(
            created_by=self.request.user, 
            receive_no=receive_no,
            company=company,
            status=AssetReceive.Status.COMPLETED  # 直接设置为已完成
        )
        
        # 更新所有领用资产的状态和使用人信息
        for item in receive.items.all():
            asset = item.asset
            old_status = asset.get_status_display()
            old_user = asset.using_user.display_name if asset.using_user else None
            
            # 更新资产状态
            asset.status = Asset.Status.IN_USE
            asset.using_user = receive.receive_user
            asset.using_department = receive.receive_department
            asset.save()
            
            # 记录变动
            AssetOperation.objects.create(
                asset=asset,
                operation_type=AssetOperation.OperationType.RECEIVE,
                operation_no=receive_no,
                description=f'资产领用：{receive.receive_user.display_name if receive.receive_user else "未知"} 领用',
                old_data={
                    'status': old_status,
                    'using_user': old_user,
                },
                new_data={
                    'status': asset.get_status_display(),
                    'using_user': asset.using_user.display_name if asset.using_user else None,
                },
                operator=self.request.user
            )
    
    @action(detail=True, methods=['post'])
    def return_assets(self, request, pk=None):
        """资产退还 - 委托给 ReceiveService"""
        receive = self.get_object()
        asset_ids = request.data.get('asset_ids', [])
        return_date = request.data.get('return_date', timezone.now().date())
        reason = request.data.get('reason', '')
        
        result = ReceiveService.return_assets(
            receive=receive,
            asset_ids=asset_ids,
            return_date=return_date,
            reason=reason,
            user=request.user
        )
        
        return Response({'message': '退还成功', **result})


class AssetBorrowViewSet(viewsets.ModelViewSet):
    """
    资产借用视图集
    
    遵循 .cursorrules: 业务逻辑委托给 BorrowService
    """
    
    queryset = AssetBorrow.objects.select_related(
        'company', 'borrower', 'borrow_department', 'created_by'
    ).prefetch_related('items').all()
    serializer_class = AssetBorrowSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['company', 'status', 'borrower', 'borrow_department']
    search_fields = ['borrow_no', 'borrower__nickname', 'borrower__username',
                     'borrow_department__name', 'items__asset__name', 'items__asset__asset_code']
    ordering = ['-created_at']
    
    def perform_create(self, serializer):
        """创建借用单 - 委托给 BorrowService"""
        import uuid
        from apps.organizations.models import Company
        
        # 自动设置公司
        company = None
        if hasattr(self.request.user, 'company') and self.request.user.company:
            company = self.request.user.company
        else:
            company = Company.objects.first()
        
        borrow_no = f"JY{timezone.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:8].upper()}"
        borrow = serializer.save(
            created_by=self.request.user, 
            borrow_no=borrow_no,
            company=company,
            status=AssetBorrow.Status.BORROWED
        )
        
        # 更新所有借用资产的状态
        for item in borrow.items.all():
            asset = item.asset
            old_status = asset.get_status_display()
            
            # 更新资产状态为借用中
            asset.status = Asset.Status.BORROWED
            asset.save()
            
            # 记录借用操作
            AssetOperation.objects.create(
                asset=asset,
                operation_type=AssetOperation.OperationType.BORROW,
                operation_no=borrow_no,
                description=f'资产借用：{borrow.borrower.display_name if borrow.borrower else "未知"} 借用',
                old_data={'status': old_status},
                new_data={'status': asset.get_status_display()},
                operator=self.request.user
            )
    
    @action(detail=True, methods=['post'])
    def return_assets(self, request, pk=None):
        """资产归还 - 委托给 BorrowService"""
        borrow = self.get_object()
        asset_ids = request.data.get('asset_ids', [])
        item_ids = request.data.get('item_ids', [])
        return_date = request.data.get('return_date', timezone.now().date())
        condition = request.data.get('condition', 'good')
        remark = request.data.get('remark', '')
        
        # 如果没有 asset_ids，使用 item_ids
        if not asset_ids and item_ids:
            items = borrow.items.filter(id__in=item_ids)
            asset_ids = [item.asset_id for item in items]
        
        if not asset_ids:
            return Response({'error': '请指定要归还的资产'}, status=400)
        
        result = BorrowService.return_assets(
            borrow=borrow,
            asset_ids=asset_ids,
            return_date=return_date,
            condition=condition,
            remark=remark,
            user=request.user
        )
        
        return Response({'message': '归还成功', **result})
    
    @action(detail=False, methods=['get'])
    def pending_returns(self, request):
        """获取待归还清单 - 委托给 BorrowService"""
        filter_type = request.query_params.get('filter_type', 'all')
        results = BorrowService.get_pending_returns(
            queryset=self.queryset,
            filter_type=filter_type
        )
        return Response({
            'count': len(results),
            'results': results
        })
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """获取借用统计信息 - 委托给 BorrowService"""
        stats = BorrowService.get_statistics(queryset=self.queryset)
        return Response(stats)


class AssetTransferViewSet(viewsets.ModelViewSet):
    """
    资产调拨视图集
    
    遵循 .cursorrules: 业务逻辑委托给 TransferService
    """
    
    queryset = AssetTransfer.objects.select_related(
        'company', 'from_department', 'to_department', 'to_user', 'to_location', 'created_by'
    ).prefetch_related('items').all()
    serializer_class = AssetTransferSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['company', 'status', 'from_department', 'to_department']
    search_fields = ['transfer_no', 'from_department__name', 'to_department__name',
                     'to_user__nickname', 'to_user__username', 'items__asset__name', 'items__asset__asset_code']
    ordering = ['-created_at']
    
    def perform_create(self, serializer):
        """创建调拨单 - 委托给 TransferService"""
        import uuid
        from apps.organizations.models import Company
        
        company = None
        if hasattr(self.request.user, 'company') and self.request.user.company:
            company = self.request.user.company
        else:
            company = Company.objects.first()
        
        transfer_no = f"DB{timezone.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:8].upper()}"
        transfer = serializer.save(
            created_by=self.request.user, 
            transfer_no=transfer_no,
            company=company,
            status=AssetTransfer.Status.COMPLETED
        )
        
        # 更新所有调拨资产的信息并记录变动
        for item in transfer.items.all():
            asset = item.asset
            
            # 记录原始数据
            old_data = {
                'using_user': asset.using_user.display_name if asset.using_user else None,
                'using_department': asset.using_department.name if asset.using_department else None,
                'location': asset.location.name if asset.location else None,
            }
            
            # 构建变更描述
            changes = []
            
            # 更新使用人（如果指定）
            if transfer.to_user:
                asset.using_user = transfer.to_user
                changes.append(f'使用人变更为 {transfer.to_user.display_name}')
            
            # 更新部门（如果指定）
            if transfer.to_department:
                asset.using_department = transfer.to_department
                changes.append(f'部门变更为 {transfer.to_department.name}')
            
            # 更新位置（如果指定）
            if transfer.to_location:
                asset.location = transfer.to_location
                changes.append(f'位置变更为 {transfer.to_location.name}')
            
            asset.save()
            
            # 新数据
            new_data = {
                'using_user': asset.using_user.display_name if asset.using_user else None,
                'using_department': asset.using_department.name if asset.using_department else None,
                'location': asset.location.name if asset.location else None,
            }
            
            # 记录调拨操作
            description = f'资产调拨：{"; ".join(changes)}' if changes else '资产调拨'
            if transfer.reason:
                description += f'（原因：{transfer.reason}）'
            
            AssetOperation.objects.create(
                asset=asset,
                operation_type=AssetOperation.OperationType.TRANSFER,
                operation_no=transfer_no,
                description=description,
                old_data=old_data,
                new_data=new_data,
                operator=self.request.user
            )


class AssetDisposalViewSet(viewsets.ModelViewSet):
    """
    资产处置视图集
    
    遵循 .cursorrules: 业务逻辑委托给 DisposalService
    """
    
    queryset = AssetDisposal.objects.select_related(
        'company', 'created_by'
    ).prefetch_related('items').all()
    serializer_class = AssetDisposalSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['company', 'status', 'disposal_method']
    search_fields = ['disposal_no', 'reason', 'items__asset__name', 'items__asset__asset_code']
    ordering = ['-created_at']
    
    def perform_create(self, serializer):
        """创建处置单 - 委托给 DisposalService"""
        import uuid
        from apps.organizations.models import Company
        
        company = None
        if hasattr(self.request.user, 'company') and self.request.user.company:
            company = self.request.user.company
        else:
            company = Company.objects.first()
        
        disposal_no = f"CZ{timezone.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:8].upper()}"
        disposal = serializer.save(
            created_by=self.request.user, 
            disposal_no=disposal_no,
            company=company,
            status=AssetDisposal.Status.COMPLETED
        )
        
        # 更新所有处置资产的状态并记录变动
        for item in disposal.items.all():
            asset = item.asset
            old_status = asset.get_status_display()
            
            # 更新资产状态为已处置
            asset.status = Asset.Status.DISPOSED
            asset.save()
            
            # 记录处置操作
            AssetOperation.objects.create(
                asset=asset,
                operation_type=AssetOperation.OperationType.DISPOSE,
                operation_no=disposal_no,
                description=f'资产处置：{disposal.get_disposal_method_display()} - {disposal.reason or "无说明"}',
                old_data={'status': old_status},
                new_data={'status': asset.get_status_display()},
                operator=self.request.user
            )


class AssetMaintenanceViewSet(viewsets.ModelViewSet):
    """
    资产维保视图集
    
    遵循 .cursorrules: 业务逻辑委托给 MaintenanceService
    """
    
    queryset = AssetMaintenance.objects.select_related('asset', 'created_by').all()
    serializer_class = AssetMaintenanceSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['asset', 'maintenance_type', 'status']
    search_fields = ['maintenance_no', 'description', 'asset__name', 'asset__asset_code']
    ordering = ['-created_at']
    
    def perform_create(self, serializer):
        """创建维保单 - 委托给 MaintenanceService"""
        import uuid
        maintenance_no = f"WB{timezone.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:8].upper()}"
        maintenance = serializer.save(created_by=self.request.user, maintenance_no=maintenance_no)
        
        # 更新资产状态为维修中并记录变动
        asset = maintenance.asset
        if asset:
            old_status = asset.get_status_display()
            asset.status = Asset.Status.MAINTENANCE
            asset.save()
            
            # 记录维保操作
            AssetOperation.objects.create(
                asset=asset,
                operation_type=AssetOperation.OperationType.MAINTENANCE,
                operation_no=maintenance_no,
                description=f'资产维保：{maintenance.get_maintenance_type_display()} - {maintenance.description or "无说明"}',
                old_data={'status': old_status},
                new_data={'status': asset.get_status_display()},
                operator=self.request.user
            )
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """完成维保 - 委托给 MaintenanceService"""
        maintenance = self.get_object()
        MaintenanceService.complete_maintenance(
            maintenance=maintenance,
            user=request.user
        )
        return Response({'message': '维保已完成'})


class AssetLabelViewSet(viewsets.ModelViewSet):
    """资产标签模板视图集"""
    
    queryset = AssetLabel.objects.all()
    serializer_class = AssetLabelSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['company', 'is_default', 'is_active']
