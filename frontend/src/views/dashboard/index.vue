<template>
  <div class="dashboard-container">
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stat-cards">
      <el-col :xs="24" :sm="12" :md="6">
        <div class="stat-card assets">
          <div class="stat-icon">
            <el-icon><Box /></el-icon>
          </div>
          <div class="stat-info">
            <p class="stat-value">{{ statistics.totalAssets }}</p>
            <p class="stat-label">资产总数</p>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <div class="stat-card value">
          <div class="stat-icon">
            <el-icon><Money /></el-icon>
          </div>
          <div class="stat-info">
            <p class="stat-value">{{ formatMoney(statistics.totalValue) }}</p>
            <p class="stat-label">资产总值</p>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <div class="stat-card inuse">
          <div class="stat-icon">
            <el-icon><User /></el-icon>
          </div>
          <div class="stat-info">
            <p class="stat-value">{{ statistics.inUseAssets }}</p>
            <p class="stat-label">使用中资产</p>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <div class="stat-card idle">
          <div class="stat-icon">
            <el-icon><Box /></el-icon>
          </div>
          <div class="stat-info">
            <p class="stat-value">{{ statistics.idleAssets }}</p>
            <p class="stat-label">闲置资产</p>
          </div>
        </div>
      </el-col>
    </el-row>
    
    <!-- 图表区域 -->
    <el-row :gutter="20" class="chart-section">
      <el-col :xs="24" :lg="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>资产分类统计</span>
              <el-radio-group v-model="categoryChartType" size="small">
                <el-radio-button label="pie">饼图</el-radio-button>
                <el-radio-button label="bar">柱图</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div ref="categoryChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
      <el-col :xs="24" :lg="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>资产状态分布</span>
            </div>
          </template>
          <div ref="statusChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" class="chart-section">
      <el-col :xs="24" :lg="16">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>近12个月资产变化趋势</span>
            </div>
          </template>
          <div ref="trendChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
      <el-col :xs="24" :lg="8">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>部门资产Top5</span>
            </div>
          </template>
          <div ref="deptChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 待办事项和快捷操作 -->
    <el-row :gutter="20" class="bottom-section">
      <el-col :xs="24" :lg="12">
        <el-card class="todo-card">
          <template #header>
            <div class="card-header">
              <span>待办事项</span>
              <el-link type="primary" @click="goToTodo">查看全部</el-link>
            </div>
          </template>
          <div class="todo-list">
            <div v-if="todoList.length === 0" class="empty-state">
              <el-icon><DocumentChecked /></el-icon>
              <p>暂无待办事项</p>
            </div>
            <div
              v-for="item in todoList"
              :key="item.id"
              class="todo-item"
              @click="handleTodoClick(item)"
            >
              <div class="todo-type" :class="item.type">
                {{ item.typeLabel }}
              </div>
              <div class="todo-content">
                <p class="todo-title">{{ item.title }}</p>
                <p class="todo-meta">{{ item.creator }} · {{ item.createTime }}</p>
              </div>
              <el-icon class="todo-arrow"><ArrowRight /></el-icon>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :lg="12">
        <el-card class="quick-actions-card">
          <template #header>
            <div class="card-header">
              <span>快捷操作</span>
            </div>
          </template>
          <div class="quick-actions">
            <div class="action-item" @click="goTo('/assets/create')">
              <div class="action-icon add">
                <el-icon><Plus /></el-icon>
              </div>
              <span>资产录入</span>
            </div>
            <div class="action-item" @click="goTo('/assets/receive')">
              <div class="action-icon receive">
                <el-icon><Download /></el-icon>
              </div>
              <span>资产领用</span>
            </div>
            <div class="action-item" @click="goTo('/assets/borrow')">
              <div class="action-icon borrow">
                <el-icon><Share /></el-icon>
              </div>
              <span>资产借用</span>
            </div>
            <div class="action-item" @click="goTo('/assets/transfer')">
              <div class="action-icon transfer">
                <el-icon><Switch /></el-icon>
              </div>
              <span>资产调拨</span>
            </div>
            <div class="action-item" @click="goTo('/inventory/tasks')">
              <div class="action-icon inventory">
                <el-icon><Document /></el-icon>
              </div>
              <span>资产盘点</span>
            </div>
            <div class="action-item" @click="goTo('/assets/disposal')">
              <div class="action-icon disposal">
                <el-icon><Delete /></el-icon>
              </div>
              <span>资产处置</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'
import {
  Box,
  Money,
  User,
  ArrowRight,
  Plus,
  Download,
  Share,
  Switch,
  Document,
  Delete,
  DocumentChecked
} from '@element-plus/icons-vue'

const router = useRouter()

// 统计数据
const statistics = ref({
  totalAssets: 1256,
  totalValue: 12580000,
  inUseAssets: 892,
  idleAssets: 364
})

