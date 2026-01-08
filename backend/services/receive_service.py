"""
领用服务 - Receive Service

处理资产领用相关的业务逻辑:
- 领用单创建
- 资产退还
"""
from django.db import transaction
from django.utils import timezone
from typing import Dict, List, Optional

from .base import BaseService


class ReceiveService(BaseService):
    """资产领用业务服务"""
    
    @classmethod
    @transaction.atomic
    def create_receive(cls, receive_data: Dict, items_data: List[Dict], user) -> 'AssetReceive':
        """
        创建领用单并更新资产状态
        
        遵循 .cursorrules: 涉及多表更新的操作必须包裹在 @transaction.atomic 装饰器中
        
        Args:
            receive_data: 领用单主表数据
            items_data: 领用明细数据列表
            user: 操作用户
            
        Returns:
            创建的领用单对象
        """
        from apps.assets.models import Asset, AssetReceive, AssetReceiveItem, AssetOperation
        
        # 获取公司
        company = cls.get_user_company(user)
        
        # 生成单号
        receive_no = cls.generate_order_no('LY')
        
        # 创建领用单
        receive = AssetReceive.objects.create(
            **receive_data,
            created_by=user,
            receive_no=receive_no,
            company=company,
            status=AssetReceive.Status.COMPLETED
        )
        
        # 创建明细并更新资产
        for item_data in items_data:
            asset_id = item_data.get('asset') or item_data.get('asset_id')
            asset = Asset.objects.select_for_update().get(pk=asset_id)
            
            # 创建明细
            AssetReceiveItem.objects.create(
                receive=receive,
                asset=asset,
                **{k: v for k, v in item_data.items() if k not in ['asset', 'asset_id']}
            )
            
            # 更新资产状态
            cls._update_asset_on_receive(asset, receive, receive_no, user)
        
        return receive
    
    @classmethod
    @transaction.atomic
    def return_assets(cls, receive, asset_ids: List[int], return_date, reason: str, user) -> Dict:
        """
        资产退还
        
        Args:
            receive: 领用单对象
            asset_ids: 要退还的资产ID列表
            return_date: 退还日期
            reason: 退还原因
            user: 操作用户
            
        Returns:
            退还结果 {'return_no': str, 'returned_count': int}
        """
        from apps.assets.models import Asset, AssetOperation
        
        return_no = cls.generate_order_no('TH')
        returned_count = 0
        
        for item in receive.items.filter(asset_id__in=asset_ids, is_returned=False):
            asset = item.asset
            old_status = asset.get_status_display()
            old_user = asset.using_user.display_name if asset.using_user else None
            
            # 更新资产状态
            asset.status = Asset.Status.IDLE
            asset.using_user = None
            asset.save()
            
            # 更新领用明细
            item.is_returned = True
            item.return_date = return_date
            item.save()
            
            # 记录退还操作
            AssetOperation.objects.create(
                asset=asset,
                operation_type=AssetOperation.OperationType.RETURN,
                operation_no=return_no,
                description=f'资产退还：{reason}' if reason else '资产退还',
                old_data={
                    'status': old_status,
                    'using_user': old_user,
                },
                new_data={
                    'status': asset.get_status_display(),
                    'using_user': None,
                },
                operator=user
            )
            returned_count += 1
        
        return {'return_no': return_no, 'returned_count': returned_count}
    
    @classmethod
    def _update_asset_on_receive(cls, asset, receive, receive_no: str, user) -> None:
        """领用时更新资产状态"""
        from apps.assets.models import Asset, AssetOperation
        
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
            operator=user
        )
