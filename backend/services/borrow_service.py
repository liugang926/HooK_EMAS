"""
借用服务 - Borrow Service

处理资产借用相关的业务逻辑:
- 借用单创建
- 资产归还
- 待归还清单
- 借用统计
"""
from django.db import transaction
from django.db.models import Count
from django.utils import timezone
from datetime import date, timedelta
from typing import Dict, List, Optional

from .base import BaseService


class BorrowService(BaseService):
    """资产借用业务服务"""
    
    @classmethod
    @transaction.atomic
    def create_borrow(cls, borrow_data: Dict, items_data: List[Dict], user) -> 'AssetBorrow':
        """
        创建借用单并更新资产状态
        
        Args:
            borrow_data: 借用单主表数据
            items_data: 借用明细数据列表
            user: 操作用户
            
        Returns:
            创建的借用单对象
        """
        from apps.assets.models import Asset, AssetBorrow, AssetBorrowItem, AssetOperation
        
        company = cls.get_user_company(user)
        borrow_no = cls.generate_order_no('JY')
        
        # 创建借用单
        borrow = AssetBorrow.objects.create(
            **borrow_data,
            created_by=user,
            borrow_no=borrow_no,
            company=company,
            status=AssetBorrow.Status.BORROWED
        )
        
        # 创建明细并更新资产
        for item_data in items_data:
            asset_id = item_data.get('asset') or item_data.get('asset_id')
            asset = Asset.objects.select_for_update().get(pk=asset_id)
            
            AssetBorrowItem.objects.create(
                borrow=borrow,
                asset=asset,
                **{k: v for k, v in item_data.items() if k not in ['asset', 'asset_id']}
            )
            
            cls._update_asset_on_borrow(asset, borrow, borrow_no, user)
        
        return borrow
    
    @classmethod
    @transaction.atomic
    def return_assets(cls, borrow, asset_ids: List[int], return_date, 
                      condition: str, remark: str, user) -> Dict:
        """
        资产归还
        
        Args:
            borrow: 借用单对象
            asset_ids: 要归还的资产ID列表
            return_date: 归还日期
            condition: 归还状况
            remark: 备注
            user: 操作用户
            
        Returns:
            归还结果
        """
        from apps.assets.models import Asset, AssetOperation
        
        return_no = cls.generate_order_no('GH')
        returned_count = 0
        
        items = borrow.items.filter(asset_id__in=asset_ids, is_returned=False)
        
        for item in items:
            asset = item.asset
            old_status = asset.get_status_display()
            
            item.is_returned = True
            item.return_date = return_date if isinstance(return_date, str) else return_date
            item.remark = remark
            item.save()
            
            # 更新资产状态
            asset.status = Asset.Status.IDLE
            asset.save()
            
            # 记录归还操作
            AssetOperation.objects.create(
                asset=asset,
                operation_type=AssetOperation.OperationType.GIVE_BACK,
                operation_no=return_no,
                description=f'资产归还：{remark}（状况：{condition}）' if remark else f'资产归还（状况：{condition}）',
                old_data={
                    'status': old_status, 
                    'borrower': borrow.borrower.display_name if borrow.borrower else None
                },
                new_data={'status': asset.get_status_display(), 'condition': condition},
                operator=user
            )
            returned_count += 1
        
        # 检查是否全部归还
        if not borrow.items.filter(is_returned=False).exists():
            borrow.status = borrow.Status.RETURNED
            borrow.actual_return_date = return_date if isinstance(return_date, str) else return_date
            borrow.save()
        
        return {'return_no': return_no, 'returned_count': returned_count}
    
    @classmethod
    def get_pending_returns(cls, queryset, filter_type: str = 'all') -> List[Dict]:
        """
        获取待归还清单
        
        Args:
            queryset: 借用单查询集
            filter_type: 过滤类型 (all/overdue/upcoming)
            
        Returns:
            待归还清单
        """
        from apps.assets.models import AssetBorrow
        
        today = date.today()
        
        # 筛选有未归还资产的借用单
        queryset = queryset.filter(
            status__in=[AssetBorrow.Status.BORROWED],
            items__is_returned=False
        ).distinct()
        
        if filter_type == 'overdue':
            queryset = queryset.filter(expected_return_date__lt=today)
        elif filter_type == 'upcoming':
            queryset = queryset.filter(
                expected_return_date__gte=today,
                expected_return_date__lte=today + timedelta(days=7)
            )
        
        queryset = queryset.order_by('expected_return_date')
        
        results = []
        for borrow in queryset:
            unreturned_items = borrow.items.filter(is_returned=False)
            days_remaining = None
            is_overdue = False
            
            if borrow.expected_return_date:
                days_remaining = (borrow.expected_return_date - today).days
                is_overdue = days_remaining < 0
            
            results.append({
                'id': borrow.id,
                'borrow_no': borrow.borrow_no,
                'borrower': borrow.borrower.display_name if borrow.borrower else None,
                'borrower_id': borrow.borrower_id,
                'borrow_department': borrow.borrow_department.name if borrow.borrow_department else None,
                'borrow_date': borrow.borrow_date,
                'expected_return_date': borrow.expected_return_date,
                'days_remaining': days_remaining,
                'is_overdue': is_overdue,
                'unreturned_count': unreturned_items.count(),
                'unreturned_items': [
                    {
                        'id': item.id,
                        'asset_id': item.asset_id,
                        'asset_name': item.asset.name,
                        'asset_code': item.asset.asset_code
                    }
                    for item in unreturned_items
                ],
                'reason': borrow.reason
            })
        
        return results
    
    @classmethod
    def get_statistics(cls, queryset) -> Dict:
        """
        获取借用统计信息
        
        Args:
            queryset: 借用单查询集
            
        Returns:
            统计数据
        """
        from apps.assets.models import AssetBorrow, AssetBorrowItem
        
        today = date.today()
        this_month_start = today.replace(day=1)
        
        # 总借用数
        total_borrows = queryset.count()
        
        # 借用中的数量
        borrowing_count = queryset.filter(
            status__in=[AssetBorrow.Status.BORROWED],
            items__is_returned=False
        ).distinct().count()
        
        # 已超期的借用数
        overdue_count = queryset.filter(
            status__in=[AssetBorrow.Status.BORROWED],
            items__is_returned=False,
            expected_return_date__lt=today
        ).distinct().count()
        
        # 即将到期的借用数（7天内）
        upcoming_count = queryset.filter(
            status__in=[AssetBorrow.Status.BORROWED],
            items__is_returned=False,
            expected_return_date__gte=today,
            expected_return_date__lte=today + timedelta(days=7)
        ).distinct().count()
        
        # 本月借用数
        this_month_count = queryset.filter(borrow_date__gte=this_month_start).count()
        
        # 本月归还数
        this_month_returned = AssetBorrowItem.objects.filter(
            return_date__gte=this_month_start,
            is_returned=True
        ).count()
        
        # 按借用人统计（Top 10）
        borrower_stats = queryset.filter(
            status__in=[AssetBorrow.Status.BORROWED],
            items__is_returned=False
        ).values(
            'borrower__nickname', 'borrower_id'
        ).annotate(
            count=Count('id', distinct=True)
        ).order_by('-count')[:10]
        
        return {
            'total_borrows': total_borrows,
            'borrowing_count': borrowing_count,
            'overdue_count': overdue_count,
            'upcoming_count': upcoming_count,
            'this_month_count': this_month_count,
            'this_month_returned': this_month_returned,
            'borrower_stats': list(borrower_stats)
        }
    
    @classmethod
    def _update_asset_on_borrow(cls, asset, borrow, borrow_no: str, user) -> None:
        """借用时更新资产状态"""
        from apps.assets.models import Asset, AssetOperation
        
        old_status = asset.get_status_display()
        
        asset.status = Asset.Status.BORROWED
        asset.save()
        
        AssetOperation.objects.create(
            asset=asset,
            operation_type=AssetOperation.OperationType.BORROW,
            operation_no=borrow_no,
            description=f'资产借用：{borrow.borrower.display_name if borrow.borrower else "未知"} 借用',
            old_data={'status': old_status},
            new_data={'status': asset.get_status_display()},
            operator=user
        )
