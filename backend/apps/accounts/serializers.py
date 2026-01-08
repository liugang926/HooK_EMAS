"""
用户账户序列化器 - 精臣云资产管理系统
Multi-company architecture support
"""
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from .models import Role, UserRole, OperationLog, UserCompanyMembership, UserDepartment

User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """自定义 JWT 令牌序列化器"""
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # 添加自定义声明
        token['username'] = user.username
        token['email'] = user.email
        token['display_name'] = user.display_name
        return token
    
    def validate(self, attrs):
        data = super().validate(attrs)
        # 添加用户信息
        data['user'] = UserSerializer(self.user).data
        return data


class UserDepartmentSerializer(serializers.ModelSerializer):
    """
    用户部门关联序列化器 - 支持一人多部门场景
    Serializer for user-department relationships (multi-department support)
    """
    
    department_id = serializers.IntegerField(source='department.id', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    department_code = serializers.CharField(source='department.code', read_only=True)
    
    class Meta:
        model = UserDepartment
        fields = [
            'id', 'department', 'department_id', 'department_name', 'department_code',
            'is_primary', 'is_leader', 'position', 'sso_order',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserSerializer(serializers.ModelSerializer):
    """用户序列化器 - Enhanced for multi-company and multi-department support"""
    
    department_name = serializers.CharField(source='department.name', read_only=True)
    primary_company_name = serializers.CharField(source='primary_company.name', read_only=True)
    # Asset department for fixed asset management
    asset_department_name = serializers.CharField(source='asset_department.name', read_only=True)
    # Multi-department memberships
    department_memberships = serializers.SerializerMethodField()
    all_departments = serializers.SerializerMethodField()
    roles = serializers.SerializerMethodField()
    company_memberships = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'employee_no', 'phone', 'gender', 'avatar', 'nickname',
            'primary_company', 'primary_company_name',
            'department', 'department_name',
            'asset_department', 'asset_department_name',
            'department_memberships', 'all_departments',
            'position', 'sso_type', 'is_active', 'last_login', 'created_at',
            'display_name', 'roles', 'company_memberships'
        ]
        read_only_fields = ['id', 'created_at', 'last_login', 'display_name']
    
    def get_department_memberships(self, obj):
        """获取用户所属的所有部门（多部门支持）"""
        memberships = obj.department_memberships.select_related('department').all()
        return [
            {
                'id': m.id,
                'department_id': m.department_id,
                'department_name': m.department.name if m.department else None,
                'department_code': m.department.code if m.department else None,
                'is_primary': m.is_primary,
                'is_leader': m.is_leader,
                'position': m.position,
                'sso_order': m.sso_order
            }
            for m in memberships
        ]
    
    def get_all_departments(self, obj):
        """获取用户所属的所有部门ID列表（简化版）"""
        return list(obj.department_memberships.values_list('department_id', flat=True))
    
    def get_roles(self, obj):
        """获取用户角色列表"""
        user_roles = obj.user_roles.select_related('role').all()
        return [
            {
                'id': ur.role.id,
                'name': ur.role.name,
                'code': ur.role.code
            }
            for ur in user_roles
        ]
    
    def get_company_memberships(self, obj):
        """获取用户公司关联列表"""
        memberships = obj.company_memberships.select_related('company', 'department').filter(
            end_date__isnull=True
        )
        return [
            {
                'id': m.id,
                'company_id': m.company_id,
                'company_name': m.company.name if m.company else None,
                'department_id': m.department_id,
                'department_name': m.department.name if m.department else None,
                'membership_type': m.membership_type,
                'is_admin': m.is_admin,
                'data_scope': m.data_scope
            }
            for m in memberships
        ]


class UserCreateSerializer(serializers.ModelSerializer):
    """用户创建序列化器"""
    
    password = serializers.CharField(write_only=True, min_length=6)
    confirm_password = serializers.CharField(write_only=True, min_length=6)
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'confirm_password',
            'first_name', 'last_name', 'employee_no', 'phone',
            'gender', 'department', 'position'
        ]
    
    def validate(self, attrs):
        if attrs['password'] != attrs.pop('confirm_password'):
            raise serializers.ValidationError({'confirm_password': '两次输入的密码不一致'})
        return attrs
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """用户更新序列化器"""
    
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email', 'phone',
            'gender', 'avatar', 'nickname',
            'department', 'asset_department', 'position'
        ]
    
    def validate_asset_department(self, value):
        """
        Validate asset_department - must be one of user's departments
        资产归属部门必须是用户所属的部门之一
        """
        user = self.instance
        if not user:
            return value
        
        if value is None:
            return value
        
        # Check if the department is in user's department memberships
        user_dept_ids = list(user.department_memberships.values_list('department_id', flat=True))
        
        # Also include the main department
        if user.department_id:
            user_dept_ids.append(user.department_id)
        
        if value.id not in user_dept_ids:
            raise serializers.ValidationError(
                f'资产归属部门必须是用户所属的部门之一。当前可选部门ID: {user_dept_ids}'
            )
        
        return value


