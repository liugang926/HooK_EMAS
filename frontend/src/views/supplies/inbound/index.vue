<template>
  <div class="supplies-inbound-container">
    <el-card class="page-card">
      <template #header>
        <div class="page-header">
          <h2>鍏ュ簱绠＄悊</h2>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            鏂板鍏ュ簱鍗?          </el-button>
        </div>
      </template>
      
      <el-form :inline="true" class="filter-form">
        <el-form-item label="鍏ュ簱鍗曞彿">
          <el-input v-model="filterForm.inbound_no" placeholder="璇疯緭鍏? clearable />
        </el-form-item>
        <el-form-item label="鐘舵€?>
          <el-select v-model="filterForm.status" placeholder="鍏ㄩ儴" clearable style="width: 120px">
            <el-option label="鑽夌" value="draft" />
            <el-option label="寰呭鎵? value="pending" />
            <el-option label="宸插叆搴? value="approved" />
            <el-option label="宸插彇娑? value="cancelled" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">鎼滅储</el-button>
          <el-button @click="handleReset">閲嶇疆</el-button>
        </el-form-item>
      </el-form>
      
      <el-table :data="inboundList" style="width: 100%" v-loading="loading">
        <el-table-column prop="inbound_no" label="鍏ュ簱鍗曞彿" width="160" />
        <el-table-column prop="warehouse_name" label="鍏ュ簱浠撳簱" width="120" />
        <el-table-column prop="supplier_name" label="渚涘簲鍟? width="150" />
        <el-table-column prop="inbound_date" label="鍏ュ簱鏃ユ湡" width="120" />
        <el-table-column prop="item_count" label="鐢ㄥ搧绉嶇被" width="100" align="center" />
        <el-table-column prop="total_amount" label="鎬婚噾棰? width="120">
          <template #default="{ row }">{{ row.total_amount }}</template>
        </el-table-column>
        <el-table-column prop="status" label="鐘舵€? width="100">
          <template #default="{ row }">
            <el-tag :type="statusMap[row.status]?.type">{{ statusMap[row.status]?.label }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_by_name" label="鍒涘缓浜? width="100" />
        <el-table-column prop="created_at" label="鍒涘缓鏃堕棿" width="170" />
        <el-table-column label="鎿嶄綔" width="220" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleView(row)">鏌ョ湅</el-button>
            <el-button type="primary" link @click="handleEdit(row)" v-if="row.status === 'draft'">缂栬緫</el-button>
            <el-button type="success" link @click="handleApprove(row)" v-if="row.status === 'draft'">纭鍏ュ簱</el-button>
            <el-button type="danger" link @click="handleDelete(row)" v-if="row.status === 'draft'">鍒犻櫎</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next"
          @size-change="loadData"
          @current-change="loadData"
        />
      </div>
    </el-card>
    
    <el-dialog v-model="formDialogVisible" :title="formDialogTitle" width="900px" destroy-on-close>
      <el-form :model="inboundForm" label-width="100px" ref="formRef">
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="鍏ュ簱浠撳簱" prop="warehouse">
              <el-select v-model="inboundForm.warehouse" placeholder="璇烽€夋嫨" style="width: 100%">
                <el-option v-for="item in warehouseOptions" :key="item.id" :label="item.name" :value="item.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="鍏ュ簱鏃ユ湡" prop="inbound_date">
              <el-date-picker v-model="inboundForm.inbound_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="渚涘簲鍟?>
              <el-select v-model="inboundForm.supplier" placeholder="璇烽€夋嫨" style="width: 100%" clearable filterable>
                <el-option v-for="item in supplierOptions" :key="item.id" :label="item.name" :value="item.id" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-divider content-position="left">鍏ュ簱鏄庣粏</el-divider>
        
        <el-table :data="inboundForm.items" style="width: 100%" border>
          <el-table-column label="鐢ㄥ搧" min-width="200">
            <template #default="{ row, $index }">
              <el-select v-model="row.consumable" placeholder="璇烽€夋嫨鐢ㄥ搧" style="width: 100%" filterable @change="onSupplyChange($index)">
                <el-option v-for="item in supplyOptions" :key="item.id" :label="`${item.code} - ${item.name}`" :value="item.id" />
              </el-select>
            </template>
          </el-table-column>
          <el-table-column label="鏁伴噺" width="130">
            <template #default="{ row }">
              <el-input-number v-model="row.quantity" :min="1" size="small" style="width: 100%" />
            </template>
          </el-table-column>
          <el-table-column label="鍗曚环" width="130">
            <template #default="{ row }">
              <el-input-number v-model="row.price" :min="0" :precision="2" size="small" style="width: 100%" />
            </template>
          </el-table-column>
          <el-table-column label="閲戦" width="120">
            <template #default="{ row }">
              {{ ((row.quantity || 0) * (row.price || 0)).toFixed(2) }}
            </template>
          </el-table-column>
          <el-table-column label="鎿嶄綔" width="80" align="center">
            <template #default="{ $index }">
              <el-button type="danger" link @click="removeItem($index)" :disabled="inboundForm.items.length <= 1">
                <el-icon><Delete /></el-icon>
              </el-button>
            </template>
          </el-table-column>
        </el-table>
        
        <el-button type="primary" link @click="addItem" style="margin-top: 10px">
          <el-icon><Plus /></el-icon> 娣诲姞鐢ㄥ搧
        </el-button>
        
        <el-form-item label="澶囨敞" style="margin-top: 16px">
          <el-input v-model="inboundForm.remark" type="textarea" :rows="2" placeholder="璇疯緭鍏ュ娉? />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="formDialogVisible = false">鍙栨秷</el-button>
        <el-button type="primary" @click="submitForm" :loading="submitting">淇濆瓨</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Plus, Delete } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/api/request'
