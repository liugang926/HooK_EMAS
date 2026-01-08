"""
资产服务 - Asset Service

处理资产相关的业务逻辑:
- 资产创建/编辑
- 资产统计
- 资产软删除/恢复
"""
from django.db import transaction
from django.db.models import Sum, Count
from django.utils import timezone
from typing import Dict, Any, Optional

from .base import BaseService


class AssetService(BaseService):
    """资产业务服务"""
    
    @classmethod
    @transaction.atomic
    def create_asset(cls, validated_data: Dict, user) -> 'Asset':
        """
        创建资产并记录变动
        
        遵循 .cursorrules: 涉及多表更新的操作必须包裹在 @transaction.atomic 装饰器中
        
        Args:
            validated_data: 已验证的资产数据
            user: 创建用户
            
        Returns:
            创建的资产对象
        """
        from apps.assets.models import Asset, AssetOperation
        
        # 获取公司
        company = cls.get_user_company(user)
        if not company:
            raise ValueError("无法找到公司信息，请先创建公司")
        
        # 自动生成资产编码(如果未提供)
        asset_code = validated_data.get('asset_code', '')
        if not asset_code or asset_code.strip() == '':
            asset_code = cls.generate_asset_code(company)
        
        # 创建资产
        validated_data['created_by'] = user
        validated_data['company'] = company
        validated_data['asset_code'] = asset_code
        
        asset = Asset.objects.create(**validated_data)
        
        # 记录资产录入操作
        cls._record_create_operation(asset, user)
        
        return asset
    
    @classmethod
    def generate_asset_code(cls, company) -> str:
        """
        Generate asset code based on company's code rule configuration.
        
        Uses the CodeRule model to generate codes according to the configured pattern:
        - prefix: Code prefix (e.g., 'ZC')
        - date_format: Date format (YYYY, YYYYMM, YYYYMMDD)
        - serial_length: Length of serial number
        - separator: Separator between parts
        - reset_cycle: When to reset serial (daily, monthly, yearly, never)
        
        Formula: {prefix}{separator}{date}{separator}{serial}
        Example: ZC20260108001
        
        Args:
            company: Company object
            
        Returns:
            Generated asset code string
        """
        from apps.system.models import CodeRule
        from django.db.models import F
        
        try:
            # Get or create code rule for this company
            rule, created = CodeRule.objects.get_or_create(
                company=company,
                code='asset_code',
                defaults={
                    'name': '资产编号规则',
                    'prefix': 'ZC',
                    'date_format': 'YYYYMMDD',
                    'serial_length': 4,
                    'separator': '',
                    'reset_cycle': 'daily',
                    'current_serial': 0,
                    'is_active': True
                }
            )
            
            now = timezone.now()
            today = now.date()
            
            # Check if we need to reset the serial number
            should_reset = False
            if rule.reset_cycle == 'daily':
                if rule.last_reset_date != today:
                    should_reset = True
            elif rule.reset_cycle == 'monthly':
                if rule.last_reset_date is None or \
                   rule.last_reset_date.year != today.year or \
                   rule.last_reset_date.month != today.month:
                    should_reset = True
            elif rule.reset_cycle == 'yearly':
                if rule.last_reset_date is None or rule.last_reset_date.year != today.year:
                    should_reset = True
            
            if should_reset:
                rule.current_serial = 0
                rule.last_reset_date = today
            
            # Increment serial number
            rule.current_serial = F('current_serial') + 1
            rule.save()
            rule.refresh_from_db()
            
            # Build the date string
            date_str = ''
            if rule.date_format == 'YYYY':
                date_str = now.strftime('%Y')
            elif rule.date_format == 'YYYYMM':
                date_str = now.strftime('%Y%m')
            elif rule.date_format == 'YYYYMMDD':
                date_str = now.strftime('%Y%m%d')
            
            # Build the serial number string
            serial_str = str(rule.current_serial).zfill(rule.serial_length)
            
            # Combine parts
            sep = rule.separator or ''
            prefix = rule.prefix or ''
            
            asset_code = f"{prefix}{sep}{date_str}{sep}{serial_str}"
            
            return asset_code
            
        except Exception as e:
            # Fallback to old method if anything fails
            import logging
            logging.warning(f"Failed to generate asset code using rule: {e}")
            return cls.generate_order_no('ZC')
    
    @classmethod
    @transaction.atomic
    def update_asset(cls, asset, validated_data: Dict, user) -> 'Asset':
        """
        更新资产并记录变动
        
        Args:
            asset: 资产对象
            validated_data: 已验证的更新数据
            user: 操作用户
            
        Returns:
            更新后的资产对象
        """
        from apps.assets.models import AssetOperation
        
        # 记录更新前数据
        old_data = cls._build_asset_snapshot(asset)
        
        # 更新资产
        for key, value in validated_data.items():
            setattr(asset, key, value)
        asset.save()
        
        # 记录更新后数据
        new_data = cls._build_asset_snapshot(asset)
        
        # 比较变化并记录
        changes = cls._compare_changes(old_data, new_data)
        if changes:
            AssetOperation.objects.create(
                asset=asset,
                operation_type=AssetOperation.OperationType.UPDATE,
                description=f'资产编辑：{", ".join(changes[:3])}{"..." if len(changes) > 3 else ""}',
                old_data=old_data,
                new_data=new_data,
                operator=user
            )
        
        return asset
    
    @classmethod
    def get_statistics(cls, company_id: Optional[int] = None) -> Dict:
        """
        获取资产统计数据
        
        Args:
            company_id: 公司ID (可选)
            
        Returns:
            统计数据字典
        """
        from apps.assets.models import Asset
        
        queryset = Asset.objects.filter(is_deleted=False)
        if company_id:
            queryset = queryset.filter(company_id=company_id)
        
        # 状态统计
        status_stats = queryset.values('status').annotate(
            count=Count('id'),
            total_value=Sum('original_value')
        )
        
        # 分类统计
        category_stats = queryset.values('category__name').annotate(
            count=Count('id'),
            total_value=Sum('original_value')
        )
        
        # 部门统计
        department_stats = queryset.values('using_department__name').annotate(
            count=Count('id'),
            total_value=Sum('original_value')
        )
        
        # 总计
        totals = queryset.aggregate(
            total_count=Count('id'),
            total_value=Sum('original_value'),
            total_current_value=Sum('current_value')
        )
        
        return {
            'status_stats': list(status_stats),
            'category_stats': list(category_stats),
            'department_stats': list(department_stats),
            'totals': totals
        }
    
    @classmethod
    @transaction.atomic
    def soft_delete(cls, asset, user) -> None:
        """
        软删除资产
        
        遵循 .cursorrules: 禁止物理删除，必须实现 soft_delete 逻辑
        
        Args:
            asset: 资产对象
            user: 操作用户
        """
        asset.is_deleted = True
        asset.deleted_at = timezone.now()
        asset.save()
    
    @classmethod
    @transaction.atomic
    def restore(cls, asset_id: int) -> 'Asset':
        """
        恢复已删除资产
        
        Args:
            asset_id: 资产ID
            
        Returns:
            恢复的资产对象
        """
        from apps.assets.models import Asset
        
        asset = Asset.objects.get(pk=asset_id)
        asset.is_deleted = False
        asset.deleted_at = None
        asset.save()
        return asset
    
    @classmethod
    def _record_create_operation(cls, asset, user) -> None:
        """记录资产创建操作"""
        from apps.assets.models import AssetOperation
        
        AssetOperation.objects.create(
            asset=asset,
            operation_type=AssetOperation.OperationType.CREATE,
            description=f'资产录入：{asset.name}',
            new_data={
                'asset_code': asset.asset_code,
                'name': asset.name,
                'category': asset.category.name if asset.category else None,
                'original_value': str(asset.original_value) if asset.original_value else None,
                'status': asset.get_status_display(),
            },
            operator=user
        )
    
    @classmethod
    def _build_asset_snapshot(cls, asset) -> Dict:
        """构建资产快照数据"""
        return {
            'asset_code': asset.asset_code,
            'name': asset.name,
            'category': asset.category.name if asset.category else None,
            'brand': asset.brand,
            'model': asset.model,
            'serial_number': asset.serial_number,
            'original_value': str(asset.original_value) if asset.original_value else None,
            'status': asset.get_status_display(),
            'using_user': asset.using_user.display_name if asset.using_user else None,
            'using_department': asset.using_department.name if asset.using_department else None,
            'location': asset.location.full_name if asset.location else None,
        }
    
    @classmethod
    def _compare_changes(cls, old_data: Dict, new_data: Dict) -> list:
        """比较前后数据变化"""
        changes = []
        for key in old_data:
            if old_data.get(key) != new_data.get(key):
                changes.append(f'{key}: {old_data[key]} → {new_data[key]}')
        return changes
