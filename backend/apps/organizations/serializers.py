"""
组织架构序列化器 - 精臣云资产管理系统
Multi-company architecture support
"""
from rest_framework import serializers
from .models import Company, Department, Location, OrganizationChange, CrossCompanyTransfer, CrossCompanyTransferItem


class CompanySerializer(serializers.ModelSerializer):
    """公司序列化器 - Enhanced for multi-company hierarchy"""
    
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    company_type_display = serializers.CharField(source='get_company_type_display', read_only=True)
    org_mode_display = serializers.CharField(source='get_org_mode_display', read_only=True)
    children_count = serializers.SerializerMethodField()
    is_group_root = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Company
        fields = [
            'id', 'name', 'code', 'short_name', 'logo',
            'address', 'phone', 'email', 'website', 'description',
            # Hierarchy
            'parent', 'parent_name', 'company_type', 'company_type_display',
            'org_mode', 'org_mode_display',
            # Financial
            'tax_id', 'legal_representative', 'currency', 'fiscal_year_start',
            # SSO (deprecated, kept for backwards compatibility)
            'wework_corp_id', 'dingtalk_corp_id', 'feishu_corp_id',
            # Status
            'is_active', 'is_group_root', 'children_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_group_root']
    
    def get_children_count(self, obj):
        """Get count of child companies"""
        return obj.children.filter(is_active=True).count()


class CompanyTreeSerializer(serializers.ModelSerializer):
    """公司树形结构序列化器 - For group hierarchy display"""
    
    children = serializers.SerializerMethodField()
    company_type_display = serializers.CharField(source='get_company_type_display', read_only=True)
    
    class Meta:
        model = Company
        fields = [
            'id', 'name', 'code', 'short_name',
            'company_type', 'company_type_display',
            'is_active', 'children'
        ]
    
    def get_children(self, obj):
        children = obj.children.filter(is_active=True).order_by('name')
        return CompanyTreeSerializer(children, many=True).data


class CompanyListSerializer(serializers.ModelSerializer):
    """公司列表简化序列化器"""
    
    class Meta:
        model = Company
        fields = ['id', 'name', 'code', 'short_name', 'is_active']


class DepartmentSerializer(serializers.ModelSerializer):
    """部门序列化器"""
    
    company_name = serializers.CharField(source='company.name', read_only=True)
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    manager_name = serializers.CharField(source='manager.display_name', read_only=True)
    children_count = serializers.SerializerMethodField()
    employee_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Department
        fields = [
            'id', 'company', 'company_name', 'name', 'code',
            'parent', 'parent_name', 'manager', 'manager_name',
            'description', 'sort_order', 'full_name',
            'children_count', 'employee_count',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'full_name', 'created_at', 'updated_at']
    
    def get_children_count(self, obj):
        return obj.get_children().count()
    
    def get_employee_count(self, obj):
        return obj.employees.count()


class DepartmentTreeSerializer(serializers.ModelSerializer):
    """部门树形序列化器"""
    
    children = serializers.SerializerMethodField()
    employee_count = serializers.SerializerMethodField()
    total_employee_count = serializers.SerializerMethodField()
    manager_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Department
        fields = [
            'id', 'name', 'code', 'parent', 'sort_order',
            'is_active', 'children', 'employee_count', 'total_employee_count',
            'manager', 'manager_name'
        ]
    
    def get_manager_name(self, obj):
        """获取部门负责人姓名"""
        if obj.manager:
            return obj.manager.nickname or obj.manager.display_name or obj.manager.get_full_name() or obj.manager.username
        return None
    
    def get_children(self, obj):
        children = obj.get_children().filter(is_active=True).order_by('sort_order', 'name')
        return DepartmentTreeSerializer(children, many=True).data
    
    def get_employee_count(self, obj):
        """当前部门的直属员工数"""
        return obj.employees.filter(is_active=True).count()
    
    def get_total_employee_count(self, obj):
        """递归计算包含子部门的总员工数"""
        count = obj.employees.filter(is_active=True).count()
        for child in obj.get_children().filter(is_active=True):
            count += self._get_recursive_employee_count(child)
        return count
    
    def _get_recursive_employee_count(self, dept):
        """递归计算子部门员工数"""
        count = dept.employees.filter(is_active=True).count()
        for child in dept.get_children().filter(is_active=True):
            count += self._get_recursive_employee_count(child)
        return count


class LocationSerializer(serializers.ModelSerializer):
    """存放区域序列化器"""
    
    company_name = serializers.CharField(source='company.name', read_only=True, default='')
    parent_name = serializers.CharField(source='parent.name', read_only=True, default='')
    children_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Location
        fields = [
            'id', 'company', 'company_name', 'name', 'code',
            'parent', 'parent_name', 'address', 'description',
            'sort_order', 'full_name', 'children_count',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'company', 'full_name', 'created_at', 'updated_at']
    
    def get_children_count(self, obj):
        return obj.get_children().count()


class LocationTreeSerializer(serializers.ModelSerializer):
    """存放区域树形序列化器"""
    
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = Location
        fields = [
            'id', 'name', 'code', 'parent', 'sort_order',
            'is_active', 'children'
        ]
    
    def get_children(self, obj):
        children = obj.get_children().filter(is_active=True)
        return LocationTreeSerializer(children, many=True).data