// 待办事项
const todoList = ref([
  {
    id: 1,
    type: 'receive',
    typeLabel: '领用申请',
    title: '张三申请领用笔记本电脑',
    creator: '张三',
    createTime: '2024-01-15 10:30'
  },
  {
    id: 2,
    type: 'borrow',
    typeLabel: '借用申请',
    title: '李四申请借用投影仪',
    creator: '李四',
    createTime: '2024-01-15 09:20'
  },
  {
    id: 3,
    type: 'disposal',
    typeLabel: '处置申请',
    title: '王五提交旧电脑报废申请',
    creator: '王五',
    createTime: '2024-01-14 16:45'
  }
])

// 图表相关
const categoryChartType = ref('pie')
const categoryChartRef = ref()
const statusChartRef = ref()
const trendChartRef = ref()
const deptChartRef = ref()

let categoryChart = null
let statusChart = null
let trendChart = null
let deptChart = null

// 格式化金额
function formatMoney(value) {
  if (value >= 10000) {
    return (value / 10000).toFixed(2) + ' 万'
  }
  return value.toFixed(2)
}

// 导航
function goTo(path) {
  router.push(path)
}

function goToTodo() {
  router.push('/todo')
}

function handleTodoClick(item) {
  // 跳转到对应的待办详情
}

// 初始化图表
function initCharts() {
  // 分类统计图
  categoryChart = echarts.init(categoryChartRef.value)
  updateCategoryChart()
  
  // 状态分布图
  statusChart = echarts.init(statusChartRef.value)
  statusChart.setOption({
    tooltip: {
      trigger: 'item'
    },
    legend: {
      orient: 'vertical',
      right: 20,
      top: 'center'
    },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      center: ['40%', '50%'],
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 10,
        borderColor: '#fff',
        borderWidth: 2
      },
      label: {
        show: false
      },
      emphasis: {
        label: {
          show: true,
          fontSize: 16,
          fontWeight: 'bold'
        }
      },
      data: [
        { value: 892, name: '使用中', itemStyle: { color: '#10b981' } },
        { value: 364, name: '闲置', itemStyle: { color: '#f59e0b' } },
        { value: 45, name: '维修中', itemStyle: { color: '#ef4444' } },
        { value: 23, name: '已报废', itemStyle: { color: '#6b7280' } }
      ]
    }]
  })
  
  // 趋势图
  trendChart = echarts.init(trendChartRef.value)
  trendChart.setOption({
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['新增资产', '处置资产', '资产总数']
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: ['2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月', '1月']
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: '新增资产',
        type: 'bar',
        data: [45, 32, 28, 56, 42, 38, 52, 48, 36, 44, 50, 62],
        itemStyle: { color: '#10b981' }
      },
      {
        name: '处置资产',
        type: 'bar',
        data: [12, 8, 15, 10, 6, 18, 14, 9, 11, 7, 13, 16],
        itemStyle: { color: '#ef4444' }
      },
      {
        name: '资产总数',
        type: 'line',
        yAxisIndex: 0,
        data: [1100, 1124, 1137, 1183, 1219, 1239, 1277, 1316, 1341, 1378, 1415, 1461],
        itemStyle: { color: '#3b82f6' },
        smooth: true
      }
    ]
  })
  
  // 部门Top5图
  deptChart = echarts.init(deptChartRef.value)
  deptChart.setOption({
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    grid: {
      left: '3%',
      right: '10%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'value'
    },
    yAxis: {
      type: 'category',
      data: ['人力资源部', '市场部', '财务部', '研发部', '行政部']
    },
    series: [{
      type: 'bar',
      data: [120, 156, 189, 345, 412],
      itemStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
          { offset: 0, color: '#667eea' },
          { offset: 1, color: '#764ba2' }
        ])
      },
      barWidth: 20,
      label: {
        show: true,
        position: 'right'
      }
    }]
  })
}

function updateCategoryChart() {
  if (!categoryChart) return
  
  const option = categoryChartType.value === 'pie'
    ? {
        tooltip: {
          trigger: 'item'
        },
        legend: {
          orient: 'vertical',
          right: 20,
          top: 'center'
        },
        series: [{
          type: 'pie',
          radius: ['40%', '70%'],
          center: ['40%', '50%'],
          avoidLabelOverlap: false,
          itemStyle: {
            borderRadius: 10,
            borderColor: '#fff',
            borderWidth: 2
          },
          label: {
            show: false
          },
          emphasis: {
            label: {
              show: true,
              fontSize: 14,
              fontWeight: 'bold'
            }
          },
          data: [
            { value: 456, name: '办公设备' },
            { value: 312, name: '电子设备' },
            { value: 189, name: '家具' },
            { value: 145, name: '交通工具' },
            { value: 98, name: '其他' }
          ]
        }]
      }
    : {
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow'
          }
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: ['办公设备', '电子设备', '家具', '交通工具', '其他']
        },
        yAxis: {
          type: 'value'
        },
        series: [{
          type: 'bar',
          data: [456, 312, 189, 145, 98],
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: '#667eea' },
              { offset: 1, color: '#764ba2' }
            ])
          },
          barWidth: 40
        }]
      }
  
  categoryChart.setOption(option, true)
}

