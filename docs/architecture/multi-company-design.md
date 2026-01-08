# Multi-Company Architecture Design

## Overview

This document outlines the multi-company architecture design for the Enterprise Fixed Assets Management System (EAMS), supporting various business scenarios including independent companies, shared organizations, and hybrid models.

## Business Scenarios

### Scenario 1: Independent Companies (独立公司模式)
- Multiple completely independent legal entities
- Complete data isolation between companies
- Each company has its own organization structure, users, and assets
- **Use Case**: Different subsidiaries with no operational overlap

### Scenario 2: Shared Organization (共享组织模式)
- Group/holding company structure
- Shared organization structure across multiple companies
- Users can work across multiple companies
- Company-specific asset and financial data
- **Use Case**: One HR department managing multiple legal entities

### Scenario 3: Hybrid Mode (混合模式)
- Some shared elements (certain departments, users)
- Company-specific assets and financial data
- Cross-company asset transfers with audit trail
- **Use Case**: Shared services center model

## Data Model Design

### Company Model
```python
class Company(models.Model):
    """Enterprise/Company - Represents a legal entity"""
    
    class CompanyType(models.TextChoices):
        GROUP = 'group', '集团总部'          # Group headquarters
        SUBSIDIARY = 'subsidiary', '子公司'  # Subsidiary
        BRANCH = 'branch', '分公司'          # Branch
        DEPARTMENT = 'department', '独立核算部门'  # Independent accounting unit
    
    # Hierarchy
    parent = models.ForeignKey('self', null=True, blank=True, 
                               on_delete=models.SET_NULL,
                               related_name='children')
    company_type = models.CharField(max_length=20, choices=CompanyType.choices)
    
    # Organization Mode
    class OrgMode(models.TextChoices):
        INDEPENDENT = 'independent', '独立组织架构'
        SHARED = 'shared', '共享组织架构'
        INHERIT = 'inherit', '继承上级架构'
    
    org_mode = models.CharField(max_length=20, choices=OrgMode.choices, 
                                default=OrgMode.INDEPENDENT)
    
    # Financial Settings
    currency = models.CharField('核算货币', max_length=10, default='CNY')
    fiscal_year_start = models.IntegerField('财年起始月', default=1)
    
    # Basic Info
    name = models.CharField('公司名称', max_length=200)
    code = models.CharField('公司代码', max_length=50, unique=True)
    tax_id = models.CharField('税务登记号', max_length=50, blank=True)
    legal_representative = models.CharField('法人代表', max_length=100, blank=True)
```

### User-Company Relationship
```python
class UserCompanyMembership(models.Model):
    """User's membership in companies - supports multi-company users"""
    
    class MembershipType(models.TextChoices):
        PRIMARY = 'primary', '主公司'     # User's primary company
        SECONDARY = 'secondary', '兼职公司'  # Secondary affiliation
        TEMPORARY = 'temporary', '临时借调'  # Temporary assignment
    
    user = models.ForeignKey('User', on_delete=models.CASCADE,
                             related_name='company_memberships')
    company = models.ForeignKey('Company', on_delete=models.CASCADE,
                                related_name='user_memberships')
    department = models.ForeignKey('Department', on_delete=models.SET_NULL,
                                   null=True, blank=True)
    
    membership_type = models.CharField(max_length=20, choices=MembershipType.choices,
                                       default=MembershipType.PRIMARY)
    
    # Permission Scope
    is_admin = models.BooleanField('是否公司管理员', default=False)
    can_view_finance = models.BooleanField('可查看财务数据', default=False)
    data_scope = models.CharField('数据范围', max_length=20, 
                                  choices=[('all', '全部'), ('department', '本部门'),
                                           ('self', '仅自己')],
                                  default='self')
    
    # Audit
    start_date = models.DateField('生效日期')
    end_date = models.DateField('失效日期', null=True, blank=True)
    created_by = models.ForeignKey('User', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'company', 'membership_type']
```

### Role with Company Scope
```python
class Role(models.Model):
    """Role with optional company scope"""
    
    class RoleScope(models.TextChoices):
        GLOBAL = 'global', '全局角色'       # Available to all companies
        COMPANY = 'company', '公司角色'     # Company-specific
        GROUP = 'group', '集团角色'         # Available to company group
    
    scope = models.CharField(max_length=20, choices=RoleScope.choices,
                             default=RoleScope.COMPANY)
    company = models.ForeignKey('Company', on_delete=models.CASCADE,
                                null=True, blank=True,
                                related_name='roles')
    
    name = models.CharField('角色名称', max_length=100)
    code = models.CharField('角色代码', max_length=50)
    permissions = models.JSONField('权限配置', default=dict)
    
    class Meta:
        unique_together = ['company', 'code']  # Allow same code in different companies
```

### SSO Configuration (Enhanced)
```python
class SSOConfig(models.Model):
    """SSO Configuration per company"""
    
    company = models.ForeignKey('Company', on_delete=models.CASCADE,
                                related_name='sso_configs')
    provider = models.CharField('SSO平台', max_length=20,
                                choices=[('wework', '企业微信'),
                                        ('dingtalk', '钉钉'),
                                        ('feishu', '飞书')])
    
    # Corp Level Settings
    corp_id = models.CharField('企业ID', max_length=200)
    
    # Agent/App Settings
    agent_id = models.CharField('应用ID', max_length=200, blank=True)
    app_secret = models.CharField('应用密钥', max_length=500, blank=True)
    
    # OAuth Settings  
    oauth_enabled = models.BooleanField('启用OAuth登录', default=True)
    callback_url = models.URLField('回调地址', blank=True)
    
    # Sync Settings
    sync_enabled = models.BooleanField('启用同步', default=True)
    sync_departments = models.BooleanField('同步部门', default=True)
    sync_users = models.BooleanField('同步用户', default=True)
    sync_interval = models.IntegerField('同步间隔(分钟)', default=60)
    
    # Department Mapping
    root_department_id = models.CharField('同步根部门ID', max_length=50, blank=True)
    
    # Encrypted secrets (should use encryption in production)
    extra_config = models.JSONField('扩展配置', default=dict)
    
    is_enabled = models.BooleanField('启用状态', default=True)
    
    class Meta:
        unique_together = ['company', 'provider']
```

