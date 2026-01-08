/**
 * 资产借用 Composable
 * 
 * 遵循 .cursorrules 规约:
 * - 组件 <script> 长度禁止超过 100 行
 * - 复杂交互逻辑必须提取到 @/composables
 */
import { ref, reactive, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

/**
 * 借用表单逻辑
 */
export function useBorrowForm() {
  const borrowFormRef = ref()
  const submitting = ref(false)
  
  const borrowForm = reactive({
    assets: [],
    borrow_user: null,
    borrow_department: null,
    borrow_date: new Date().toISOString().split('T')[0],
    expected_return_date: '',
    reason: ''
  })
  
  const borrowRules = {
    assets: [{ required: true, message: '请选择要借用的资产', trigger: 'change' }],
    borrow_user: [{ required: true, message: '请选择借用人', trigger: 'change' }],
    borrow_date: [{ required: true, message: '请选择借用日期', trigger: 'change' }],
    expected_return_date: [{ required: true, message: '请选择预计归还日期', trigger: 'change' }]
  }
  
  function resetBorrowForm() {
    borrowForm.assets = []
    borrowForm.borrow_user = null
    borrowForm.borrow_department = null
    borrowForm.borrow_date = new Date().toISOString().split('T')[0]
    borrowForm.expected_return_date = ''
    borrowForm.reason = ''
  }
  
  async function submitBorrow(callback) {
    if (!borrowFormRef.value) return false
    
    try {
      await borrowFormRef.value.validate()
    } catch {
      return false
    }
    
    submitting.value = true
    try {
      const payload = {
        borrower: borrowForm.borrow_user,
        borrow_department: borrowForm.borrow_department,
        borrow_date: borrowForm.borrow_date,
        expected_return_date: borrowForm.expected_return_date,
        reason: borrowForm.reason,
        items: borrowForm.assets.map(id => ({ asset: id }))
      }
      
      await request.post('/assets/borrows/', payload)
      ElMessage.success('借用申请提交成功')
      resetBorrowForm()
      
      if (callback) callback()
      return true
    } catch (error) {
      console.error('提交借用失败:', error)
      ElMessage.error(error.response?.data?.msg || '提交失败')
      return false
    } finally {
      submitting.value = false
    }
  }
  
  return {
    borrowFormRef,
    borrowForm,
    borrowRules,
    submitting,
    resetBorrowForm,
    submitBorrow
  }
}

/**
 * 归还表单逻辑
 */
export function useReturnForm() {
  const returnFormRef = ref()
  const submitting = ref(false)
  
  const returnForm = reactive({
    borrow_id: null,
    asset_ids: [],
    return_date: new Date().toISOString().split('T')[0],
    condition: 'good',
    remark: ''
  })
  
  const returnRules = {
    return_date: [{ required: true, message: '请选择归还日期', trigger: 'change' }]
  }
  
  function resetReturnForm() {
    returnForm.borrow_id = null
    returnForm.asset_ids = []
    returnForm.return_date = new Date().toISOString().split('T')[0]
    returnForm.condition = 'good'
    returnForm.remark = ''
  }
  
  async function submitReturn(callback) {
    if (!returnFormRef.value) return false
    
    try {
      await returnFormRef.value.validate()
    } catch {
      return false
    }
    
    if (!returnForm.asset_ids.length) {
      ElMessage.warning('请选择要归还的资产')
      return false
    }
    
    submitting.value = true
    try {
      await request.post(`/assets/borrows/${returnForm.borrow_id}/return_assets/`, {
        asset_ids: returnForm.asset_ids,
        return_date: returnForm.return_date,
        condition: returnForm.condition,
        remark: returnForm.remark
      })
      
      ElMessage.success('资产归还成功')
      resetReturnForm()
      
      if (callback) callback()
      return true
    } catch (error) {
      console.error('归还失败:', error)
      ElMessage.error(error.response?.data?.msg || '归还失败')
      return false
    } finally {
      submitting.value = false
    }
  }
  
  return {
    returnFormRef,
    returnForm,
    returnRules,
    submitting,
    resetReturnForm,
    submitReturn
  }
}

/**
 * 借用列表数据逻辑
 */
export function useBorrowList() {
  const loading = ref(false)
  const borrowList = ref([])
  const returnList = ref([])
  const pendingReturnList = ref([])
  const statistics = ref(null)
  
  const pagination = reactive({
    current: 1,
    pageSize: 10,
    total: 0
  })
  
  // 加载借用统计
  async function loadStatistics() {
    try {
      const res = await request.get('/assets/borrows/statistics/')
      statistics.value = res
    } catch (error) {
      console.error('加载统计失败:', error)
    }
  }
  
  // 加载借用列表
  async function loadBorrowList(params = {}) {
    loading.value = true
    try {
      const queryParams = {
        page: pagination.current,
        page_size: pagination.pageSize,
        ...params
      }
      
      const res = await request.get('/assets/borrows/', { params: queryParams })
      borrowList.value = res.results || []
      pagination.total = res.count || 0
    } catch (error) {
      console.error('加载借用列表失败:', error)
      ElMessage.error('加载借用列表失败')
    } finally {
      loading.value = false
    }
  }
  
  // 加载归还记录
  async function loadReturnList(params = {}) {
    loading.value = true
    try {
      const queryParams = {
        page: pagination.current,
        page_size: pagination.pageSize,
        status: 'returned',
        ...params
      }
      
      const res = await request.get('/assets/borrows/', { params: queryParams })
      returnList.value = res.results || []
      pagination.total = res.count || 0
    } catch (error) {
      console.error('加载归还记录失败:', error)
    } finally {
      loading.value = false
    }
  }
  
  // 加载待归还列表
  async function loadPendingReturns(filterType = 'all') {
    loading.value = true
    try {
      const res = await request.get('/assets/borrows/pending_returns/', {
        params: { filter_type: filterType }
      })
      pendingReturnList.value = res.results || []
    } catch (error) {
      console.error('加载待归还列表失败:', error)
    } finally {
      loading.value = false
    }
  }
  
  return {
    loading,
    borrowList,
    returnList,
    pendingReturnList,
    statistics,
    pagination,
    loadStatistics,
    loadBorrowList,
    loadReturnList,
    loadPendingReturns
  }
}

/**
 * 借用状态辅助
 */
export function useBorrowStatus() {
  const statusMap = {
    draft: { label: '草稿', type: 'info' },
    pending: { label: '待审批', type: 'warning' },
    approved: { label: '已通过', type: 'success' },
    rejected: { label: '已拒绝', type: 'danger' },
    borrowed: { label: '借用中', type: 'warning' },
    completed: { label: '已完成', type: 'success' },
    returned: { label: '已归还', type: 'success' },
    cancelled: { label: '已取消', type: 'info' }
  }
  
  function getStatusType(status) {
    return statusMap[status]?.type || 'info'
  }
  
  function getStatusLabel(status) {
    return statusMap[status]?.label || status
  }
  
  // 判断是否超期
  function isOverdue(row) {
    if (!row || !row.expected_return_date) return false
    if (row.status === 'returned') return false
    const today = new Date().toISOString().split('T')[0]
    return row.expected_return_date < today && hasUnreturnedItems(row)
  }
  
  // 判断是否有未归还资产
  function hasUnreturnedItems(row) {
    if (!row) return false
    if (row.unreturned_items) return row.unreturned_items.length > 0
    if (row.items) return row.items.some(item => !item.is_returned)
    return false
  }
  
  // 获取未归还资产
  function getUnreturnedItems(row) {
    if (!row) return []
    if (row.unreturned_items) return row.unreturned_items
    if (row.items) return row.items.filter(item => !item.is_returned)
    return []
  }
  
  // 获取超期样式类
  function getExpiredClass(row) {
    if (isOverdue(row)) return 'text-danger'
    if (!row.expected_return_date) return ''
    
    const today = new Date()
    const expDate = new Date(row.expected_return_date)
    const diffDays = Math.ceil((expDate - today) / (1000 * 60 * 60 * 24))
    
    if (diffDays <= 7 && diffDays >= 0 && hasUnreturnedItems(row)) return 'text-warning'
    return ''
  }
  
  return {
    statusMap,
    getStatusType,
    getStatusLabel,
    isOverdue,
    hasUnreturnedItems,
    getUnreturnedItems,
    getExpiredClass
  }
}
