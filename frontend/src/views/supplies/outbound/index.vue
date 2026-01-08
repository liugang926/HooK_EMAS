<template>
  <div class="supplies-outbound-container">
    <el-card class="page-card">
      <template #header>
        <div class="page-header">
          <h2>棰嗙敤绠＄悊</h2>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            鏂板棰嗙敤鍗?          </el-button>
        </div>
      </template>
      
      <el-form :inline="true" class="filter-form">
        <el-form-item label="棰嗙敤鍗曞彿">
          <el-input v-model="filterForm.outbound_no" placeholder="璇疯緭鍏? clearable />
        </el-form-item>
        <el-form-item label="鐘舵€?>
          <el-select v-model="filterForm.status" placeholder="鍏ㄩ儴" clearable style="width: 120px">
            <el-option label="鑽夌" value="draft" />
            <el-option label="寰呭鎵? value="pending" />
            <el-option label="宸查鐢? value="approved" />
            <el-option label="宸插彇娑? value="cancelled" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">鎼滅储</el-button>
          <el-button @click="handleReset">閲嶇疆</el-button>
        </el-form-item>
      </el-form>
      
      <el-table :data="outboundList" style="width: 100%" v-loading="loading">
        <el-table-column prop="outbound_no" label="棰嗙敤鍗曞彿" width="160" />
        <el-table-column prop="warehouse_name" label="鍑哄簱浠撳簱" width="120" />
        <el-table-column prop="receive_user_name" label="棰嗙敤浜? width="100" />
        <el-table-column prop="receive_department_name" label="棰嗙敤閮ㄩ棬" width="120" />
        <el-table-column prop="outbound_date" label="棰嗙敤鏃ユ湡" width="120" />
        <el-table-column prop="item_count" label="鐢ㄥ搧绉嶇被" width="100" align="center" />
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
            <el-button type="success" link @click="handleApprove(row)" v-if="row.status === 'draft'">纭棰嗙敤</el-button>
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
      <el-form :model="outboundForm" label-width="100px" ref="formRef">
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="鍑哄簱浠撳簱" prop="warehouse">
              <el-select v-model="outboundForm.warehouse" placeholder="璇烽€夋嫨" style="width: 100%">
                <el-option v-for="item in warehouseOptions" :key="item.id" :label="item.name" :value="item.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="棰嗙敤鏃ユ湡" prop="outbound_date">
              <el-date-picker v-model="outboundForm.outbound_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="棰嗙敤浜?>
              <el-select v-model="outboundForm.receive_user" placeholder="璇烽€夋嫨" style="width: 100%" filterable>
                <el-option v-for="item in userOptions" :key="item.id" :label="item.display_name || item.username" :value="item.id" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="棰嗙敤閮ㄩ棬">
              <el-select v-model="outboundForm.receive_department" placeholder="璇烽€夋嫨" style="width: 100%" filterable>
                <el-option v-for="item in departmentOptions" :key="item.id" :label="item.name" :value="item.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="16">
            <el-form-item label="棰嗙敤鍘熷洜">
              <el-input v-model="outboundForm.reason" placeholder="璇疯緭鍏ラ鐢ㄥ師鍥? />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-divider content-position="left">棰嗙敤鏄庣粏</el-divider>
        
        <el-table :data="outboundForm.items" style="width: 100%" border>
          <el-table-column label="鐢ㄥ搧" min-width="200">
            <template #default="{ row, $index }">
              <el-select v-model="row.consumable" placeholder="璇烽€夋嫨鐢ㄥ搧" style="width: 100%" filterable @change="onSupplyChange($index)">
                <el-option v-for="item in supplyOptions" :key="item.id" :label="`${item.code} - ${item.name}`" :value="item.id" />
              </el-select>
            </template>
          </el-table-column>
          <el-table-column label="鍙敤搴撳瓨" width="100" align="center">
            <template #default="{ row }">{{ getAvailableStock(row.consumable) }}</template>
          </el-table-column>
          <el-table-column label="棰嗙敤鏁伴噺" width="130">
            <template #default="{ row }">
              <el-input-number v-model="row.quantity" :min="1" :max="getAvailableStock(row.consumable) || 9999" size="small" style="width: 100%" />
            </template>
          </el-table-column>
          <el-table-column label="鎿嶄綔" width="80" align="center">
            <template #default="{ $index }">
              <el-button type="danger" link @click="removeItem($index)" :disabled="outboundForm.items.length <= 1">
                <el-icon><Delete /></el-icon>
              </el-button>
            </template>
          </el-table-column>
        </el-table>
        
        <el-button type="primary" link @click="addItem" style="margin-top: 10px">
          <el-icon><Plus /></el-icon> 娣诲姞鐢ㄥ搧
        </el-button>
        
        <el-form-item label="澶囨敞" style="margin-top: 16px">
          <el-input v-model="outboundForm.remark" type="textarea" :rows="2" placeholder="璇疯緭鍏ュ娉? />
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
const filterForm = reactive({ outbound_no: '', status: '' })
const outboundList = ref([])
const pagination = reactive({ page: 1, pageSize: 20, total: 0 })