class PasswordChangeSerializer(serializers.Serializer):
    """密码修改序列化器"""
    
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=6)
    confirm_password = serializers.CharField(required=True, min_length=6)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({'confirm_password': '两次输入的密码不一致'})
        return attrs
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('原密码错误')
        return value


class RoleSerializer(serializers.ModelSerializer):
    """角色序列化器 - Enhanced for multi-company support"""
    
    user_count = serializers.SerializerMethodField()
    company_name = serializers.CharField(source='company.name', read_only=True)
    scope_display = serializers.CharField(source='get_scope_display', read_only=True)
    
    class Meta:
        model = Role
        fields = [
            'id', 'name', 'code', 'description',
            'scope', 'scope_display', 'company', 'company_name',
            'permissions', 'is_system', 'is_active',
            'created_at', 'updated_at', 'user_count'
        ]
        read_only_fields = ['id', 'is_system', 'created_at', 'updated_at']
    
    def get_user_count(self, obj):
        """获取该角色的用户数量"""
        return obj.user_roles.count()
    
    def validate(self, attrs):
        """Validate role scope and company relationship"""
        scope = attrs.get('scope', self.instance.scope if self.instance else Role.RoleScope.COMPANY)
        company = attrs.get('company', self.instance.company if self.instance else None)
        
        # Global roles should not have a company
        if scope == Role.RoleScope.GLOBAL and company:
            raise serializers.ValidationError({
                'company': '全局角色不能关联公司'
            })
        
        # Company/Group roles must have a company
        if scope in [Role.RoleScope.COMPANY, Role.RoleScope.GROUP] and not company:
            raise serializers.ValidationError({
                'company': '公司角色或集团角色必须关联公司'
            })
        
        return attrs


class UserRoleSerializer(serializers.ModelSerializer):
    """用户角色序列化器"""
    
    user_name = serializers.CharField(source='user.display_name', read_only=True)
    user_position = serializers.CharField(source='user.position', read_only=True)
    user_department = serializers.SerializerMethodField()
    role_name = serializers.CharField(source='role.name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    
    class Meta:
        model = UserRole
        fields = [
            'id', 'user', 'user_name', 'user_position', 'user_department',
            'role', 'role_name', 'department', 'department_name', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_user_department(self, obj):
        """获取用户所属部门名称"""
        if obj.user and obj.user.department:
            return obj.user.department.name
        return None


class OperationLogSerializer(serializers.ModelSerializer):
    """操作日志序列化器"""
    
    user_name = serializers.CharField(source='user.display_name', read_only=True)
    operation_type_display = serializers.CharField(source='get_operation_type_display', read_only=True)
    
    class Meta:
        model = OperationLog
        fields = [
            'id', 'user', 'user_name', 'operation_type',
            'operation_type_display', 'module', 'description',
            'request_path', 'request_method', 'ip_address',
            'created_at'
        ]
        read_only_fields = fields


class UserCompanyMembershipSerializer(serializers.ModelSerializer):
    """
    用户公司关联序列化器
    Serializer for user's company memberships (multi-company support)
    """
    
    user_name = serializers.CharField(source='user.display_name', read_only=True)
    company_name = serializers.CharField(source='company.name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    membership_type_display = serializers.CharField(source='get_membership_type_display', read_only=True)
    data_scope_display = serializers.CharField(source='get_data_scope_display', read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = UserCompanyMembership
        fields = [
            'id', 'user', 'user_name',
            'company', 'company_name',
            'department', 'department_name',
            'membership_type', 'membership_type_display',
            'is_admin', 'can_view_finance',
            'data_scope', 'data_scope_display',
            'start_date', 'end_date', 'is_active',
            'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_active']
    
    def validate(self, attrs):
        """Validate membership data"""
        user = attrs.get('user', self.instance.user if self.instance else None)
        company = attrs.get('company', self.instance.company if self.instance else None)
        membership_type = attrs.get('membership_type', 
                                     self.instance.membership_type if self.instance else 'primary')
        
        # Check for existing primary membership
        if membership_type == UserCompanyMembership.MembershipType.PRIMARY:
            existing = UserCompanyMembership.objects.filter(
                user=user,
                membership_type=UserCompanyMembership.MembershipType.PRIMARY,
                end_date__isnull=True
            ).exclude(pk=self.instance.pk if self.instance else None)
            
            if existing.exists():
                raise serializers.ValidationError({
                    'membership_type': '用户已有主公司关联，请先结束现有关联或选择其他类型'
                })
        
        return attrs


class UserCompanyMembershipCreateSerializer(serializers.ModelSerializer):
    """用户公司关联创建序列化器"""
    
    class Meta:
        model = UserCompanyMembership
        fields = [
            'user', 'company', 'department',
            'membership_type', 'is_admin', 'can_view_finance',
            'data_scope', 'start_date', 'end_date'
        ]
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)
