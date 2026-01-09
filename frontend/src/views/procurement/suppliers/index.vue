<template>
  <div class="suppliers-container">
    <DynamicList
      ref="listRef"
      module="supplier"
      :actions="['create', 'edit', 'delete', 'view', 'export']"
      search-placeholder="搜索供应商名称、联系人..."
      create-button-text="新增供应商"
      @row-click="handleRowClick"
    >
      <!-- Custom column for status with switch -->
      <template #column-status="{ row, value }">
        <el-switch
          v-model="row.status"
          active-value="active"
          inactive-value="inactive"
          @click.stop
          @change="handleStatusChange(row)"
        />
      </template>
      
      <!-- Custom batch actions -->
      <template #batch-actions="{ selected }">
        <el-button size="small" type="danger" @click="handleBatchDelete(selected)">
          批量删除
        </el-button>
        <el-button size="small" @click="handleBatchEnable(selected)">
          批量启用
        </el-button>
        <el-button size="small" @click="handleBatchDisable(selected)">
          批量停用
        </el-button>
      </template>
    </DynamicList>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import DynamicList from '@/components/list/DynamicList.vue'
import request from '@/api/request'

const listRef = ref(null)

// Handle row click
function handleRowClick(row) {
  console.log('Row clicked:', row)
}

// Handle status toggle
async function handleStatusChange(row) {
  try {
    await request.patch(`/procurement/suppliers/${row.id}/`, {
      status: row.status
    })
    ElMessage.success(`供应商 "${row.name}" 已${row.status === 'active' ? '启用' : '停用'}`)
  } catch (error) {
    // Revert on error
    row.status = row.status === 'active' ? 'inactive' : 'active'
    ElMessage.error('状态更新失败')
  }
}

// Batch delete
async function handleBatchDelete(selected) {
  if (selected.length === 0) return
  
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selected.length} 个供应商吗？`,
      '批量删除确认',
      { type: 'warning' }
    )
    
    const ids = selected.map(item => item.id)
    await request.post('/procurement/suppliers/bulk_delete/', { ids })
    
    ElMessage.success('批量删除成功')
    listRef.value?.loadData()
    listRef.value?.clearSelection()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量删除失败')
    }
  }
}

// Batch enable
async function handleBatchEnable(selected) {
  if (selected.length === 0) return
  
  try {
    const ids = selected.map(item => item.id)
    await request.post('/procurement/suppliers/bulk_update/', {
      ids,
      data: { status: 'active' }
    })
    
    ElMessage.success('批量启用成功')
    listRef.value?.loadData()
    listRef.value?.clearSelection()
  } catch (error) {
    ElMessage.error('批量启用失败')
  }
}

// Batch disable
async function handleBatchDisable(selected) {
  if (selected.length === 0) return
  
  try {
    const ids = selected.map(item => item.id)
    await request.post('/procurement/suppliers/bulk_update/', {
      ids,
      data: { status: 'inactive' }
    })
    
    ElMessage.success('批量停用成功')
    listRef.value?.loadData()
    listRef.value?.clearSelection()
  } catch (error) {
    ElMessage.error('批量停用失败')
  }
}
</script>

<style lang="scss" scoped>
.suppliers-container {
  width: 100%;
}
</style>
