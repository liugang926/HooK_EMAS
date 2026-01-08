from django.contrib import admin
from .models import ConsumableCategory, Consumable, ConsumableStock, ConsumableInbound, ConsumableInboundItem, ConsumableOutbound, ConsumableOutboundItem


@admin.register(ConsumableCategory)
class ConsumableCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'parent', 'level', 'company']
    list_filter = ['company', 'level']
    search_fields = ['name', 'code']


@admin.register(Consumable)
class ConsumableAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'category', 'brand', 'unit', 'price', 'min_stock', 'is_active']
    list_filter = ['category', 'is_active', 'company']
    search_fields = ['code', 'name', 'brand']


@admin.register(ConsumableStock)
class ConsumableStockAdmin(admin.ModelAdmin):
    list_display = ['consumable', 'warehouse', 'quantity']
    list_filter = ['warehouse']
    search_fields = ['consumable__name']


class ConsumableInboundItemInline(admin.TabularInline):
    model = ConsumableInboundItem
    extra = 1


@admin.register(ConsumableInbound)
class ConsumableInboundAdmin(admin.ModelAdmin):
    list_display = ['inbound_no', 'warehouse', 'status', 'inbound_date', 'total_amount', 'created_by']
    list_filter = ['status', 'inbound_date']
    search_fields = ['inbound_no']
    inlines = [ConsumableInboundItemInline]


class ConsumableOutboundItemInline(admin.TabularInline):
    model = ConsumableOutboundItem
    extra = 1


@admin.register(ConsumableOutbound)
class ConsumableOutboundAdmin(admin.ModelAdmin):
    list_display = ['outbound_no', 'warehouse', 'outbound_type', 'status', 'receive_user', 'outbound_date']
    list_filter = ['status', 'outbound_type', 'outbound_date']
    search_fields = ['outbound_no']
    inlines = [ConsumableOutboundItemInline]
