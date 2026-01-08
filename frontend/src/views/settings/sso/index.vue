<template>
  <div class="sso-container">
    <el-card class="page-card">
      <template #header>
        <div class="page-header">
          <div class="header-left">
            <h2>SSO单点登录配置</h2>
            <el-select
              v-model="selectedCompanyId"
              placeholder="选择公司"
              style="width: 200px; margin-left: 16px"
              @change="handleCompanyChange"
            >
              <el-option
                v-for="company in companies"
                :key="company.id"
                :label="company.name"
                :value="company.id"
              />
            </el-select>
          </div>
          <el-button type="primary" @click="openSyncDialog">
            <el-icon><Refresh /></el-icon>
            立即同步
          </el-button>
        </div>
      </template>
      
      <el-tabs v-model="activeTab" type="border-card">
        <!-- 企业微信 -->
        <el-tab-pane name="wework">
          <template #label>
            <span class="tab-label">
              <img src="data:image/svg+xml,%3Csvg viewBox='0 0 24 24' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath fill='%2307C160' d='M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2z'/%3E%3C/svg%3E" class="platform-icon" />
              企业微信
            </span>
          </template>
          
          <div class="config-section">
            <el-row :gutter="40">
              <el-col :span="14">
                <el-form :model="weworkConfig" label-width="140px" :rules="configRules" ref="weworkFormRef">
                  <el-divider content-position="left">基本配置</el-divider>
                  <el-form-item label="启用状态">
                    <el-switch v-model="weworkConfig.enabled" active-text="启用" inactive-text="禁用" />
                  </el-form-item>
                  <el-form-item label="企业ID" prop="corpId">
                    <el-input v-model="weworkConfig.corpId" placeholder="请输入企业ID (CorpID)" />
                  </el-form-item>
                  <el-form-item label="应用AgentId" prop="agentId">
                    <el-input v-model="weworkConfig.agentId" placeholder="请输入应用AgentId" />
                  </el-form-item>
                  <el-form-item label="应用Secret" prop="secret">
                    <el-input v-model="weworkConfig.secret" type="password" show-password placeholder="请输入应用Secret" />
                  </el-form-item>
                  <el-form-item label="通讯录Secret" prop="contactSecret">
                    <el-input v-model="weworkConfig.contactSecret" type="password" show-password placeholder="请输入通讯录同步Secret" />
                  </el-form-item>
                  
                  <el-divider content-position="left">OAuth配置</el-divider>
                  <el-form-item label="启用OAuth登录">
                    <el-switch v-model="weworkConfig.oauthEnabled" />
                  </el-form-item>
                  <el-form-item label="回调地址">
                    <el-input v-model="weworkConfig.callbackUrl" placeholder="https://your-domain.com/api/sso/callback/wework" />
                  </el-form-item>
                  
                  <el-divider content-position="left">同步配置</el-divider>
                  <el-form-item label="启用数据同步">
                    <el-switch v-model="weworkConfig.syncEnabled" />
                  </el-form-item>
                  <el-form-item label="同步部门">
                    <el-switch v-model="weworkConfig.syncDepartments" :disabled="!weworkConfig.syncEnabled" />
                  </el-form-item>
                  <el-form-item label="同步用户">
                    <el-switch v-model="weworkConfig.syncUsers" :disabled="!weworkConfig.syncEnabled" />
                  </el-form-item>
                  <el-form-item label="同步根部门ID">
                    <el-input v-model="weworkConfig.rootDepartmentId" placeholder="留空表示同步全部" :disabled="!weworkConfig.syncEnabled" />
                    <span style="color: #9ca3af; font-size: 12px">仅同步该部门及其子部门</span>
                  </el-form-item>
                  <el-form-item label="同步间隔(分钟)">
                    <el-input-number v-model="weworkConfig.syncInterval" :min="0" :max="1440" :disabled="!weworkConfig.syncEnabled" />
                    <span style="margin-left: 12px; color: #9ca3af; font-size: 12px">设为0禁用自动同步</span>
                  </el-form-item>
                  
                  <el-divider content-position="left">用户创建配置</el-divider>
                  <el-form-item label="自动创建用户">
                    <el-switch v-model="weworkConfig.autoCreateUser" />
                    <span style="margin-left: 12px; color: #9ca3af; font-size: 12px">首次登录自动创建</span>
                  </el-form-item>
                  <el-form-item label="自动创建部门">
                    <el-switch v-model="weworkConfig.autoCreateDepartment" />
                  </el-form-item>
                  <el-form-item label="默认角色">
                    <el-select v-model="weworkConfig.defaultRoleId" placeholder="选择新用户默认角色" clearable style="width: 200px">
                      <el-option v-for="role in roles" :key="role.id" :label="role.name" :value="role.id" />
                    </el-select>
                  </el-form-item>
                  
                  <el-form-item>
                    <el-button type="primary" @click="saveWeworkConfig">保存配置</el-button>
                    <el-button @click="testWeworkConnection">测试连接</el-button>
                  </el-form-item>
                </el-form>
              </el-col>
              <el-col :span="10">
                <div class="help-section">
                  <h4><el-icon><InfoFilled /></el-icon> 配置说明</h4>
                  <ol>
                    <li>登录<a href="https://work.weixin.qq.com" target="_blank">企业微信管理后台</a></li>
                    <li>在「应用管理」创建自建应用</li>
                    <li>获取企业ID、应用AgentId和Secret</li>
                    <li>在「管理工具」-「通讯录同步」获取通讯录Secret</li>
                    <li>配置可信域名和回调地址</li>
                  </ol>
                </div>
              </el-col>
            </el-row>
          </div>
        </el-tab-pane>
        
        <!-- 钉钉 -->
        <el-tab-pane name="dingtalk">
          <template #label>
            <span class="tab-label">
              <img src="data:image/svg+xml,%3Csvg viewBox='0 0 24 24' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath fill='%230089FF' d='M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2z'/%3E%3C/svg%3E" class="platform-icon" />
              钉钉
            </span>
          </template>
          
          <div class="config-section">
            <el-row :gutter="40">
              <el-col :span="14">
                <el-form :model="dingtalkConfig" label-width="120px" :rules="configRules" ref="dingtalkFormRef">
                  <el-form-item label="启用状态">
                    <el-switch v-model="dingtalkConfig.enabled" active-text="启用" inactive-text="禁用" />
                  </el-form-item>
                  <el-form-item label="AppKey" prop="appKey">
                    <el-input v-model="dingtalkConfig.appKey" placeholder="请输入AppKey" />
                  </el-form-item>
                  <el-form-item label="AppSecret" prop="appSecret">
                    <el-input v-model="dingtalkConfig.appSecret" type="password" show-password placeholder="请输入AppSecret" />
                  </el-form-item>
                  <el-form-item label="AgentId" prop="agentId">
                    <el-input v-model="dingtalkConfig.agentId" placeholder="请输入AgentId" />
                  </el-form-item>
                  <el-form-item label="CorpId" prop="corpId">
                    <el-input v-model="dingtalkConfig.corpId" placeholder="请输入CorpId" />
                  </el-form-item>
                  <el-form-item label="回调域名">
                    <el-input v-model="dingtalkConfig.callbackUrl" placeholder="https://your-domain.com" />
                  </el-form-item>
                  <el-form-item label="自动同步">
                    <el-switch v-model="dingtalkConfig.autoSync" />
                    <span style="margin-left: 12px; color: #9ca3af; font-size: 12px">开启后每天自动同步组织架构</span>
                  </el-form-item>
                  <el-form-item>
                    <el-button type="primary" @click="saveDingtalkConfig">保存配置</el-button>
                    <el-button @click="testDingtalkConnection">测试连接</el-button>
                  </el-form-item>
                </el-form>
              </el-col>
              <el-col :span="10">
                <div class="help-section">
                  <h4><el-icon><InfoFilled /></el-icon> 配置说明</h4>
                  <ol>
                    <li>登录<a href="https://open.dingtalk.com" target="_blank">钉钉开放平台</a></li>
                    <li>创建企业内部应用</li>
                    <li>在应用信息中获取AppKey和AppSecret</li>
                    <li>获取AgentId和CorpId</li>
                    <li>配置回调域名白名单</li>
                  </ol>
                </div>
              </el-col>
            </el-row>
          </div>
        </el-tab-pane>
        
        <!-- 飞书 -->
        <el-tab-pane name="feishu">
          <template #label>
            <span class="tab-label">
              <img src="data:image/svg+xml,%3Csvg viewBox='0 0 24 24' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath fill='%233370FF' d='M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2z'/%3E%3C/svg%3E" class="platform-icon" />
              飞书
            </span>
          </template>
          
          <div class="config-section">
            <el-row :gutter="40">
              <el-col :span="14">
                <el-form :model="feishuConfig" label-width="120px" :rules="configRules" ref="feishuFormRef">
                  <el-form-item label="启用状态">
                    <el-switch v-model="feishuConfig.enabled" active-text="启用" inactive-text="禁用" />
                  </el-form-item>
                  <el-form-item label="App ID" prop="appId">
                    <el-input v-model="feishuConfig.appId" placeholder="请输入App ID" />
                  </el-form-item>
                  <el-form-item label="App Secret" prop="appSecret">
                    <el-input v-model="feishuConfig.appSecret" type="password" show-password placeholder="请输入App Secret" />
                  </el-form-item>
                  <el-form-item label="Encrypt Key">
                    <el-input v-model="feishuConfig.encryptKey" type="password" show-password placeholder="请输入Encrypt Key (可选)" />
                  </el-form-item>
                  <el-form-item label="Verification Token">
                    <el-input v-model="feishuConfig.verificationToken" placeholder="请输入Verification Token (可选)" />
                  </el-form-item>
                  <el-form-item label="回调域名">
                    <el-input v-model="feishuConfig.callbackUrl" placeholder="https://your-domain.com" />
                  </el-form-item>
                  <el-form-item label="自动同步">
                    <el-switch v-model="feishuConfig.autoSync" />
                    <span style="margin-left: 12px; color: #9ca3af; font-size: 12px">开启后每天自动同步组织架构</span>
                  </el-form-item>
                  <el-form-item>
                    <el-button type="primary" @click="saveFeishuConfig">保存配置</el-button>
                    <el-button @click="testFeishuConnection">测试连接</el-button>
                  </el-form-item>
                </el-form>
              </el-col>
              <el-col :span="10">
                <div class="help-section">
                  <h4><el-icon><InfoFilled /></el-icon> 配置说明</h4>
                  <ol>
                    <li>登录<a href="https://open.feishu.cn" target="_blank">飞书开放平台</a></li>
                    <li>创建企业自建应用</li>
                    <li>在凭证与基础信息中获取App ID和App Secret</li>
                    <li>申请通讯录权限</li>
                    <li>配置重定向URL和事件订阅</li>
                  </ol>
                </div>
              </el-col>
            </el-row>
          </div>
        </el-tab-pane>
        
        <!-- 同步管理 -->
        <el-tab-pane name="sync">
          <template #label>
            <span class="tab-label">
              <el-icon><Refresh /></el-icon>
              同步管理
            </span>
          </template>
          
          <div class="sync-section">
            <el-row :gutter="20" class="stat-row">
              <el-col :span="6">
                <div class="stat-card primary">
                  <div class="stat-value">{{ syncStats.totalUsers }}</div>
                  <div class="stat-label">已同步用户</div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="stat-card success">
                  <div class="stat-value">{{ syncStats.totalDepts }}</div>
                  <div class="stat-label">已同步部门</div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="stat-card warning">
                  <div class="stat-value">{{ syncStats.totalManagers }}</div>
                  <div class="stat-label">部门负责人</div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="stat-card info">
                  <div class="stat-value">{{ syncStats.syncSource }}</div>
                  <div class="stat-label">同步来源</div>
                </div>
              </el-col>
            </el-row>
            
            <el-card shadow="never" style="margin-bottom: 20px">
              <template #header>
                <div class="sync-header">
                  <span>同步设置</span>
                </div>
              </template>
              <el-form :model="syncSettings" label-width="160px">
                <el-row :gutter="40">
                  <el-col :span="12">
                    <el-form-item label="同步数据范围">
                      <el-checkbox-group v-model="syncSettings.scope">
                        <el-checkbox label="departments">部门</el-checkbox>
                        <el-checkbox label="users">用户</el-checkbox>
                        <el-checkbox label="managers">部门负责人</el-checkbox>
                      </el-checkbox-group>
                    </el-form-item>
                    <el-form-item label="同步策略">
                      <el-radio-group v-model="syncSettings.strategy">
                        <el-radio label="full">
                          全量同步
                          <el-tooltip content="同步所有数据，适合首次同步或数据修复" placement="top">
                            <el-icon style="margin-left: 4px"><QuestionFilled /></el-icon>
                          </el-tooltip>
                        </el-radio>
                        <el-radio label="incremental">
                          增量同步
                          <el-tooltip content="只同步变更的数据，适合日常同步" placement="top">
                            <el-icon style="margin-left: 4px"><QuestionFilled /></el-icon>
                          </el-tooltip>
                        </el-radio>
                      </el-radio-group>
                    </el-form-item>
                    <el-form-item label="用户匹配规则">
                      <el-select v-model="syncSettings.matchRule" style="width: 200px">
                        <el-option label="按手机号匹配" value="phone" />
                        <el-option label="按邮箱匹配" value="email" />
                        <el-option label="按工号匹配" value="employeeNo" />
                      </el-select>
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item label="全量同步间隔">
                      <el-select v-model="syncSettings.fullSyncInterval" style="width: 200px">
                        <el-option label="每天" value="daily" />
                        <el-option label="每周" value="weekly" />
                        <el-option label="每月" value="monthly" />
                        <el-option label="手动触发" value="manual" />
                      </el-select>
                    </el-form-item>
                    <el-form-item label="增量同步间隔">
                      <el-select v-model="syncSettings.incrementalSyncInterval" style="width: 200px">
                        <el-option label="每小时" value="hourly" />
                        <el-option label="每6小时" value="every6hours" />
                        <el-option label="每天" value="daily" />
                        <el-option label="手动触发" value="manual" />
                      </el-select>
                    </el-form-item>
                    <el-form-item label="自动同步时间">
                      <el-time-picker v-model="syncSettings.autoSyncTime" placeholder="选择时间" format="HH:mm" value-format="HH:mm" />
                      <span style="margin-left: 12px; color: #9ca3af; font-size: 12px">定时同步执行时间</span>
                    </el-form-item>
                  </el-col>
                </el-row>
                <el-form-item>
                  <el-button type="primary" @click="saveSyncSettings">保存设置</el-button>
                </el-form-item>
              </el-form>
            </el-card>
            
            <el-card shadow="never">
              <template #header>
                <div class="sync-header">
                  <span>同步日志</span>
                  <el-button type="primary" size="small" @click="openSyncDialog">
                    <el-icon><Refresh /></el-icon>
                    立即同步
                  </el-button>
                </div>
              </template>
              <el-table :data="syncLogs" style="width: 100%">
                <el-table-column prop="time" label="同步时间" width="180" />
                <el-table-column prop="source" label="同步来源" width="100" />
                <el-table-column prop="type" label="同步类型" width="100" />
                <el-table-column label="同步结果" width="100">
                  <template #default="{ row }">
                    <el-tag :type="row.success ? 'success' : 'danger'" size="small">
                      {{ row.success ? '成功' : '失败' }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="addedDepts" label="部门数" width="80" />
                <el-table-column prop="addedUsers" label="用户数" width="80" />
                <el-table-column prop="managers" label="负责人" width="80" />
                <el-table-column prop="message" label="备注" min-width="150" />
              </el-table>
            </el-card>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>
    
    <!-- 同步对话框 -->
    <el-dialog v-model="syncDialogVisible" title="同步组织架构" width="560px">
      <el-form :model="syncForm" label-width="140px">
        <el-form-item label="同步来源">
          <el-radio-group v-model="syncForm.provider">
            <el-radio label="wework" :disabled="!weworkConfig.enabled">企业微信</el-radio>
            <el-radio label="dingtalk" :disabled="!dingtalkConfig.enabled">钉钉</el-radio>
            <el-radio label="feishu" :disabled="!feishuConfig.enabled">飞书</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="同步类型">
          <el-radio-group v-model="syncForm.syncType">
            <el-radio label="full">全量同步</el-radio>
            <el-radio label="incremental">增量同步</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="同步数据范围">
          <el-checkbox-group v-model="syncForm.syncScope">
            <el-checkbox label="departments">部门</el-checkbox>
            <el-checkbox label="users">用户</el-checkbox>
            <el-checkbox label="managers">部门负责人</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        <el-form-item label="清空现有数据">
          <el-switch v-model="syncForm.clearExisting" />
          <el-tag type="danger" size="small" style="margin-left: 12px" v-if="syncForm.clearExisting">
            危险操作
          </el-tag>
          <div class="form-tip" v-if="syncForm.clearExisting">
            <el-icon><Warning /></el-icon>
            将删除现有的所有同步数据（部门、用户及绑定关系），不可恢复！
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="syncDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="executeSync" :loading="syncing">
          {{ syncing ? '同步中...' : '开始同步' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { Refresh, InfoFilled, QuestionFilled, Warning } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox, ElLoading } from 'element-plus'
import request from '@/utils/request'
import { useAppStore } from '@/stores/app'

const appStore = useAppStore()

const activeTab = ref('wework')
const selectedCompanyId = ref(null)
const companies = ref([])
const roles = ref([])

const weworkFormRef = ref(null)
const dingtalkFormRef = ref(null)
const feishuFormRef = ref(null)

// 企业微信配置
const weworkConfig = reactive({
  id: null,
  enabled: true,
  corpId: '',
  agentId: '',
  secret: '',
  contactSecret: '',
  callbackUrl: '',
  oauthEnabled: true,
  syncEnabled: true,
  syncDepartments: true,
  syncUsers: true,
  rootDepartmentId: '',
  syncInterval: 60,
  autoCreateUser: true,
  autoCreateDepartment: true,
  defaultRoleId: null,
  autoSync: true
})

// 钉钉配置
const dingtalkConfig = reactive({
  id: null,
  enabled: false,
  appKey: '',
  appSecret: '',
  agentId: '',
  corpId: '',
  callbackUrl: '',
  autoSync: false,
  syncEnabled: true,
  syncDepartments: true,
  syncUsers: true
})

// 飞书配置
const feishuConfig = reactive({
  id: null,
  enabled: false,
  appId: '',
  appSecret: '',
  encryptKey: '',
  verificationToken: '',
  callbackUrl: '',
  autoSync: false,
  syncEnabled: true,
  syncDepartments: true,
  syncUsers: true
})

// 同步统计
const syncStats = reactive({
  totalUsers: 0,
  totalDepts: 0,
  totalManagers: 0,
  lastSyncTime: '-',
  syncSource: '未配置'
})

// 同步设置
const syncSettings = reactive({
  scope: ['departments', 'users', 'managers'],
  strategy: 'incremental',
  matchRule: 'phone',
  autoSyncTime: '08:00',
  fullSyncInterval: 'weekly',
  incrementalSyncInterval: 'daily'
})

// 同步日志
const syncLogs = ref([])

// 同步对话框
const syncDialogVisible = ref(false)
const syncing = ref(false)
const syncForm = reactive({
  provider: 'wework',
  syncType: 'full',
  syncScope: ['departments', 'users', 'managers'],
  clearExisting: false
})

const configRules = {
  corpId: [{ required: true, message: '请输入企业ID', trigger: 'blur' }],
  agentId: [{ required: true, message: '请输入AgentId', trigger: 'blur' }],
  secret: [{ required: true, message: '请输入Secret', trigger: 'blur' }],
  appKey: [{ required: true, message: '请输入AppKey', trigger: 'blur' }],
  appSecret: [{ required: true, message: '请输入AppSecret', trigger: 'blur' }],
  appId: [{ required: true, message: '请输入App ID', trigger: 'blur' }]
}

// 打开同步对话框
function openSyncDialog() {
  // 自动选择已启用的平台
  if (weworkConfig.enabled) syncForm.provider = 'wework'
  else if (dingtalkConfig.enabled) syncForm.provider = 'dingtalk'
  else if (feishuConfig.enabled) syncForm.provider = 'feishu'
  
  syncForm.syncType = syncSettings.strategy
  syncForm.syncScope = [...syncSettings.scope]
  syncForm.clearExisting = false
  syncDialogVisible.value = true
}

// 执行同步
async function executeSync() {
  if (syncForm.clearExisting) {
    try {
      await ElMessageBox.confirm(
        '确定要清空现有的所有同步数据吗？此操作将删除所有通过SSO同步的部门和用户信息，不可恢复！',
        '危险操作确认',
        {
          confirmButtonText: '确定清空并同步',
          cancelButtonText: '取消',
          type: 'warning'
        }
      )
    } catch {
      return
    }
  }
  
  syncing.value = true
  try {
    const res = await request.post('/sso/sync-organization/', {
      provider: syncForm.provider,
      sync_type: syncForm.syncType,
      clear_existing: syncForm.clearExisting,
      sync_departments: syncForm.syncScope.includes('departments'),
      sync_users: syncForm.syncScope.includes('users'),
      sync_managers: syncForm.syncScope.includes('managers')
    })
    
    ElMessage.success(`同步完成！部门: ${res.departments}, 用户: ${res.users}, 负责人: ${res.managers || 0}`)
    syncDialogVisible.value = false
    
    // 刷新统计和日志
    await loadStats()
    await loadSyncLogs()
  } catch (error) {
    ElMessage.error('同步失败: ' + (error.response?.data?.error || error.message))
  } finally {
    syncing.value = false
  }
}

// 加载公司列表
async function loadCompanies() {
  try {
    const res = await request.get('/organizations/companies/')
    companies.value = res.results || res || []
    if (companies.value.length > 0) {
      selectedCompanyId.value = appStore.currentCompany?.id || companies.value[0].id
      loadConfigs()
    }
  } catch (error) {
    console.error('加载公司列表失败:', error)
  }
}

// 加载角色列表
async function loadRoles() {
  try {
    const params = selectedCompanyId.value ? { company: selectedCompanyId.value } : {}
    const res = await request.get('/auth/roles/', { params })
    roles.value = res.results || res || []
  } catch (error) {
    console.error('加载角色列表失败:', error)
  }
}

// 切换公司
function handleCompanyChange() {
  loadConfigs()
  loadRoles()
}

// 加载SSO配置
async function loadConfigs() {
  if (!selectedCompanyId.value) return
  
  try {
    const res = await request.get('/sso/configs/', { params: { company: selectedCompanyId.value } })
    const configs = res.results || res || []
    
    // 重置配置
    resetConfigs()
    
    configs.forEach(config => {
      if (config.provider === 'wework') {
        weworkConfig.id = config.id
        weworkConfig.enabled = config.is_enabled
        weworkConfig.corpId = config.corp_id || ''
        weworkConfig.agentId = config.agent_id || ''
        weworkConfig.secret = '' // 不返回密钥
        weworkConfig.contactSecret = config.extra_config?.contact_secret || ''
        weworkConfig.callbackUrl = config.callback_url || ''
        weworkConfig.oauthEnabled = config.oauth_enabled
        weworkConfig.syncEnabled = config.sync_enabled
        weworkConfig.syncDepartments = config.sync_departments
        weworkConfig.syncUsers = config.sync_users
        weworkConfig.rootDepartmentId = config.root_department_id || ''
        weworkConfig.syncInterval = config.sync_interval || 60
        weworkConfig.autoCreateUser = config.auto_create_user
        weworkConfig.autoCreateDepartment = config.auto_create_department
        weworkConfig.defaultRoleId = config.default_role_id
        weworkConfig.autoSync = config.auto_sync
      } else if (config.provider === 'dingtalk') {
        dingtalkConfig.id = config.id
        dingtalkConfig.enabled = config.is_enabled
        dingtalkConfig.appKey = config.app_id || ''
        dingtalkConfig.agentId = config.agent_id || ''
        dingtalkConfig.corpId = config.corp_id || ''
        dingtalkConfig.callbackUrl = config.callback_url || ''
        dingtalkConfig.autoSync = config.auto_sync
        dingtalkConfig.syncEnabled = config.sync_enabled
        dingtalkConfig.syncDepartments = config.sync_departments
        dingtalkConfig.syncUsers = config.sync_users
      } else if (config.provider === 'feishu') {
        feishuConfig.id = config.id
        feishuConfig.enabled = config.is_enabled
        feishuConfig.appId = config.app_id || ''
        feishuConfig.callbackUrl = config.callback_url || ''
        feishuConfig.autoSync = config.auto_sync
        feishuConfig.syncEnabled = config.sync_enabled
        feishuConfig.syncDepartments = config.sync_departments
        feishuConfig.syncUsers = config.sync_users
      }
    })
  } catch (error) {
    console.error('加载SSO配置失败:', error)
  }
}

// 重置配置
function resetConfigs() {
  Object.assign(weworkConfig, {
    id: null, enabled: false, corpId: '', agentId: '', secret: '', contactSecret: '',
    callbackUrl: '', oauthEnabled: true, syncEnabled: true, syncDepartments: true,
    syncUsers: true, rootDepartmentId: '', syncInterval: 60, autoCreateUser: true,
    autoCreateDepartment: true, defaultRoleId: null, autoSync: true
  })
  Object.assign(dingtalkConfig, {
    id: null, enabled: false, appKey: '', appSecret: '', agentId: '', corpId: '',
    callbackUrl: '', autoSync: false, syncEnabled: true, syncDepartments: true, syncUsers: true
  })
  Object.assign(feishuConfig, {
    id: null, enabled: false, appId: '', appSecret: '', encryptKey: '', verificationToken: '',
    callbackUrl: '', autoSync: false, syncEnabled: true, syncDepartments: true, syncUsers: true
  })
}

// 加载同步统计
async function loadStats() {
  try {
    const res = await request.get('/sso/stats/')
    syncStats.totalUsers = res.total_users || 0
    syncStats.totalDepts = res.total_depts || 0
    syncStats.totalManagers = res.total_managers || 0
    syncStats.lastSyncTime = res.last_sync_time ? new Date(res.last_sync_time).toLocaleString() : '-'
    syncStats.syncSource = res.sync_source || '未配置'
  } catch (error) {
    console.error('加载同步统计失败:', error)
  }
}

// 加载同步日志
async function loadSyncLogs() {
  try {
    const res = await request.get('/sso/sync-logs/')
    syncLogs.value = res.map(log => ({
      id: log.id,
      time: new Date(log.started_at).toLocaleString(),
      source: log.provider_display,
      type: log.sync_type === 'full' ? '全量' : '增量',
      success: log.status === 'success',
      addedUsers: log.detail?.result?.users || log.detail?.users || 0,
      addedDepts: log.detail?.result?.departments || log.detail?.departments || 0,
      managers: log.detail?.result?.managers || 0,
      message: log.error_message || '同步完成'
    }))
  } catch (error) {
    console.error('加载同步日志失败:', error)
  }
}

async function saveWeworkConfig() {
  weworkFormRef.value?.validate(async (valid) => {
    if (valid) {
      try {
        const data = {
          company: selectedCompanyId.value,
          provider: 'wework',
          corp_id: weworkConfig.corpId,
          agent_id: weworkConfig.agentId,
          app_secret: weworkConfig.secret || undefined,
          is_enabled: weworkConfig.enabled,
          oauth_enabled: weworkConfig.oauthEnabled,
          callback_url: weworkConfig.callbackUrl,
          sync_enabled: weworkConfig.syncEnabled,
          sync_departments: weworkConfig.syncDepartments,
          sync_users: weworkConfig.syncUsers,
          root_department_id: weworkConfig.rootDepartmentId || null,
          sync_interval: weworkConfig.syncInterval,
          auto_create_user: weworkConfig.autoCreateUser,
          auto_create_department: weworkConfig.autoCreateDepartment,
          default_role_id: weworkConfig.defaultRoleId,
          auto_sync: weworkConfig.autoSync,
          extra_config: {
            contact_secret: weworkConfig.contactSecret
          }
        }
        
        if (weworkConfig.id) {
          await request.patch(`/sso/configs/${weworkConfig.id}/`, data)
        } else {
          await request.post('/sso/configs/', data)
        }
        ElMessage.success('企业微信配置保存成功')
        loadConfigs()
      } catch (error) {
        ElMessage.error('保存失败: ' + (error.response?.data?.msg || error.message || '未知错误'))
      }
    }
  })
}

async function saveDingtalkConfig() {
  dingtalkFormRef.value?.validate(async (valid) => {
    if (valid) {
      try {
        const data = {
          company: selectedCompanyId.value,
          provider: 'dingtalk',
          corp_id: dingtalkConfig.corpId,
          agent_id: dingtalkConfig.agentId,
          app_id: dingtalkConfig.appKey,
          app_secret: dingtalkConfig.appSecret || undefined,
          is_enabled: dingtalkConfig.enabled,
          callback_url: dingtalkConfig.callbackUrl,
          sync_enabled: dingtalkConfig.syncEnabled,
          sync_departments: dingtalkConfig.syncDepartments,
          sync_users: dingtalkConfig.syncUsers,
          auto_sync: dingtalkConfig.autoSync
        }
        
        if (dingtalkConfig.id) {
          await request.patch(`/sso/configs/${dingtalkConfig.id}/`, data)
        } else {
          await request.post('/sso/configs/', data)
        }
        ElMessage.success('钉钉配置保存成功')
        loadConfigs()
      } catch (error) {
        ElMessage.error('保存失败: ' + (error.response?.data?.msg || error.message || '未知错误'))
      }
    }
  })
}

async function saveFeishuConfig() {
  feishuFormRef.value?.validate(async (valid) => {
    if (valid) {
      try {
        const data = {
          company: selectedCompanyId.value,
          provider: 'feishu',
          app_id: feishuConfig.appId,
          app_secret: feishuConfig.appSecret || undefined,
          is_enabled: feishuConfig.enabled,
          callback_url: feishuConfig.callbackUrl,
          sync_enabled: feishuConfig.syncEnabled,
          sync_departments: feishuConfig.syncDepartments,
          sync_users: feishuConfig.syncUsers,
          auto_sync: feishuConfig.autoSync,
          extra_config: {
            encrypt_key: feishuConfig.encryptKey,
            verification_token: feishuConfig.verificationToken
          }
        }
        
        if (feishuConfig.id) {
          await request.patch(`/sso/configs/${feishuConfig.id}/`, data)
        } else {
          await request.post('/sso/configs/', data)
        }
        ElMessage.success('飞书配置保存成功')
        loadConfigs()
      } catch (error) {
        ElMessage.error('保存失败: ' + (error.response?.data?.msg || error.message || '未知错误'))
      }
    }
  })
}

async function testWeworkConnection() {
  if (!weworkConfig.corpId || !weworkConfig.secret) {
    ElMessage.warning('请先完整填写企业微信配置')
    return
  }
  
  const loading = ElLoading.service({ text: '正在测试连接...' })
  try {
    const res = await request.post('/sso/test-connection/', {
      provider: 'wework',
      app_id: weworkConfig.corpId,
      app_secret: weworkConfig.secret,
      extra_config: { agent_id: weworkConfig.agentId }
    })
    if (res.success) {
      ElMessage.success('企业微信连接测试成功')
    } else {
      ElMessage.error(res.message || '连接测试失败')
    }
  } catch (error) {
    ElMessage.error('连接测试失败: ' + (error.response?.data?.message || error.message))
  } finally {
    loading.close()
  }
}

async function testDingtalkConnection() {
  if (!dingtalkConfig.appKey || !dingtalkConfig.appSecret) {
    ElMessage.warning('请先完整填写钉钉配置')
    return
  }
  
  const loading = ElLoading.service({ text: '正在测试连接...' })
  try {
    const res = await request.post('/sso/test-connection/', {
      provider: 'dingtalk',
      app_id: dingtalkConfig.appKey,
      app_secret: dingtalkConfig.appSecret
    })
    if (res.success) {
      ElMessage.success('钉钉连接测试成功')
    } else {
      ElMessage.error(res.message || '连接测试失败')
    }
  } catch (error) {
    ElMessage.error('连接测试失败: ' + (error.response?.data?.message || error.message))
  } finally {
    loading.close()
  }
}

async function testFeishuConnection() {
  if (!feishuConfig.appId || !feishuConfig.appSecret) {
    ElMessage.warning('请先完整填写飞书配置')
    return
  }
  
  const loading = ElLoading.service({ text: '正在测试连接...' })
  try {
    const res = await request.post('/sso/test-connection/', {
      provider: 'feishu',
      app_id: feishuConfig.appId,
      app_secret: feishuConfig.appSecret
    })
    if (res.success) {
      ElMessage.success('飞书连接测试成功')
    } else {
      ElMessage.error(res.message || '连接测试失败')
    }
  } catch (error) {
    ElMessage.error('连接测试失败: ' + (error.response?.data?.message || error.message))
  } finally {
    loading.close()
  }
}

function saveSyncSettings() {
  ElMessage.success('同步设置保存成功')
}

onMounted(() => {
  loadCompanies()
  loadRoles()
  loadStats()
  loadSyncLogs()
})
</script>

<style lang="scss" scoped>
.sso-container {
  .page-card { border-radius: 16px; }
  .page-header { 
    display: flex; 
    justify-content: space-between; 
    align-items: center; 
    h2 { margin: 0; font-size: 18px; color: #1f2937; }
    .header-left {
      display: flex;
      align-items: center;
    }
  }
  
  .tab-label {
    display: flex;
    align-items: center;
    gap: 8px;
    .platform-icon {
      width: 20px;
      height: 20px;
      border-radius: 4px;
    }
  }
  
  .config-section {
    padding: 20px 0;
  }
  
  .help-section {
    background: #f0f9ff;
    border-radius: 12px;
    padding: 20px;
    h4 {
      display: flex;
      align-items: center;
      gap: 8px;
      margin: 0 0 16px;
      color: #1e40af;
    }
    ol {
      margin: 0;
      padding-left: 20px;
      li {
        margin-bottom: 8px;
        color: #374151;
        line-height: 1.6;
        a {
          color: #3b82f6;
          text-decoration: none;
          &:hover { text-decoration: underline; }
        }
      }
    }
  }
  
  .sync-section {
    padding: 20px 0;
  }
  
  .stat-row { margin-bottom: 20px; }
  .stat-card {
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    color: #fff;
    &.primary { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
    &.success { background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); }
    &.warning { background: linear-gradient(135deg, #f6d365 0%, #fda085 100%); }
    &.info { background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); color: #1f2937; }
    .stat-value { font-size: 24px; font-weight: bold; margin-bottom: 4px; }
    .stat-label { font-size: 14px; opacity: 0.9; }
  }
  
  .sync-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .form-tip {
    margin-top: 8px;
    padding: 8px 12px;
    background: #fef2f2;
    border-radius: 6px;
    color: #dc2626;
    font-size: 12px;
    display: flex;
    align-items: center;
    gap: 6px;
  }
}
</style>