// 监听图表类型变化
watch(categoryChartType, () => {
  updateCategoryChart()
})

// 窗口大小变化时重绘图表
function handleResize() {
  categoryChart?.resize()
  statusChart?.resize()
  trendChart?.resize()
  deptChart?.resize()
}

onMounted(() => {
  initCharts()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  categoryChart?.dispose()
  statusChart?.dispose()
  trendChart?.dispose()
  deptChart?.dispose()
})
</script>

<style lang="scss" scoped>
.dashboard-container {
  .stat-cards {
    margin-bottom: 20px;
    
    .stat-card {
      display: flex;
      align-items: center;
      padding: 24px;
      border-radius: 16px;
      background: #fff;
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
      transition: transform 0.3s, box-shadow 0.3s;
      
      &:hover {
        transform: translateY(-4px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
      }
      
      .stat-icon {
        width: 56px;
        height: 56px;
        border-radius: 14px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 16px;
        
        .el-icon {
          font-size: 28px;
          color: #fff;
        }
      }
      
      .stat-info {
        .stat-value {
          font-size: 28px;
          font-weight: 700;
          color: #1f2937;
          margin: 0 0 4px;
        }
        
        .stat-label {
          font-size: 14px;
          color: #6b7280;
          margin: 0;
        }
      }
      
      &.assets .stat-icon {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      }
      
      &.value .stat-icon {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
      }
      
      &.inuse .stat-icon {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
      }
      
      &.idle .stat-icon {
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
      }
    }
  }
  
  .chart-section {
    margin-bottom: 20px;
    
    .chart-card {
      border-radius: 16px;
      
      .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        
        span {
          font-size: 16px;
          font-weight: 600;
          color: #1f2937;
        }
      }
      
      .chart-container {
        height: 300px;
      }
    }
  }
  
  .bottom-section {
    .todo-card,
    .quick-actions-card {
      border-radius: 16px;
      
      .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        
        span {
          font-size: 16px;
          font-weight: 600;
          color: #1f2937;
        }
      }
    }
    
    .todo-list {
      .empty-state {
        text-align: center;
        padding: 40px 0;
        color: #9ca3af;
        
        .el-icon {
          font-size: 48px;
          margin-bottom: 12px;
        }
        
        p {
          margin: 0;
        }
      }
      
      .todo-item {
        display: flex;
        align-items: center;
        padding: 16px;
        border-radius: 12px;
        cursor: pointer;
        transition: background 0.2s;
        
        &:hover {
          background: #f9fafb;
        }
        
        &:not(:last-child) {
          border-bottom: 1px solid #f3f4f6;
        }
        
        .todo-type {
          padding: 4px 12px;
          border-radius: 20px;
          font-size: 12px;
          margin-right: 12px;
          
          &.receive {
            background: #dbeafe;
            color: #2563eb;
          }
          
          &.borrow {
            background: #fef3c7;
            color: #d97706;
          }
          
          &.disposal {
            background: #fee2e2;
            color: #dc2626;
          }
        }
        
        .todo-content {
          flex: 1;
          
          .todo-title {
            font-size: 14px;
            color: #1f2937;
            margin: 0 0 4px;
          }
          
          .todo-meta {
            font-size: 12px;
            color: #9ca3af;
            margin: 0;
          }
        }
        
        .todo-arrow {
          color: #9ca3af;
        }
      }
    }
    
    .quick-actions {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 20px;
      
      .action-item {
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 20px;
        border-radius: 12px;
        cursor: pointer;
        transition: all 0.3s;
        
        &:hover {
          background: #f9fafb;
          
          .action-icon {
            transform: scale(1.1);
          }
        }
        
        .action-icon {
          width: 48px;
          height: 48px;
          border-radius: 12px;
          display: flex;
          align-items: center;
          justify-content: center;
          margin-bottom: 8px;
          transition: transform 0.3s;
          
          .el-icon {
            font-size: 24px;
            color: #fff;
          }
          
          &.add {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          }
          
          &.receive {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
          }
          
          &.borrow {
            background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
          }
          
          &.transfer {
            background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
          }
          
          &.inventory {
            background: linear-gradient(135deg, #d299c2 0%, #fef9d7 100%);
          }
          
          &.disposal {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
          }
        }
        
        span {
          font-size: 14px;
          color: #4b5563;
        }
      }
    }
  }
}
</style>
