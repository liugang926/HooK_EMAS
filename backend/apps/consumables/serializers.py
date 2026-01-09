from rest_framework import serializers
from .models import ConsumableCategory, Consumable, ConsumableStock, ConsumableInbound, ConsumableInboundItem, ConsumableOutbound, ConsumableOutboundItem


class ConsumableCategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = ConsumableCategory
        fields = ['id', 'name', 'code', 'parent', 'level', 'sort_order', 'children']
    
    def get_children(self, obj):
        children = obj.children.all()
        return ConsumableCategorySerializer(children, many=True).data


class ConsumableSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    total_stock = serializers.SerializerMethodField()
    current_stock = serializers.SerializerMethodField()  # Kept for backward compatibility
    
    class Meta:
        model = Consumable
        fields = '__all__'
    
    def get_total_stock(self, obj):
        """Calculate total stock across all warehouses using Sum aggregation"""
        from django.db.models import Sum
        result = ConsumableStock.objects.filter(consumable=obj).aggregate(total=Sum('quantity'))
        return result['total'] or 0
    
    def get_current_stock(self, obj):
        """Legacy method for backward compatibility"""
        return self.get_total_stock(obj)


class ConsumableStockSerializer(serializers.ModelSerializer):
    # Fields expected by frontend stock view
    code = serializers.CharField(source='consumable.code', read_only=True)
    name = serializers.CharField(source='consumable.name', read_only=True)
    consumable_name = serializers.CharField(source='consumable.name', read_only=True)  # backward compat
    category_name = serializers.SerializerMethodField()
    unit = serializers.CharField(source='consumable.unit', read_only=True)
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    min_stock = serializers.IntegerField(source='consumable.min_stock', read_only=True)
    
    class Meta:
        model = ConsumableStock
        fields = ['id', 'code', 'name', 'consumable_name', 'category_name', 'unit', 
                  'warehouse_name', 'quantity', 'min_stock', 'updated_at', 
                  'consumable', 'warehouse']
    
    def get_category_name(self, obj):
        if obj.consumable and obj.consumable.category:
            return obj.consumable.category.name
        return None


class ConsumableInboundItemSerializer(serializers.ModelSerializer):
    consumable_name = serializers.CharField(source='consumable.name', read_only=True)
    
    class Meta:
        model = ConsumableInboundItem
        fields = ['id', 'consumable', 'consumable_name', 'quantity', 'price', 'amount']


class ConsumableInboundSerializer(serializers.ModelSerializer):
    items = ConsumableInboundItemSerializer(many=True, read_only=True)
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    supplier_name = serializers.SerializerMethodField()
    created_by_name = serializers.CharField(source='created_by.display_name', read_only=True)
    item_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ConsumableInbound
        fields = ['id', 'inbound_no', 'company', 'warehouse', 'warehouse_name', 
                  'supplier', 'supplier_name', 'status', 'inbound_date', 
                  'total_amount', 'remark', 'created_by', 'created_by_name', 
                  'created_at', 'items', 'item_count']
        read_only_fields = ['created_by', 'created_at']
    
    def get_supplier_name(self, obj):
        return obj.supplier.name if obj.supplier else None
    
    def get_item_count(self, obj):
        return obj.items.count()


class ConsumableOutboundItemSerializer(serializers.ModelSerializer):
    consumable_name = serializers.CharField(source='consumable.name', read_only=True)
    
    class Meta:
        model = ConsumableOutboundItem
        fields = ['id', 'consumable', 'consumable_name', 'quantity']


class ConsumableOutboundSerializer(serializers.ModelSerializer):
    items = ConsumableOutboundItemSerializer(many=True, read_only=True)
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    receive_user_name = serializers.SerializerMethodField()
    receive_department_name = serializers.SerializerMethodField()
    created_by_name = serializers.CharField(source='created_by.display_name', read_only=True)
    item_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ConsumableOutbound
        fields = ['id', 'outbound_no', 'company', 'warehouse', 'warehouse_name',
                  'outbound_type', 'status', 'outbound_date', 
                  'receive_user', 'receive_user_name', 
                  'receive_department', 'receive_department_name',
                  'reason', 'remark', 'created_by', 'created_by_name',
                  'created_at', 'items', 'item_count']
        read_only_fields = ['created_by', 'created_at']
    
    def get_receive_user_name(self, obj):
        return obj.receive_user.display_name if obj.receive_user else None
    
    def get_receive_department_name(self, obj):
        return obj.receive_department.name if obj.receive_department else None
    
    def get_item_count(self, obj):
        return obj.items.count()
