<template>
  <div class="todo-container">
    <el-card class="page-card">
      <template #header>
        <div class="page-header">
          <h2>待办事项</h2>
          <div class="header-actions">
            <el-radio-group v-model="filterType" size="default">
              <el-radio-button label="all">全部</el-radio-button>
              <el-radio-button label="pending">待处理</el-radio-button>
              <el-radio-button label="processed">已处理</el-radio-button>
            </el-radio-group>
          </div>
        </div>
      </template>
      
      <el-table :data="todoList" style="width: 100%">
        <el-table-column label="类型" width="120">
          <template #default="{ row }">
            <el-tag :type="getTypeTagType(row.type)">{{ row.typeLabel }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="title" label="标题" min-width="200" />
        <el-table-column prop="creator" label="申请人" width="120" />
        <el-table-column prop="createTime" label="申请时间" width="180" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'pending' ? 'warning' : 'success'">
              {{ row.status === 'pending' ? '待处理' : '已处理' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleView(row)">查看</el-button>
            <template v-if="row.status === 'pending'">
              <el-button type="success" link @click="handleApprove(row)">通过</el-button>
              <el-button type="danger" link @click="handleReject(row)">拒绝</el-button>
            </template>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.current"
          v-model:page-size="pagination.pageSize"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'

const filterType = ref('all')

const todoList = ref([
  {
    id: 1,
    type: 'receive',
    typeLabel: '领用申请',
    title: '张三申请领用笔记本电脑',
    creator: '张三',
    createTime: '2024-01-15 10:30',
    status: 'pending'
  },
  {
    id: 2,
    type: 'borrow',
    typeLabel: '借用申请',
    title: '李四申请借用投影仪',
    creator: '李四',
    createTime: '2024-01-15 09:20',
    status: 'pending'
  },
  {
    id: 3,
    type: 'disposal',
    typeLabel: '处置申请',
    title: '王五提交旧电脑报废申请',
    creator: '王五',
    createTime: '2024-01-14 16:45',
    status: 'processed'
  }
])

const pagination = reactive({
  current: 1,
  pageSize: 10,
  total: 3
})

function getTypeTagType(type) {
  const types = {
    receive: 'primary',
    borrow: 'warning',
    disposal: 'danger',
    transfer: 'info'
  }
  return types[type] || 'info'
}

function handleView(row) {
  // 查看详情
}

function handleApprove(row) {
  // 通过审批
}

function handleReject(row) {
  // 拒绝审批
}
</script>

<style lang="scss" scoped>
.todo-container {
  .page-card {
    border-radius: 16px;
    
    .page-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      
      h2 {
        margin: 0;
        font-size: 18px;
        color: #1f2937;
      }
    }
  }
  
  .pagination-container {
    display: flex;
    justify-content: flex-end;
    margin-top: 20px;
  }
}
</style>
