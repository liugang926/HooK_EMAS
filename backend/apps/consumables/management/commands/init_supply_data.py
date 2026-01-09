"""
Initialize mock data for office supplies (办公用品)
Usage: python manage.py init_supply_data
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from decimal import Decimal
from datetime import date, timedelta
import random

from apps.consumables.models import (
    ConsumableCategory, Consumable, ConsumableStock,
    ConsumableInbound, ConsumableInboundItem,
    ConsumableOutbound, ConsumableOutboundItem
)
from apps.organizations.models import Company, Location, Department
from apps.accounts.models import User


class Command(BaseCommand):
    help = 'Initialize mock data for office supplies'

    def add_arguments(self, parser):
        parser.add_argument(
            '--company',
            type=int,
            default=1,
            help='Company ID to create data for (default: 1)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before creating new data'
        )

    @transaction.atomic
    def handle(self, *args, **options):
        company_id = options['company']
        clear = options['clear']
        
        try:
            company = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            self.stderr.write(f'Company with ID {company_id} not found')
            return
        
        self.stdout.write(f'Creating office supplies data for company: {company.name}')
        
        if clear:
            self.stdout.write('Clearing existing data...')
            ConsumableOutboundItem.objects.filter(outbound__company=company).delete()
            ConsumableOutbound.objects.filter(company=company).delete()
            ConsumableInboundItem.objects.filter(inbound__company=company).delete()
            ConsumableInbound.objects.filter(company=company).delete()
            ConsumableStock.objects.filter(consumable__company=company).delete()
            Consumable.objects.filter(company=company).delete()
            ConsumableCategory.objects.filter(company=company).delete()
        
        # Create categories
        categories = self._create_categories(company)
        self.stdout.write(f'  Created {len(categories)} categories')
        
        # Create consumables
        consumables = self._create_consumables(company, categories)
        self.stdout.write(f'  Created {len(consumables)} consumables')
        
        # Create warehouse/location if not exists
        warehouse = self._get_or_create_warehouse(company)
        
        # Create stock
        stocks = self._create_stocks(consumables, warehouse)
        self.stdout.write(f'  Created {len(stocks)} stock records')
        
        # Create inbound records
        inbounds = self._create_inbounds(company, consumables, warehouse)
        self.stdout.write(f'  Created {len(inbounds)} inbound records')
        
        # Create outbound records
        outbounds = self._create_outbounds(company, consumables, warehouse)
        self.stdout.write(f'  Created {len(outbounds)} outbound records')
        
        self.stdout.write(self.style.SUCCESS('Office supplies data initialized successfully!'))

    def _create_categories(self, company):
        """Create consumable categories"""
        category_data = [
            {'code': 'WJ', 'name': '文具用品', 'children': [
                {'code': 'WJ-BG', 'name': '笔类'},
                {'code': 'WJ-BJ', 'name': '本册'},
                {'code': 'WJ-WJ', 'name': '文件夹'},
            ]},
            {'code': 'BG', 'name': '办公耗材', 'children': [
                {'code': 'BG-DY', 'name': '打印耗材'},
                {'code': 'BG-ZZ', 'name': '纸张'},
            ]},
            {'code': 'QJ', 'name': '清洁用品', 'children': [
                {'code': 'QJ-ZJ', 'name': '纸巾'},
                {'code': 'QJ-QX', 'name': '清洗用品'},
            ]},
            {'code': 'RS', 'name': '日常用品', 'children': [
                {'code': 'RS-YS', 'name': '饮食用品'},
                {'code': 'RS-QT', 'name': '其他'},
            ]},
        ]
        
        categories = []
        for cat_data in category_data:
            parent, created = ConsumableCategory.objects.get_or_create(
                company=company,
                code=cat_data['code'],
                defaults={
                    'name': cat_data['name'],
                    'is_active': True
                }
            )
            categories.append(parent)
            
            for child_data in cat_data.get('children', []):
                child, created = ConsumableCategory.objects.get_or_create(
                    company=company,
                    code=child_data['code'],
                    defaults={
                        'name': child_data['name'],
                        'parent': parent,
                        'is_active': True
                    }
                )
                categories.append(child)
        
        return categories

    def _create_consumables(self, company, categories):
        """Create consumable items"""
        # Map category codes to objects
        cat_map = {c.code: c for c in categories}
        
        consumable_data = [
            # 笔类
            {'code': 'BG20250101', 'name': '中性笔-黑色', 'category': 'WJ-BG', 'unit': '支', 'price': 2.00, 'min_stock': 100, 'brand': '晨光'},
            {'code': 'BG20250102', 'name': '中性笔-红色', 'category': 'WJ-BG', 'unit': '支', 'price': 2.00, 'min_stock': 50, 'brand': '晨光'},
            {'code': 'BG20250103', 'name': '中性笔-蓝色', 'category': 'WJ-BG', 'unit': '支', 'price': 2.00, 'min_stock': 50, 'brand': '晨光'},
            {'code': 'BG20250104', 'name': '记号笔-黑色', 'category': 'WJ-BG', 'unit': '支', 'price': 3.50, 'min_stock': 30, 'brand': '斑马'},
            {'code': 'BG20250105', 'name': '白板笔-黑色', 'category': 'WJ-BG', 'unit': '支', 'price': 5.00, 'min_stock': 20, 'brand': '得力'},
            {'code': 'BG20250106', 'name': '铅笔 2B', 'category': 'WJ-BG', 'unit': '支', 'price': 1.00, 'min_stock': 50, 'brand': '中华'},
            
            # 本册
            {'code': 'BG20250201', 'name': 'A4笔记本', 'category': 'WJ-BJ', 'unit': '本', 'price': 8.00, 'min_stock': 50, 'model': '80页'},
            {'code': 'BG20250202', 'name': 'A5笔记本', 'category': 'WJ-BJ', 'unit': '本', 'price': 5.00, 'min_stock': 50, 'model': '60页'},
            {'code': 'BG20250203', 'name': '便签纸', 'category': 'WJ-BJ', 'unit': '本', 'price': 3.00, 'min_stock': 100, 'model': '100张/本'},
            
            # 文件夹
            {'code': 'BG20250301', 'name': '文件夹 A4', 'category': 'WJ-WJ', 'unit': '个', 'price': 6.00, 'min_stock': 30, 'model': '双夹'},
            {'code': 'BG20250302', 'name': '档案盒', 'category': 'WJ-WJ', 'unit': '个', 'price': 12.00, 'min_stock': 20, 'model': '55mm'},
            {'code': 'BG20250303', 'name': '透明文件袋', 'category': 'WJ-WJ', 'unit': '个', 'price': 1.50, 'min_stock': 100, 'model': 'A4'},
            
            # 打印耗材
            {'code': 'BG20250401', 'name': 'HP打印机墨盒-黑色', 'category': 'BG-DY', 'unit': '个', 'price': 180.00, 'min_stock': 5, 'model': 'HP 680'},
            {'code': 'BG20250402', 'name': 'HP打印机墨盒-彩色', 'category': 'BG-DY', 'unit': '个', 'price': 220.00, 'min_stock': 3, 'model': 'HP 680'},
            {'code': 'BG20250403', 'name': '复印纸 A4', 'category': 'BG-ZZ', 'unit': '包', 'price': 28.00, 'min_stock': 50, 'model': '500张/包'},
            {'code': 'BG20250404', 'name': '复印纸 A3', 'category': 'BG-ZZ', 'unit': '包', 'price': 55.00, 'min_stock': 10, 'model': '500张/包'},
            
            # 清洁用品
            {'code': 'BG20250501', 'name': '抽纸', 'category': 'QJ-ZJ', 'unit': '盒', 'price': 5.00, 'min_stock': 100, 'brand': '维达'},
            {'code': 'BG20250502', 'name': '卷纸', 'category': 'QJ-ZJ', 'unit': '提', 'price': 25.00, 'min_stock': 20, 'brand': '维达', 'model': '12卷/提'},
            {'code': 'BG20250503', 'name': '洗手液', 'category': 'QJ-QX', 'unit': '瓶', 'price': 15.00, 'min_stock': 10, 'brand': '蓝月亮'},
            {'code': 'BG20250504', 'name': '垃圾袋', 'category': 'QJ-QX', 'unit': '卷', 'price': 8.00, 'min_stock': 20, 'model': '30只/卷'},
            
            # 日常用品
            {'code': 'BG20250601', 'name': '一次性纸杯', 'category': 'RS-YS', 'unit': '包', 'price': 12.00, 'min_stock': 20, 'model': '50只/包'},
            {'code': 'BG20250602', 'name': '咖啡', 'category': 'RS-YS', 'unit': '盒', 'price': 35.00, 'min_stock': 10, 'brand': '雀巢', 'model': '30条/盒'},
            {'code': 'BG20250603', 'name': '茶叶-绿茶', 'category': 'RS-YS', 'unit': '盒', 'price': 45.00, 'min_stock': 5, 'model': '100g'},
            {'code': 'BG20250604', 'name': '订书机', 'category': 'RS-QT', 'unit': '个', 'price': 15.00, 'min_stock': 10, 'brand': '得力'},
            {'code': 'BG20250605', 'name': '订书钉', 'category': 'RS-QT', 'unit': '盒', 'price': 3.00, 'min_stock': 30, 'model': '24/6'},
        ]
        
        consumables = []
        for item_data in consumable_data:
            category = cat_map.get(item_data.pop('category'))
            consumable, created = Consumable.objects.get_or_create(
                company=company,
                code=item_data['code'],
                defaults={
                    'name': item_data['name'],
                    'category': category,
                    'unit': item_data['unit'],
                    'price': Decimal(str(item_data['price'])),
                    'min_stock': item_data.get('min_stock', 10),
                    'brand': item_data.get('brand', ''),
                    'model': item_data.get('model', ''),
                    'is_active': True
                }
            )
            consumables.append(consumable)
        
        return consumables

    def _get_or_create_warehouse(self, company):
        """Get or create a default warehouse"""
        warehouse, created = Location.objects.get_or_create(
            company=company,
            code='WH-DEFAULT',
            defaults={
                'name': '办公用品仓库',
                'description': '办公用品存放仓库'
            }
        )
        return warehouse

    def _create_stocks(self, consumables, warehouse):
        """Create stock records for consumables"""
        stocks = []
        for consumable in consumables:
            # Random initial stock
            quantity = random.randint(20, 200)
            stock, created = ConsumableStock.objects.get_or_create(
                consumable=consumable,
                warehouse=warehouse,
                defaults={'quantity': quantity}
            )
            if not created:
                stock.quantity = quantity
                stock.save()
            stocks.append(stock)
        return stocks

    def _create_inbounds(self, company, consumables, warehouse):
        """Create inbound records"""
        user = User.objects.filter(is_active=True).first()
        if not user:
            return []
        
        inbounds = []
        base_date = date.today() - timedelta(days=30)
        
        for i in range(5):
            inbound_date = base_date + timedelta(days=i * 5)
            inbound_no = f'RK{inbound_date.strftime("%Y%m%d")}{str(i+1).zfill(4)}'
            
            inbound, created = ConsumableInbound.objects.get_or_create(
                inbound_no=inbound_no,
                defaults={
                    'company': company,
                    'warehouse': warehouse,
                    'status': 'approved',
                    'inbound_date': inbound_date,
                    'total_amount': Decimal('0'),
                    'created_by': user
                }
            )
            
            if created:
                # Add random items
                selected_items = random.sample(consumables, min(5, len(consumables)))
                total = Decimal('0')
                for item in selected_items:
                    quantity = random.randint(10, 50)
                    price = item.price or Decimal('10.00')
                    amount = price * quantity
                    total += amount
                    
                    ConsumableInboundItem.objects.create(
                        inbound=inbound,
                        consumable=item,
                        quantity=quantity,
                        price=price,
                        amount=amount
                    )
                
                inbound.total_amount = total
                inbound.save()
            
            inbounds.append(inbound)
        
        return inbounds

    def _create_outbounds(self, company, consumables, warehouse):
        """Create outbound records"""
        user = User.objects.filter(is_active=True).first()
        department = Department.objects.filter(company=company).first()
        if not user:
            return []
        
        outbounds = []
        base_date = date.today() - timedelta(days=25)
        
        for i in range(5):
            outbound_date = base_date + timedelta(days=i * 4)
            outbound_no = f'LY{outbound_date.strftime("%Y%m%d")}{str(i+1).zfill(4)}'
            
            outbound, created = ConsumableOutbound.objects.get_or_create(
                outbound_no=outbound_no,
                defaults={
                    'company': company,
                    'warehouse': warehouse,
                    'outbound_type': 'receive',
                    'status': 'approved',
                    'outbound_date': outbound_date,
                    'receive_user': user,
                    'receive_department': department,
                    'reason': '日常办公领用',
                    'created_by': user
                }
            )
            
            if created:
                # Add random items
                selected_items = random.sample(consumables, min(3, len(consumables)))
                for item in selected_items:
                    quantity = random.randint(1, 10)
                    ConsumableOutboundItem.objects.create(
                        outbound=outbound,
                        consumable=item,
                        quantity=quantity
                    )
            
            outbounds.append(outbound)
        
        return outbounds
