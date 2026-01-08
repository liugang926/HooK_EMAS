"""
资产管理序列化器 - 精臣云资产管理系统
"""
from rest_framework import serializers
from .models import (
    AssetCategory, Asset, AssetImage, AssetOperation,
    AssetReceive, AssetReceiveItem,
    AssetBorrow, AssetBorrowItem,
    AssetTransfer, AssetTransferItem,
    AssetDisposal, AssetDisposalItem,
    AssetMaintenance, AssetLabel
)


class AssetCategorySerializer(serializers.ModelSerializer):
    """资产分类序列化器"""
    
    parent_name = serializers.CharField(source='parent.name', read_only=True, default='')
    children_count = serializers.SerializerMethodField()
    assets_count = serializers.SerializerMethodField()
    
    class Meta:
        model = AssetCategory
        fields = [
            'id', 'company', 'name', 'code', 'parent', 'parent_name',
            'description', 'depreciation_method', 'useful_life',
            'salvage_rate', 'custom_fields', 'sort_order',
            'children_count', 'assets_count',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'company', 'created_at', 'updated_at']
    
    def get_children_count(self, obj):
        return obj.get_children().count()
    
    def get_assets_count(self, obj):
        return obj.assets.count()


class AssetCategoryTreeSerializer(serializers.ModelSerializer):
    """资产分类树形序列化器"""
    
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = AssetCategory
        fields = ['id', 'name', 'code', 'parent', 'is_active', 'children']
    
    def get_children(self, obj):
        children = obj.get_children().filter(is_active=True)
        return AssetCategoryTreeSerializer(children, many=True).data


class AssetImageSerializer(serializers.ModelSerializer):
    """资产图片序列化器"""
    
    class Meta:
        model = AssetImage
        fields = ['id', 'asset', 'image', 'is_primary', 'sort_order', 'created_at']
        read_only_fields = ['id', 'created_at']


class AssetSerializer(serializers.ModelSerializer):
    """资产序列化器"""
    
    category_name = serializers.CharField(source='category.name', read_only=True, default='')
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    acquisition_method_display = serializers.CharField(source='get_acquisition_method_display', read_only=True)
    using_department_name = serializers.CharField(source='using_department.name', read_only=True, default='')
    using_user_name = serializers.CharField(source='using_user.display_name', read_only=True, default='')
    location_name = serializers.CharField(source='location.full_name', read_only=True, default='')
    manage_department_name = serializers.CharField(source='manage_department.name', read_only=True, default='')
    manager_name = serializers.CharField(source='manager.display_name', read_only=True, default='')
    images = AssetImageSerializer(many=True, read_only=True)
    
    # 资产编号允许编辑，但新增时可以为空（由后端自动生成）
    asset_code = serializers.CharField(required=False, allow_blank=True)
    
    class Meta:
        model = Asset
        fields = [
            'id', 'company', 'asset_code', 'name', 'category', 'category_name',
            'status', 'status_display', 'brand', 'model', 'serial_number',
            'unit', 'quantity', 'image', 'images',
            'acquisition_method', 'acquisition_method_display', 'acquisition_date', 
            'original_value', 'current_value', 'accumulated_depreciation',
            'using_department', 'using_department_name',
            'using_user', 'using_user_name',
            'location', 'location_name',
            'manage_department', 'manage_department_name',
            'manager', 'manager_name',
            'rfid_code', 'barcode', 'qrcode',
            'supplier', 'warranty_expiry',
            'custom_data', 'remark',
            'created_by', 'created_at', 'updated_at'
        ]
        # 移除 asset_code 从 read_only_fields，允许编辑
        read_only_fields = ['id', 'company', 'created_by', 'created_at', 'updated_at']


