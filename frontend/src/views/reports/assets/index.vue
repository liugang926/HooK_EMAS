<template>
  <div class="asset-reports-container">
    <el-card class="page-card">
      <template #header>
        <div class="page-header">
          <h2>资产报表</h2>
          <el-button type="primary" @click="handleExport">
            <el-icon><Download /></el-icon>
            导出报表
          </el-button>
        </div>
      </template>
      
      <el-form :inline="true" class="filter-form">
        <el-form-item label="报表类型">
          <el-select v-model="reportType" style="width: 200px">
            <el-option label="资产汇总表" value="summary" />
            <el-option label="资产明细表" value="detail" />
            <el-option label="部门资产表" value="department" />
            <el-option label="分类统计表" value="category" />
          </el-select>
        </el-form-item>
        <el-form-item label="时间范围">
          <el-date-picker v-model="dateRange" type="daterange" range-separator="至" start-placeholder="开始日期" end-placeholder="结束日期" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary">生成报表</el-button>
        </el-form-item>
      </el-form>
      
      <div ref="chartRef" class="chart-container"></div>
      
      <el-table :data="reportData" style="width: 100%">
        <el-table-column prop="category" label="资产分类" />
        <el-table-column prop="count" label="数量" />
        <el-table-column prop="value" label="原值合计" />
        <el-table-column prop="netValue" label="净值合计" />
        <el-table-column prop="percentage" label="占比">
          <template #default="{ row }">
            <el-progress :percentage="row.percentage" :stroke-width="10" />
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Download } from '@element-plus/icons-vue'
import * as echarts from 'echarts'

const reportType = ref('summary')
const dateRange = ref([])
const chartRef = ref()

const reportData = ref([
  { category: '办公设备', count: 456, value: '¥2,580,000', netValue: '¥1,806,000', percentage: 36 },
  { category: '电子设备', count: 312, value: '¥1,890,000', netValue: '¥1,134,000', percentage: 25 },
  { category: '家具', count: 189, value: '¥680,000', netValue: '¥544,000', percentage: 15 },
  { category: '交通工具', count: 145, value: '¥1,200,000', netValue: '¥720,000', percentage: 12 },
  { category: '其他', count: 98, value: '¥450,000', netValue: '¥315,000', percentage: 12 }
])

function handleExport() {}

onMounted(() => {
  const chart = echarts.init(chartRef.value)
  chart.setOption({
    tooltip: { trigger: 'item' },
    legend: { orient: 'vertical', left: 'left' },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      data: reportData.value.map(item => ({ name: item.category, value: item.count }))
    }]
  })
})
</script>

<style lang="scss" scoped>
.asset-reports-container {
  .page-card { border-radius: 16px; }
  .page-header { display: flex; justify-content: space-between; align-items: center; h2 { margin: 0; font-size: 18px; } }
  .filter-form { margin-bottom: 20px; }
  .chart-container { height: 300px; margin-bottom: 20px; }
}
</style>
