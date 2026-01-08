"""
调拨服务 - Transfer Service

处理资产调拨相关的业务逻辑:
- 调拨单创建
- 资产信息更新
"""
from django.db import transaction
from typing import Dict, List

from .base import BaseService


class TransferService(BaseService):
    """资产调拨业务服务"""
    
    @classmethod
    @transaction.atomic
    def create_transfer(cls, transfer_data: Dict, items_data: List[Dict], user) -> 'AssetTransfer':
        """
        创建调拨单并更新资产信息
        
        Args:
            transfer_data: 调拨单主表数据
            items_data: 调拨明细数据列表
            user: 操作用户
            
        Returns:
            创建的调拨单对象
        """
        from apps.assets.models import Asset, AssetTransfer, AssetTransferItem, AssetOperation
        
        company = cls.get_user_company(user)
        transfer_no = cls.generate_order_no('DB')
        
        # 创建调拨单
        transfer = AssetTransfer.objects.create(
            **transfer_data,
            created_by=user,
            transfer_no=transfer_no,
            company=company,
            status=AssetTransfer.Status.COMPLETED
        )
        
        # 创建明细并更新资产
        for item_data in items_data:
            asset_id = item_data.get('asset') or item_data.get('asset_id')
            asset = Asset.objects.select_for_update().get(pk=asset_id)
            
            # 创建调拨明细（包含原资产信息）
            AssetTransferItem.objects.create(
                transfer=transfer,
                asset=asset,
                original_using_user=asset.using_user,
                original_using_department=asset.using_department,
                original_location=asset.location,
                **{k: v for k, v in item_data.items() if k not in ['asset', 'asset_id']}
            )
            
            # 更新资产信息
            cls._update_asset_on_transfer(asset, transfer, transfer_no, user)
        
        return transfer
    
    @classmethod
    def _update_asset_on_transfer(cls, asset, transfer, transfer_no: str, user) -> None:
        """调拨时更新资产信息"""
        from apps.assets.models import AssetOperation
        
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
            operator=user
        )
