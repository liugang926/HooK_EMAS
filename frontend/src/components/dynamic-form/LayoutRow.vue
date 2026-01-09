<template>
  <div class="layout-row" :class="{ 'is-empty': !row.cols?.length }">
    <div class="row-handle">
      <el-icon><Rank /></el-icon>
    </div>
    
    <draggable
      v-model="row.cols"
      :group="{ name: 'fields', pull: false, put: true }"
      item-key="field"
      class="row-content"
      @add="handleFieldAdd"
    >
      <template #item="{ element: col, index: colIndex }">
        <div
          class="field-col"
          :style="{ width: `${(col.span / 24) * 100}%` }"
          :class="{ 'is-selected': isSelected(col.field) }"
          @click="handleSelect(col.field)"
        >
          <div class="field-preview">
            <span class="field-label">{{ getFieldLabel(col.field) }}</span>
            <span class="field-span">{{ col.span }}/24</span>
          </div>
          <el-button
            class="remove-btn"
            type="danger"
            :icon="Close"
            circle
            size="small"
            @click.stop="emit('remove-field', colIndex)"
          />
        </div>
      </template>
    </draggable>
    
    <el-button
      v-if="row.cols?.length"
      class="row-remove"
      type="danger"
      link
      :icon="Delete"
      @click="emit('remove')"
    />
    
    <div v-if="!row.cols?.length" class="empty-row">
      拖拽字段到此处
    </div>
  </div>
</template>

<script setup>
import { Rank, Close, Delete } from '@element-plus/icons-vue'
import draggable from 'vuedraggable'

const props = defineProps({
  row: {
    type: Object,
    required: true
  },
  fieldsMap: {
    type: Object,
    default: () => ({})
  },
  selectedField: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['remove', 'select-field', 'remove-field'])

function getFieldLabel(fieldKey) {
  return props.fieldsMap[fieldKey]?.label || fieldKey
}

function isSelected(fieldKey) {
  return props.selectedField === fieldKey
}

function handleSelect(fieldKey) {
  emit('select-field', fieldKey, props.row.id)
}

function handleFieldAdd(event) {
  // 新添加的字段默认宽度为 12
  const newIndex = event.newIndex
  if (props.row.cols[newIndex] && !props.row.cols[newIndex].span) {
    props.row.cols[newIndex].span = 12
  }
}
</script>

<style lang="scss" scoped>
.layout-row {
  display: flex;
  align-items: stretch;
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  margin-bottom: 8px;
  min-height: 50px;
  
  &.is-empty {
    border-style: dashed;
    background: #fafafa;
  }
  
  .row-handle {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    background: #f5f7fa;
    border-right: 1px solid #e4e7ed;
    cursor: grab;
    color: #909399;
    
    &:hover {
      background: #e6e8eb;
    }
  }
  
  .row-content {
    flex: 1;
    display: flex;
    flex-wrap: wrap;
    padding: 8px;
    gap: 8px;
    min-height: 40px;
  }
  
  .field-col {
    position: relative;
    min-width: 100px;
    
    .field-preview {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 8px 12px;
      background: #ecf5ff;
      border: 1px solid #b3d8ff;
      border-radius: 4px;
      cursor: pointer;
      transition: all 0.2s;
      
      .field-label {
        font-size: 13px;
        color: #409eff;
      }
      
      .field-span {
        font-size: 11px;
        color: #909399;
      }
    }
    
    &.is-selected .field-preview {
      border-color: #409eff;
      box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
    }
    
    .remove-btn {
      position: absolute;
      top: -8px;
      right: -8px;
      opacity: 0;
      transition: opacity 0.2s;
    }
    
    &:hover .remove-btn {
      opacity: 1;
    }
  }
  
  .row-remove {
    display: flex;
    align-items: center;
    padding: 0 8px;
    opacity: 0;
    transition: opacity 0.2s;
  }
  
  &:hover .row-remove {
    opacity: 1;
  }
  
  .empty-row {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #c0c4cc;
    font-size: 13px;
  }
}
</style>
