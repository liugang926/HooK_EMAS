<template>
  <div class="messages-container">
    <el-card class="page-card">
      <template #header>
        <h2>消息设置</h2>
      </template>
      
      <el-tabs v-model="activeTab" tab-position="left">
        <el-tab-pane label="消息模板" name="templates">
          <div class="section-header">
            <h3>消息通知模板</h3>
            <el-button type="primary" size="small" @click="handleAddTemplate">
              <el-icon><Plus /></el-icon>
              新增模板
            </el-button>
          </div>
          
          <el-table :data="templateList">
            <el-table-column prop="name" label="模板名称" min-width="150" />
            <el-table-column prop="type" label="消息类型" width="100" />
            <el-table-column prop="channel" label="发送渠道" width="150">
              <template #default="{ row }">
                <el-tag v-for="c in row.channels" :key="c" size="small" style="margin-right: 4px">{{ c }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="状态" width="80">
              <template #default="{ row }">
                <el-switch v-model="row.enabled" size="small" @change="handleTemplateStatusChange(row)" />
              </template>
            </el-table-column>
            <el-table-column label="操作" width="150">
              <template #default="{ row }">
                <el-button type="primary" link size="small" @click="handleEditTemplate(row)">编辑</el-button>
                <el-button type="danger" link size="small" @click="handleDeleteTemplate(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
        
        <el-tab-pane label="通知渠道" name="channels">
          <h3>通知渠道配置</h3>
          <el-form label-width="120px" style="max-width: 600px">
            <el-divider content-position="left">企业微信</el-divider>
            <el-form-item label="启用状态">
              <el-switch v-model="channels.wework.enabled" />
            </el-form-item>
            <el-form-item label="应用AgentId">
              <el-input v-model="channels.wework.agentId" placeholder="请输入AgentId" />
            </el-form-item>
            
            <el-divider content-position="left">钉钉</el-divider>
            <el-form-item label="启用状态">
              <el-switch v-model="channels.dingtalk.enabled" />
            </el-form-item>
            <el-form-item label="应用AppKey">
              <el-input v-model="channels.dingtalk.appKey" placeholder="请输入AppKey" />
            </el-form-item>
            
            <el-divider content-position="left">飞书</el-divider>
            <el-form-item label="启用状态">
              <el-switch v-model="channels.feishu.enabled" />
            </el-form-item>
            <el-form-item label="App ID">
              <el-input v-model="channels.feishu.appId" placeholder="请输入App ID" />
            </el-form-item>
            
            <el-divider content-position="left">邮件</el-divider>
            <el-form-item label="启用状态">
              <el-switch v-model="channels.email.enabled" />
            </el-form-item>
            <el-form-item label="SMTP服务器">
              <el-input v-model="channels.email.smtp" placeholder="请输入SMTP服务器地址" />
            </el-form-item>
            <el-form-item label="SMTP端口">
              <el-input-number v-model="channels.email.port" :min="1" :max="65535" />
            </el-form-item>
            <el-form-item label="发件人邮箱">
              <el-input v-model="channels.email.sender" placeholder="请输入发件人邮箱" />
            </el-form-item>
            <el-form-item label="邮箱密码">
              <el-input v-model="channels.email.password" type="password" show-password placeholder="请输入邮箱密码或授权码" />
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="saveChannels">保存配置</el-button>
              <el-button @click="testEmail">测试邮件</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
        
        <el-tab-pane label="提醒规则" name="rules">
          <div class="section-header">
            <h3>自动提醒规则</h3>
            <el-button type="primary" size="small" @click="handleAddRule">
              <el-icon><Plus /></el-icon>
              新增规则
            </el-button>
          </div>
          <el-table :data="reminderRules">
            <el-table-column prop="name" label="规则名称" />
            <el-table-column prop="trigger" label="触发条件" />
            <el-table-column prop="receivers" label="接收人" />
            <el-table-column label="状态" width="80">
              <template #default="{ row }">
                <el-switch v-model="row.enabled" size="small" @change="handleRuleStatusChange(row)" />
              </template>
            </el-table-column>
            <el-table-column label="操作" width="120">
              <template #default="{ row }">
                <el-button type="primary" link size="small" @click="handleEditRule(row)">编辑</el-button>
                <el-button type="danger" link size="small" @click="handleDeleteRule(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </el-card>
    
    <!-- 模板弹窗 -->
    <el-dialog v-model="templateDialogVisible" :title="templateDialogTitle" width="600px">
      <el-form :model="templateForm" label-width="100px" :rules="templateRules" ref="templateFormRef">
        <el-form-item label="模板名称" prop="name">
          <el-input v-model="templateForm.name" placeholder="请输入模板名称" />
        </el-form-item>
        <el-form-item label="消息类型" prop="type">
          <el-select v-model="templateForm.type" placeholder="请选择" style="width: 100%">
            <el-option label="系统通知" value="系统通知" />
            <el-option label="待办提醒" value="待办提醒" />
            <el-option label="自动提醒" value="自动提醒" />
          </el-select>
        </el-form-item>
        <el-form-item label="发送渠道" prop="channels">
          <el-checkbox-group v-model="templateForm.channels">
            <el-checkbox label="企业微信" />
            <el-checkbox label="钉钉" />
            <el-checkbox label="飞书" />
            <el-checkbox label="邮件" />
          </el-checkbox-group>
        </el-form-item>
        <el-form-item label="消息内容" prop="content">
          <el-input v-model="templateForm.content" type="textarea" :rows="4" placeholder="请输入消息内容模板，支持变量如 ${assetName}、${userName}" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="templateDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveTemplate">保存</el-button>
      </template>
    </el-dialog>
    
    <!-- 规则弹窗 -->
    <el-dialog v-model="ruleDialogVisible" :title="ruleDialogTitle" width="600px">
      <el-form :model="ruleForm" label-width="100px" :rules="ruleRules" ref="ruleFormRef">
        <el-form-item label="规则名称" prop="name">
          <el-input v-model="ruleForm.name" placeholder="请输入规则名称" />
        </el-form-item>
        <el-form-item label="触发条件" prop="trigger">
          <el-select v-model="ruleForm.triggerType" placeholder="请选择触发类型" style="width: 200px; margin-right: 12px">
            <el-option label="维保到期前" value="maintenance_expire" />
            <el-option label="库存低于" value="stock_low" />
            <el-option label="资产闲置超过" value="asset_idle" />
          </el-select>
          <el-input-number v-model="ruleForm.triggerValue" :min="1" style="width: 100px" />
          <span style="margin-left: 8px">{{ ruleForm.triggerType === 'stock_low' ? '件' : '天' }}</span>
        </el-form-item>
        <el-form-item label="接收人" prop="receivers">
          <el-select v-model="ruleForm.receivers" placeholder="请选择接收人" style="width: 100%">
            <el-option label="资产管理员" value="资产管理员" />
            <el-option label="耗材管理员" value="耗材管理员" />
            <el-option label="部门主管" value="部门主管" />
            <el-option label="资产使用人" value="资产使用人" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="ruleDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveRule">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const activeTab = ref('templates')
const templateFormRef = ref()
const ruleFormRef = ref()

const templateList = ref([
  { id: 1, name: '资产领用通知', type: '系统通知', channels: ['企业微信', '邮件'], enabled: true, content: '您申请的资产 ${assetName} 已通过审批' },
  { id: 2, name: '审批待办提醒', type: '待办提醒', channels: ['企业微信'], enabled: true, content: '您有新的审批待办：${taskName}' },
  { id: 3, name: '资产到期提醒', type: '自动提醒', channels: ['邮件'], enabled: true, content: '资产 ${assetName} 将于 ${expireDate} 到期' }
])

const channels = reactive({
  wework: { enabled: true, agentId: '1000001' },
  dingtalk: { enabled: false, appKey: '' },
  feishu: { enabled: false, appId: '' },
  email: { enabled: true, smtp: 'smtp.company.com', port: 465, sender: 'asset@company.com', password: '' }
})

const reminderRules = ref([
  { id: 1, name: '资产维保到期提醒', trigger: '维保到期前7天', triggerType: 'maintenance_expire', triggerValue: 7, receivers: '资产管理员', enabled: true },
  { id: 2, name: '库存预警提醒', trigger: '库存低于安全线', triggerType: 'stock_low', triggerValue: 10, receivers: '耗材管理员', enabled: true },
  { id: 3, name: '资产闲置提醒', trigger: '闲置超过30天', triggerType: 'asset_idle', triggerValue: 30, receivers: '部门主管', enabled: false }
])

// 模板弹窗
const templateDialogVisible = ref(false)
const templateDialogTitle = ref('新增模板')
const templateForm = reactive({
  id: null,
  name: '',
  type: '',
  channels: [],
  content: ''
})

const templateRules = {
  name: [{ required: true, message: '请输入模板名称', trigger: 'blur' }],
  type: [{ required: true, message: '请选择消息类型', trigger: 'change' }],
  channels: [{ required: true, type: 'array', min: 1, message: '请选择至少一个发送渠道', trigger: 'change' }]
}

// 规则弹窗
const ruleDialogVisible = ref(false)
const ruleDialogTitle = ref('新增规则')
const ruleForm = reactive({
  id: null,
  name: '',
  triggerType: '',
  triggerValue: 7,
  receivers: ''
})

const ruleRules = {
  name: [{ required: true, message: '请输入规则名称', trigger: 'blur' }],
  receivers: [{ required: true, message: '请选择接收人', trigger: 'change' }]
}

let idCounter = 100

function handleAddTemplate() {
  templateDialogTitle.value = '新增模板'
  Object.assign(templateForm, { id: null, name: '', type: '', channels: [], content: '' })
  templateDialogVisible.value = true
}

function handleEditTemplate(row) {
  templateDialogTitle.value = '编辑模板'
  Object.assign(templateForm, { id: row.id, name: row.name, type: row.type, channels: [...row.channels], content: row.content })
  templateDialogVisible.value = true
}

function handleDeleteTemplate(row) {
  ElMessageBox.confirm(`确定要删除模板 "${row.name}" 吗？`, '删除确认', {
    confirmButtonText: '确定删除',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    const index = templateList.value.findIndex(item => item.id === row.id)
    if (index !== -1) templateList.value.splice(index, 1)
    ElMessage.success('删除成功')
  }).catch(() => {})
}

function handleTemplateStatusChange(row) {
  ElMessage.success(`模板 "${row.name}" 已${row.enabled ? '启用' : '停用'}`)
}

function saveTemplate() {
  templateFormRef.value?.validate((valid) => {
    if (valid) {
      if (templateForm.id) {
        const index = templateList.value.findIndex(item => item.id === templateForm.id)
        if (index !== -1) Object.assign(templateList.value[index], templateForm)
        ElMessage.success('模板编辑成功')
      } else {
        templateList.value.push({ ...templateForm, id: ++idCounter, enabled: true })
        ElMessage.success('模板新增成功')
      }
      templateDialogVisible.value = false
    }
  })
}

function handleAddRule() {
  ruleDialogTitle.value = '新增规则'
  Object.assign(ruleForm, { id: null, name: '', triggerType: '', triggerValue: 7, receivers: '' })
  ruleDialogVisible.value = true
}

function handleEditRule(row) {
  ruleDialogTitle.value = '编辑规则'
  Object.assign(ruleForm, { id: row.id, name: row.name, triggerType: row.triggerType, triggerValue: row.triggerValue, receivers: row.receivers })
  ruleDialogVisible.value = true
}

function handleDeleteRule(row) {
  ElMessageBox.confirm(`确定要删除规则 "${row.name}" 吗？`, '删除确认', {
    confirmButtonText: '确定删除',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    const index = reminderRules.value.findIndex(item => item.id === row.id)
    if (index !== -1) reminderRules.value.splice(index, 1)
    ElMessage.success('删除成功')
  }).catch(() => {})
}

function handleRuleStatusChange(row) {
  ElMessage.success(`规则 "${row.name}" 已${row.enabled ? '启用' : '停用'}`)
}

function saveRule() {
  ruleFormRef.value?.validate((valid) => {
    if (valid) {
      const triggerMap = {
        maintenance_expire: `维保到期前${ruleForm.triggerValue}天`,
        stock_low: `库存低于${ruleForm.triggerValue}件`,
        asset_idle: `闲置超过${ruleForm.triggerValue}天`
      }
      if (ruleForm.id) {
        const index = reminderRules.value.findIndex(item => item.id === ruleForm.id)
        if (index !== -1) {
          Object.assign(reminderRules.value[index], { ...ruleForm, trigger: triggerMap[ruleForm.triggerType] })
        }
        ElMessage.success('规则编辑成功')
      } else {
        reminderRules.value.push({ ...ruleForm, id: ++idCounter, trigger: triggerMap[ruleForm.triggerType], enabled: true })
        ElMessage.success('规则新增成功')
      }
      ruleDialogVisible.value = false
    }
  })
}

function saveChannels() {
  ElMessage.success('通知渠道配置保存成功')
}

function testEmail() {
  if (!channels.email.smtp || !channels.email.sender) {
    ElMessage.warning('请先配置SMTP服务器和发件人邮箱')
    return
  }
  ElMessage.success('测试邮件发送成功')
}
</script>

<style lang="scss" scoped>
.messages-container {
  .page-card { border-radius: 16px; h2 { margin: 0; font-size: 18px; color: #1f2937; } }
  .section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; h3 { margin: 0; } }
  h3 { font-size: 16px; margin: 0 0 16px; color: #1f2937; }
}
</style>
