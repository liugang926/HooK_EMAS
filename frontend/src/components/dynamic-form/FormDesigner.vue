<template>
  <div class="form-designer">
    <!-- 顶部工具栏 -->
    <div class="designer-header">
      <h2>{{ moduleLabel || '表单设计器' }}</h2>
      <div class="header-actions">
        <el-button @click="handlePreview">
          <el-icon><View /></el-icon>
          预览
        </el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">
          <el-icon><Check /></el-icon>
          保存布局
        </el-button>
      </div>
    </div>

    <div class="designer-body">
      <!-- 左侧：字段库 -->
      <div class="field-library">
        <div class="panel-header">
          <span>可用字段</span>
          <el-input
            v-model="fieldSearch"
            placeholder="搜索字段"
            size="small"
            clearable
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </div>
        
        <div class="field-list">
          <draggable
            v-model="availableFields"
            :group="{ name: 'fields', pull: 'clone', put: false }"
            :sort="false"
            item-key="key"
            :clone="cloneField"
          >
            <template #item="{ element }">
              <div class="field-item" :class="{ 'is-used': isFieldUsed(element.key) }">
                <el-icon><component :is="getFieldIcon(element.type)" /></el-icon>
                <span class="field-name">{{ element.label }}</span>
                <span class="field-type">{{ getFieldTypeLabel(element.type) }}</span>
              </div>
            </template>
          </draggable>
        </div>
      </div>

      <!-- 中间：画布 -->
      <div class="design-canvas">
        <div class="panel-header">
          <span>表单布局</span>
          <el-button-group size="small">
            <el-button @click="addRow">
              <el-icon><Plus /></el-icon>
              添加行
            </el-button>
            <el-button @click="addGroup">
              <el-icon><FolderAdd /></el-icon>
              添加分组
            </el-button>
          </el-button-group>
        </div>

        <div class="canvas-content">
          <!-- 分组区域 -->
          <draggable
            v-model="layoutConfig.groups"
            group="groups"
            item-key="id"
            handle=".group-handle"
          >
            <template #item="{ element: group, index: groupIndex }">
              <div class="layout-group">
                <div class="group-header">
                  <el-icon class="group-handle"><Rank /></el-icon>
                  <el-input
                    v-model="group.title"
                    size="small"
                    placeholder="分组名称"
                    style="width: 200px"
                  />
                  <el-switch v-model="group.collapsed" size="small" />
                  <span class="switch-label">默认折叠</span>
                  <el-button
                    type="danger"
                    link
                    size="small"
                    @click="removeGroup(groupIndex)"
                  >
                    删除分组
                  </el-button>
                </div>
                
                <!-- 分组内的行 -->
                <draggable
                  v-model="group.rows"
                  group="rows"
                  item-key="id"
                  class="group-rows"
                >
                  <template #item="{ element: row, index: rowIndex }">
                    <LayoutRow
                      :row="row"
                      :fields-map="fieldsMap"
                      @remove="removeRowFromGroup(groupIndex, rowIndex)"
                      @select-field="selectField"
                      @remove-field="removeFieldFromGroupRow(groupIndex, rowIndex, $event)"
                    />
                  </template>
                </draggable>
                
                <el-button
                  class="add-row-btn"
                  size="small"
                  @click="addRowToGroup(groupIndex)"
                >
                  <el-icon><Plus /></el-icon>
                  添加行
                </el-button>
              </div>
            </template>
          </draggable>

          <!-- 独立行区域 -->
          <draggable
            v-model="layoutConfig.rows"
            group="rows"
            item-key="id"
            class="standalone-rows"
          >
            <template #item="{ element: row, index: rowIndex }">
              <LayoutRow
                :row="row"
                :fields-map="fieldsMap"
                @remove="removeRow(rowIndex)"
                @select-field="selectField"
                @remove-field="removeFieldFromRow(rowIndex, $event)"
              />
            </template>
          </draggable>

          <!-- 空状态 -->
          <div
            v-if="!layoutConfig.rows?.length && !layoutConfig.groups?.length"
            class="empty-canvas"
          >
            <el-empty description="从左侧拖拽字段到此处">
              <el-button @click="addRow">添加行</el-button>
            </el-empty>
          </div>
        </div>
      </div>

      <!-- 右侧：属性面板 -->
      <div class="property-panel">
        <div class="panel-header">
          <span>{{ selectedField ? '字段属性' : '布局属性' }}</span>
        </div>

        <div v-if="selectedField" class="property-content">
          <el-form label-position="top" size="small">
            <el-form-item label="字段标识">
              <el-input :value="selectedField.key" disabled />
            </el-form-item>
            <el-form-item label="显示名称">
              <el-input v-model="selectedField.label" />
            </el-form-item>
            <el-form-item label="字段类型">
              <el-input :value="getFieldTypeLabel(selectedField.type)" disabled />
            </el-form-item>
            <el-form-item label="栅格宽度">
              <el-slider
                v-model="selectedFieldSpan"
                :min="4"
                :max="24"
                :step="4"
                show-stops
                :marks="{ 8: '1/3', 12: '1/2', 16: '2/3', 24: '全宽' }"
              />
            </el-form-item>
            <el-form-item label="是否必填">
              <el-switch v-model="selectedField.required" />
            </el-form-item>
            <el-form-item label="占位提示">
              <el-input v-model="selectedField.placeholder" />
            </el-form-item>
            <el-form-item label="帮助文本">
              <el-input v-model="selectedField.helpText" type="textarea" :rows="2" />
            </el-form-item>
            
            <!-- 公式配置 -->
            <template v-if="selectedField.type === 'formula'">
              <el-divider content-position="left">公式配置</el-divider>
              <el-form-item label="计算表达式">
                <el-input
                  v-model="selectedField.formulaConfig.expression"
                  placeholder="如: price * quantity"
                />
              </el-form-item>
              <el-form-item label="小数精度">
                <el-input-number
                  v-model="selectedField.formulaConfig.precision"
                  :min="0"
                  :max="6"
                />
              </el-form-item>
            </template>
          </el-form>
        </div>

        <div v-else class="property-content">
          <el-form label-position="top" size="small">
            <el-form-item label="表单标签宽度">
              <el-input v-model="formSettings.labelWidth" placeholder="100px" />
            </el-form-item>
            <el-form-item label="列间距">
              <el-input-number v-model="formSettings.gutter" :min="0" :max="32" />
            </el-form-item>
          </el-form>
        </div>
      </div>
    </div>

    <!-- 预览对话框 -->
    <el-dialog v-model="previewVisible" title="表单预览" width="900px">
      <DynamicForm
        v-if="previewVisible"
        :config="previewConfig"
        :layout="layoutConfig"
        mode="create"
      />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  View, Check, Search, Plus, FolderAdd, Rank,
  Edit, Calendar, Select, Document, Switch, Link
} from '@element-plus/icons-vue'
import draggable from 'vuedraggable'
import DynamicForm from '@/components/dynamic-form/DynamicForm.vue'
import LayoutRow from './LayoutRow.vue'

