from django.contrib import admin
from .models import Supplier, PurchaseRequest, PurchaseRequestItem, PurchaseOrder, PurchaseOrderItem


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'contact', 'phone', 'is_active', 'company']
    list_filter = ['is_active', 'company']
    search_fields = ['code', 'name', 'contact']


class PurchaseRequestItemInline(admin.TabularInline):
    model = PurchaseRequestItem
    extra = 1


@admin.register(PurchaseRequest)
class PurchaseRequestAdmin(admin.ModelAdmin):
    list_display = ['request_no', 'department', 'created_by', 'total_amount', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['request_no']
    inlines = [PurchaseRequestItemInline]


class PurchaseOrderItemInline(admin.TabularInline):
    model = PurchaseOrderItem
    extra = 1


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ['order_no', 'supplier', 'total_amount', 'status', 'order_date']
    list_filter = ['status', 'order_date']
    search_fields = ['order_no', 'supplier__name']
    inlines = [PurchaseOrderItemInline]