## Cross-Company Operations

### Asset Transfer Audit Trail
```python
class CrossCompanyTransfer(models.Model):
    """Cross-company asset transfer record for audit"""
    
    class TransferType(models.TextChoices):
        TRANSFER = 'transfer', '调拨'
        LEASE = 'lease', '租借'
        ALLOCATION = 'allocation', '划拨'
    
    transfer_no = models.CharField('调拨单号', max_length=50, unique=True)
    transfer_type = models.CharField(max_length=20, choices=TransferType.choices)
    
    # Source
    from_company = models.ForeignKey('Company', on_delete=models.CASCADE,
                                     related_name='outgoing_transfers')
    from_department = models.ForeignKey('Department', on_delete=models.SET_NULL,
                                        null=True, related_name='+')
    
    # Destination  
    to_company = models.ForeignKey('Company', on_delete=models.CASCADE,
                                   related_name='incoming_transfers')
    to_department = models.ForeignKey('Department', on_delete=models.SET_NULL,
                                      null=True, related_name='+')
    
    # Assets
    assets = models.ManyToManyField('Asset', through='CrossCompanyTransferItem')
    
    # Financial Impact
    transfer_value = models.DecimalField('调拨价值', max_digits=19, decimal_places=4)
    settlement_type = models.CharField('结算方式', max_length=20,
                                       choices=[('internal', '内部划转'),
                                               ('cost_allocation', '费用分摊'),
                                               ('market_price', '市场定价')])
    
    # Audit Fields
    reason = models.TextField('调拨原因')
    approved_by = models.ForeignKey('User', on_delete=models.SET_NULL, null=True)
    approved_at = models.DateTimeField(null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True)
```

## API Design

### Company Context in API Requests
```python
# Request interceptor adds company context
{
    "headers": {
        "X-Company-ID": "1",           # Current company context
        "X-Company-Scope": "group"     # Can access group data
    }
}
```

### Multi-Company Query Filter
```python
class CompanyFilterMixin:
    """Mixin to filter data by company context"""
    
    def get_queryset(self):
        queryset = super().get_queryset()
        company_id = self.request.headers.get('X-Company-ID')
        company_scope = self.request.headers.get('X-Company-Scope', 'self')
        
        if company_scope == 'group':
            # Include parent and sibling companies
            company = Company.objects.get(id=company_id)
            company_ids = self._get_group_company_ids(company)
            return queryset.filter(company_id__in=company_ids)
        else:
            return queryset.filter(company_id=company_id)
```

## Financial Audit Considerations

### Required Audit Fields
```python
class AuditMixin(models.Model):
    """Mixin for financial audit requirements"""
    
    # Standard audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('User', on_delete=models.SET_NULL, null=True)
    
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey('User', on_delete=models.SET_NULL, null=True)
    
    # Company context at creation (for historical accuracy)
    company_at_creation = models.ForeignKey('Company', on_delete=models.PROTECT)
    
    # Soft delete with audit
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True)
    deleted_by = models.ForeignKey('User', on_delete=models.SET_NULL, null=True)
    deletion_reason = models.TextField(blank=True)
    
    class Meta:
        abstract = True
```

### Depreciation across Companies
```python
class DepreciationRecord(models.Model):
    """Depreciation record with company context for financial reporting"""
    
    asset = models.ForeignKey('Asset', on_delete=models.CASCADE)
    company = models.ForeignKey('Company', on_delete=models.CASCADE)  # Owner at time of depreciation
    
    period_start = models.DateField()
    period_end = models.DateField()
    
    depreciation_amount = models.DecimalField(max_digits=19, decimal_places=4)
    accumulated_depreciation = models.DecimalField(max_digits=19, decimal_places=4)
    book_value = models.DecimalField(max_digits=19, decimal_places=4)
    
    # For cross-company transfers
    transfer_adjustment = models.DecimalField(max_digits=19, decimal_places=4, default=0)
    
    class Meta:
        unique_together = ['asset', 'period_start', 'period_end']
```

## Migration Strategy

### Phase 1: Add Company FK to User
1. Add `primary_company` FK to User model
2. Populate based on department.company
3. Create UserCompanyMembership records

### Phase 2: Scope Roles
1. Add `scope` and `company` fields to Role
2. Migrate existing roles to company scope
3. Create global system roles

### Phase 3: SSO Consolidation
1. Move SSO CorpIDs from Company to SSOConfig only
2. Update sync services
3. Update login flow

### Phase 4: Cross-Company Features
1. Add CrossCompanyTransfer model
2. Update transfer workflow
3. Add consolidated reporting

## Configuration Options

### System Settings
```python
MULTI_COMPANY_SETTINGS = {
    # Organization Mode
    'allow_shared_organization': True,
    'allow_user_multi_company': True,
    
    # SSO Settings  
    'sso_auto_create_user': True,
    'sso_auto_assign_department': True,
    
    # Cross-Company
    'allow_cross_company_transfer': True,
    'require_transfer_approval': True,
    
    # Financial
    'track_cross_company_value': True,
    'depreciation_by_company': True,
}
```