const props = defineProps({
  module: {
    type: String,
    required: true
  },
  moduleLabel: {
    type: String,
    default: ''
  },
  // 字段定义列表
  fields: {
    type: Array,
    default: () => []
  },
  // 初始布局
  initialLayout: {
    type: Object,
    default: () => ({ rows: [], groups: [] })
  }
})

const emit = defineEmits(['save'])

// 状态
const saving = ref(false)
const previewVisible = ref(false)
const fieldSearch = ref('')
const selectedField = ref(null)
const selectedColIndex = ref(null)
const selectedRowId = ref(null)

// 表单设置
const formSettings = reactive({
  labelWidth: '100px',
  gutter: 16
})

// 布局配置
const layoutConfig = reactive({
  rows: [],
  groups: []
})

// 字段映射
const fieldsMap = computed(() => {
  const map = {}
  for (const field of props.fields) {
    map[field.key] = field
  }
  return map
})

// 可用字段列表（过滤搜索）
const availableFields = computed({
  get() {
    if (!fieldSearch.value) return props.fields
    const search = fieldSearch.value.toLowerCase()
    return props.fields.filter(f =>
      f.label.toLowerCase().includes(search) ||
      f.key.toLowerCase().includes(search)
    )
  },
  set() {
    // 不实际修改，draggable 需要 setter
  }
})

// 选中字段的宽度
const selectedFieldSpan = computed({
  get() {
    if (!selectedField.value || !selectedRowId.value) return 12
    // 查找字段所在的 col
    for (const row of layoutConfig.rows) {
      if (row.id === selectedRowId.value) {
        const col = row.cols.find(c => c.field === selectedField.value.key)
        return col?.span || 12
      }
    }
    for (const group of layoutConfig.groups) {
      for (const row of group.rows || []) {
        if (row.id === selectedRowId.value) {
          const col = row.cols.find(c => c.field === selectedField.value.key)
          return col?.span || 12
        }
      }
    }
    return 12
  },
  set(val) {
    if (!selectedField.value || !selectedRowId.value) return
    // 更新字段宽度
    for (const row of layoutConfig.rows) {
      if (row.id === selectedRowId.value) {
        const col = row.cols.find(c => c.field === selectedField.value.key)
        if (col) col.span = val
        return
      }
    }
    for (const group of layoutConfig.groups) {
      for (const row of group.rows || []) {
        if (row.id === selectedRowId.value) {
          const col = row.cols.find(c => c.field === selectedField.value.key)
          if (col) col.span = val
          return
        }
      }
    }
  }
})

// 预览配置
const previewConfig = computed(() => ({
  groups: [],
  ungroupedFields: props.fields
}))

// 判断字段是否已使用
function isFieldUsed(fieldKey) {
  for (const row of layoutConfig.rows) {
    if (row.cols.some(c => c.field === fieldKey)) return true
  }
  for (const group of layoutConfig.groups) {
    for (const row of group.rows || []) {
      if (row.cols.some(c => c.field === fieldKey)) return true
    }
  }
  return false
}

// 克隆字段
function cloneField(original) {
  return {
    field: original.key,
    span: original.width || 12
  }
}

