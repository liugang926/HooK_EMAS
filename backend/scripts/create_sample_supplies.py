# -*- coding: utf-8 -*-
"""
Sample data script for Office Supplies module
Run with: python manage.py shell < scripts/create_sample_supplies.py
Or: docker exec asset_backend python scripts/create_sample_supplies.py
"""
import os
import sys
import django

# Setup Django environment
sys.path.insert(0, '/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.consumables.models import ConsumableCategory, Consumable
from apps.organizations.models import Company


def create_sample_data():
    # Get the first company
    company = Company.objects.first()
    if not company:
        print('No company found! Please create a company first.')
        return
    
    print(f'Using company: {company.name} (ID: {company.id})')
    
    # Create categories
    categories_data = [
        {'name': '纸张类', 'code': 'ZZ', 'description': '各类打印纸、复印纸等', 'sort_order': 1},
        {'name': '书写工具', 'code': 'SX', 'description': '笔、铅笔、记号笔等', 'sort_order': 2},
        {'name': '文件管理', 'code': 'WJ', 'description': '文件夹、档案盒、资料册等', 'sort_order': 3},
        {'name': '办公设备耗材', 'code': 'SB', 'description': '墨盒、硒鼓、色带等', 'sort_order': 4},
        {'name': '桌面文具', 'code': 'ZM', 'description': '订书机、胶带、剪刀等', 'sort_order': 5},
        {'name': '清洁用品', 'code': 'QJ', 'description': '纸巾、垃圾袋等', 'sort_order': 6},
    ]
    
    print('\n--- Creating Categories ---')
    category_map = {}
    for cat_data in categories_data:
        cat, created = ConsumableCategory.objects.get_or_create(
            company=company,
            code=cat_data['code'],
            defaults={
                'name': cat_data['name'],
                'description': cat_data['description'],
                'sort_order': cat_data['sort_order'],
                'is_active': True
            }
        )
        category_map[cat_data['code']] = cat
        status = 'Created' if created else 'Exists'
        print(f'  {status}: {cat.name} ({cat.code})')
    
    # Create supplies
    supplies_data = [
        {'code': 'BG-0001', 'name': 'A4复印纸', 'category': 'ZZ', 'brand': '得力', 'model': '70g 500张/包', 'unit': '包', 'price': 25.00, 'min_stock': 50, 'max_stock': 500},
        {'code': 'BG-0002', 'name': 'A3复印纸', 'category': 'ZZ', 'brand': '得力', 'model': '80g 500张/包', 'unit': '包', 'price': 45.00, 'min_stock': 20, 'max_stock': 200},
        {'code': 'BG-0003', 'name': '中性笔（黑）', 'category': 'SX', 'brand': '晨光', 'model': '0.5mm', 'unit': '支', 'price': 2.50, 'min_stock': 100, 'max_stock': 1000},
        {'code': 'BG-0004', 'name': '中性笔（蓝）', 'category': 'SX', 'brand': '晨光', 'model': '0.5mm', 'unit': '支', 'price': 2.50, 'min_stock': 50, 'max_stock': 500},
        {'code': 'BG-0005', 'name': '铅笔', 'category': 'SX', 'brand': '中华', 'model': '2B', 'unit': '支', 'price': 1.00, 'min_stock': 50, 'max_stock': 300},
        {'code': 'BG-0006', 'name': 'A4文件夹', 'category': 'WJ', 'brand': '得力', 'model': '双强力夹', 'unit': '个', 'price': 8.00, 'min_stock': 30, 'max_stock': 200},
        {'code': 'BG-0007', 'name': '档案盒', 'category': 'WJ', 'brand': '得力', 'model': '55mm', 'unit': '个', 'price': 12.00, 'min_stock': 20, 'max_stock': 100},
        {'code': 'BG-0008', 'name': '资料册', 'category': 'WJ', 'brand': '得力', 'model': '60页', 'unit': '本', 'price': 15.00, 'min_stock': 20, 'max_stock': 100},
        {'code': 'BG-0009', 'name': 'HP墨盒（黑）', 'category': 'SB', 'brand': 'HP', 'model': '680', 'unit': '个', 'price': 89.00, 'min_stock': 5, 'max_stock': 30},
        {'code': 'BG-0010', 'name': 'HP墨盒（彩）', 'category': 'SB', 'brand': 'HP', 'model': '680', 'unit': '个', 'price': 99.00, 'min_stock': 5, 'max_stock': 30},
        {'code': 'BG-0011', 'name': '订书机', 'category': 'ZM', 'brand': '得力', 'model': '12号', 'unit': '台', 'price': 18.00, 'min_stock': 10, 'max_stock': 50},
        {'code': 'BG-0012', 'name': '订书钉', 'category': 'ZM', 'brand': '得力', 'model': '12号 1000枚', 'unit': '盒', 'price': 3.00, 'min_stock': 30, 'max_stock': 200},
        {'code': 'BG-0013', 'name': '透明胶带', 'category': 'ZM', 'brand': '得力', 'model': '48mm*100m', 'unit': '卷', 'price': 5.00, 'min_stock': 20, 'max_stock': 100},
        {'code': 'BG-0014', 'name': '抽纸', 'category': 'QJ', 'brand': '维达', 'model': '200抽', 'unit': '包', 'price': 6.00, 'min_stock': 50, 'max_stock': 300},
        {'code': 'BG-0015', 'name': '垃圾袋', 'category': 'QJ', 'brand': '妙洁', 'model': '45*50cm 30只', 'unit': '卷', 'price': 8.00, 'min_stock': 30, 'max_stock': 150},
    ]
    
    print('\n--- Creating Office Supplies ---')
    for supply_data in supplies_data:
        cat = category_map.get(supply_data['category'])
        supply, created = Consumable.objects.get_or_create(
            company=company,
            code=supply_data['code'],
            defaults={
                'name': supply_data['name'],
                'category': cat,
                'brand': supply_data['brand'],
                'model': supply_data['model'],
                'unit': supply_data['unit'],
                'price': supply_data['price'],
                'min_stock': supply_data['min_stock'],
                'max_stock': supply_data['max_stock'],
                'is_active': True
            }
        )
        status = 'Created' if created else 'Exists'
        print(f'  {status}: {supply.code} - {supply.name}')
    
    print('\n=== Sample data creation completed! ===')
    print(f'Total categories: {ConsumableCategory.objects.filter(company=company).count()}')
    print(f'Total supplies: {Consumable.objects.filter(company=company).count()}')


if __name__ == '__main__':
    create_sample_data()
