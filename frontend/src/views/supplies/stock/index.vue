<template>
  <div class="supplies-stock-container">
    <el-card class="page-card">
      <template #header>
        <div class="page-header">
          <h2>实时库存</h2>
        </div>
      </template>
      
      <!-- List Toolbar -->
      <div class="list-toolbar">
        <div class="toolbar-search">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索用品名称..."
            clearable
            style="width: 280px"
            @keyup.enter="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="toggleAdvanced">
            <el-icon><Filter /></el-icon>
            {{ showAdvanced ? '收起筛选' : '高级筛选' }}
          </el-button>
          <el-button @click="handleReset">
            <el-icon><Refresh /></el-icon>
            重置
          </el-button>
        </div>
      </div>

      <!-- Advanced Filters -->
      <el-collapse-transition>
        <div v-show="showAdvanced" class="advanced-filters">
          <el-form :inline="true" class="filter-form">
            <el-form-item label="库存状态">
              <el-select v-model="filterForm.stockStatus" placeholder="全部" clearable style="width: 140px">
                <el-option label="正常" value="normal" />
                <el-option label="低库存预警" value="low" />
                <el-option label="缺货" value="out" />
              </el-select>
            </el-form-item>
          </el-form>
        </div>
      </el-collapse-transition>
      
      <!-- 库存统计卡片 -->
      <el-row :gutter="20" class="stat-cards">
        <el-col :span="6">
          <div class="stat-card">
            <div class="stat-value">{{ statistics.totalItems }}</div>
            <div class="stat-label">用品种类</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-card">
            <div class="stat-value">{{ statistics.totalStock }}</div>
            <div class="stat-label">总库存数量</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-card warning">
            <div class="stat-value">{{ statistics.lowStock }}</div>
            <div class="stat-label">低库存预警</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-card danger">
            <div class="stat-value">{{ statistics.outOfStock }}</div>
            <div class="stat-label">缺货用品</div>
          </div>
        </el-col>
      </el-row>
      
      <el-table :data="stockList" style="width: 100%" v-loading="loading">
        <el-table-column prop="code" label="用品编号" width="120" />
        <el-table-column prop="name" label="用品名称" min-width="150" />
        <el-table-column prop="category_name" label="分类" width="120" />
        <el-table-column prop="unit" label="单位" width="80" />
        <el-table-column prop="warehouse_name" label="仓库" width="120" />
        <el-table-column prop="quantity" label="库存数量" width="100">
          <template #default="{ row }">
            <span :class="getStockClass(row)">{{ row.quantity }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="min_stock" label="安全库存" width="100" />
        <el-table-column prop="status" label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="getStockStatus(row).type">{{ getStockStatus(row).label }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="updated_at" label="更新时间" width="180" />
      </el-table>
      
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next"
          @size-change="loadData"
          @current-change="loadData"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'

import { ElMessage } from 'element-plus'
import { Search, Filter, Refresh } from '@element-plus/icons-vue'
import request from '@/api/request'
import { useAppStore } from '@/stores/app'
import { extractListData, extractPaginationInfo } from '@/utils/api-helpers'

const appStore = useAppStore()
const loading = ref(false)
const searchKeyword = ref('')
const showAdvanced = ref(false)
const filterForm = reactive({ stockStatus: '' })
const stockList = ref([])
const pagination = reactive({ page: 1, pageSize: 20, total: 0 })

const statistics = computed(() => {
  const totalItems = stockList.value.length
  const totalStock = stockList.value.reduce((sum, item) => sum + (item.quantity || 0), 0)
  const lowStock = stockList.value.filter(item => item.quantity > 0 && item.quantity <= item.min_stock).length
  const outOfStock = stockList.value.filter(item => item.quantity <= 0).length
  return { totalItems, totalStock, lowStock, outOfStock }
})

function getStockClass(row) {
  if (row.quantity <= 0) return 'stock-out'
  if (row.quantity <= row.min_stock) return 'stock-low'
  return 'stock-normal'
}

function getStockStatus(row) {
  if (row.quantity <= 0) return { type: 'danger', label: '缺货' }
  if (row.quantity <= row.min_stock) return { type: 'warning', label: '低库存' }
  return { type: 'success', label: '正常' }
}

async function loadData() {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
      company: appStore.currentCompany?.id
    }
    if (searchKeyword.value) params.search = searchKeyword.value
    
    const res = await request.get('/consumables/stocks/', { params })
    stockList.value = extractListData(res)
    const pageInfo = extractPaginationInfo(res)
    pagination.total = pageInfo.total || stockList.value.length
  } catch (error) {
    // Mock data
    stockList.value = [
      { id: 1, code: 'BG-0001', name: 'A4打印纸', category_name: '纸张类', unit: '包', warehouse_name: '总仓库', quantity: 50, min_stock: 20, updated_at: '2026-01-08 10:00' },
      { id: 2, code: 'BG-0002', name: '签字笔', category_name: '书写工具', unit: '支', warehouse_name: '总仓库', quantity: 10, min_stock: 50, updated_at: '2026-01-08 09:30' },
      { id: 3, code: 'BG-0003', name: '文件夹', category_name: '文件管理', unit: '个', warehouse_name: '总仓库', quantity: 100, min_stock: 30, updated_at: '2026-01-07 16:00' },
      { id: 4, code: 'BG-0004', name: '墨盒', category_name: '办公设备耗材', unit: '个', warehouse_name: '总仓库', quantity: 0, min_stock: 5, updated_at: '2026-01-06 14:00' }
    ]
  } finally {
    loading.value = false
  }
}

function toggleAdvanced() {
  showAdvanced.value = !showAdvanced.value
}

function handleSearch() {
  pagination.page = 1
  loadData()
}

function handleReset() {
  searchKeyword.value = ''
  filterForm.stockStatus = ''
  handleSearch()
}

onMounted(() => {
  loadData()
})
</script>

<style lang="scss" scoped>
.supplies-stock-container {
  .page-card { border-radius: 16px; }
  
  .page-header { 
    display: flex; 
    justify-content: space-between; 
    align-items: center; 
    h2 { margin: 0; font-size: 18px; color: #1f2937; } 
  }
  
  .list-toolbar {
    display: flex;
    flex-wrap: wrap;
    align-items: flex-start;
    justify-content: space-between;
    gap: 12px;
    margin-bottom: 16px;
    padding: 16px;
    background: #f8fafc;
    border-radius: 8px;
    
    .toolbar-search {
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
    }
  }
  
  .advanced-filters {
    padding: 16px;
    background-color: #f8fafc;
    border-radius: 8px;
    margin-bottom: 16px;
    
    .filter-form {
      margin-bottom: 0;
      :deep(.el-form-item) {
        margin-bottom: 0;
      }
    }
  }
  
  .stat-cards {
    margin-bottom: 20px;
    
    .stat-card {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      border-radius: 12px;
      padding: 20px;
      color: white;
      text-align: center;
      
      &.warning {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
      }
      
      &.danger {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
      }
      
      .stat-value {
        font-size: 28px;
        font-weight: bold;
        margin-bottom: 4px;
      }
      
      .stat-label {
        font-size: 14px;
        opacity: 0.9;
      }
    }
  }
  
  .stock-out { color: #f56c6c; font-weight: bold; }
  .stock-low { color: #e6a23c; font-weight: bold; }
  .stock-normal { color: #67c23a; }
  
  .pagination-wrapper {
    margin-top: 16px;
    display: flex;
    justify-content: flex-end;
  }
}
</style>
