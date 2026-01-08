"""
审批流程模型 - 精臣云资产管理系统
"""
from django.db import models


class WorkflowTemplate(models.Model):
    """审批流程模板"""
    
    class BusinessType(models.TextChoices):
        ASSET_RECEIVE = 'asset_receive', '资产领用'
        ASSET_RETURN = 'asset_return', '资产退还'
        ASSET_BORROW = 'asset_borrow', '资产借用'
        ASSET_GIVE_BACK = 'asset_give_back', '资产归还'
        ASSET_TRANSFER = 'asset_transfer', '资产调拨'
        ASSET_DISPOSAL = 'asset_disposal', '资产处置'
        ASSET_CHANGE = 'asset_change', '资产变更'
        PURCHASE_REQUEST = 'purchase_request', '采购申请'
        CONSUMABLE_RECEIVE = 'consumable_receive', '耗材领用'
    
    company = models.ForeignKey(
        'organizations.Company',
        on_delete=models.CASCADE,
        related_name='workflow_templates',
        verbose_name='所属公司'
    )
    name = models.CharField('模板名称', max_length=100)
    business_type = models.CharField('业务类型', max_length=30, choices=BusinessType.choices)
    description = models.TextField('描述', blank=True, null=True)
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '审批流程模板'
        verbose_name_plural = '审批流程模板'
    
    def __str__(self):
        return f"{self.name} ({self.get_business_type_display()})"


class WorkflowNode(models.Model):
    """审批节点"""
    
    class NodeType(models.TextChoices):
        START = 'start', '开始节点'
        APPROVAL = 'approval', '审批节点'
        CC = 'cc', '抄送节点'
        CONDITION = 'condition', '条件节点'
        END = 'end', '结束节点'
    
    class ApproverType(models.TextChoices):
        FIXED = 'fixed', '指定人员'
        ROLE = 'role', '指定角色'
        DEPARTMENT_MANAGER = 'department_manager', '部门主管'
        SUPERIOR = 'superior', '直接上级'
        SELF = 'self', '发起人自己'
    
    template = models.ForeignKey(
        WorkflowTemplate,
        on_delete=models.CASCADE,
        related_name='nodes',
        verbose_name='流程模板'
    )
    name = models.CharField('节点名称', max_length=100)
    node_type = models.CharField('节点类型', max_length=20, choices=NodeType.choices)
    approver_type = models.CharField('审批人类型', max_length=30, choices=ApproverType.choices, blank=True, null=True)
    
    # 审批人配置
    approvers = models.ManyToManyField(
        'accounts.User',
        blank=True,
        related_name='workflow_nodes',
        verbose_name='审批人'
    )
    roles = models.ManyToManyField(
        'accounts.Role',
        blank=True,
        related_name='workflow_nodes',
        verbose_name='审批角色'
    )
    
    # 条件配置
    conditions = models.JSONField('条件配置', default=dict)
    
    # 节点顺序
    sort_order = models.IntegerField('排序', default=0)
    next_node = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='prev_nodes',
        verbose_name='下一节点'
    )
    
    class Meta:
        verbose_name = '审批节点'
        verbose_name_plural = '审批节点'
        ordering = ['sort_order']
    
    def __str__(self):
        return f"{self.template.name} - {self.name}"


class WorkflowInstance(models.Model):
    """审批流程实例"""
    
    class Status(models.TextChoices):
        PENDING = 'pending', '审批中'
        APPROVED = 'approved', '已通过'
        REJECTED = 'rejected', '已拒绝'
        CANCELLED = 'cancelled', '已撤销'
    
    template = models.ForeignKey(
        WorkflowTemplate,
        on_delete=models.SET_NULL,
        null=True,
        related_name='instances',
        verbose_name='流程模板'
    )
    business_type = models.CharField('业务类型', max_length=30)
    business_id = models.IntegerField('业务ID')
    business_no = models.CharField('业务单号', max_length=50)
    title = models.CharField('审批标题', max_length=200)
    status = models.CharField('状态', max_length=20, choices=Status.choices, default=Status.PENDING)
    
    current_node = models.ForeignKey(
        WorkflowNode,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='current_instances',
        verbose_name='当前节点'
    )
    
    initiator = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='initiated_workflows',
        verbose_name='发起人'
    )
    created_at = models.DateTimeField('发起时间', auto_now_add=True)
    completed_at = models.DateTimeField('完成时间', null=True, blank=True)
    
    class Meta:
        verbose_name = '审批流程实例'
        verbose_name_plural = '审批流程实例'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"


class WorkflowTask(models.Model):
    """审批任务"""
    
    class Status(models.TextChoices):
        PENDING = 'pending', '待处理'
        APPROVED = 'approved', '已通过'
        REJECTED = 'rejected', '已拒绝'
        TRANSFERRED = 'transferred', '已转交'
        CANCELLED = 'cancelled', '已取消'
    
    instance = models.ForeignKey(
        WorkflowInstance,
        on_delete=models.CASCADE,
        related_name='tasks',
        verbose_name='流程实例'
    )
    node = models.ForeignKey(
        WorkflowNode,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='审批节点'
    )
    assignee = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='workflow_tasks',
        verbose_name='审批人'
    )
    status = models.CharField('状态', max_length=20, choices=Status.choices, default=Status.PENDING)
    comment = models.TextField('审批意见', blank=True, null=True)
    
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    completed_at = models.DateTimeField('处理时间', null=True, blank=True)
    
    class Meta:
        verbose_name = '审批任务'
        verbose_name_plural = '审批任务'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.instance.title} - {self.assignee.display_name if self.assignee else '未指定'}"
