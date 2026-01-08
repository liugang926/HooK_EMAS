"""
维保服务 - Maintenance Service

处理资产维保相关的业务逻辑:
- 维保单创建
- 维保完成
- 资产状态更新
"""
from django.db import transaction
from django.utils import timezone
from typing import Dict

from .base import BaseService


class MaintenanceService(BaseService):
    """资产维保业务服务"""
    
    @classmethod
    @transaction.atomic
    def create_maintenance(cls, maintenance_data: Dict, user) -> 'AssetMaintenance':
        """
        创建维保单并更新资产状态
        
        Args:
            maintenance_data: 维保单数据
            user: 操作用户
            
        Returns:
            创建的维保单对象
        """
        from apps.assets.models import AssetMaintenance, AssetOperation
        
        maintenance_no = cls.generate_order_no('WB')
        
        # 创建维保单
        maintenance = AssetMaintenance.objects.create(
            **maintenance_data,
            created_by=user,
            maintenance_no=maintenance_no
        )
        
        # 更新资产状态
        asset = maintenance.asset
        if asset:
            cls._update_asset_on_maintenance_start(asset, maintenance, maintenance_no, user)
        
        return maintenance
    
    @classmethod
    @transaction.atomic
    def complete_maintenance(cls, maintenance, user) -> 'AssetMaintenance':
        """
        完成维保
        
        Args:
            maintenance: 维保单对象
            user: 操作用户
            
        Returns:
            更新后的维保单对象
        """
        from apps.assets.models import Asset, AssetMaintenance, AssetOperation
        
        # 更新维保单状态
        maintenance.status = AssetMaintenance.Status.COMPLETED
        maintenance.actual_end_date = timezone.now().date()
        maintenance.save()
        
        # 更新资产状态
        asset = maintenance.asset
        if asset:
            old_status = asset.get_status_display()
            asset.status = Asset.Status.IDLE
            asset.save()
            
            # 记录维保完成
            AssetOperation.objects.create(
                asset=asset,
                operation_type=AssetOperation.OperationType.MAINTENANCE,
                operation_no=maintenance.maintenance_no,
                description=f'维保完成：{maintenance.get_maintenance_type_display()}',
                old_data={'status': old_status},
                new_data={'status': asset.get_status_display()},
                operator=user
            )
        
        return maintenance
    
    @classmethod
    def _update_asset_on_maintenance_start(cls, asset, maintenance, maintenance_no: str, user) -> None:
        """开始维保时更新资产状态"""
        from apps.assets.models import Asset, AssetOperation
        
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
            operator=user
        )