class AssetListSerializer(serializers.ModelSerializer):
    """资产列表序列化器（简化版）"""
    
    category_name = serializers.CharField(source='category.name', read_only=True, default='')
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    using_user_name = serializers.SerializerMethodField()
    using_department_name = serializers.SerializerMethodField()
    location_name = serializers.SerializerMethodField()
    manager_name = serializers.SerializerMethodField()
    manage_department_name = serializers.SerializerMethodField()
    supplier_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Asset
        fields = [
            'id', 'asset_code', 'name', 'category', 'category_name',
            'status', 'status_display', 'brand', 'model', 'serial_number', 'unit',
            'original_value', 'current_value', 'accumulated_depreciation',
            'acquisition_method', 'acquisition_date', 'warranty_expiry',
            'using_user', 'using_user_name',
            'using_department', 'using_department_name',
            'location', 'location_name',
            'manage_department', 'manage_department_name',
            'manager', 'manager_name',
            'supplier', 'supplier_name',
            'image', 'remark', 'created_at'
        ]
    
    def get_using_user_name(self, obj):
        return obj.using_user.display_name if obj.using_user else None
    
    def get_using_department_name(self, obj):
        return obj.using_department.name if obj.using_department else None
    
    def get_location_name(self, obj):
        return obj.location.name if obj.location else None
    
    def get_manager_name(self, obj):
        return obj.manager.display_name if obj.manager else None
    
    def get_manage_department_name(self, obj):
        return obj.manage_department.name if obj.manage_department else None
    
    def get_supplier_name(self, obj):
        return obj.supplier.name if obj.supplier else None


class AssetOperationSerializer(serializers.ModelSerializer):
    """资产操作记录序列化器"""
    
    operation_type_display = serializers.CharField(source='get_operation_type_display', read_only=True)
    operator_name = serializers.CharField(source='operator.display_name', read_only=True)
    asset_code = serializers.CharField(source='asset.asset_code', read_only=True)
    asset_name = serializers.CharField(source='asset.name', read_only=True)
    
    class Meta:
        model = AssetOperation
        fields = [
            'id', 'asset', 'asset_code', 'asset_name',
            'operation_type', 'operation_type_display',
            'operation_no', 'description', 'old_data', 'new_data',
            'operator', 'operator_name', 'created_at'
        ]
        read_only_fields = fields


class AssetReceiveItemSerializer(serializers.ModelSerializer):
    """资产领用明细序列化器"""
    
    asset_code = serializers.CharField(source='asset.asset_code', read_only=True)
    asset_name = serializers.CharField(source='asset.name', read_only=True)
    
    class Meta:
        model = AssetReceiveItem
        fields = ['id', 'receive', 'asset', 'asset_code', 'asset_name', 'quantity', 'remark']
        read_only_fields = ['id']
        extra_kwargs = {
            'receive': {'required': False}
        }


class AssetReceiveItemWriteSerializer(serializers.Serializer):
    """资产领用明细写入序列化器"""
    asset = serializers.IntegerField()
    quantity = serializers.IntegerField(default=1, required=False)
    remark = serializers.CharField(required=False, allow_blank=True, default='')