const statusMap = {
  draft: { type: 'info', label: '鑽夌' },
  pending: { type: 'warning', label: '寰呭鎵? },
  approved: { type: 'success', label: '宸查鐢? },
  cancelled: { type: 'danger', label: '宸插彇娑? }
}

const warehouseOptions = ref([])
const userOptions = ref([])
const departmentOptions = ref([])
const supplyOptions = ref([])

async function loadData() {
  loading.value = true
  try {
    const params = { page: pagination.page, page_size: pagination.pageSize, company: appStore.currentCompany?.id, outbound_type: 'receive' }
    if (filterForm.outbound_no) params.search = filterForm.outbound_no
    if (filterForm.status) params.status = filterForm.status
    const res = await request.get('/consumables/outbounds/', { params })
    outboundList.value = res.results || res || []
    pagination.total = res.count || 0
  } catch (error) {
    console.error('Load outbounds failed:', error)
    outboundList.value = []
  } finally {
    loading.value = false
  }
}

async function loadOptions() {
  try {
    const locRes = await request.get('/organizations/locations/', { params: { company: appStore.currentCompany?.id, type: 'warehouse' } })
    warehouseOptions.value = locRes.results || locRes || []
    const userRes = await request.get('/accounts/users/', { params: { company: appStore.currentCompany?.id } })
    userOptions.value = userRes.results || userRes || []
    const deptRes = await request.get('/organizations/departments/', { params: { company: appStore.currentCompany?.id } })
    departmentOptions.value = deptRes.results || deptRes || []
    const conRes = await request.get('/consumables/list/', { params: { company: appStore.currentCompany?.id, is_active: true } })
    supplyOptions.value = conRes.results || conRes || []
  } catch (error) {
    console.error('Load options failed:', error)
  }
}

function getAvailableStock(consumableId) {
  if (!consumableId) return 0
  const supply = supplyOptions.value.find(s => s.id === consumableId)
  return supply?.total_stock || 0
}

function handleSearch() { pagination.page = 1; loadData() }
function handleReset() { filterForm.outbound_no = ''; filterForm.status = ''; handleSearch() }

const formDialogVisible = ref(false)
const formDialogTitle = ref('鏂板棰嗙敤鍗?)
const formRef = ref(null)
const outboundForm = reactive({
  id: null, warehouse: null, outbound_date: new Date().toISOString().split('T')[0],
  receive_user: null, receive_department: null, reason: '',
  items: [{ consumable: null, quantity: 1 }], remark: ''
})

function handleAdd() {
  formDialogTitle.value = '鏂板棰嗙敤鍗?
  Object.assign(outboundForm, { id: null, warehouse: warehouseOptions.value[0]?.id || null, outbound_date: new Date().toISOString().split('T')[0], receive_user: null, receive_department: null, reason: '', items: [{ consumable: null, quantity: 1 }], remark: '' })
  formDialogVisible.value = true
}

function handleView(row) { ElMessage.info('鏌ョ湅棰嗙敤鍗? ' + row.outbound_no) }
function handleEdit(row) { formDialogTitle.value = '缂栬緫棰嗙敤鍗?; formDialogVisible.value = true }

async function handleApprove(row) {
  try {
    await ElMessageBox.confirm('纭棰嗙敤鍚庡皢鎵ｅ噺搴撳瓨锛屾槸鍚︾户缁紵', '纭棰嗙敤', { type: 'warning' })
    await request.post(`/consumables/outbounds/${row.id}/approve/`)
    ElMessage.success('棰嗙敤鎴愬姛')
    loadData()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('鎿嶄綔澶辫触: ' + (e.response?.data?.detail || e.message))
  }
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm('纭畾瑕佸垹闄よ棰嗙敤鍗曞悧锛?, '纭鍒犻櫎', { type: 'warning' })
    await request.delete(`/consumables/outbounds/${row.id}/`)
    ElMessage.success('鍒犻櫎鎴愬姛')
    loadData()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('鍒犻櫎澶辫触')
  }
}

function addItem() { outboundForm.items.push({ consumable: null, quantity: 1 }) }
function removeItem(index) { outboundForm.items.splice(index, 1) }
function onSupplyChange(index) { outboundForm.items[index].quantity = 1 }

async function submitForm() {
  if (!outboundForm.warehouse) { ElMessage.warning('璇烽€夋嫨鍑哄簱浠撳簱'); return }
  if (!outboundForm.receive_user) { ElMessage.warning('璇烽€夋嫨棰嗙敤浜?); return }
  if (outboundForm.items.some(i => !i.consumable)) { ElMessage.warning('璇烽€夋嫨鐢ㄥ搧'); return }
  
  submitting.value = true
  try {
    const data = {
      company: appStore.currentCompany?.id, warehouse: outboundForm.warehouse, outbound_type: 'receive',
      outbound_date: outboundForm.outbound_date, receive_user: outboundForm.receive_user,
      receive_department: outboundForm.receive_department, reason: outboundForm.reason, remark: outboundForm.remark,
      items: outboundForm.items.map(i => ({ consumable: i.consumable, quantity: i.quantity }))
    }
    if (outboundForm.id) await request.put(`/consumables/outbounds/${outboundForm.id}/`, data)
    else await request.post('/consumables/outbounds/', data)
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
.supplies-outbound-container {
  .page-card { border-radius: 16px; }
  .page-header { display: flex; justify-content: space-between; align-items: center; h2 { margin: 0; font-size: 18px; color: #1f2937; } }
  .filter-form { margin-bottom: 16px; }
  .pagination-wrapper { margin-top: 16px; display: flex; justify-content: flex-end; }
}
</style>