import { useAppStore } from '@/stores/app'

const appStore = useAppStore()
const loading = ref(false)
const submitting = ref(false)
const filterForm = reactive({ inbound_no: '', status: '' })
const inboundList = ref([])
const pagination = reactive({ page: 1, pageSize: 20, total: 0 })

const statusMap = {
  draft: { type: 'info', label: '鑽夌' },
  pending: { type: 'warning', label: '寰呭鎵? },
  approved: { type: 'success', label: '宸插叆搴? },
  cancelled: { type: 'danger', label: '宸插彇娑? }
}

const warehouseOptions = ref([])
const supplierOptions = ref([])
const supplyOptions = ref([])

async function loadData() {
  loading.value = true
  try {
    const params = { page: pagination.page, page_size: pagination.pageSize, company: appStore.currentCompany?.id }
    if (filterForm.inbound_no) params.search = filterForm.inbound_no
    if (filterForm.status) params.status = filterForm.status
    const res = await request.get('/consumables/inbounds/', { params })
    inboundList.value = res.results || res || []
    pagination.total = res.count || 0
  } catch (error) {
    console.error('Load inbounds failed:', error)
    inboundList.value = []
  } finally {
    loading.value = false
  }
}

async function loadOptions() {
  try {
    const locRes = await request.get('/organizations/locations/', { params: { company: appStore.currentCompany?.id, type: 'warehouse' } })
    warehouseOptions.value = locRes.results || locRes || []
    const supRes = await request.get('/procurement/suppliers/', { params: { company: appStore.currentCompany?.id } })
    supplierOptions.value = supRes.results || supRes || []
    const conRes = await request.get('/consumables/list/', { params: { company: appStore.currentCompany?.id, is_active: true } })
    supplyOptions.value = conRes.results || conRes || []
  } catch (error) {
    console.error('Load options failed:', error)
  }
}

function handleSearch() { pagination.page = 1; loadData() }
function handleReset() { filterForm.inbound_no = ''; filterForm.status = ''; handleSearch() }

const formDialogVisible = ref(false)
const formDialogTitle = ref('鏂板鍏ュ簱鍗?)
const formRef = ref(null)
const inboundForm = reactive({
  id: null, warehouse: null, inbound_date: new Date().toISOString().split('T')[0],
  supplier: null, items: [{ consumable: null, quantity: 1, price: 0 }], remark: ''
})

function handleAdd() {
  formDialogTitle.value = '鏂板鍏ュ簱鍗?
  Object.assign(inboundForm, { id: null, warehouse: warehouseOptions.value[0]?.id || null, inbound_date: new Date().toISOString().split('T')[0], supplier: null, items: [{ consumable: null, quantity: 1, price: 0 }], remark: '' })
  formDialogVisible.value = true
}

function handleView(row) { ElMessage.info('鏌ョ湅鍏ュ簱鍗? ' + row.inbound_no) }
function handleEdit(row) { formDialogTitle.value = '缂栬緫鍏ュ簱鍗?; formDialogVisible.value = true }

async function handleApprove(row) {
  try {
    await ElMessageBox.confirm('纭鍏ュ簱鍚庡皢鏇存柊搴撳瓨锛屾槸鍚︾户缁紵', '纭鍏ュ簱', { type: 'warning' })
    await request.post(`/consumables/inbounds/${row.id}/approve/`)
    ElMessage.success('鍏ュ簱鎴愬姛')
    loadData()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('鎿嶄綔澶辫触: ' + (e.response?.data?.detail || e.message))
  }
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm('纭畾瑕佸垹闄よ鍏ュ簱鍗曞悧锛?, '纭鍒犻櫎', { type: 'warning' })
    await request.delete(`/consumables/inbounds/${row.id}/`)
    ElMessage.success('鍒犻櫎鎴愬姛')
    loadData()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('鍒犻櫎澶辫触')
  }
}

function addItem() { inboundForm.items.push({ consumable: null, quantity: 1, price: 0 }) }
function removeItem(index) { inboundForm.items.splice(index, 1) }

function onSupplyChange(index) {
  const item = inboundForm.items[index]
  const supply = supplyOptions.value.find(s => s.id === item.consumable)
  if (supply) item.price = parseFloat(supply.price) || 0
}

async function submitForm() {
  if (!inboundForm.warehouse) { ElMessage.warning('璇烽€夋嫨鍏ュ簱浠撳簱'); return }
  if (inboundForm.items.some(i => !i.consumable)) { ElMessage.warning('璇烽€夋嫨鐢ㄥ搧'); return }
  
  submitting.value = true
  try {
    const totalAmount = inboundForm.items.reduce((sum, i) => sum + (i.quantity * i.price), 0)
    const data = {
      company: appStore.currentCompany?.id, warehouse: inboundForm.warehouse, inbound_date: inboundForm.inbound_date,
      supplier: inboundForm.supplier, total_amount: totalAmount.toFixed(2), remark: inboundForm.remark,
      items: inboundForm.items.map(i => ({ consumable: i.consumable, quantity: i.quantity, price: i.price, amount: (i.quantity * i.price).toFixed(2) }))
    }
    if (inboundForm.id) await request.put(`/consumables/inbounds/${inboundForm.id}/`, data)
    else await request.post('/consumables/inbounds/', data)
    ElMessage.success('淇濆瓨鎴愬姛')
    formDialogVisible.value = false
    loadData()
  } catch (error) {
    ElMessage.error('淇濆瓨澶辫触: ' + (error.response?.data?.detail || error.message))
  } finally {
    submitting.value = false
  }
}

onMounted(() => { loadData(); loadOptions() })
</script>

<style lang="scss" scoped>
.supplies-inbound-container {
  .page-card { border-radius: 16px; }
  .page-header { display: flex; justify-content: space-between; align-items: center; h2 { margin: 0; font-size: 18px; color: #1f2937; } }
  .filter-form { margin-bottom: 16px; }
  .pagination-wrapper { margin-top: 16px; display: flex; justify-content: flex-end; }
}
</style>