class AssetReceiveSerializer(serializers.ModelSerializer):
    """资产领用单序列化器"""
    
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    receive_user_name = serializers.CharField(source='receive_user.display_name', read_only=True)
    receive_department_name = serializers.CharField(source='receive_department.name', read_only=True)
    items = AssetReceiveItemSerializer(many=True, read_only=True)
    items_data = AssetReceiveItemWriteSerializer(many=True, write_only=True, required=False)
    
    class Meta:
        model = AssetReceive
        fields = [
            'id', 'receive_no', 'company', 'status', 'status_display',
            'receive_user', 'receive_user_name',
            'receive_department', 'receive_department_name',
            'receive_date', 'expected_return_date', 'reason', 'remark',
            'items', 'items_data', 'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'receive_no', 'company', 'created_by', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        items_data = validated_data.pop('items_data', [])
        receive = super().create(validated_data)
        
        # 创建领用明细
        for item_data in items_data:
            AssetReceiveItem.objects.create(
                receive=receive,
                asset_id=item_data['asset'],
                quantity=item_data.get('quantity', 1),
                remark=item_data.get('remark', '')
            )
        
        return receive


class AssetBorrowItemSerializer(serializers.ModelSerializer):
    """资产借用明细序列化器"""
    
    asset_code = serializers.CharField(source='asset.asset_code', read_only=True)
    asset_name = serializers.CharField(source='asset.name', read_only=True)
    
    class Meta:
        model = AssetBorrowItem
        fields = [
            'id', 'borrow', 'asset', 'asset_code', 'asset_name',
            'quantity', 'is_returned', 'return_date', 'remark'
        ]
        read_only_fields = ['id']


class AssetBorrowItemWriteSerializer(serializers.Serializer):
    """资产借用明细写入序列化器"""
    asset = serializers.IntegerField()
    quantity = serializers.IntegerField(default=1, required=False)
    remark = serializers.CharField(required=False, allow_blank=True, default='')


class AssetBorrowSerializer(serializers.ModelSerializer):
    """资产借用单序列化器"""
    
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    borrower_name = serializers.CharField(source='borrower.display_name', read_only=True)
    borrow_department_name = serializers.CharField(source='borrow_department.name', read_only=True)
    items = AssetBorrowItemSerializer(many=True, read_only=True)
    items_data = AssetBorrowItemWriteSerializer(many=True, write_only=True, required=False)
    
    class Meta:
        model = AssetBorrow
        fields = [
            'id', 'borrow_no', 'company', 'status', 'status_display',
            'borrower', 'borrower_name',
            'borrow_department', 'borrow_department_name',
            'borrow_date', 'expected_return_date', 'actual_return_date',
            'reason', 'remark', 'items', 'items_data',
            'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'borrow_no', 'company', 'created_by', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        items_data = validated_data.pop('items_data', [])
        borrow = super().create(validated_data)
        
        # 创建借用明细
        for item_data in items_data:
            AssetBorrowItem.objects.create(
                borrow=borrow,
                asset_id=item_data['asset'],
                quantity=item_data.get('quantity', 1),
                remark=item_data.get('remark', '')
            )
        
        return borrow


class AssetTransferItemSerializer(serializers.ModelSerializer):
    """资产调拨明细序列化器"""
    
    asset_code = serializers.CharField(source='asset.asset_code', read_only=True)
    asset_name = serializers.CharField(source='asset.name', read_only=True)
    from_user_name = serializers.CharField(source='from_user.display_name', read_only=True, default='')
    from_department_name = serializers.CharField(source='from_department.name', read_only=True, default='')
    from_location_name = serializers.CharField(source='from_location.name', read_only=True, default='')
    
    class Meta:
        model = AssetTransferItem
        fields = [
            'id', 'transfer', 'asset', 'asset_code', 'asset_name', 'quantity',
            'from_user', 'from_user_name', 'from_department', 'from_department_name',
            'from_location', 'from_location_name', 'remark'
        ]
        read_only_fields = ['id']


class AssetTransferItemWriteSerializer(serializers.Serializer):
    """资产调拨明细写入序列化器"""
    asset = serializers.IntegerField()
    quantity = serializers.IntegerField(default=1, required=False)
    from_user = serializers.IntegerField(required=False, allow_null=True)
    from_department = serializers.IntegerField(required=False, allow_null=True)
    from_location = serializers.IntegerField(required=False, allow_null=True)
    remark = serializers.CharField(required=False, allow_blank=True, default='')


class AssetTransferSerializer(serializers.ModelSerializer):
    """资产调拨单序列化器"""
    
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    from_department_name = serializers.CharField(source='from_department.name', read_only=True, default='')
    to_department_name = serializers.CharField(source='to_department.name', read_only=True, default='')
    to_user_name = serializers.CharField(source='to_user.display_name', read_only=True, default='')
    to_location_name = serializers.CharField(source='to_location.name', read_only=True, default='')
    items = AssetTransferItemSerializer(many=True, read_only=True)
    items_data = AssetTransferItemWriteSerializer(many=True, write_only=True, required=False)
    
    class Meta:
        model = AssetTransfer
        fields = [
            'id', 'transfer_no', 'company', 'status', 'status_display',
            'from_department', 'from_department_name', 'from_user', 'from_location',
            'to_department', 'to_department_name', 'to_user', 'to_user_name',
            'to_location', 'to_location_name',
            'transfer_date', 'reason', 'remark', 'items', 'items_data',
            'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'transfer_no', 'company', 'created_by', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        items_data = validated_data.pop('items_data', [])
        transfer = super().create(validated_data)
        
        # 创建调拨明细
        for item_data in items_data:
            AssetTransferItem.objects.create(
                transfer=transfer,
                asset_id=item_data['asset'],
                quantity=item_data.get('quantity', 1),
                from_user_id=item_data.get('from_user'),
                from_department_id=item_data.get('from_department'),
                from_location_id=item_data.get('from_location'),
                remark=item_data.get('remark', '')
            )
        
        return transfer


class AssetDisposalItemSerializer(serializers.ModelSerializer):
    """资产处置明细序列化器"""
    
    asset_code = serializers.CharField(source='asset.asset_code', read_only=True)
    asset_name = serializers.CharField(source='asset.name', read_only=True)
    
    class Meta:
        model = AssetDisposalItem
        fields = [
            'id', 'disposal', 'asset', 'asset_code', 'asset_name',
            'original_value', 'current_value', 'disposal_value',
            'quantity', 'remark'
        ]
        read_only_fields = ['id']


class AssetDisposalItemWriteSerializer(serializers.Serializer):
    """资产处置明细写入序列化器"""
    asset = serializers.IntegerField()
    quantity = serializers.IntegerField(default=1, required=False)
    remark = serializers.CharField(required=False, allow_blank=True, default='')


class AssetDisposalSerializer(serializers.ModelSerializer):
    """资产处置单序列化器"""
    
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    disposal_method_display = serializers.CharField(source='get_disposal_method_display', read_only=True)
    items = AssetDisposalItemSerializer(many=True, read_only=True)
    items_data = AssetDisposalItemWriteSerializer(many=True, write_only=True, required=False)
    
    class Meta:
        model = AssetDisposal
        fields = [
            'id', 'disposal_no', 'company', 'status', 'status_display',
            'disposal_method', 'disposal_method_display',
            'disposal_date', 'disposal_amount', 'reason', 'remark', 'items', 'items_data',
            'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'disposal_no', 'company', 'created_by', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        items_data = validated_data.pop('items_data', [])
        disposal = super().create(validated_data)
        
        # 创建处置明细
        for item_data in items_data:
            AssetDisposalItem.objects.create(
                disposal=disposal,
                asset_id=item_data['asset'],
                quantity=item_data.get('quantity', 1),
                remark=item_data.get('remark', '')
            )
        
        return disposal


class AssetMaintenanceSerializer(serializers.ModelSerializer):
    """资产维保序列化器"""
    
    maintenance_type_display = serializers.CharField(source='get_maintenance_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    asset_code = serializers.CharField(source='asset.asset_code', read_only=True)
    asset_name = serializers.CharField(source='asset.name', read_only=True)
    
    class Meta:
        model = AssetMaintenance
        fields = [
            'id', 'maintenance_no', 'asset', 'asset_code', 'asset_name',
            'maintenance_type', 'maintenance_type_display',
            'status', 'status_display',
            'description', 'start_date', 'end_date',
            'cost', 'service_provider', 'result',
            'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'maintenance_no', 'created_by', 'created_at', 'updated_at']


class AssetLabelSerializer(serializers.ModelSerializer):
    """资产标签模板序列化器"""
    
    class Meta:
        model = AssetLabel
        fields = [
            'id', 'company', 'name', 'width', 'height',
            'template_config', 'is_default', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
