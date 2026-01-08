<template>
  <div class="ledger-container">
    <el-card class="page-card">
      <template #header>
        <div class="page-header">
          <h2>资产财务台账</h2>
          <div>
            <el-button type="success" @click="exportLedger">
              <el-icon><Download /></el-icon>
              导出台账
            </el-button>
          </div>
        </div>
      </template>
      
      <el-form :inline="true" class="filter-form">
        <el-form-item label="资产分类">
          <el-cascader v-model="filterForm.category" :options="categoryOptions" clearable placeholder="请选择" />
        </el-form-item>
        <el-form-item label="使用部门">
          <el-select v-model="filterForm.department" clearable placeholder="请选择">
            <el-option label="全部部门" value="" />
            <el-option label="研发部" value="研发部" />
            <el-option label="市场部" value="市场部" />
            <el-option label="财务部" value="财务部" />
            <el-option label="行政部" value="行政部" />
          </el-select>
        </el-form-item>
        <el-form-item label="折旧方法">
          <el-select v-model="filterForm.method" clearable placeholder="请选择">
            <el-option label="全部方法" value="" />
            <el-option label="直线法" value="直线法" />
            <el-option label="双倍余额递减法" value="双倍余额递减法" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
      
      <el-row :gutter="20" class="stat-row">
        <el-col :span="6">
          <div class="stat-card primary">
            <div class="stat-value">¥{{ stats.originalTotal }}</div>
            <div class="stat-label">资产原值合计</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-card warning">
            <div class="stat-value">¥{{ stats.depreciationTotal }}</div>
            <div class="stat-label">累计折旧</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-card success">
            <div class="stat-value">¥{{ stats.netTotal }}</div>
            <div class="stat-label">资产净值</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-card info">
            <div class="stat-value">¥{{ stats.monthlyTotal }}</div>
            <div class="stat-label">本月折旧</div>
          </div>
        </el-col>
      </el-row>
      
      <el-table :data="filteredList" style="width: 100%">
        <el-table-column prop="assetCode" label="资产编号" width="130" />
        <el-table-column prop="name" label="资产名称" min-width="150" />
        <el-table-column prop="category" label="分类" width="100" />
        <el-table-column prop="department" label="使用部门" width="100" />
        <el-table-column prop="originalValue" label="原值" width="120" />
        <el-table-column prop="accumulatedDepreciation" label="累计折旧" width="120" />
        <el-table-column prop="netValue" label="净值" width="120" />
        <el-table-column prop="monthlyDepreciation" label="月折旧额" width="100" />
        <el-table-column prop="depreciationMethod" label="折旧方法" width="120" />
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleView(row)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.size"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next"
        style="margin-top: 20px; justify-content: flex-end"
      />
    </el-card>
    
    <!-- 详情弹窗 -->
    <el-dialog v-model="viewDialogVisible" title="资产财务详情" width="700px">
      <el-descriptions :column="2" border v-if="currentAsset">
        <el-descriptions-item label="资产编号">{{ currentAsset.assetCode }}</el-descriptions-item>
        <el-descriptions-item label="资产名称">{{ currentAsset.name }}</el-descriptions-item>
        <el-descriptions-item label="资产分类">{{ currentAsset.category }}</el-descriptions-item>
        <el-descriptions-item label="使用部门">{{ currentAsset.department }}</el-descriptions-item>
        <el-descriptions-item label="入账日期">{{ currentAsset.purchaseDate }}</el-descriptions-item>
        <el-descriptions-item label="折旧方法">{{ currentAsset.depreciationMethod }}</el-descriptions-item>
        <el-descriptions-item label="资产原值">{{ currentAsset.originalValue }}</el-descriptions-item>
        <el-descriptions-item label="残值率">{{ currentAsset.residualRate }}%</el-descriptions-item>
        <el-descriptions-item label="折旧年限">{{ currentAsset.usefulLife }} 年</el-descriptions-item>
        <el-descriptions-item label="月折旧额">{{ currentAsset.monthlyDepreciation }}</el-descriptions-item>
        <el-descriptions-item label="累计折旧">{{ currentAsset.accumulatedDepreciation }}</el-descriptions-item>
        <el-descriptions-item label="资产净值">{{ currentAsset.netValue }}</el-descriptions-item>
      </el-descriptions>
      
      <div style="margin-top: 20px">
        <h4>折旧历史记录</h4>
        <el-table :data="depreciationHistory" border size="small" max-height="200">
          <el-table-column prop="period" label="折旧期间" width="100" />
          <el-table-column prop="depreciation" label="本期折旧" width="100" />
          <el-table-column prop="accumulated" label="累计折旧" width="100" />
          <el-table-column prop="netValue" label="期末净值" width="100" />
          <el-table-column prop="executeTime" label="计算时间" min-width="150" />
        </el-table>
      </div>
      
      <template #footer>
        <el-button @click="viewDialogVisible = false">关闭</el-button>
        <el-button type="primary" @click="exportAssetDetail">导出详情</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { Download } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const filterForm = reactive({ 
  category: [], 
  department: '',
  method: ''
})

