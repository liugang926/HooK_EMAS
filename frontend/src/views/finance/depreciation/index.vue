<template>
  <div class="depreciation-container">
    <el-card class="page-card">
      <template #header>
        <div class="page-header">
          <h2>折旧方案</h2>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            新建方案
          </el-button>
        </div>
      </template>
      
      <el-table :data="schemeList" style="width: 100%">
        <el-table-column prop="name" label="方案名称" min-width="150" />
        <el-table-column prop="method" label="折旧方法" width="150" />
        <el-table-column prop="residualRate" label="残值率(%)" width="100" />
        <el-table-column prop="usefulLife" label="折旧年限(年)" width="120" />
        <el-table-column prop="assetCount" label="关联资产数" width="100" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-switch
              v-model="row.status"
              active-value="active"
              inactive-value="inactive"
              @change="handleStatusChange(row)"
            />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleView(row)">查看</el-button>
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <el-card class="page-card" style="margin-top: 20px">
      <template #header>
        <div class="page-header">
          <h2>月度折旧汇总</h2>
          <el-button type="success" @click="runDepreciation">
            <el-icon><Refresh /></el-icon>
            执行本月折旧
          </el-button>
        </div>
      </template>
      
      <el-row :gutter="20" class="stat-row">
        <el-col :span="6">
          <div class="stat-card primary">
            <div class="stat-value">{{ stats.totalAssets }}</div>
            <div class="stat-label">折旧资产数</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-card success">
            <div class="stat-value">¥{{ stats.monthlyTotal }}</div>
            <div class="stat-label">本月折旧总额</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-card warning">
            <div class="stat-value">¥{{ stats.accumulated }}</div>
            <div class="stat-label">累计折旧</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-card info">
            <div class="stat-value">{{ stats.lastRunDate }}</div>
            <div class="stat-label">上次执行日期</div>
          </div>
        </el-col>
      </el-row>
      
      <el-table :data="depreciationRecords" style="width: 100%" max-height="300">
        <el-table-column prop="period" label="折旧期间" width="120" />
        <el-table-column prop="assetCount" label="资产数量" width="100" />
        <el-table-column prop="totalAmount" label="折旧总额" width="120" />
        <el-table-column prop="executeTime" label="执行时间" width="180" />
        <el-table-column prop="executor" label="执行人" width="100" />
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button type="primary" link @click="viewDepreciationDetail(row)">明细</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <el-card class="page-card" style="margin-top: 20px">
      <template #header>
        <h2>折旧计算说明</h2>
      </template>
      <div class="depreciation-info">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="直线法">年折旧额 = (原值 - 残值) / 折旧年限</el-descriptions-item>
          <el-descriptions-item label="双倍余额递减法">年折旧额 = 账面净值 × (2 / 折旧年限)</el-descriptions-item>
          <el-descriptions-item label="年数总和法">年折旧额 = (原值 - 残值) × (剩余年限 / 年数总和)</el-descriptions-item>
        </el-descriptions>
      </div>
    </el-card>
    
    <!-- 查看详情弹窗 -->
    <el-dialog v-model="viewDialogVisible" title="方案详情" width="600px">
      <el-descriptions :column="2" border v-if="currentScheme">
        <el-descriptions-item label="方案名称">{{ currentScheme.name }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="currentScheme.status === 'active' ? 'success' : 'info'">
            {{ currentScheme.status === 'active' ? '启用' : '停用' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="折旧方法">{{ currentScheme.method }}</el-descriptions-item>
        <el-descriptions-item label="残值率">{{ currentScheme.residualRate }}%</el-descriptions-item>
        <el-descriptions-item label="折旧年限">{{ currentScheme.usefulLife }} 年</el-descriptions-item>
        <el-descriptions-item label="关联资产数">{{ currentScheme.assetCount }} 个</el-descriptions-item>
        <el-descriptions-item label="月折旧额计算" :span="2">
          月折旧额 = (原值 × (1 - {{ currentScheme.residualRate }}%)) / ({{ currentScheme.usefulLife }} × 12)
        </el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="viewDialogVisible = false">关闭</el-button>
        <el-button type="primary" @click="handleEditFromView">编辑</el-button>
      </template>
    </el-dialog>
    
    <!-- 新建/编辑弹窗 -->
    <el-dialog v-model="formDialogVisible" :title="formDialogTitle" width="600px">
      <el-form :model="schemeForm" label-width="100px" ref="formRef" :rules="formRules">
        <el-form-item label="方案名称" prop="name">
          <el-input v-model="schemeForm.name" placeholder="请输入方案名称" />
        </el-form-item>
        <el-form-item label="折旧方法" prop="method">
          <el-select v-model="schemeForm.method" placeholder="请选择" style="width: 100%">
            <el-option label="直线法" value="直线法" />
            <el-option label="双倍余额递减法" value="双倍余额递减法" />
            <el-option label="年数总和法" value="年数总和法" />
          </el-select>
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="残值率" prop="residualRate">
              <el-input-number v-model="schemeForm.residualRate" :min="0" :max="100" :precision="2" style="width: 100%">
                <template #suffix>%</template>
              </el-input-number>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="折旧年限" prop="usefulLife">
              <el-input-number v-model="schemeForm.usefulLife" :min="1" :max="50" style="width: 100%">
                <template #suffix>年</template>
              </el-input-number>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="适用分类">
          <el-select v-model="schemeForm.categories" multiple placeholder="请选择适用的资产分类" style="width: 100%">
            <el-option label="电子设备" value="电子设备" />
            <el-option label="办公家具" value="办公家具" />
            <el-option label="交通工具" value="交通工具" />
            <el-option label="机器设备" value="机器设备" />
          </el-select>
        </el-form-item>
        <el-form-item label="方案说明">
          <el-input v-model="schemeForm.remark" type="textarea" :rows="3" placeholder="请输入方案说明" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="formDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm">保存</el-button>
      </template>
    </el-dialog>
    
    <!-- 折旧明细弹窗 -->
    <el-dialog v-model="detailDialogVisible" title="折旧明细" width="900px">
      <el-descriptions :column="4" border v-if="currentRecord" style="margin-bottom: 20px">
        <el-descriptions-item label="折旧期间">{{ currentRecord.period }}</el-descriptions-item>
        <el-descriptions-item label="资产数量">{{ currentRecord.assetCount }}</el-descriptions-item>
        <el-descriptions-item label="折旧总额">{{ currentRecord.totalAmount }}</el-descriptions-item>
        <el-descriptions-item label="执行时间">{{ currentRecord.executeTime }}</el-descriptions-item>
      </el-descriptions>
      
      <el-table :data="depreciationDetails" border size="small">
        <el-table-column prop="assetCode" label="资产编号" width="120" />
        <el-table-column prop="assetName" label="资产名称" min-width="150" />
        <el-table-column prop="originalValue" label="原值" width="100" />
        <el-table-column prop="depreciation" label="本期折旧" width="100" />
        <el-table-column prop="accumulated" label="累计折旧" width="100" />
        <el-table-column prop="netValue" label="净值" width="100" />
      </el-table>
      <template #footer>
        <el-button @click="detailDialogVisible = false">关闭</el-button>
        <el-button type="primary" @click="exportDetail">导出明细</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { Plus, Refresh } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const formRef = ref(null)

const stats = reactive({
  totalAssets: 546,
  monthlyTotal: '156,800',
  accumulated: '3,890,000',
  lastRunDate: '2024-01-31'
})

const schemeList = ref([
  { id: 1, name: '电子设备折旧方案', method: '直线法', residualRate: 5, usefulLife: 3, assetCount: 312, status: 'active', categories: ['电子设备'] },
  { id: 2, name: '办公家具折旧方案', method: '直线法', residualRate: 5, usefulLife: 5, assetCount: 189, status: 'active', categories: ['办公家具'] },
  { id: 3, name: '交通工具折旧方案', method: '双倍余额递减法', residualRate: 10, usefulLife: 8, assetCount: 45, status: 'active', categories: ['交通工具'] }
])

const depreciationRecords = ref([
  { id: 1, period: '2024-01', assetCount: 546, totalAmount: '¥156,800', executeTime: '2024-01-31 18:00:00', executor: 'admin' },
  { id: 2, period: '2023-12', assetCount: 540, totalAmount: '¥154,200', executeTime: '2023-12-31 18:00:00', executor: 'admin' },
  { id: 3, period: '2023-11', assetCount: 535, totalAmount: '¥152,600', executeTime: '2023-11-30 18:00:00', executor: 'admin' }
])

const depreciationDetails = ref([
  { assetCode: 'ZC-2024-0001', assetName: 'MacBook Pro', originalValue: '¥19,999', depreciation: '¥527.75', accumulated: '¥5,277.50', netValue: '¥14,721.50' },
  { assetCode: 'ZC-2024-0002', assetName: 'ThinkPad X1', originalValue: '¥12,999', depreciation: '¥343.16', accumulated: '¥3,431.60', netValue: '¥9,567.40' },
  { assetCode: 'ZC-2024-0003', assetName: 'Dell显示器', originalValue: '¥3,999', depreciation: '¥105.55', accumulated: '¥1,055.50', netValue: '¥2,943.50' }
])

// 查看弹窗
const viewDialogVisible = ref(false)
const currentScheme = ref(null)

// 表单弹窗
const formDialogVisible = ref(false)
const formDialogTitle = ref('新建折旧方案')
const schemeForm = reactive({
  id: null,
  name: '',
  method: '',
  residualRate: 5,
  usefulLife: 3,
  categories: [],
  remark: ''
})

const formRules = {
  name: [{ required: true, message: '请输入方案名称', trigger: 'blur' }],
  method: [{ required: true, message: '请选择折旧方法', trigger: 'change' }],
  residualRate: [{ required: true, message: '请输入残值率', trigger: 'blur' }],
  usefulLife: [{ required: true, message: '请输入折旧年限', trigger: 'blur' }]
}

// 折旧明细弹窗
const detailDialogVisible = ref(false)
const currentRecord = ref(null)

let idCounter = 100

function handleView(row) {
  currentScheme.value = row
  viewDialogVisible.value = true
}

function handleAdd() {
  formDialogTitle.value = '新建折旧方案'
  Object.assign(schemeForm, {
    id: null,
    name: '',
    method: '',
    residualRate: 5,
    usefulLife: 3,
    categories: [],
    remark: ''
  })
  formDialogVisible.value = true
}

function handleEdit(row) {
  formDialogTitle.value = '编辑折旧方案'
  Object.assign(schemeForm, {
    id: row.id,
    name: row.name,
    method: row.method,
    residualRate: row.residualRate,
    usefulLife: row.usefulLife,
    categories: row.categories || [],
    remark: row.remark || ''
  })
  formDialogVisible.value = true
}

function handleEditFromView() {
  viewDialogVisible.value = false
  handleEdit(currentScheme.value)
}

function handleDelete(row) {
  ElMessageBox.confirm(`确定要删除折旧方案 "${row.name}" 吗？`, '删除确认', {
    confirmButtonText: '确定删除',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    const index = schemeList.value.findIndex(item => item.id === row.id)
    if (index !== -1) {
      schemeList.value.splice(index, 1)
    }
    ElMessage.success('删除成功')
  }).catch(() => {})
}

function handleStatusChange(row) {
  ElMessage.success(`方案 "${row.name}" 已${row.status === 'active' ? '启用' : '停用'}`)
}

function submitForm() {
  formRef.value?.validate((valid) => {
    if (valid) {
      if (schemeForm.id) {
        const index = schemeList.value.findIndex(item => item.id === schemeForm.id)
        if (index !== -1) {
          Object.assign(schemeList.value[index], {
            name: schemeForm.name,
            method: schemeForm.method,
            residualRate: schemeForm.residualRate,
            usefulLife: schemeForm.usefulLife,
            categories: schemeForm.categories,
            remark: schemeForm.remark
          })
        }
        ElMessage.success('编辑成功')
      } else {
        schemeList.value.push({
          id: ++idCounter,
          name: schemeForm.name,
          method: schemeForm.method,
          residualRate: schemeForm.residualRate,
          usefulLife: schemeForm.usefulLife,
          assetCount: 0,
          status: 'active',
          categories: schemeForm.categories,
          remark: schemeForm.remark
        })
        ElMessage.success('新建成功')
      }
      formDialogVisible.value = false
    }
  })
}

function runDepreciation() {
  ElMessageBox.confirm('确定要执行本月折旧计算吗？此操作将为所有启用方案的资产计算折旧。', '执行确认', {
    confirmButtonText: '确定执行',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    const now = new Date()
    const period = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`
    depreciationRecords.value.unshift({
      id: depreciationRecords.value.length + 1,
      period: period,
      assetCount: stats.totalAssets,
      totalAmount: `¥${stats.monthlyTotal}`,
      executeTime: now.toLocaleString(),
      executor: 'admin'
    })
    stats.lastRunDate = now.toISOString().slice(0, 10)
    ElMessage.success('折旧计算完成')
  }).catch(() => {})
}

function viewDepreciationDetail(row) {
  currentRecord.value = row
  detailDialogVisible.value = true
}

function exportDetail() {
  ElMessage.success('折旧明细导出成功')
}
</script>

<style lang="scss" scoped>
.depreciation-container {
  .page-card { border-radius: 16px; h2 { margin: 0; font-size: 18px; color: #1f2937; } }
  .page-header { display: flex; justify-content: space-between; align-items: center; }
  .stat-row { margin-bottom: 20px; }
  .stat-card {
    border-radius: 12px; padding: 20px; text-align: center; color: #fff;
    &.primary { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
    &.success { background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); }
    &.warning { background: linear-gradient(135deg, #f6d365 0%, #fda085 100%); }
    &.info { background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); color: #1f2937; }
    .stat-value { font-size: 24px; font-weight: bold; margin-bottom: 4px; }
    .stat-label { font-size: 14px; opacity: 0.9; }
  }
}
</style>