// 选择字段
function selectField(fieldKey, rowId) {
  selectedField.value = fieldsMap.value[fieldKey]
  selectedRowId.value = rowId
}

// 生成唯一 ID
function generateId() {
  return `id_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
}

// 添加行
function addRow() {
  layoutConfig.rows.push({
    id: generateId(),
    cols: []
  })
}

// 删除行
function removeRow(index) {
  layoutConfig.rows.splice(index, 1)
}

// 从行中删除字段
function removeFieldFromRow(rowIndex, colIndex) {
  layoutConfig.rows[rowIndex].cols.splice(colIndex, 1)
}

// 添加分组
function addGroup() {
  layoutConfig.groups.push({
    id: generateId(),
    title: '新分组',
    collapsed: false,
    rows: []
  })
}

// 删除分组
function removeGroup(index) {
  layoutConfig.groups.splice(index, 1)
}

// 向分组添加行
function addRowToGroup(groupIndex) {
  layoutConfig.groups[groupIndex].rows.push({
    id: generateId(),
    cols: []
  })
}

// 从分组删除行
function removeRowFromGroup(groupIndex, rowIndex) {
  layoutConfig.groups[groupIndex].rows.splice(rowIndex, 1)
}

// 从分组行中删除字段
function removeFieldFromGroupRow(groupIndex, rowIndex, colIndex) {
  layoutConfig.groups[groupIndex].rows[rowIndex].cols.splice(colIndex, 1)
}

// 获取字段图标
function getFieldIcon(type) {
  const iconMap = {
    text: Edit,
    textarea: Edit,
    number: Document,
    decimal: Document,
    date: Calendar,
    datetime: Calendar,
    select: Select,
    multi_select: Select,
    radio: Select,
    switch: Switch,
    reference: Link,
    tree_select: Link,
    formula: Document,
    code: Document
  }
  return iconMap[type] || Edit
}

// 获取字段类型标签
function getFieldTypeLabel(type) {
  const labelMap = {
    text: '文本',
    textarea: '多行文本',
    number: '数字',
    decimal: '小数',
    date: '日期',
    datetime: '日期时间',
    select: '下拉',
    multi_select: '多选',
    radio: '单选',
    switch: '开关',
    reference: '引用',
    tree_select: '树选择',
    formula: '公式',
    code: '编号'
  }
  return labelMap[type] || type
}

// 预览
function handlePreview() {
  previewVisible.value = true
}

// 保存
async function handleSave() {
  saving.value = true
  try {
    emit('save', {
      module: props.module,
      layoutConfig: JSON.parse(JSON.stringify(layoutConfig)),
      formSettings: { ...formSettings }
    })
    ElMessage.success('布局保存成功')
  } catch (error) {
    ElMessage.error('保存失败: ' + error.message)
  } finally {
    saving.value = false
  }
}

// 初始化
onMounted(() => {
  if (props.initialLayout) {
    Object.assign(layoutConfig, JSON.parse(JSON.stringify(props.initialLayout)))
  }
})
</script>

<style lang="scss" scoped>
.form-designer {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
}

.designer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  
  h2 {
    margin: 0;
    font-size: 18px;
  }
}

.designer-body {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #e4e7ed;
  font-weight: 500;
}

// 左侧字段库
.field-library {
  width: 280px;
  background: #fff;
  border-right: 1px solid #e4e7ed;
  display: flex;
  flex-direction: column;
  
  .field-list {
    flex: 1;
    overflow-y: auto;
    padding: 12px;
  }
  
  .field-item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 10px 12px;
    background: #f5f7fa;
    border-radius: 6px;
    margin-bottom: 8px;
    cursor: grab;
    transition: all 0.2s;
    
    &:hover {
      background: #e6f0ff;
      transform: translateX(4px);
    }
    
    &.is-used {
      opacity: 0.5;
      cursor: not-allowed;
    }
    
    .field-name {
      flex: 1;
      font-size: 14px;
    }
    
    .field-type {
      font-size: 12px;
      color: #909399;
    }
  }
}

// 中间画布
.design-canvas {
  flex: 1;
  display: flex;
  flex-direction: column;
  
  .canvas-content {
    flex: 1;
    overflow-y: auto;
    padding: 16px;
  }
}

.layout-group {
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  margin-bottom: 16px;
  
  .group-header {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 16px;
    background: #f5f7fa;
    border-radius: 8px 8px 0 0;
    
    .group-handle {
      cursor: grab;
      color: #909399;
    }
    
    .switch-label {
      font-size: 12px;
      color: #606266;
    }
  }
  
  .group-rows {
    padding: 12px;
    min-height: 60px;
  }
  
  .add-row-btn {
    margin: 0 12px 12px;
  }
}

.standalone-rows {
  min-height: 100px;
}

.empty-canvas {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
  background: #fff;
  border: 2px dashed #dcdfe6;
  border-radius: 8px;
}

// 右侧属性面板
.property-panel {
  width: 300px;
  background: #fff;
  border-left: 1px solid #e4e7ed;
  display: flex;
  flex-direction: column;
  
  .property-content {
    flex: 1;
    overflow-y: auto;
    padding: 16px;
  }
}
</style>
