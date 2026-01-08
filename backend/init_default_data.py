#!/usr/bin/env python
"""初始化默认数据"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.assets.models import AssetCategory
from apps.organizations.models import Company, Location

def init_categories():
    """初始化资产分类"""
    company = Company.objects.first()
    if not company:
        print('No company found!')
        return
    
    print(f'Company: {company.name}')
    
    # Create default categories
    categories = [
        {'name': '办公设备', 'code': '01', 'sort_order': 1, 'children': [
            ('电脑', '0101'), ('打印机', '0102'), ('复印机', '0103'), ('投影仪', '0104')
        ]},
        {'name': '电子设备', 'code': '02', 'sort_order': 2, 'children': [
            ('手机', '0201'), ('平板', '0202'), ('相机', '0203')
        ]},
        {'name': '家具', 'code': '03', 'sort_order': 3, 'children': [
            ('办公桌', '0301'), ('办公椅', '0302'), ('文件柜', '0303')
        ]},
        {'name': '交通工具', 'code': '04', 'sort_order': 4, 'children': [
            ('轿车', '0401'), ('货车', '0402')
        ]},
        {'name': '其他', 'code': '99', 'sort_order': 99, 'children': []},
    ]
    
    for cat_data in categories:
        cat, created = AssetCategory.objects.get_or_create(
            company=company,
            name=cat_data['name'],
            parent=None,
            defaults={
                'code': cat_data['code'],
                'sort_order': cat_data['sort_order'],
                'is_active': True
            }
        )
        status = 'Created' if created else 'Exists'
        print(f'{status}: {cat.name}')
        
        # Add sub-categories
        for name, code in cat_data.get('children', []):
            sub, sub_created = AssetCategory.objects.get_or_create(
                company=company, 
                name=name, 
                parent=cat,
                defaults={'code': code, 'is_active': True}
            )
            sub_status = 'Created' if sub_created else 'Exists'
            print(f'  {sub_status}: {sub.name}')


def init_locations():
    """初始化存放位置"""
    company = Company.objects.first()
    if not company:
        print('No company found!')
        return
    
    # Create default locations
    locations = [
        {'name': '总部', 'code': 'HQ', 'children': [
            ('1楼', 'HQ-1F'), ('2楼', 'HQ-2F'), ('3楼', 'HQ-3F')
        ]},
        {'name': '仓库', 'code': 'WH', 'children': [
            ('主仓库', 'WH-MAIN'), ('临时仓库', 'WH-TEMP')
        ]},
    ]
    
    for loc_data in locations:
        loc, created = Location.objects.get_or_create(
            company=company,
            name=loc_data['name'],
            parent=None,
            defaults={
                'code': loc_data['code'],
                'is_active': True
            }
        )
        status = 'Created' if created else 'Exists'
        print(f'{status}: {loc.name}')
        
        # Add sub-locations
        for name, code in loc_data.get('children', []):
            sub, sub_created = Location.objects.get_or_create(
                company=company, 
                name=name, 
                parent=loc,
                defaults={'code': code, 'is_active': True}
            )
            sub_status = 'Created' if sub_created else 'Exists'
            print(f'  {sub_status}: {sub.name}')


if __name__ == '__main__':
    print('=== Initializing Asset Categories ===')
    init_categories()
    print('\n=== Initializing Locations ===')
    init_locations()
    print('\n=== Done! ===')