const categoryOptions = ref([
  { value: 'office', label: '办公设备', children: [
    { value: 'computer', label: '电脑' },
    { value: 'printer', label: '打印机' }
  ]},
  { value: 'electronic', label: '电子设备', children: [
    { value: 'phone', label: '手机' },
    { value: 'tablet', label: '平板' }
  ]},
  { value: 'furniture', label: '办公家具', children: [
    { value: 'desk', label: '桌椅' },
    { value: 'cabinet', label: '柜子' }
  ]}
])

const stats = reactive({
  originalTotal: '12,580,000',
  depreciationTotal: '3,890,000',
  netTotal: '8,690,000',
  monthlyTotal: '156,800'
})

const pagination = reactive({
  page: 1,
  size: 10,
  total: 546
})

const ledgerList = ref([
  { id: 1, assetCode: 'ZC-2024-0001', name: 'MacBook Pro 16寸', category: '电脑', department: '研发部', originalValue: '¥19,999', accumulatedDepreciation: '¥5,555', netValue: '¥14,444', monthlyDepreciation: '¥527.75', depreciationMethod: '直线法', purchaseDate: '2023-06-15', residualRate: 5, usefulLife: 3 },
  { id: 2, assetCode: 'ZC-2024-0002', name: 'ThinkPad X1 Carbon', category: '电脑', department: '研发部', originalValue: '¥12,999', accumulatedDepreciation: '¥3,611', netValue: '¥9,388', monthlyDepreciation: '¥343.16', depreciationMethod: '直线法', purchaseDate: '2023-07-20', residualRate: 5, usefulLife: 3 },
  { id: 3, assetCode: 'ZC-2024-0003', name: 'Dell 27寸显示器', category: '电脑', department: '研发部', originalValue: '¥3,999', accumulatedDepreciation: '¥1,111', netValue: '¥2,888', monthlyDepreciation: '¥105.55', depreciationMethod: '直线法', purchaseDate: '2023-08-10', residualRate: 5, usefulLife: 3 },
  { id: 4, assetCode: 'ZC-2024-0004', name: '办公桌椅套装', category: '桌椅', department: '市场部', originalValue: '¥5,000', accumulatedDepreciation: '¥1,000', netValue: '¥4,000', monthlyDepreciation: '¥79.17', depreciationMethod: '直线法', purchaseDate: '2023-05-01', residualRate: 5, usefulLife: 5 },
  { id: 5, assetCode: 'ZC-2024-0005', name: 'HP打印机', category: '打印机', department: '行政部', originalValue: '¥8,000', accumulatedDepreciation: '¥2,222', netValue: '¥5,778', monthlyDepreciation: '¥211.11', depreciationMethod: '直线法', purchaseDate: '2023-06-01', residualRate: 5, usefulLife: 3 },
  { id: 6, assetCode: 'ZC-2024-0006', name: '会议室投影仪', category: '电子设备', department: '行政部', originalValue: '¥15,000', accumulatedDepreciation: '¥4,167', netValue: '¥10,833', monthlyDepreciation: '¥395.83', depreciationMethod: '直线法', purchaseDate: '2023-04-15', residualRate: 5, usefulLife: 3 }
])

const filteredList = computed(() => {
  return ledgerList.value.filter(item => {
    const deptMatch = !filterForm.department || item.department === filterForm.department
    const methodMatch = !filterForm.method || item.depreciationMethod === filterForm.method
    return deptMatch && methodMatch
  })
})

// 详情弹窗
const viewDialogVisible = ref(false)
const currentAsset = ref(null)

const depreciationHistory = ref([
  { period: '2024-01', depreciation: '¥527.75', accumulated: '¥5,555.00', netValue: '¥14,444.00', executeTime: '2024-01-31 18:00:00' },
  { period: '2023-12', depreciation: '¥527.75', accumulated: '¥5,027.25', netValue: '¥14,971.75', executeTime: '2023-12-31 18:00:00' },
  { period: '2023-11', depreciation: '¥527.75', accumulated: '¥4,499.50', netValue: '¥15,499.50', executeTime: '2023-11-30 18:00:00' },
  { period: '2023-10', depreciation: '¥527.75', accumulated: '¥3,971.75', netValue: '¥16,027.25', executeTime: '2023-10-31 18:00:00' }
])

function handleSearch() {
  ElMessage.success('查询完成')
}

function handleReset() {
  filterForm.category = []
  filterForm.department = ''
  filterForm.method = ''
  ElMessage.success('已重置筛选条件')
}

function handleView(row) {
  currentAsset.value = row
  viewDialogVisible.value = true
}

function exportLedger() {
  ElMessage.success('资产财务台账导出成功')
}

function exportAssetDetail() {
  ElMessage.success('资产详情导出成功')
}
</script>

<style lang="scss" scoped>
.ledger-container {
  .page-card { border-radius: 16px; }
  .page-header { 
    display: flex; 
    justify-content: space-between; 
    align-items: center; 
    h2 { margin: 0; font-size: 18px; color: #1f2937; } 
  }
  .filter-form { margin-bottom: 20px; }
  .stat-row { margin-bottom: 20px; }
  .stat-card {
    border-radius: 12px; padding: 20px; text-align: center; color: #fff;
    &.primary { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
    &.warning { background: linear-gradient(135deg, #f6d365 0%, #fda085 100%); }
    &.success { background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); }
    &.info { background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); color: #1f2937; }
    .stat-value { font-size: 24px; font-weight: bold; margin-bottom: 4px; }
    .stat-label { font-size: 14px; opacity: 0.9; }
  }
}
</style>
