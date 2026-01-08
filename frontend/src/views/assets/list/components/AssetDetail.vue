<template>
  <el-dialog
    v-model="visible"
    title="资产详情"
    width="800px"
    @close="handleClose"
  >
    <div class="asset-detail" v-if="asset">
      <div class="detail-header">
        <el-image
          :src="asset.image || defaultImage"
          fit="cover"
          class="detail-image"
        >
          <template #error>
            <div class="image-placeholder">
              <el-icon><Picture /></el-icon>
            </div>
          </template>
        </el-image>
        <div class="detail-basic">
          <h2>{{ asset.name }}</h2>
          <p class="asset-code">资产编号：{{ asset.asset_code }}</p>
          <div class="tags-row">
            <el-tag :type="getStatusType(asset.status)" size="large">
              {{ getStatusLabel(asset.status) }}
            </el-tag>
            <el-tag v-if="asset.category_name" type="info" size="large">
              {{ asset.category_name }}
            </el-tag>
          </div>
        </div>
      </div>
      
      <el-tabs v-model="activeTab">
        <el-tab-pane label="基本信息" name="basic">
          <el-descriptions :column="3" border>
            <el-descriptions-item label="资产分类">
              {{ asset.category_name || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="品牌">
              {{ asset.brand || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="型号">
              {{ asset.model || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="序列号">
              {{ asset.serial_number || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="计量单位">
              {{ asset.unit || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="数量">
              {{ asset.quantity || 1 }}
            </el-descriptions-item>
          </el-descriptions>
        </el-tab-pane>
        
        <el-tab-pane label="财务信息" name="finance">
          <el-descriptions :column="3" border>
            <el-descriptions-item label="原值(元)">
              {{ formatMoney(asset.original_value) }}
            </el-descriptions-item>
            <el-descriptions-item label="净值(元)">
              {{ formatMoney(asset.current_value) }}
            </el-descriptions-item>
            <el-descriptions-item label="累计折旧">
              {{ formatMoney(asset.accumulated_depreciation) }}
            </el-descriptions-item>
            <el-descriptions-item label="取得方式">
              {{ asset.acquisition_method_display || getAcquisitionLabel(asset.acquisition_method) }}
            </el-descriptions-item>
            <el-descriptions-item label="取得日期">
              {{ asset.acquisition_date || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="保修到期">
              {{ asset.warranty_expiry || '-' }}
            </el-descriptions-item>
          </el-descriptions>
        </el-tab-pane>
        
        <el-tab-pane label="使用信息" name="usage">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="使用人">
              {{ asset.using_user_name || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="使用部门">
              {{ asset.using_department_name || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="存放位置">
              {{ asset.location_name || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="管理部门">
              {{ asset.manage_department_name || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="资产管理员">
              {{ asset.manager_name || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="供应商">
              {{ asset.supplier_name || '-' }}
            </el-descriptions-item>
          </el-descriptions>
        </el-tab-pane>
        
        <el-tab-pane label="标签信息" name="tags">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="RFID编码">
              {{ asset.rfid_code || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="条形码">
              {{ asset.barcode || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="二维码">
              {{ asset.qrcode || '-' }}
            </el-descriptions-item>
          </el-descriptions>
        </el-tab-pane>
        
        <el-tab-pane label="备注" name="remark">
          <div class="remark-content">
            {{ asset.remark || '暂无备注' }}
          </div>
        </el-tab-pane>
        
        <el-tab-pane label="变动记录" name="operations">
          <div class="operations-container">
            <el-timeline v-if="operations.length > 0">
              <el-timeline-item
                v-for="op in operations"
                :key="op.id"
                :timestamp="op.created_at"
                :type="getOperationIconType(op.operation_type)"
                placement="top"
              >
                <el-card class="operation-card">
                  <div class="operation-header">
                    <el-tag :type="getOperationTagType(op.operation_type)" size="small">
                      {{ op.operation_type_display || getOperationLabel(op.operation_type) }}
                    </el-tag>
                    <span class="operator">{{ op.operator_name || '系统' }}</span>
                  </div>
                  <p class="operation-desc">{{ op.description }}</p>
                  <div v-if="op.old_data || op.new_data" class="operation-changes">
                    <el-collapse v-if="hasChanges(op)">
                      <el-collapse-item title="变更详情">
                        <div class="change-list">
                          <div v-for="(change, key) in getChanges(op)" :key="key" class="change-item">
                            <span class="change-label">{{ getFieldLabel(key) }}：</span>
                            <span class="change-old">{{ change.old || '(空)' }}</span>
                            <el-icon><ArrowRight /></el-icon>
                            <span class="change-new">{{ change.new || '(空)' }}</span>
                          </div>
                        </div>
                      </el-collapse-item>
                    </el-collapse>
                  </div>
                </el-card>
              </el-timeline-item>
            </el-timeline>
            <el-empty v-else description="暂无变动记录" />
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>
    
    <template #footer>
      <el-button @click="handleClose">关闭</el-button>
      <el-button type="primary" @click="handleEdit">编辑</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { Picture, ArrowRight } from '@element-plus/icons-vue'
import request from '@/utils/request'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  asset: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['update:modelValue', 'edit'])

const activeTab = ref('basic')
const operations = ref([])
const loadingOperations = ref(false)

// 默认图片
const defaultImage = 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMDAiIGhlaWdodD0iMTAwIj48cmVjdCBmaWxsPSIjZjNmNGY2IiB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIvPjx0ZXh0IHg9IjUwIiB5PSI1MCIgZm9udC1zaXplPSIxNCIgZmlsbD0iIzlhOWE5YSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPuaXoOWbvueJhzwvdGV4dD48L3N2Zz4='

// 显示状态
const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

// 状态映射
const statusMap = {
  idle: { label: '闲置', type: 'warning' },
  in_use: { label: '在用', type: 'success' },
  borrowed: { label: '借用', type: 'primary' },
  maintenance: { label: '维修中', type: 'danger' },
  pending_maintenance: { label: '待维修', type: 'warning' },
  disposed: { label: '已处置', type: 'info' },
  pending_disposal: { label: '待处置', type: 'warning' },
  approving: { label: '审批中', type: 'primary' }
}

// 取得方式映射
const acquisitionMap = {
  purchase: '采购',
  lease: '租赁',
  gift: '赠予',
  transfer: '调入',
  self_build: '自建',
  other: '其他'
}

function getStatusType(status) {
  return statusMap[status]?.type || 'info'
}

function getStatusLabel(status) {
  return statusMap[status]?.label || status
}

function getAcquisitionLabel(method) {
  return acquisitionMap[method] || method || '-'
}

function formatMoney(value) {
  if (value === null || value === undefined) return '-'
  return Number(value).toLocaleString('zh-CN', { minimumFractionDigits: 2 })
}

// 操作类型映射
const operationTypeMap = {
  create: { label: '录入', type: 'success', icon: 'success' },
  update: { label: '编辑', type: 'primary', icon: 'primary' },
  receive: { label: '领用', type: 'warning', icon: 'warning' },
  return: { label: '退还', type: 'info', icon: 'info' },
  borrow: { label: '借用', type: 'warning', icon: 'warning' },
  give_back: { label: '归还', type: 'success', icon: 'success' },
  transfer: { label: '调拨', type: 'primary', icon: 'primary' },
  change: { label: '变更', type: 'primary', icon: 'primary' },
  maintenance: { label: '维保', type: 'danger', icon: 'danger' },
  dispose: { label: '处置', type: 'danger', icon: 'danger' },
  inventory: { label: '盘点', type: 'info', icon: 'info' }
}

// 字段标签映射
const fieldLabelMap = {
  asset_code: '资产编号',
  name: '资产名称',
  category: '分类',
  brand: '品牌',
  model: '型号',
  serial_number: '序列号',
  original_value: '原值',
  current_value: '净值',
  status: '状态',
  using_user: '使用人',
  using_department: '使用部门',
  location: '存放位置',
  manager: '管理员',
  remark: '备注'
}

function getOperationLabel(type) {
  return operationTypeMap[type]?.label || type
}

function getOperationTagType(type) {
  return operationTypeMap[type]?.type || 'info'
}

function getOperationIconType(type) {
  return operationTypeMap[type]?.icon || 'info'
}

function getFieldLabel(key) {
  return fieldLabelMap[key] || key
}

function hasChanges(op) {
  if (!op.old_data || !op.new_data) return false
  return Object.keys(op.old_data).some(key => op.old_data[key] !== op.new_data[key])
}

function getChanges(op) {
  const changes = {}
  if (!op.old_data || !op.new_data) return changes
  
  Object.keys(op.old_data).forEach(key => {
    if (op.old_data[key] !== op.new_data[key]) {
      changes[key] = {
        old: op.old_data[key],
        new: op.new_data[key]
      }
    }
  })
  return changes
}

// 加载变动记录
async function loadOperations(assetId) {
  if (!assetId) return
  
  loadingOperations.value = true
  try {
    const res = await request.get('/assets/operations/', {
      params: { asset: assetId, page_size: 100 }
    })
    // Note: request interceptor returns response.data directly, so res is already the data
    operations.value = res?.results || res || []
  } catch (error) {
    console.error('加载变动记录失败:', error)
    operations.value = []
  } finally {
    loadingOperations.value = false
  }
}

// 监听资产变化，加载变动记录
watch(() => props.asset?.id, (newId) => {
  if (newId && props.modelValue) {
    loadOperations(newId)
  }
}, { immediate: true })

// 监听对话框打开，加载变动记录
watch(() => props.modelValue, (newVal) => {
  if (newVal && props.asset?.id) {
    loadOperations(props.asset.id)
  }
})

function handleClose() {
  visible.value = false
  activeTab.value = 'basic'
  operations.value = []
}

function handleEdit() {
  emit('edit', props.asset)
  handleClose()
}
</script>

<style lang="scss" scoped>
.asset-detail {
  .detail-header {
    display: flex;
    gap: 24px;
    margin-bottom: 24px;
    padding-bottom: 24px;
    border-bottom: 1px solid #e5e7eb;
    
    .detail-image {
      width: 160px;
      height: 160px;
      border-radius: 12px;
      border: 1px solid #e5e7eb;
      overflow: hidden;
      
      .image-placeholder {
        width: 100%;
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        background: #f3f4f6;
        color: #9ca3af;
        font-size: 48px;
      }
    }
    
    .detail-basic {
      flex: 1;
      display: flex;
      flex-direction: column;
      justify-content: center;
      
      h2 {
        margin: 0 0 8px;
        font-size: 24px;
        color: #1f2937;
      }
      
      .asset-code {
        color: #6b7280;
        margin: 0 0 16px;
        font-size: 14px;
      }
      
      .tags-row {
        display: flex;
        gap: 8px;
      }
    }
  }
  
  .remark-content {
    padding: 16px;
    background: #f9fafb;
    border-radius: 8px;
    min-height: 100px;
    color: #4b5563;
    line-height: 1.6;
  }
  
  .operations-container {
    padding: 16px 0;
    max-height: 400px;
    overflow-y: auto;
    
    .operation-card {
      margin-bottom: 8px;
      
      :deep(.el-card__body) {
        padding: 12px 16px;
      }
      
      .operation-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 8px;
        
        .operator {
          color: #6b7280;
          font-size: 13px;
        }
      }
      
      .operation-desc {
        margin: 0;
        color: #374151;
        font-size: 14px;
        line-height: 1.5;
      }
      
      .operation-changes {
        margin-top: 8px;
        
        .change-list {
          background: #f9fafb;
          padding: 12px;
          border-radius: 6px;
          
          .change-item {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 6px 0;
            font-size: 13px;
            
            &:not(:last-child) {
              border-bottom: 1px dashed #e5e7eb;
            }
            
            .change-label {
              color: #6b7280;
              min-width: 80px;
            }
            
            .change-old {
              color: #ef4444;
              text-decoration: line-through;
            }
            
            .el-icon {
              color: #9ca3af;
            }
            
            .change-new {
              color: #10b981;
            }
          }
        }
      }
    }
  }
}
</style>
