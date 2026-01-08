/**
 * 资产领用 Composable
 * 
 * 遵循 .cursorrules 规约:
 * - 组件 <script> 长度禁止超过 100 行
 * - 复杂交互逻辑必须提取到 @/composables
 */
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

/**
 * 领用表单逻辑
 */
export function useReceiveForm() {
  const receiveFormRef = ref()
  const submitting = ref(false)
  
  const receiveForm = reactive({
    assets: [],
    receive_user: null,
    receive_department: null,
    receive_date: new Date().toISOString().split('T')[0],
    reason: ''
  })
  
  const receiveRules = {
    assets: [{ required: true, message: '请选择要领用的资产', trigger: 'change' }],
    receive_user: [{ required: true, message: '请选择领用人', trigger: 'change' }],
    receive_date: [{ required: true, message: '请选择领用日期', trigger: 'change' }]
  }
  
  function resetReceiveForm() {
    receiveForm.assets = []
    receiveForm.receive_user = null
    receiveForm.receive_department = null
    receiveForm.receive_date = new Date().toISOString().split('T')[0]
    receiveForm.reason = ''
  }
  
  async function submitReceive(callback) {
    if (!receiveFormRef.value) return false
    
    try {
      await receiveFormRef.value.validate()
    } catch {
      return false
    }
    
    submitting.value = true
    try {
      const payload = {
        receive_user: receiveForm.receive_user,
        receive_department: receiveForm.receive_department,
        receive_date: receiveForm.receive_date,
        reason: receiveForm.reason,
        items: receiveForm.assets.map(id => ({ asset: id }))
      }
      
      await request.post('/assets/receives/', payload)
      ElMessage.success('领用申请提交成功')
      resetReceiveForm()
      
      if (callback) callback()
      return true
    } catch (error) {
      console.error('提交领用失败:', error)
      ElMessage.error(error.response?.data?.msg || '提交失败')
      return false
    } finally {
      submitting.value = false
    }
  }
  
  return {
    receiveFormRef,
    receiveForm,
    receiveRules,
    submitting,
    resetReceiveForm,
    submitReceive
  }
}

/**
 * 退还表单逻辑
 */
export function useReceiveReturnForm() {
  const returnFormRef = ref()
  const submitting = ref(false)
  
  const returnForm = reactive({
    receive_id: null,
    asset_ids: [],
    return_date: new Date().toISOString().split('T')[0],
    reason: ''
  })
  
  const returnRules = {
    return_date: [{ required: true, message: '请选择退还日期', trigger: 'change' }]
  }
  
  function resetReturnForm() {
    returnForm.receive_id = null
    returnForm.asset_ids = []
    returnForm.return_date = new Date().toISOString().split('T')[0]
    returnForm.reason = ''
  }
  
  async function submitReturn(callback) {
    if (!returnFormRef.value) return false
    
    try {
      await returnFormRef.value.validate()
    } catch {
      return false
    }
    
    if (!returnForm.asset_ids.length) {
      ElMessage.warning('请选择要退还的资产')
      return false
    }
    
    submitting.value = true
    try {
      await request.post(`/assets/receives/${returnForm.receive_id}/return_assets/`, {
        asset_ids: returnForm.asset_ids,
        return_date: returnForm.return_date,
        reason: returnForm.reason
      })
      
      ElMessage.success('资产退还成功')
      resetReturnForm()
      
      if (callback) callback()
      return true
    } catch (error) {
      console.error('退还失败:', error)
      ElMessage.error(error.response?.data?.msg || '退还失败')
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
 * 领用列表数据逻辑
 */
export function useReceiveList() {
  const loading = ref(false)
  const receiveList = ref([])
  const returnList = ref([])
  
  const pagination = reactive({
    current: 1,
    pageSize: 10,
    total: 0
  })
  
  // 加载领用列表
  async function loadReceiveList(params = {}) {
    loading.value = true
    try {
      const queryParams = {
        page: pagination.current,
        page_size: pagination.pageSize,
        ...params
      }
      
      const res = await request.get('/assets/receives/', { params: queryParams })
      receiveList.value = res?.results || res || []
      pagination.total = res?.count || 0
    } catch (error) {
      console.error('加载领用记录失败:', error)
      ElMessage.error('加载领用记录失败')
    } finally {
      loading.value = false
    }
  }
  
  // 加载退还记录
  async function loadReturnList(params = {}) {
    loading.value = true
    try {
      const queryParams = {
        operation_type: 'return',
        page: pagination.current,
        page_size: pagination.pageSize,
        ...params
      }
      
      const res = await request.get('/assets/operations/', { params: queryParams })
      returnList.value = (res?.results || res || []).map(op => ({
        id: op.id,
        return_no: op.operation_no || `TH-${op.id}`,
        asset_name: op.asset_name,
        asset_code: op.asset_code,
        return_user_name: op.operator_name,
        return_date: op.created_at?.split('T')[0],
        status: 'completed',
        reason: op.description
      }))
      pagination.total = res?.count || 0
    } catch (error) {
      console.error('加载退还记录失败:', error)
    } finally {
      loading.value = false
    }
  }
  
  return {
    loading,
    receiveList,
    returnList,
    pagination,
    loadReceiveList,
    loadReturnList
  }
}

/**
 * 领用状态辅助
 */
export function useReceiveStatus() {
  const statusMap = {
    draft: { label: '草稿', type: 'info' },
    pending: { label: '待审批', type: 'warning' },
    approved: { label: '已通过', type: 'success' },
    rejected: { label: '已拒绝', type: 'danger' },
    completed: { label: '已完成', type: 'success' },
    cancelled: { label: '已取消', type: 'info' }
  }
  
  const returnStatusMap = {
    pending: { label: '待处理', type: 'warning' },
    completed: { label: '已完成', type: 'success' }
  }
  
  function getStatusType(status) {
    return statusMap[status]?.type || 'info'
  }
  
  function getStatusLabel(status) {
    return statusMap[status]?.label || status
  }
  
  function getReturnStatusType(status) {
    return returnStatusMap[status]?.type || 'info'
  }
  
  function getReturnStatusLabel(status) {
    return returnStatusMap[status]?.label || status
  }
  
  // 判断是否可退还
  function canReturn(record) {
    if (!record || !record.items) return false
    return record.status === 'completed' && 
           record.items.some(item => !item.is_returned)
  }
  
  // 获取未退还资产
  function getUnreturnedItems(record) {
    if (!record || !record.items) return []
    return record.items.filter(item => !item.is_returned)
  }
  
  return {
    statusMap,
    returnStatusMap,
    getStatusType,
    getStatusLabel,
    getReturnStatusType,
    getReturnStatusLabel,
    canReturn,
    getUnreturnedItems
  }
}
