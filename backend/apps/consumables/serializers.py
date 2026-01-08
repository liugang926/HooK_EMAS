from rest_framework import serializers
from .models import ConsumableCategory, Consumable, ConsumableStock, ConsumableInbound, ConsumableOutbound


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
    current_stock = serializers.SerializerMethodField()
    
    class Meta:
        model = Consumable
        fields = '__all__'
    
    def get_current_stock(self, obj):
        stock = ConsumableStock.objects.filter(consumable=obj).first()
        return stock.quantity if stock else 0


class ConsumableStockSerializer(serializers.ModelSerializer):
    consumable_name = serializers.CharField(source='consumable.name', read_only=True)
    
    class Meta:
        model = ConsumableStock
        fields = '__all__'


class ConsumableInboundSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsumableInbound
        fields = '__all__'


class ConsumableOutboundSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsumableOutbound
        fields = '__all__'
