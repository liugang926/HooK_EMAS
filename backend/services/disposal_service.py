"""
处置服务 - Disposal Service

处理资产处置相关的业务逻辑:
- 处置单创建
- 资产状态更新
"""
from django.db import transaction
from typing import Dict, List

from .base import BaseService


class DisposalService(BaseService):
    """资产处置业务服务"""
    
    @classmethod
    @transaction.atomic
    def create_disposal(cls, disposal_data: Dict, items_data: List[Dict], user) -> 'AssetDisposal':
        """
        创建处置单并更新资产状态
        
        Args:
            disposal_data: 处置单主表数据
            items_data: 处置明细数据列表
            user: 操作用户
            
        Returns:
            创建的处置单对象
        """
        from apps.assets.models import Asset, AssetDisposal, AssetDisposalItem, AssetOperation
        
        company = cls.get_user_company(user)
        disposal_no = cls.generate_order_no('CZ')
        
        # 创建处置单
        disposal = AssetDisposal.objects.create(
            **disposal_data,
            created_by=user,
            disposal_no=disposal_no,
            company=company,
            status=AssetDisposal.Status.COMPLETED
        )
        
        # 创建明细并更新资产
        for item_data in items_data:
            asset_id = item_data.get('asset') or item_data.get('asset_id')
            asset = Asset.objects.select_for_update().get(pk=asset_id)
            
            AssetDisposalItem.objects.create(
                disposal=disposal,
                asset=asset,
                **{k: v for k, v in item_data.items() if k not in ['asset', 'asset_id']}
            )
            
            cls._update_asset_on_disposal(asset, disposal, disposal_no, user)
        
        return disposal
    
    @classmethod
    def _update_asset_on_disposal(cls, asset, disposal, disposal_no: str, user) -> None:
        """处置时更新资产状态"""
        from apps.assets.models import Asset, AssetOperation
        
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
            operator=user
        )
