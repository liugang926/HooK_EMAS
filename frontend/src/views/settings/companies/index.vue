<template>
  <div class="company-management">
    <!-- Header -->
    <div class="page-header">
      <div class="header-left">
        <h2>公司管理</h2>
        <span class="subtitle">管理系统中的多个公司/组织，支持集团架构和多公司模式</span>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="openCreateDialog">
          <el-icon><Plus /></el-icon>
          新增公司
        </el-button>
      </div>
    </div>

    <!-- Company List -->
    <el-card class="company-list-card">
      <el-table
        v-loading="loading"
        :data="companies"
        style="width: 100%"
        row-key="id"
      >
        <el-table-column prop="name" label="公司名称" min-width="220">
          <template #default="{ row }">
            <div class="company-name-cell">
              <el-avatar v-if="row.logo" :src="row.logo" :size="36" />
              <el-avatar v-else :size="36" style="background: var(--el-color-primary)">
                {{ row.name?.charAt(0) }}
              </el-avatar>
              <div class="company-info">
                <span class="name">{{ row.name }}</span>
                <span class="code">{{ row.code }}</span>
              </div>
              <el-tag v-if="currentCompanyId === row.id" type="success" size="small">
                当前
              </el-tag>
              <el-tag v-if="row.is_group_root" type="warning" size="small">
                集团
              </el-tag>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="company_type_display" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="getCompanyTypeColor(row.company_type)" size="small">
              {{ row.company_type_display || getCompanyTypeLabel(row.company_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="parent_name" label="上级公司" width="120">
          <template #default="{ row }">
            {{ row.parent_name || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="org_mode_display" label="组织模式" width="120">
          <template #default="{ row }">
            {{ row.org_mode_display || getOrgModeLabel(row.org_mode) }}
          </template>
        </el-table-column>
        <el-table-column prop="phone" label="联系电话" width="140" />
        <el-table-column prop="is_active" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="160">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="switchToCompany(row)">
              <el-icon><Switch /></el-icon>
              切换
            </el-button>
            <el-button type="primary" link @click="openEditDialog(row)">
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            <el-popconfirm
              title="确定要删除该公司吗？"
              confirm-button-text="确定"
              cancel-button-text="取消"
              @confirm="deleteCompanyItem(row)"
            >
              <template #reference>
                <el-button type="danger" link :disabled="companies.length <= 1 || row.children_count > 0">
                  <el-icon><Delete /></el-icon>
                  删除
                </el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- Company Dialog -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑公司' : '新增公司'"
      width="700px"
      destroy-on-close
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
        class="company-form"
      >
        <el-tabs v-model="activeTab">
          <!-- Basic Info Tab -->
          <el-tab-pane label="基本信息" name="basic">
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="公司名称" prop="name">
                  <el-input v-model="formData.name" placeholder="请输入公司名称" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="公司代码" prop="code">
                  <el-input v-model="formData.code" placeholder="请输入公司代码" :disabled="isEdit" />
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="公司简称" prop="short_name">
                  <el-input v-model="formData.short_name" placeholder="请输入公司简称" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="联系电话" prop="phone">
                  <el-input v-model="formData.phone" placeholder="请输入联系电话" />
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="邮箱" prop="email">
                  <el-input v-model="formData.email" placeholder="请输入邮箱" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="网站" prop="website">
                  <el-input v-model="formData.website" placeholder="请输入网站地址" />
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-form-item label="公司地址" prop="address">
              <el-input v-model="formData.address" placeholder="请输入公司地址" />
            </el-form-item>
            
            <el-form-item label="公司简介" prop="description">
              <el-input
                v-model="formData.description"
                type="textarea"
                :rows="3"
                placeholder="请输入公司简介"
              />
            </el-form-item>
            
            <el-form-item label="状态" prop="is_active">
              <el-switch v-model="formData.is_active" active-text="启用" inactive-text="禁用" />
            </el-form-item>
          </el-tab-pane>
          
          <!-- Hierarchy Tab -->
          <el-tab-pane label="组织层级" name="hierarchy">
            <el-alert
              title="组织层级设置"
              type="info"
              :closable="false"
              show-icon
              style="margin-bottom: 20px"
            >
              配置公司类型和上下级关系，支持集团公司管理模式
            </el-alert>
            
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="公司类型" prop="company_type">
                  <el-select v-model="formData.company_type" placeholder="选择公司类型" style="width: 100%">
                    <el-option label="集团总部" value="group" />
                    <el-option label="子公司" value="subsidiary" />
                    <el-option label="分公司" value="branch" />
                    <el-option label="关联公司" value="affiliate" />
                    <el-option label="独立核算部门" value="dept_unit" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="上级公司" prop="parent">
                  <el-select 
                    v-model="formData.parent" 
                    placeholder="选择上级公司" 
                    style="width: 100%"
                    clearable
                    :disabled="formData.company_type === 'group'"
                  >
                    <el-option 
                      v-for="c in availableParentCompanies" 
                      :key="c.id" 
                      :label="c.name" 
                      :value="c.id"
                      :disabled="c.id === formData.id"
                    />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-form-item label="组织模式" prop="org_mode">
              <el-radio-group v-model="formData.org_mode">
                <el-radio value="independent">
                  <span>独立组织架构</span>
                  <el-tooltip content="公司拥有独立的部门和用户数据">
                    <el-icon style="margin-left: 4px; color: #909399"><QuestionFilled /></el-icon>
                  </el-tooltip>
                </el-radio>
                <el-radio value="shared">
                  <span>共享组织架构</span>
                  <el-tooltip content="与上级公司共享部门和用户数据">
                    <el-icon style="margin-left: 4px; color: #909399"><QuestionFilled /></el-icon>
                  </el-tooltip>
                </el-radio>
                <el-radio value="inherit">
                  <span>继承上级架构</span>
                  <el-tooltip content="继承上级公司的组织架构，可在此基础上扩展">
                    <el-icon style="margin-left: 4px; color: #909399"><QuestionFilled /></el-icon>
                  </el-tooltip>
                </el-radio>
              </el-radio-group>
            </el-form-item>
          </el-tab-pane>
          
          <!-- Financial Tab -->
          <el-tab-pane label="财务信息" name="finance">
            <el-alert
              title="财务信息配置"
              type="info"
              :closable="false"
              show-icon
              style="margin-bottom: 20px"
            >
              用于财务审计和资产折旧计算
            </el-alert>
            
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="税务登记号" prop="tax_id">
                  <el-input v-model="formData.tax_id" placeholder="请输入税务登记号" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="法人代表" prop="legal_representative">
                  <el-input v-model="formData.legal_representative" placeholder="请输入法人代表" />
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="核算货币" prop="currency">
                  <el-select v-model="formData.currency" style="width: 100%">
                    <el-option label="人民币 (CNY)" value="CNY" />
                    <el-option label="美元 (USD)" value="USD" />
                    <el-option label="欧元 (EUR)" value="EUR" />
                    <el-option label="港币 (HKD)" value="HKD" />
                    <el-option label="日元 (JPY)" value="JPY" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="财年起始月" prop="fiscal_year_start">
                  <el-select v-model="formData.fiscal_year_start" style="width: 100%">
                    <el-option v-for="m in 12" :key="m" :label="`${m}月`" :value="m" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>
          </el-tab-pane>
          
          <!-- SSO Tab -->
          <el-tab-pane label="SSO配置" name="sso">
            <el-alert
              title="SSO配置说明"
              type="warning"
              :closable="false"
              show-icon
              style="margin-bottom: 20px"
            >
              此处配置仅用于快速设置，详细SSO配置请前往 "SSO单点登录" 页面
            </el-alert>
            
            <el-row :gutter="20">
              <el-col :span="8">
                <el-form-item label="企微CorpID" prop="wework_corp_id">
                  <el-input v-model="formData.wework_corp_id" placeholder="企业微信" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="钉钉CorpID" prop="dingtalk_corp_id">
                  <el-input v-model="formData.dingtalk_corp_id" placeholder="钉钉" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="飞书CorpID" prop="feishu_corp_id">
                  <el-input v-model="formData.feishu_corp_id" placeholder="飞书" />
                </el-form-item>
              </el-col>
            </el-row>
          </el-tab-pane>
        </el-tabs>
      </el-form>
      
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="submitting">
          {{ isEdit ? '保存' : '创建' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { Plus, Edit, Delete, Switch, QuestionFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useAppStore } from '@/stores/app'
import {
  getCompanies,
  createCompany,
  updateCompany,
  deleteCompany
} from '@/api/organizations'

const appStore = useAppStore()

// State
const loading = ref(false)
const companies = ref([])
const dialogVisible = ref(false)
const isEdit = ref(false)
const submitting = ref(false)
const formRef = ref(null)
const activeTab = ref('basic')

// Current company ID
const currentCompanyId = computed(() => appStore.currentCompany?.id)

// Available parent companies (exclude self and children)
const availableParentCompanies = computed(() => {
  return companies.value.filter(c => c.id !== formData.id)
})

// Form data with new fields
const defaultFormData = {
  id: null,
  name: '',
  code: '',
  short_name: '',
  phone: '',
  email: '',
  website: '',
  address: '',
  description: '',
  // Hierarchy
  parent: null,
  company_type: 'subsidiary',
  org_mode: 'independent',
  // Financial
  tax_id: '',
  legal_representative: '',
  currency: 'CNY',
  fiscal_year_start: 1,
  // SSO
  wework_corp_id: '',
  dingtalk_corp_id: '',
  feishu_corp_id: '',
  is_active: true
}

const formData = reactive({ ...defaultFormData })

// Form rules
const formRules = {
  name: [{ required: true, message: '请输入公司名称', trigger: 'blur' }],
  code: [
    { required: true, message: '请输入公司代码', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9_-]+$/, message: '只能包含字母、数字、下划线和横线', trigger: 'blur' }
  ],
  email: [{ type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }],
  website: [{ type: 'url', message: '请输入正确的网址', trigger: 'blur' }],
  company_type: [{ required: true, message: '请选择公司类型', trigger: 'change' }],
  org_mode: [{ required: true, message: '请选择组织模式', trigger: 'change' }]
}

// Helper functions for display
function getCompanyTypeColor(type) {
  const colors = {
    group: 'warning',
    subsidiary: 'primary',
    branch: 'success',
    affiliate: 'info',
    dept_unit: ''
  }
  return colors[type] || ''
}

function getCompanyTypeLabel(type) {
  const labels = {
    group: '集团总部',
    subsidiary: '子公司',
    branch: '分公司',
    affiliate: '关联公司',
    dept_unit: '独立核算部门'
  }
  return labels[type] || type
}

function getOrgModeLabel(mode) {
  const labels = {
    independent: '独立组织架构',
    shared: '共享组织架构',
    inherit: '继承上级架构'
  }
  return labels[mode] || mode
}

// Load companies
async function loadCompanies() {
  loading.value = true
  try {
    const res = await getCompanies()
    companies.value = res.results || res || []
  } catch (error) {
    console.error('加载公司列表失败:', error)
    ElMessage.error('加载公司列表失败')
  } finally {
    loading.value = false
  }
}

// Open create dialog
function openCreateDialog() {
  isEdit.value = false
  activeTab.value = 'basic'
  Object.assign(formData, defaultFormData)
  dialogVisible.value = true
}

// Open edit dialog
function openEditDialog(company) {
  isEdit.value = true
  activeTab.value = 'basic'
  Object.assign(formData, {
    ...defaultFormData,
    ...company
  })
  dialogVisible.value = true
}

// Submit form
async function submitForm() {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    submitting.value = true
    try {
      if (isEdit.value) {
        await updateCompany(formData.id, formData)
        ElMessage.success('公司更新成功')
        
        // Update current company if it was edited
        if (appStore.currentCompany?.id === formData.id) {
          appStore.setCurrentCompany({ ...formData })
        }
      } else {
        await createCompany(formData)
        ElMessage.success('公司创建成功')
      }
      
      dialogVisible.value = false
      await loadCompanies()
    } catch (error) {
      ElMessage.error(isEdit.value ? '更新失败' : '创建失败')
    } finally {
      submitting.value = false
    }
  })
}

// Delete company
async function deleteCompanyItem(company) {
  if (company.id === currentCompanyId.value) {
    ElMessage.warning('无法删除当前使用的公司')
    return
  }
  
  try {
    await deleteCompany(company.id)
    ElMessage.success('公司删除成功')
    await loadCompanies()
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

// Switch to company
function switchToCompany(company) {
  appStore.setCurrentCompany(company)
  ElMessage.success(`已切换到: ${company.name}`)
}

// Format date
function formatDate(dateStr) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

// Init
onMounted(() => {
  loadCompanies()
})
</script>

<style lang="scss" scoped>
.company-management {
  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 24px;
    
    .header-left {
      h2 {
        margin: 0 0 4px 0;
        font-size: 20px;
        font-weight: 600;
        color: #1f2937;
      }
      
      .subtitle {
        font-size: 14px;
        color: #6b7280;
      }
    }
  }
  
  .company-list-card {
    border-radius: 12px;
    
    .company-name-cell {
      display: flex;
      align-items: center;
      gap: 12px;
      
      .company-info {
        display: flex;
        flex-direction: column;
        
        .name {
          font-weight: 500;
          color: #1f2937;
        }
        
        .code {
          font-size: 12px;
          color: #9ca3af;
        }
      }
    }
  }
  
  .company-form {
    .el-divider {
      margin: 20px 0;
      
      :deep(.el-divider__text) {
        font-size: 13px;
        color: #6b7280;
      }
    }
  }
}
</style>
