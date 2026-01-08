<template>
  <div class="consumable-list-container">
    <el-card class="page-card">
      <template #header>
        <div class="page-header">
          <h2>耗材档案</h2>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            新增耗材
          </el-button>
        </div>
      </template>
      
      <el-form :inline="true" class="filter-form">
        <el-form-item label="耗材名称">
          <el-input v-model="filterForm.name" placeholder="请输入" clearable />
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="filterForm.category" placeholder="请选择" clearable>
            <el-option label="办公用品" value="办公用品" />
            <el-option label="清洁用品" value="清洁用品" />
            <el-option label="电子耗材" value="电子耗材" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
      
      <el-table :data="filteredList" style="width: 100%">
        <el-table-column prop="code" label="耗材编号" width="120" />
        <el-table-column prop="name" label="耗材名称" min-width="150" />
        <el-table-column prop="category" label="分类" width="100" />
        <el-table-column prop="unit" label="单位" width="80" />
        <el-table-column prop="price" label="单价" width="100">
          <template #default="{ row }">
            ¥ {{ row.price }}
          </template>
        </el-table-column>
        <el-table-column prop="stock" label="库存" width="100">
          <template #default="{ row }">
            <el-tag :type="row.stock <= row.minStock ? 'danger' : 'success'">{{ row.stock }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="minStock" label="安全库存" width="100" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleView(row)">查看</el-button>
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button type="success" link @click="handleInbound(row)">入库</el-button>
            <el-button type="warning" link @click="handleOutbound(row)">领用</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- 新增/编辑弹窗 -->
    <el-dialog v-model="formDialogVisible" :title="formDialogTitle" width="600px">
      <el-form :model="consumableForm" label-width="100px" ref="formRef" :rules="formRules">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="耗材名称" prop="name">
              <el-input v-model="consumableForm.name" placeholder="请输入耗材名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="耗材编号" prop="code">
              <el-input v-model="consumableForm.code" placeholder="请输入耗材编号" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="分类" prop="category">
              <el-select v-model="consumableForm.category" placeholder="请选择分类" style="width: 100%">
                <el-option label="办公用品" value="办公用品" />
                <el-option label="清洁用品" value="清洁用品" />
                <el-option label="电子耗材" value="电子耗材" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="单位" prop="unit">
              <el-select v-model="consumableForm.unit" placeholder="请选择单位" style="width: 100%">
                <el-option label="个" value="个" />
                <el-option label="包" value="包" />
                <el-option label="支" value="支" />
                <el-option label="盒" value="盒" />
                <el-option label="箱" value="箱" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="单价" prop="price">
              <el-input-number v-model="consumableForm.price" :min="0" :precision="2" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="安全库存" prop="minStock">
              <el-input-number v-model="consumableForm.minStock" :min="0" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="规格">
          <el-input v-model="consumableForm.spec" placeholder="请输入规格型号" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="consumableForm.remark" type="textarea" :rows="2" placeholder="请输入备注" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="formDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm">保存</el-button>
      </template>
    </el-dialog>
    
    <!-- 查看详情弹窗 -->
    <el-dialog v-model="viewDialogVisible" title="耗材详情" width="600px">
      <el-descriptions :column="2" border v-if="currentConsumable">
        <el-descriptions-item label="耗材编号">{{ currentConsumable.code }}</el-descriptions-item>
        <el-descriptions-item label="耗材名称">{{ currentConsumable.name }}</el-descriptions-item>
        <el-descriptions-item label="分类">{{ currentConsumable.category }}</el-descriptions-item>
        <el-descriptions-item label="单位">{{ currentConsumable.unit }}</el-descriptions-item>
        <el-descriptions-item label="单价">¥ {{ currentConsumable.price }}</el-descriptions-item>
        <el-descriptions-item label="当前库存">
          <el-tag :type="currentConsumable.stock <= currentConsumable.minStock ? 'danger' : 'success'">
            {{ currentConsumable.stock }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="安全库存">{{ currentConsumable.minStock }}</el-descriptions-item>
        <el-descriptions-item label="规格">{{ currentConsumable.spec || '-' }}</el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">{{ currentConsumable.remark || '-' }}</el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="viewDialogVisible = false">关闭</el-button>
        <el-button type="primary" @click="handleEditFromView">编辑</el-button>
      </template>
    </el-dialog>
    
    <!-- 入库弹窗 -->
    <el-dialog v-model="inboundDialogVisible" title="耗材入库" width="500px">
      <el-form :model="inboundForm" label-width="100px">
        <el-form-item label="耗材名称">
          <span>{{ inboundForm.name }} ({{ inboundForm.code }})</span>
        </el-form-item>
        <el-form-item label="当前库存">
          <el-tag>{{ inboundForm.currentStock }}</el-tag>
        </el-form-item>
        <el-form-item label="入库数量">
          <el-input-number v-model="inboundForm.quantity" :min="1" style="width: 100%" />
        </el-form-item>
        <el-form-item label="入库日期">
          <el-date-picker v-model="inboundForm.date" type="date" placeholder="请选择日期" style="width: 100%" />
        </el-form-item>
        <el-form-item label="供应商">
          <el-input v-model="inboundForm.supplier" placeholder="请输入供应商" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="inboundForm.remark" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="inboundDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitInbound">确认入库</el-button>
      </template>
    </el-dialog>
    
    <!-- 领用弹窗 -->
    <el-dialog v-model="outboundDialogVisible" title="耗材领用" width="500px">
      <el-form :model="outboundForm" label-width="100px">
        <el-form-item label="耗材名称">
          <span>{{ outboundForm.name }} ({{ outboundForm.code }})</span>
        </el-form-item>
        <el-form-item label="当前库存">
          <el-tag>{{ outboundForm.currentStock }}</el-tag>
        </el-form-item>
        <el-form-item label="领用数量">
          <el-input-number v-model="outboundForm.quantity" :min="1" :max="outboundForm.currentStock" style="width: 100%" />
        </el-form-item>
        <el-form-item label="领用人">
          <el-select v-model="outboundForm.userId" placeholder="请选择领用人" style="width: 100%">
            <el-option label="张三" value="1" />
            <el-option label="李四" value="2" />
            <el-option label="王五" value="3" />
          </el-select>
        </el-form-item>
        <el-form-item label="领用部门">
          <el-select v-model="outboundForm.deptId" placeholder="请选择部门" style="width: 100%">
            <el-option label="研发部" value="1" />
            <el-option label="市场部" value="2" />
            <el-option label="财务部" value="3" />
          </el-select>
        </el-form-item>
        <el-form-item label="领用日期">
          <el-date-picker v-model="outboundForm.date" type="date" placeholder="请选择日期" style="width: 100%" />
        </el-form-item>
        <el-form-item label="用途说明">
          <el-input v-model="outboundForm.purpose" type="textarea" :rows="2" placeholder="请输入用途说明" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="outboundDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitOutbound">确认领用</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const filterForm = reactive({ name: '', category: '' })
const formRef = ref(null)

const consumableList = ref([
  { id: 1, code: 'HC-0001', name: 'A4打印纸', category: '办公用品', unit: '包', price: '25.00', stock: 50, minStock: 20, spec: '500张/包', remark: '' },
  { id: 2, code: 'HC-0002', name: '签字笔', category: '办公用品', unit: '支', price: '3.00', stock: 10, minStock: 50, spec: '0.5mm黑色', remark: '库存不足' },
  { id: 3, code: 'HC-0003', name: '文件夹', category: '办公用品', unit: '个', price: '8.00', stock: 100, minStock: 30, spec: 'A4双夹', remark: '' },
  { id: 4, code: 'HC-0004', name: '墨盒', category: '电子耗材', unit: '个', price: '180.00', stock: 5, minStock: 10, spec: 'HP原装', remark: '' }
])

const filteredList = computed(() => {
  return consumableList.value.filter(item => {
    const nameMatch = !filterForm.name || item.name.includes(filterForm.name)
    const categoryMatch = !filterForm.category || item.category === filterForm.category
    return nameMatch && categoryMatch
  })
})

// 表单弹窗
const formDialogVisible = ref(false)
const formDialogTitle = ref('新增耗材')
const consumableForm = reactive({
  id: null,
  code: '',
  name: '',
  category: '',
  unit: '',
  price: 0,
  minStock: 0,
  spec: '',
  remark: ''
})

const formRules = {
  name: [{ required: true, message: '请输入耗材名称', trigger: 'blur' }],
  code: [{ required: true, message: '请输入耗材编号', trigger: 'blur' }],
  category: [{ required: true, message: '请选择分类', trigger: 'change' }],
  unit: [{ required: true, message: '请选择单位', trigger: 'change' }],
  price: [{ required: true, message: '请输入单价', trigger: 'blur' }]
}

// 查看弹窗
const viewDialogVisible = ref(false)
const currentConsumable = ref(null)

// 入库弹窗
const inboundDialogVisible = ref(false)
const inboundForm = reactive({
  id: null,
  code: '',
  name: '',
  currentStock: 0,
  quantity: 1,
  date: new Date(),
  supplier: '',
  remark: ''
})

// 领用弹窗
const outboundDialogVisible = ref(false)
const outboundForm = reactive({
  id: null,
  code: '',
  name: '',
  currentStock: 0,
  quantity: 1,
  userId: '',
  deptId: '',
  date: new Date(),
  purpose: ''
})

let idCounter = 100

function handleSearch() {
  ElMessage.success('搜索完成')
}

function handleReset() {
  filterForm.name = ''
  filterForm.category = ''
  ElMessage.success('已重置')
}

function handleAdd() {
  formDialogTitle.value = '新增耗材'
  Object.assign(consumableForm, {
    id: null,
    code: `HC-${String(consumableList.value.length + 1).padStart(4, '0')}`,
    name: '',
    category: '',
    unit: '',
    price: 0,
    minStock: 0,
    spec: '',
    remark: ''
  })
  formDialogVisible.value = true
}

function handleView(row) {
  currentConsumable.value = row
  viewDialogVisible.value = true
}

function handleEdit(row) {
  formDialogTitle.value = '编辑耗材'
  Object.assign(consumableForm, {
    id: row.id,
    code: row.code,
    name: row.name,
    category: row.category,
    unit: row.unit,
    price: parseFloat(row.price),
    minStock: row.minStock,
    spec: row.spec || '',
    remark: row.remark || ''
  })
  formDialogVisible.value = true
}

function handleEditFromView() {
  viewDialogVisible.value = false
  handleEdit(currentConsumable.value)
}

function handleInbound(row) {
  Object.assign(inboundForm, {
    id: row.id,
    code: row.code,
    name: row.name,
    currentStock: row.stock,
    quantity: 1,
    date: new Date(),
    supplier: '',
    remark: ''
  })
  inboundDialogVisible.value = true
}

function handleOutbound(row) {
  Object.assign(outboundForm, {
    id: row.id,
    code: row.code,
    name: row.name,
    currentStock: row.stock,
    quantity: 1,
    userId: '',
    deptId: '',
    date: new Date(),
    purpose: ''
  })
  outboundDialogVisible.value = true
}

function submitForm() {
  formRef.value?.validate((valid) => {
    if (valid) {
      if (consumableForm.id) {
        // 编辑
        const index = consumableList.value.findIndex(item => item.id === consumableForm.id)
        if (index !== -1) {
          Object.assign(consumableList.value[index], {
            code: consumableForm.code,
            name: consumableForm.name,
            category: consumableForm.category,
            unit: consumableForm.unit,
            price: consumableForm.price.toFixed(2),
            minStock: consumableForm.minStock,
            spec: consumableForm.spec,
            remark: consumableForm.remark
          })
        }
        ElMessage.success('编辑成功')
      } else {
        // 新增
        consumableList.value.push({
          id: ++idCounter,
          code: consumableForm.code,
          name: consumableForm.name,
          category: consumableForm.category,
          unit: consumableForm.unit,
          price: consumableForm.price.toFixed(2),
          stock: 0,
          minStock: consumableForm.minStock,
          spec: consumableForm.spec,
          remark: consumableForm.remark
        })
        ElMessage.success('新增成功')
      }
      formDialogVisible.value = false
    }
  })
}

function submitInbound() {
  if (inboundForm.quantity <= 0) {
    ElMessage.warning('入库数量必须大于0')
    return
  }
  const index = consumableList.value.findIndex(item => item.id === inboundForm.id)
  if (index !== -1) {
    consumableList.value[index].stock += inboundForm.quantity
  }
  ElMessage.success(`入库成功，入库数量：${inboundForm.quantity}`)
  inboundDialogVisible.value = false
}

function submitOutbound() {
  if (outboundForm.quantity <= 0) {
    ElMessage.warning('领用数量必须大于0')
    return
  }
  if (outboundForm.quantity > outboundForm.currentStock) {
    ElMessage.warning('领用数量不能超过当前库存')
    return
  }
  if (!outboundForm.userId) {
    ElMessage.warning('请选择领用人')
    return
  }
  const index = consumableList.value.findIndex(item => item.id === outboundForm.id)
  if (index !== -1) {
    consumableList.value[index].stock -= outboundForm.quantity
  }
  ElMessage.success(`领用成功，领用数量：${outboundForm.quantity}`)
  outboundDialogVisible.value = false
}
</script>

<style lang="scss" scoped>
.consumable-list-container {
  .page-card { border-radius: 16px; }
  .page-header { 
    display: flex; 
    justify-content: space-between; 
    align-items: center; 
    h2 { margin: 0; font-size: 18px; color: #1f2937; } 
  }
  .filter-form { margin-bottom: 16px; }
}
</style>
