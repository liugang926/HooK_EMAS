"""
资产管理 Admin 配置
"""
from django.contrib import admin
from mptt.admin import MPTTModelAdmin
from .models import (
    AssetCategory, Asset, AssetImage, AssetOperation,
    AssetReceive, AssetReceiveItem,
    AssetBorrow, AssetBorrowItem,
    AssetTransfer, AssetTransferItem,
    AssetDisposal, AssetDisposalItem,
    AssetMaintenance, AssetLabel
)


@admin.register(AssetCategory)
class AssetCategoryAdmin(MPTTModelAdmin):
    list_display = ['name', 'code', 'company', 'parent', 'is_active']
    list_filter = ['company', 'is_active']
    search_fields = ['name', 'code']


class AssetImageInline(admin.TabularInline):
    model = AssetImage
    extra = 0


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ['asset_code', 'name', 'category', 'status', 'original_value', 'using_user', 'created_at']
    list_filter = ['company', 'status', 'category', 'is_deleted']
    search_fields = ['asset_code', 'name', 'serial_number']
    inlines = [AssetImageInline]


@admin.register(AssetOperation)
class AssetOperationAdmin(admin.ModelAdmin):
    list_display = ['asset', 'operation_type', 'operator', 'created_at']
    list_filter = ['operation_type']
    search_fields = ['asset__asset_code', 'description']
    readonly_fields = ['asset', 'operation_type', 'description', 'old_data', 'new_data', 'operator', 'created_at']


class AssetReceiveItemInline(admin.TabularInline):
    model = AssetReceiveItem
    extra = 0


@admin.register(AssetReceive)
class AssetReceiveAdmin(admin.ModelAdmin):
    list_display = ['receive_no', 'receive_user', 'receive_department', 'status', 'receive_date']
    list_filter = ['status', 'company']
    search_fields = ['receive_no']
    inlines = [AssetReceiveItemInline]


class AssetBorrowItemInline(admin.TabularInline):
    model = AssetBorrowItem
    extra = 0


@admin.register(AssetBorrow)
class AssetBorrowAdmin(admin.ModelAdmin):
    list_display = ['borrow_no', 'borrower', 'status', 'borrow_date', 'expected_return_date']
    list_filter = ['status', 'company']
    search_fields = ['borrow_no']
    inlines = [AssetBorrowItemInline]


class AssetTransferItemInline(admin.TabularInline):
    model = AssetTransferItem
    extra = 0


@admin.register(AssetTransfer)
class AssetTransferAdmin(admin.ModelAdmin):
    list_display = ['transfer_no', 'from_department', 'to_department', 'status', 'transfer_date']
    list_filter = ['status', 'company']
    search_fields = ['transfer_no']
    inlines = [AssetTransferItemInline]


class AssetDisposalItemInline(admin.TabularInline):
    model = AssetDisposalItem
    extra = 0


@admin.register(AssetDisposal)
class AssetDisposalAdmin(admin.ModelAdmin):
    list_display = ['disposal_no', 'disposal_method', 'status', 'disposal_date', 'disposal_amount']
    list_filter = ['status', 'disposal_method', 'company']
    search_fields = ['disposal_no']
    inlines = [AssetDisposalItemInline]


@admin.register(AssetMaintenance)
class AssetMaintenanceAdmin(admin.ModelAdmin):
    list_display = ['maintenance_no', 'asset', 'maintenance_type', 'status', 'cost']
    list_filter = ['status', 'maintenance_type']
    search_fields = ['maintenance_no', 'asset__asset_code']


@admin.register(AssetLabel)
class AssetLabelAdmin(admin.ModelAdmin):
    list_display = ['name', 'company', 'width', 'height', 'is_default', 'is_active']
    list_filter = ['company', 'is_default', 'is_active']
