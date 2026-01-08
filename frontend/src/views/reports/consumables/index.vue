<template>
  <div class="consumable-reports-container">
    <el-card class="page-card">
      <template #header>
        <div class="page-header">
          <h2>耗材报表</h2>
          <el-button type="primary">
            <el-icon><Download /></el-icon>
            导出报表
          </el-button>
        </div>
      </template>
      
      <el-form :inline="true" class="filter-form">
        <el-form-item label="报表类型">
          <el-select v-model="reportType" style="width: 200px">
            <el-option label="耗材汇总表" value="summary" />
            <el-option label="入库统计表" value="stock_in" />
            <el-option label="出库统计表" value="stock_out" />
            <el-option label="库存预警表" value="warning" />
          </el-select>
        </el-form-item>
        <el-form-item label="时间范围">
          <el-date-picker v-model="dateRange" type="daterange" range-separator="至" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary">生成报表</el-button>
        </el-form-item>
      </el-form>
      
      <el-table :data="reportData" style="width: 100%">
        <el-table-column prop="name" label="耗材名称" />
        <el-table-column prop="category" label="分类" />
        <el-table-column prop="stockIn" label="入库数量" />
        <el-table-column prop="stockOut" label="出库数量" />
        <el-table-column prop="currentStock" label="当前库存" />
        <el-table-column prop="totalValue" label="库存金额" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Download } from '@element-plus/icons-vue'

const reportType = ref('summary')
const dateRange = ref([])

const reportData = ref([
  { name: 'A4打印纸', category: '办公用品', stockIn: 100, stockOut: 50, currentStock: 50, totalValue: '¥1,250' },
  { name: '签字笔', category: '办公用品', stockIn: 200, stockOut: 190, currentStock: 10, totalValue: '¥30' }
])
</script>

<style lang="scss" scoped>
.consumable-reports-container {
  .page-card { border-radius: 16px; }
  .page-header { display: flex; justify-content: space-between; align-items: center; h2 { margin: 0; font-size: 18px; } }
  .filter-form { margin-bottom: 20px; }
}
</style>
