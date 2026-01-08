"""
用户账户模型 - 精臣云资产管理系统
"""
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """自定义用户管理器"""
    
    def create_user(self, username, email=None, password=None, **extra_fields):
        """创建普通用户"""
        if not username:
            raise ValueError('用户名是必填项')
        email = self.normalize_email(email) if email else None
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username, email=None, password=None, **extra_fields):
        """创建超级管理员"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('超级管理员必须设置 is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('超级管理员必须设置 is_superuser=True')
        
        return self.create_user(username, email, password, **extra_fields)


class User(AbstractUser):
    """用户模型"""
    
    class SSOType(models.TextChoices):
        NONE = 'none', '无'
        WEWORK = 'wework', '企业微信'
        DINGTALK = 'dingtalk', '钉钉'
        FEISHU = 'feishu', '飞书'
    
    class Gender(models.TextChoices):
        MALE = 'male', '男'
        FEMALE = 'female', '女'
        UNKNOWN = 'unknown', '未知'
    
    # 基本信息
    employee_no = models.CharField('工号', max_length=50, blank=True, null=True, unique=True)
    phone = models.CharField('手机号码', max_length=20, blank=True, null=True)
    gender = models.CharField('性别', max_length=10, choices=Gender.choices, default=Gender.UNKNOWN)
    avatar = models.URLField('头像', max_length=500, blank=True, null=True)
    nickname = models.CharField('显示名称', max_length=255, blank=True, null=True)
    
    # Multi-company support: User's primary company affiliation
    # 多公司支持：用户的主公司归属
    primary_company = models.ForeignKey(
        'organizations.Company',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='primary_users',
        verbose_name='主公司'
    )
    
    # 组织关系
    department = models.ForeignKey(
        'organizations.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employees',
        verbose_name='主部门',
        help_text='用户的主要部门（可能属于多个部门）'
    )
    # Asset ownership department - for fixed asset management
    # 资产归属部门：用于固定资产归属，当用户属于多部门时指定资产归属的唯一部门
    asset_department = models.ForeignKey(
        'organizations.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='asset_employees',
        verbose_name='资产归属部门',
        help_text='用户资产归属的部门，默认为主部门'
    )
    position = models.CharField('职位', max_length=200, blank=True, null=True)
    
    # SSO 关联
    sso_type = models.CharField('SSO类型', max_length=20, choices=SSOType.choices, default=SSOType.NONE)
    sso_user_id = models.CharField('SSO用户ID', max_length=200, blank=True, null=True)
    wework_user_id = models.CharField('企业微信UserID', max_length=200, blank=True, null=True)
    dingtalk_user_id = models.CharField('钉钉UserID', max_length=200, blank=True, null=True)
    feishu_user_id = models.CharField('飞书UserID', max_length=200, blank=True, null=True)
    
    # 状态和时间
    is_active = models.BooleanField('是否激活', default=True)
    last_login_ip = models.GenericIPAddressField('最后登录IP', blank=True, null=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    objects = UserManager()
    
    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.username} ({self.get_full_name() or '未设置姓名'})"
    
    @property
    def display_name(self):
        """显示名称"""
        return self.nickname or self.get_full_name() or self.username
    
    @display_name.setter
    def display_name(self, value):
        """设置显示名称"""
        self.nickname = value


class Role(models.Model):
    """
    角色模型 - Role with optional company scope
    
    Scope Types:
    - global: Available to all companies (e.g., super admin)
    - company: Company-specific role
    - group: Available to company and its subsidiaries
    """
    
    class RoleScope(models.TextChoices):
        GLOBAL = 'global', '全局角色'      # Available to all companies
        COMPANY = 'company', '公司角色'    # Company-specific
        GROUP = 'group', '集团角色'        # Available to company group
    
    # Company scope support
    scope = models.CharField(
        '角色范围',
        max_length=20,
        choices=RoleScope.choices,
        default=RoleScope.COMPANY
    )
    company = models.ForeignKey(
        'organizations.Company',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='roles',
        verbose_name='所属公司',
        help_text='全局角色无需关联公司'
    )
    
    name = models.CharField('角色名称', max_length=100)
    code = models.CharField('角色代码', max_length=50)
    description = models.TextField('角色描述', blank=True, null=True)
    permissions = models.JSONField('权限配置', default=dict)
    is_system = models.BooleanField('系统角色', default=False)
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '角色'
        verbose_name_plural = '角色'
        ordering = ['name']
        # Allow same code in different companies
        unique_together = ['company', 'code']
        constraints = [
            # Global roles must not have a company
            models.CheckConstraint(
                check=~models.Q(scope='global', company__isnull=False),
                name='global_role_no_company'
            ),
        ]
    
    def __str__(self):
        if self.company:
            return f"{self.name} ({self.company.short_name or self.company.name})"
        return f"{self.name} (全局)"


class UserRole(models.Model):
    """用户角色关联"""
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_roles',
        verbose_name='用户'
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name='user_roles',
        verbose_name='角色'
    )
    department = models.ForeignKey(
        'organizations.Department',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='user_roles',
        verbose_name='部门'
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '用户角色'
        verbose_name_plural = '用户角色'
        unique_together = ['user', 'role', 'department']
    
    def __str__(self):
        return f"{self.user.username} - {self.role.name}"


class OperationLog(models.Model):
    """操作日志"""
    
    class OperationType(models.TextChoices):
        LOGIN = 'login', '登录'
        LOGOUT = 'logout', '登出'
        CREATE = 'create', '创建'
        UPDATE = 'update', '更新'
        DELETE = 'delete', '删除'
        IMPORT = 'import', '导入'
        EXPORT = 'export', '导出'
        APPROVE = 'approve', '审批'
        OTHER = 'other', '其他'
    
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='account_operation_logs',
        verbose_name='操作用户'
    )
    operation_type = models.CharField('操作类型', max_length=20, choices=OperationType.choices)
    module = models.CharField('功能模块', max_length=50)
    description = models.TextField('操作描述')
    request_path = models.CharField('请求路径', max_length=500, blank=True, null=True)
    request_method = models.CharField('请求方法', max_length=10, blank=True, null=True)
    request_body = models.JSONField('请求内容', null=True, blank=True)
    response_status = models.IntegerField('响应状态码', null=True, blank=True)
    ip_address = models.GenericIPAddressField('IP地址', blank=True, null=True)
    user_agent = models.TextField('User Agent', blank=True, null=True)
    created_at = models.DateTimeField('操作时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '操作日志'
        verbose_name_plural = '操作日志'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username if self.user else '未知用户'} - {self.operation_type} - {self.module}"


class UserDepartment(models.Model):
    """
    User's department memberships - supports multi-department scenarios
    用户部门关联 - 支持企业微信等平台一人多部门场景
    
    Business Scenarios:
    1. Multi-department membership from WeWork/DingTalk/Feishu
    2. Track which department is the user's primary department
    3. Track which department should own the user's assets
    
    Asset Management: 
    - User may belong to multiple departments but assets must belong to ONE department
    - asset_department field on User model specifies which department owns assets
    """
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='department_memberships',
        verbose_name='用户'
    )
    department = models.ForeignKey(
        'organizations.Department',
        on_delete=models.CASCADE,
        related_name='user_memberships',
        verbose_name='部门'
    )
    
    # Flags
    is_primary = models.BooleanField('是否主部门', default=False)
    is_leader = models.BooleanField('是否部门负责人', default=False)
    
    # Position in this department (may differ from user's main position)
    position = models.CharField('部门内职位', max_length=200, blank=True, null=True)
    
    # SSO sync metadata
    sso_order = models.IntegerField('SSO部门顺序', default=0, help_text='从SSO平台同步的部门顺序，0表示主部门')
    
    # Metadata
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '用户部门关联'
        verbose_name_plural = '用户部门关联'
        ordering = ['sso_order', 'created_at']
        unique_together = ['user', 'department']
    
    def __str__(self):
        primary_tag = ' (主)' if self.is_primary else ''
        leader_tag = ' [负责人]' if self.is_leader else ''
        return f"{self.user.display_name} - {self.department.name}{primary_tag}{leader_tag}"


class UserCompanyMembership(models.Model):
    """
    User's membership in companies - supports multi-company users
    用户公司关联 - 支持用户在多个公司工作
    
    Business Scenarios:
    1. Primary membership: User's main company affiliation
    2. Secondary membership: User works part-time in another company
    3. Temporary assignment: User is temporarily assigned to another company
    
    Financial Audit: Records effective dates for accurate historical reporting
    """
    
    class MembershipType(models.TextChoices):
        PRIMARY = 'primary', '主公司'        # User's primary company
        SECONDARY = 'secondary', '兼职公司'  # Secondary affiliation
        TEMPORARY = 'temporary', '临时借调'  # Temporary assignment
    
    class DataScope(models.TextChoices):
        ALL = 'all', '全公司'              # Can view all company data
        DEPARTMENT = 'department', '本部门'  # Can only view department data
        SELF = 'self', '仅自己'             # Can only view own data
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='company_memberships',
        verbose_name='用户'
    )
    company = models.ForeignKey(
        'organizations.Company',
        on_delete=models.CASCADE,
        related_name='user_memberships',
        verbose_name='公司'
    )
    department = models.ForeignKey(
        'organizations.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='company_memberships',
        verbose_name='部门'
    )
    
    membership_type = models.CharField(
        '关联类型',
        max_length=20,
        choices=MembershipType.choices,
        default=MembershipType.PRIMARY
    )
    
    # Permission Settings
    is_admin = models.BooleanField('是否公司管理员', default=False)
    can_view_finance = models.BooleanField('可查看财务数据', default=False)
    data_scope = models.CharField(
        '数据范围',
        max_length=20,
        choices=DataScope.choices,
        default=DataScope.SELF
    )
    
    # Audit Trail - For financial reporting accuracy
    start_date = models.DateField('生效日期', auto_now_add=True)
    end_date = models.DateField('失效日期', null=True, blank=True)
    
    # Metadata
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_memberships',
        verbose_name='创建人'
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '用户公司关联'
        verbose_name_plural = '用户公司关联'
        ordering = ['-created_at']
        # A user can have multiple membership types in same company
        unique_together = ['user', 'company', 'membership_type']
    
    def __str__(self):
        return f"{self.user.display_name} - {self.company.name} ({self.get_membership_type_display()})"
    
    @property
    def is_active(self):
        """Check if membership is currently active"""
        from django.utils import timezone
        today = timezone.now().date()
        if self.end_date and self.end_date < today:
            return False
        return True
