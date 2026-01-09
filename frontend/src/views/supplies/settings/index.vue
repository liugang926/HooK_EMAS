<template>
  <div class="supply-settings-container">
    <el-card class="page-card">
      <template #header>
        <h2>用品设置</h2>
      </template>
      
      <el-tabs v-model="activeTab" tab-position="left">
        <!-- 用品分类 -->
        <el-tab-pane label="用品分类" name="category">
          <div class="setting-section">
            <div class="section-header">
              <h3>用品分类管理</h3>
              <el-button type="primary" size="small" @click="handleAddCategory">
                <el-icon><Plus /></el-icon>
                添加分类
              </el-button>
            </div>
            <el-tree
              v-loading="categoryLoading"
              :data="categoryTree"
              :props="{ label: 'name', children: 'children' }"
              default-expand-all
              node-key="id"
              draggable
              :allow-drop="allowCategoryDrop"
              @node-drop="handleCategoryDrop"
            >
              <template #default="{ node, data }">
                <span class="tree-node">
                  <span class="node-label">
                    <el-icon class="drag-handle"><Rank /></el-icon>
                    {{ node.label }}
                  </span>
                  <span class="tree-actions">
                    <el-button type="primary" link size="small" @click.stop="handleAddSubCategory(data)">添加子分类</el-button>
                    <el-button type="primary" link size="small" @click.stop="handleEditCategory(data)">编辑</el-button>
                    <el-button type="danger" link size="small" @click.stop="handleDeleteCategory(data)">删除</el-button>
                  </span>
                </span>
              </template>
            </el-tree>
            <div class="drag-tip">
              <el-icon><InfoFilled /></el-icon>
              <span>提示：可拖拽分类调整层级和顺序</span>
            </div>
          </div>
        </el-tab-pane>
        
        <!-- 仓库管理 -->
        <el-tab-pane label="仓库管理" name="warehouse">
          <div class="setting-section">
            <div class="section-header">
              <h3>仓库管理</h3>
              <el-button type="primary" size="small" @click="handleAddWarehouse">
                <el-icon><Plus /></el-icon>
                添加仓库
              </el-button>
            </div>
            <el-table :data="warehouseList" v-loading="warehouseLoading" style="width: 100%">
              <el-table-column prop="name" label="仓库名称" min-width="150" />
              <el-table-column prop="code" label="仓库编码" width="120" />
              <el-table-column prop="address" label="地址" min-width="200" />
              <el-table-column label="状态" width="80" align="center">
                <template #default="{ row }">
                  <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
                    {{ row.is_active ? '启用' : '禁用' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="150" fixed="right">
                <template #default="{ row }">
                  <el-button type="primary" link size="small" @click="handleEditWarehouse(row)">编辑</el-button>
                  <el-button type="danger" link size="small" @click="handleDeleteWarehouse(row)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-tab-pane>
        
        <!-- 编号规则 -->
        <el-tab-pane label="编号规则" name="code">
          <div class="setting-section" v-loading="codeRuleLoading">
            <h3>用品编号规则</h3>
            <el-form label-width="120px" style="max-width: 500px">
              <el-form-item label="编号前缀">
                <el-input v-model="codeRule.prefix" placeholder="如：BG" />
              </el-form-item>
              <el-form-item label="日期格式">
                <el-select v-model="codeRule.dateFormat" style="width: 100%">
                  <el-option label="年 (YYYY)" value="YYYY" />
                  <el-option label="年月 (YYYYMM)" value="YYYYMM" />
                  <el-option label="年月日 (YYYYMMDD)" value="YYYYMMDD" />
                </el-select>
              </el-form-item>
              <el-form-item label="流水号位数">
                <el-input-number v-model="codeRule.serialLength" :min="3" :max="8" />
              </el-form-item>
              <el-form-item label="流水号重置">
                <el-select v-model="codeRule.resetCycle" style="width: 100%">
                  <el-option label="每天重置" value="daily" />
                  <el-option label="每月重置" value="monthly" />
                  <el-option label="每年重置" value="yearly" />
                  <el-option label="永不重置" value="never" />
                </el-select>
                <div class="form-tip">流水号在指定周期后从1开始重新计数</div>
              </el-form-item>
              <el-form-item label="示例">
                <el-tag size="large" type="warning">{{ codeExample }}</el-tag>
              </el-form-item>
              <el-form-item>
                <el-button type="primary" :loading="codeRuleLoading" @click="handleSaveCodeRule">保存设置</el-button>
              </el-form-item>
            </el-form>
          </div>
        </el-tab-pane>
        
        <!-- 自定义字段 -->
        <el-tab-pane label="自定义字段" name="fields">
          <div class="setting-section">
            <div class="section-header">
              <h3>自定义字段</h3>
              <el-button type="primary" @click="handleAddField">
                <el-icon><Plus /></el-icon>
                添加字段
              </el-button>
            </div>
            
            <el-table :data="fieldList" v-loading="fieldLoading" style="width: 100%">
              <el-table-column prop="field_name" label="字段名称" min-width="150" />
              <el-table-column prop="field_type" label="字段类型" width="120">
                <template #default="{ row }">
                  {{ getFieldTypeLabel(row.field_type) }}
                </template>
              </el-table-column>
              <el-table-column label="是否必填" width="100" align="center">
                <template #default="{ row }">
                  <el-tag :type="row.is_required ? 'danger' : 'info'" size="small">
                    {{ row.is_required ? '必填' : '选填' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="系统字段" width="100" align="center">
                <template #default="{ row }">
                  <el-tag :type="row.is_system ? 'warning' : ''" size="small">
                    {{ row.is_system ? '系统' : '自定义' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="列表显示" width="100" align="center">
                <template #default="{ row }">
                  <el-switch 
                    v-model="row.show_in_list" 
                    :disabled="row.is_system"
                    @change="handleToggleListShow(row)"
                  />
                </template>
              </el-table-column>
              <el-table-column label="操作" width="150" fixed="right">
                <template #default="{ row }">
                  <el-button type="primary" link size="small" @click="handleEditField(row)" :disabled="row.is_system">编辑</el-button>
                  <el-button type="danger" link size="small" @click="handleDeleteField(row)" :disabled="row.is_system">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>
    
    <!-- 分类弹窗 -->
    <el-dialog v-model="categoryDialogVisible" :title="categoryDialogTitle" width="500px">
      <el-form :model="categoryForm" label-width="100px">
        <el-form-item label="分类名称">
          <el-input v-model="categoryForm.name" placeholder="请输入分类名称" />
        </el-form-item>
        <el-form-item label="上级分类" v-if="categoryForm.parentId">
          <el-input :value="categoryForm.parentName" disabled />
        </el-form-item>
        <el-form-item label="分类编码">
          <el-input v-model="categoryForm.code" placeholder="请输入分类编码（可选）" />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="categoryForm.sort" :min="0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="categoryDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitCategory">确定</el-button>
      </template>
    </el-dialog>
    
    <!-- 仓库弹窗 -->
    <el-dialog v-model="warehouseDialogVisible" :title="warehouseDialogTitle" width="500px">
      <el-form :model="warehouseForm" label-width="100px">
        <el-form-item label="仓库名称">
          <el-input v-model="warehouseForm.name" placeholder="请输入仓库名称" />
        </el-form-item>
        <el-form-item label="仓库编码">
          <el-input v-model="warehouseForm.code" placeholder="请输入仓库编码" />
        </el-form-item>
        <el-form-item label="地址">
          <el-input v-model="warehouseForm.address" type="textarea" :rows="2" placeholder="请输入仓库地址" />
        </el-form-item>
        <el-form-item label="是否启用">
          <el-switch v-model="warehouseForm.is_active" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="warehouseDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitWarehouse">确定</el-button>
      </template>
    </el-dialog>
    
    <!-- 自定义字段弹窗 -->
    <el-dialog v-model="fieldDialogVisible" :title="fieldDialogTitle" width="600px">
      <el-form :model="fieldForm" :rules="fieldRules" ref="fieldFormRef" label-width="120px">
        <el-form-item label="字段标识" prop="field_key">
          <el-input 
            v-model="fieldForm.field_key" 
            placeholder="如：custom_field_1"
            :disabled="!!fieldForm.id"
          />
          <div class="form-tip">字段标识创建后不可修改，建议使用英文和下划线</div>
        </el-form-item>
        <el-form-item label="字段名称" prop="field_name">
          <el-input v-model="fieldForm.field_name" placeholder="请输入字段显示名称" />
        </el-form-item>
        <el-form-item label="字段类型" prop="field_type">
          <el-select v-model="fieldForm.field_type" style="width: 100%" @change="handleFieldTypeChange">
            <el-option-group label="基础类型">
              <el-option label="单行文本" value="text" />
              <el-option label="多行文本" value="textarea" />
              <el-option label="数字" value="number" />
              <el-option label="小数" value="decimal" />
              <el-option label="日期" value="date" />
              <el-option label="日期时间" value="datetime" />
              <el-option label="开关" value="switch" />
            </el-option-group>
            <el-option-group label="选择类型">
              <el-option label="下拉选择" value="select" />
              <el-option label="多选" value="multi_select" />
              <el-option label="单选框" value="radio" />
            </el-option-group>
            <el-option-group label="引用类型">
              <el-option label="用户选择" value="reference" />
              <el-option label="部门选择" value="tree_select" />
            </el-option-group>
            <el-option-group label="其他类型">
              <el-option label="图片上传" value="image" />
              <el-option label="文件上传" value="file" />
            </el-option-group>
          </el-select>
        </el-form-item>
        
        <!-- 下拉选项配置 -->
        <el-form-item v-if="['select', 'multi_select', 'radio'].includes(fieldForm.field_type)" label="选项配置">
          <div class="options-editor">
            <div v-for="(opt, idx) in fieldForm.options" :key="idx" class="option-item">
              <el-input v-model="opt.label" placeholder="显示名称" style="width: 45%" />
              <el-input v-model="opt.value" placeholder="选项值" style="width: 45%" />
              <el-button type="danger" link @click="removeOption(idx)">
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
            <el-button type="primary" link @click="addOption">
              <el-icon><Plus /></el-icon> 添加选项
            </el-button>
          </div>
        </el-form-item>
        
        <!-- 数字配置 -->
        <el-form-item v-if="['number', 'decimal'].includes(fieldForm.field_type)" label="数值范围">
          <el-row :gutter="10">
            <el-col :span="12">
              <el-input-number v-model="fieldForm.number_config.min" placeholder="最小值" style="width: 100%" />
            </el-col>
            <el-col :span="12">
              <el-input-number v-model="fieldForm.number_config.max" placeholder="最大值" style="width: 100%" />
            </el-col>
          </el-row>
        </el-form-item>
        <el-form-item v-if="fieldForm.field_type === 'decimal'" label="小数位数">
          <el-input-number v-model="fieldForm.number_config.precision" :min="0" :max="6" />
        </el-form-item>
        
        <el-divider content-position="left">权限设置</el-divider>
        
        <el-form-item label="是否必填">
          <el-switch v-model="fieldForm.is_required" />
        </el-form-item>
        <el-form-item label="始终只读">
          <el-switch v-model="fieldForm.is_readonly" />
        </el-form-item>
        <el-form-item label="新增时隐藏">
          <el-switch v-model="fieldForm.is_hidden_on_create" />
        </el-form-item>
        <el-form-item label="编辑时隐藏">
          <el-switch v-model="fieldForm.is_hidden_on_edit" />
        </el-form-item>
        
        <el-divider content-position="left">显示设置</el-divider>
        
        <el-form-item label="排序">
          <el-input-number v-model="fieldForm.sort_order" :min="0" />
        </el-form-item>
        <el-form-item label="栅格宽度">
          <el-slider v-model="fieldForm.width" :min="4" :max="24" :step="4" show-stops />
          <span class="form-tip">一行最多24格，8表示一行3列</span>
        </el-form-item>
        <el-form-item label="占位提示">
          <el-input v-model="fieldForm.placeholder" placeholder="请输入占位提示文字" />
        </el-form-item>
        <el-form-item label="列表显示">
          <el-switch v-model="fieldForm.show_in_list" />
          <span class="form-tip">是否在用品列表中显示此字段</span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="fieldDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="fieldSubmitting" @click="submitField">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { Plus, Delete, Rank, InfoFilled } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  getSupplyCategories, createSupplyCategory, updateSupplyCategory, deleteSupplyCategory,
  getWarehouses 
} from '@/api/supplies'
import request from '@/api/request'

const activeTab = ref('category')

// ============ 字段类型映射 ============
const fieldTypeMap = {
  text: '单行文本',
  textarea: '多行文本',
  number: '数字',
  decimal: '小数',
  date: '日期',
  datetime: '日期时间',
  select: '下拉选择',
  multi_select: '多选',
  radio: '单选框',
  switch: '开关',
  reference: '用户选择',
  tree_select: '部门选择',
  image: '图片上传',
  file: '文件上传',
}

function getFieldTypeLabel(type) {
  return fieldTypeMap[type] || type
}

// ============ 分类管理 ============
const categoryLoading = ref(false)
const categoryTree = ref([])

const categoryDialogVisible = ref(false)
const categoryDialogTitle = ref('添加分类')
const categoryForm = reactive({
  id: null,
  name: '',
  code: '',
  sort: 0,
  parentId: null,
  parentName: ''
})

async function loadCategories() {
  categoryLoading.value = true
  try {
    const res = await getSupplyCategories()
    const data = res.results || res || []
    categoryTree.value = buildTree(Array.isArray(data) ? data : [])
  } catch (error) {
    console.error('加载分类失败:', error)
  } finally {
    categoryLoading.value = false
  }
}

function buildTree(data) {
  const ids = new Set(data.map(item => item.id))
  const isRoot = (item) => item.parent === null || !ids.has(item.parent)
  
  const buildSubTree = (parentId) => {
    return data
      .filter(item => item.parent === parentId)
      .map(item => ({
        ...item,
        children: buildSubTree(item.id)
      }))
  }
  
  return data
    .filter(isRoot)
    .map(item => ({
      ...item,
      children: buildSubTree(item.id)
    }))
}

function handleAddCategory() {
  categoryDialogTitle.value = '添加分类'
  Object.assign(categoryForm, { id: null, name: '', code: '', sort: 0, parentId: null, parentName: '' })
  categoryDialogVisible.value = true
}

function handleAddSubCategory(parent) {
  categoryDialogTitle.value = '添加子分类'
  Object.assign(categoryForm, { id: null, name: '', code: '', sort: 0, parentId: parent.id, parentName: parent.name })
  categoryDialogVisible.value = true
}

function handleEditCategory(data) {
  categoryDialogTitle.value = '编辑分类'
  const parentName = data.parent ? findCategoryName(categoryTree.value, data.parent) : ''
  Object.assign(categoryForm, { 
    id: data.id, 
    name: data.name, 
    code: data.code || '', 
    sort: data.sort_order || 0, 
    parentId: data.parent || null, 
    parentName: parentName 
  })
  categoryDialogVisible.value = true
}

function findCategoryName(tree, id) {
  for (const node of tree) {
    if (node.id === id) return node.name
    if (node.children?.length) {
      const found = findCategoryName(node.children, id)
      if (found) return found
    }
  }
  return ''
}

async function handleDeleteCategory(data) {
  try {
    await ElMessageBox.confirm(
      `确定要删除分类 "${data.name}" 吗？${data.children?.length ? '（该分类下有子分类，将一并删除）' : ''}`,
      '删除确认',
      { confirmButtonText: '确定删除', cancelButtonText: '取消', type: 'warning' }
    )
    await deleteSupplyCategory(data.id)
    ElMessage.success('删除成功')
    loadCategories()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

async function submitCategory() {
  if (!categoryForm.name.trim()) {
    ElMessage.warning('请输入分类名称')
    return
  }
  
  try {
    const data = {
      name: categoryForm.name,
      code: categoryForm.code,
      sort_order: categoryForm.sort,
      parent: categoryForm.parentId
    }
    
    if (categoryForm.id) {
      await updateSupplyCategory(categoryForm.id, data)
      ElMessage.success('编辑成功')
    } else {
      await createSupplyCategory(data)
      ElMessage.success('添加成功')
    }
    categoryDialogVisible.value = false
    loadCategories()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

function allowCategoryDrop() {
  return true
}

async function handleCategoryDrop(draggingNode, dropNode, dropType) {
  try {
    const draggedData = draggingNode.data
    let newParentId = null
    let newSortOrder = 0
    
    if (dropType === 'inner') {
      newParentId = dropNode.data.id
      newSortOrder = dropNode.data.children?.length || 0
    } else if (dropType === 'before') {
      newParentId = dropNode.data.parent || null
      newSortOrder = dropNode.data.sort_order > 0 ? dropNode.data.sort_order - 1 : 0
    } else if (dropType === 'after') {
      newParentId = dropNode.data.parent || null
      newSortOrder = (dropNode.data.sort_order || 0) + 1
    }
    
    await updateSupplyCategory(draggedData.id, {
      name: draggedData.name,
      code: draggedData.code,
      sort_order: newSortOrder,
      parent: newParentId
    })
    
    ElMessage.success('分类移动成功')
    loadCategories()
  } catch (error) {
    ElMessage.error('移动失败')
    loadCategories()
  }
}

// ============ 仓库管理 ============
const warehouseLoading = ref(false)
const warehouseList = ref([])

const warehouseDialogVisible = ref(false)
const warehouseDialogTitle = ref('添加仓库')
const warehouseForm = reactive({
  id: null,
  name: '',
  code: '',
  address: '',
  is_active: true
})

async function loadWarehouses() {
  warehouseLoading.value = true
  try {
    const res = await getWarehouses()
    warehouseList.value = res.results || res || []
  } catch (error) {
    console.error('加载仓库失败:', error)
  } finally {
    warehouseLoading.value = false
  }
}

function handleAddWarehouse() {
  warehouseDialogTitle.value = '添加仓库'
  Object.assign(warehouseForm, { id: null, name: '', code: '', address: '', is_active: true })
  warehouseDialogVisible.value = true
}

function handleEditWarehouse(data) {
  warehouseDialogTitle.value = '编辑仓库'
  Object.assign(warehouseForm, { 
    id: data.id, 
    name: data.name, 
    code: data.code || '', 
    address: data.address || '',
    is_active: data.is_active !== false
  })
  warehouseDialogVisible.value = true
}

async function handleDeleteWarehouse(data) {
  try {
    await ElMessageBox.confirm(`确定要删除仓库 "${data.name}" 吗？`, '删除确认', { type: 'warning' })
    await request.delete(`/organizations/locations/${data.id}/`)
    ElMessage.success('删除成功')
    loadWarehouses()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

async function submitWarehouse() {
  if (!warehouseForm.name.trim()) {
    ElMessage.warning('请输入仓库名称')
    return
  }
  
  try {
    const data = {
      name: warehouseForm.name,
      code: warehouseForm.code,
      address: warehouseForm.address,
      type: 'warehouse',
      is_active: warehouseForm.is_active
    }
    
    if (warehouseForm.id) {
      await request.put(`/organizations/locations/${warehouseForm.id}/`, data)
      ElMessage.success('编辑成功')
    } else {
      await request.post('/organizations/locations/', data)
      ElMessage.success('添加成功')
    }
    warehouseDialogVisible.value = false
    loadWarehouses()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

// ============ 编号规则 ============
const codeRuleLoading = ref(false)
const codeRule = reactive({
  prefix: 'BG',
  dateFormat: 'YYYYMMDD',
  serialLength: 4,
  separator: '',
  resetCycle: 'daily'
})

const codeExample = computed(() => {
  const date = new Date()
  let dateStr = ''
  if (codeRule.dateFormat === 'YYYY') dateStr = date.getFullYear()
  else if (codeRule.dateFormat === 'YYYYMM') dateStr = `${date.getFullYear()}${String(date.getMonth() + 1).padStart(2, '0')}`
  else dateStr = `${date.getFullYear()}${String(date.getMonth() + 1).padStart(2, '0')}${String(date.getDate()).padStart(2, '0')}`
  const serial = '1'.padStart(codeRule.serialLength, '0')
  const sep = codeRule.separator || ''
  return `${codeRule.prefix}${sep}${dateStr}${sep}${serial}`
})

async function loadCodeRule() {
  codeRuleLoading.value = true
  try {
    const res = await request.get('/system/code-rules/supply_code/')
    if (res) {
      codeRule.prefix = res.prefix || 'BG'
      codeRule.dateFormat = res.date_format || 'YYYYMMDD'
      codeRule.serialLength = res.serial_length || 4
      codeRule.separator = res.separator || ''
      codeRule.resetCycle = res.reset_cycle || 'daily'
    }
  } catch (error) {
    console.log('No code rule found, using defaults')
  } finally {
    codeRuleLoading.value = false
  }
}

async function handleSaveCodeRule() {
  codeRuleLoading.value = true
  try {
    await request.post('/system/code-rules/supply_code/', {
      prefix: codeRule.prefix,
      date_format: codeRule.dateFormat,
      serial_length: codeRule.serialLength,
      separator: codeRule.separator,
      reset_cycle: codeRule.resetCycle
    })
    ElMessage.success('编号规则保存成功')
  } catch (error) {
    ElMessage.error('保存失败: ' + (error.response?.data?.error || error.message))
  } finally {
    codeRuleLoading.value = false
  }
}

// ============ 自定义字段 ============
const MODULE_NAME = 'supply'

const fieldLoading = ref(false)
const fieldList = ref([])

const fieldDialogVisible = ref(false)
const fieldDialogTitle = ref('添加字段')
const fieldSubmitting = ref(false)
const fieldFormRef = ref(null)

// Default system fields for supplies
const defaultSystemFields = [
  { id: 'sys_1', field_name: '用品名称', field_key: 'name', field_type: 'text', is_required: true, is_system: true, show_in_list: true, sort_order: 1 },
  { id: 'sys_2', field_name: '用品编号', field_key: 'code', field_type: 'text', is_required: true, is_system: true, show_in_list: true, sort_order: 2 },
  { id: 'sys_3', field_name: '用品分类', field_key: 'category', field_type: 'tree_select', is_required: true, is_system: true, show_in_list: true, sort_order: 3 },
  { id: 'sys_4', field_name: '规格型号', field_key: 'model', field_type: 'text', is_required: false, is_system: true, show_in_list: true, sort_order: 4 },
  { id: 'sys_5', field_name: '单位', field_key: 'unit', field_type: 'text', is_required: true, is_system: true, show_in_list: true, sort_order: 5 },
  { id: 'sys_6', field_name: '单价', field_key: 'price', field_type: 'decimal', is_required: false, is_system: true, show_in_list: true, sort_order: 6 },
  { id: 'sys_7', field_name: '库存预警', field_key: 'min_stock', field_type: 'number', is_required: false, is_system: true, show_in_list: false, sort_order: 7 },
  { id: 'sys_8', field_name: '描述', field_key: 'description', field_type: 'textarea', is_required: false, is_system: true, show_in_list: false, sort_order: 8 },
]

const defaultFieldForm = {
  id: null,
  module: MODULE_NAME,
  field_key: '',
  field_name: '',
  field_type: 'text',
  sort_order: 0,
  is_required: false,
  is_readonly: false,
  is_hidden_on_create: false,
  is_hidden_on_edit: false,
  options: [],
  number_config: { min: 0, max: 999999, precision: 2 },
  placeholder: '',
  width: 8,
  show_in_list: false,
  is_system: false,
}

const fieldForm = reactive({ ...defaultFieldForm })

const fieldRules = {
  field_key: [
    { required: true, message: '请输入字段标识', trigger: 'blur' },
    { pattern: /^[a-zA-Z_][a-zA-Z0-9_]*$/, message: '只能包含字母、数字和下划线', trigger: 'blur' }
  ],
  field_name: [{ required: true, message: '请输入字段名称', trigger: 'blur' }],
  field_type: [{ required: true, message: '请选择字段类型', trigger: 'change' }],
}

async function loadFields() {
  fieldLoading.value = true
  try {
    const res = await request.get('/system/form/fields/', {
      params: { module: MODULE_NAME }
    })
    const apiFields = res.results || res || []
    // Combine system fields with custom fields from API
    fieldList.value = [...defaultSystemFields, ...apiFields.filter(f => !f.is_system)]
  } catch (error) {
    console.error('加载字段列表失败:', error)
    fieldList.value = [...defaultSystemFields]
  } finally {
    fieldLoading.value = false
  }
}

function handleAddField() {
  fieldDialogTitle.value = '添加字段'
  Object.assign(fieldForm, { 
    ...defaultFieldForm,
    options: [],
    number_config: { min: 0, max: 999999, precision: 2 }
  })
  fieldDialogVisible.value = true
}

function handleEditField(row) {
  if (row.is_system) {
    ElMessage.warning('系统字段不能编辑')
    return
  }
  fieldDialogTitle.value = '编辑字段'
  Object.assign(fieldForm, {
    ...defaultFieldForm,
    ...row,
    options: row.options || [],
    number_config: row.number_config || { min: 0, max: 999999, precision: 2 }
  })
  fieldDialogVisible.value = true
}

async function handleDeleteField(row) {
  if (row.is_system) {
    ElMessage.warning('系统字段不能删除')
    return
  }
  
  try {
    await ElMessageBox.confirm(`确定要删除字段 "${row.field_name}" 吗？`, '删除确认', { type: 'warning' })
    await request.delete(`/system/form/fields/${row.id}/`)
    ElMessage.success('删除成功')
    loadFields()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

async function handleToggleListShow(row) {
  if (row.is_system) return
  try {
    await request.patch(`/system/form/fields/${row.id}/`, { show_in_list: row.show_in_list })
  } catch (error) {
    row.show_in_list = !row.show_in_list
    ElMessage.error('更新失败')
  }
}

function handleFieldTypeChange(type) {
  if (['select', 'multi_select', 'radio'].includes(type)) {
    if (!fieldForm.options.length) {
      fieldForm.options = [{ label: '', value: '' }]
    }
  } else {
    fieldForm.options = []
  }
}

function addOption() {
  fieldForm.options.push({ label: '', value: '' })
}

function removeOption(index) {
  fieldForm.options.splice(index, 1)
}

async function submitField() {
  try {
    await fieldFormRef.value?.validate()
  } catch (error) {
    return
  }
  
  fieldSubmitting.value = true
  try {
    const data = {
      module: MODULE_NAME,
      field_key: fieldForm.field_key,
      field_name: fieldForm.field_name,
      field_type: fieldForm.field_type,
      sort_order: fieldForm.sort_order,
      is_required: fieldForm.is_required,
      is_readonly: fieldForm.is_readonly,
      is_hidden_on_create: fieldForm.is_hidden_on_create,
      is_hidden_on_edit: fieldForm.is_hidden_on_edit,
      options: fieldForm.options.filter(o => o.label && o.value),
      number_config: fieldForm.number_config,
      placeholder: fieldForm.placeholder,
      width: fieldForm.width,
      show_in_list: fieldForm.show_in_list,
    }
    
    if (fieldForm.id) {
      await request.put(`/system/form/fields/${fieldForm.id}/`, data)
      ElMessage.success('编辑成功')
    } else {
      await request.post('/system/form/fields/', data)
      ElMessage.success('添加成功')
    }
    
    fieldDialogVisible.value = false
    loadFields()
  } catch (error) {
    ElMessage.error('保存失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    fieldSubmitting.value = false
  }
}

// Tab 切换时加载数据
watch(activeTab, (tab) => {
  if (tab === 'category' && !categoryTree.value.length) {
    loadCategories()
  } else if (tab === 'warehouse' && !warehouseList.value.length) {
    loadWarehouses()
  } else if (tab === 'code') {
    loadCodeRule()
  } else if (tab === 'fields' && fieldList.value.length <= defaultSystemFields.length) {
    loadFields()
  }
})

onMounted(() => {
  loadCategories()
})
</script>

<style lang="scss" scoped>
.supply-settings-container {
  .page-card { 
    border-radius: 16px; 
    min-height: calc(100vh - 200px);
    h2 { margin: 0; font-size: 18px; color: #1f2937; } 
  }
  
  .setting-section {
    .section-header { 
      display: flex; 
      justify-content: space-between; 
      align-items: center; 
      margin-bottom: 16px; 
      h3 { margin: 0; font-size: 16px; color: #374151; } 
    }
    h3 { font-size: 16px; margin: 0 0 16px; color: #374151; }
  }
  
  .tree-node { 
    flex: 1; 
    display: flex; 
    justify-content: space-between; 
    align-items: center; 
    padding-right: 16px;
    font-size: 14px;
    
    .node-label {
      display: flex;
      align-items: center;
      gap: 6px;
      
      .drag-handle {
        color: #c0c4cc;
        cursor: grab;
        font-size: 14px;
        
        &:hover { color: #409eff; }
        &:active { cursor: grabbing; }
      }
    }
    
    .tree-actions {
      opacity: 0;
      transition: opacity 0.2s;
    }
    
    &:hover .tree-actions { opacity: 1; }
  }
  
  .drag-tip {
    display: flex;
    align-items: center;
    gap: 6px;
    margin-top: 12px;
    padding: 8px 12px;
    background: #f4f4f5;
    border-radius: 4px;
    font-size: 12px;
    color: #909399;
  }
  
  :deep(.el-tabs--left) {
    .el-tabs__item { height: 48px; line-height: 48px; }
  }
  
  :deep(.el-tree-node__content) {
    height: 40px;
    &:hover { background-color: #f3f4f6; }
  }
  
  .form-tip {
    font-size: 12px;
    color: #909399;
    margin-left: 8px;
  }
  
  .options-editor {
    width: 100%;
    
    .option-item {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 8px;
    }
  }
}
</style>