class OrganizationChangeSerializer(serializers.ModelSerializer):
    """组织异动序列化器"""
    
    department_name = serializers.CharField(source='department.name', read_only=True)
    change_type_display = serializers.CharField(source='get_change_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.display_name', read_only=True)
    processed_by_name = serializers.CharField(source='processed_by.display_name', read_only=True)
    
    class Meta:
        model = OrganizationChange
        fields = [
            'id', 'department', 'department_name', 'change_type',
            'change_type_display', 'status', 'status_display',
            'old_data', 'new_data', 'description',
            'created_by', 'created_by_name',
            'processed_by', 'processed_by_name',
            'created_at', 'processed_at'
        ]
        read_only_fields = ['id', 'created_at', 'processed_at']


# =============================================================================
# Cross-Company Transfer Serializers (Financial Audit)
# =============================================================================

class CrossCompanyTransferItemSerializer(serializers.ModelSerializer):
    """跨公司调拨明细序列化器"""
    
    asset_name = serializers.CharField(source='asset.name', read_only=True)
    asset_code = serializers.CharField(source='asset.asset_code', read_only=True)
    
    class Meta:
        model = CrossCompanyTransferItem
        fields = [
            'id', 'transfer', 'asset', 'asset_name', 'asset_code',
            'original_value', 'book_value', 'transfer_price',
            'asset_snapshot', 'remark', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class CrossCompanyTransferSerializer(serializers.ModelSerializer):
    """
    跨公司调拨序列化器
    For financial audit trail of cross-company asset transfers
    """
    
    # Read-only display fields
    from_company_name = serializers.CharField(source='from_company.name', read_only=True)
    to_company_name = serializers.CharField(source='to_company.name', read_only=True)
    from_department_name = serializers.CharField(source='from_department.name', read_only=True)
    to_department_name = serializers.CharField(source='to_department.name', read_only=True)
    
    transfer_type_display = serializers.CharField(source='get_transfer_type_display', read_only=True)
    settlement_type_display = serializers.CharField(source='get_settlement_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    from_approver_name = serializers.CharField(source='from_approver.display_name', read_only=True)
    to_approver_name = serializers.CharField(source='to_approver.display_name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.display_name', read_only=True)
    
    # Nested items
    items = CrossCompanyTransferItemSerializer(many=True, read_only=True)
    items_count = serializers.SerializerMethodField()
    
    class Meta:
        model = CrossCompanyTransfer
        fields = [
            'id', 'transfer_no',
            'transfer_type', 'transfer_type_display',
            # Source
            'from_company', 'from_company_name',
            'from_department', 'from_department_name',
            # Destination
            'to_company', 'to_company_name',
            'to_department', 'to_department_name',
            # Financial
            'transfer_value', 'settlement_type', 'settlement_type_display',
            'settlement_amount', 'settlement_date',
            # Status
            'status', 'status_display',
            'reason', 'remark',
            # Approval
            'from_approver', 'from_approver_name', 'from_approved_at',
            'to_approver', 'to_approver_name', 'to_approved_at',
            # Audit
            'created_by', 'created_by_name',
            'created_at', 'updated_at', 'completed_at',
            # Items
            'items', 'items_count'
        ]
        read_only_fields = [
            'id', 'transfer_no', 'created_at', 'updated_at',
            'from_approved_at', 'to_approved_at', 'completed_at'
        ]
    
    def get_items_count(self, obj):
        return obj.items.count()


class CrossCompanyTransferCreateSerializer(serializers.ModelSerializer):
    """跨公司调拨创建序列化器"""
    
    asset_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        help_text='待调拨资产ID列表'
    )
    
    class Meta:
        model = CrossCompanyTransfer
        fields = [
            'transfer_type', 'from_company', 'from_department',
            'to_company', 'to_department',
            'settlement_type', 'reason', 'remark',
            'asset_ids'
        ]
    
    def validate(self, attrs):
        """Validate transfer data"""
        from_company = attrs.get('from_company')
        to_company = attrs.get('to_company')
        
        if from_company == to_company:
            raise serializers.ValidationError({
                'to_company': '调出公司和调入公司不能相同，请使用普通调拨功能'
            })
        
        return attrs
    
    def create(self, validated_data):
        asset_ids = validated_data.pop('asset_ids', [])
        validated_data['created_by'] = self.context['request'].user
        validated_data['status'] = CrossCompanyTransfer.Status.DRAFT
        
        transfer = CrossCompanyTransfer.objects.create(**validated_data)
        
        # Create transfer items
        from apps.assets.models import Asset
        assets = Asset.objects.filter(id__in=asset_ids)
        
        for asset in assets:
            CrossCompanyTransferItem.objects.create(
                transfer=transfer,
                asset=asset,
                original_value=asset.original_value,
                book_value=asset.net_value if hasattr(asset, 'net_value') else asset.original_value,
                transfer_price=asset.original_value,
                asset_snapshot={
                    'name': asset.name,
                    'asset_code': asset.asset_code,
                    'category_name': asset.category.name if asset.category else None,
                    'location_name': asset.location.name if asset.location else None,
                    'using_department_name': asset.using_department.name if asset.using_department else None,
                    'using_user_name': asset.using_user.display_name if asset.using_user else None,
                    'status': asset.status,
                    'original_value': str(asset.original_value) if asset.original_value else None,
                }
            )
        
        # Calculate total transfer value
        transfer.transfer_value = sum(
            item.transfer_price for item in transfer.items.all()
        )
        transfer.save()
        
        return transfer
