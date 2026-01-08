import request from './request'

// 资产分类
export function getAssetCategories(params) {
  return request.get('/assets/categories/', { params })
}

export function getAssetCategoryTree(companyId) {
  return request.get('/assets/categories/tree/', { params: { company: companyId } })
}

export function createAssetCategory(data) {
  return request.post('/assets/categories/', data)
}

export function updateAssetCategory(id, data) {
  return request.put(`/assets/categories/${id}/`, data)
}

export function deleteAssetCategory(id) {
  return request.delete(`/assets/categories/${id}/`)
}

// 资产列表
export function getAssets(params) {
  return request.get('/assets/list/', { params })
}

export function getAsset(id) {
  return request.get(`/assets/list/${id}/`)
}

export function createAsset(data) {
  return request.post('/assets/list/', data)
}

export function updateAsset(id, data) {
  return request.put(`/assets/list/${id}/`, data)
}

export function deleteAsset(id) {
  return request.delete(`/assets/list/${id}/`)
}

// 资产统计
export function getAssetStatistics(params) {
  return request.get('/assets/list/statistics/', { params })
}

// 生成资产编号 (根据公司编号规则)
export function generateAssetCode(companyId) {
  return request.post('/system/code-rules/generate_code/', { company: companyId })
}

// 资产回收站
export function getAssetRecycleBin(params) {
  return request.get('/assets/list/recycle_bin/', { params })
}

export function restoreAsset(id) {
  return request.post(`/assets/list/${id}/restore/`)
}

// 资产领用
export function getAssetReceives(params) {
  return request.get('/assets/receives/', { params })
}

export function createAssetReceive(data) {
  return request.post('/assets/receives/', data)
}

// 资产借用
export function getAssetBorrows(params) {
  return request.get('/assets/borrows/', { params })
}

export function createAssetBorrow(data) {
  return request.post('/assets/borrows/', data)
}

export function returnBorrowedAssets(id, itemIds) {
  return request.post(`/assets/borrows/${id}/return_assets/`, { item_ids: itemIds })
}

// 资产调拨
export function getAssetTransfers(params) {
  return request.get('/assets/transfers/', { params })
}

export function createAssetTransfer(data) {
  return request.post('/assets/transfers/', data)
}

// 资产处置
export function getAssetDisposals(params) {
  return request.get('/assets/disposals/', { params })
}

export function createAssetDisposal(data) {
  return request.post('/assets/disposals/', data)
}

// 资产维保
export function getAssetMaintenances(params) {
  return request.get('/assets/maintenances/', { params })
}

export function createAssetMaintenance(data) {
  return request.post('/assets/maintenances/', data)
}

// 资产标签
export function getAssetLabels(params) {
  return request.get('/assets/labels/', { params })
}

export function createAssetLabel(data) {
  return request.post('/assets/labels/', data)
}

// 图片上传
export function uploadAssetImage(formData) {
  return request.post('/assets/images/upload/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// 带图片的资产创建/更新
export function createAssetWithImage(formData) {
  return request.post('/assets/list/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

export function updateAssetWithImage(id, formData) {
  return request.patch(`/assets/list/${id}/`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// ==================== Batch Import/Export ====================

/**
 * Download asset import template
 * @returns {Promise} Excel file blob
 */
export function downloadImportTemplate() {
  return request.get('/assets/list/import_template/', {
    responseType: 'blob'
  })
}

/**
 * Import assets from Excel file
 * @param {File} file - Excel file to import
 * @returns {Promise} Import result with success count and errors
 */
export function importAssets(file) {
  const formData = new FormData()
  formData.append('file', file)
  return request.post('/assets/list/import_assets/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * Export assets to Excel file
 * @param {Object} params - Export parameters
 * @param {Array<number>} params.ids - Optional array of asset IDs to export
 * @param {Array<string>} params.fields - Optional array of field names to export
 * @param {Object} params.filters - Optional filter parameters (same as list endpoint)
 * @returns {Promise} Excel file blob
 */
export function exportAssets(params = {}) {
  const queryParams = { ...params.filters }
  
  if (params.ids && params.ids.length > 0) {
    queryParams.ids = params.ids.join(',')
  }
  if (params.fields && params.fields.length > 0) {
    queryParams.fields = params.fields.join(',')
  }
  
  return request.get('/assets/list/export/', {
    params: queryParams,
    responseType: 'blob'
  })
}

// ==================== Batch Operations ====================

/**
 * Batch receive assets (assign to user/department/location)
 * @param {Object} data - Receive data
 * @param {Array<number>} data.asset_ids - Array of asset IDs
 * @param {number} data.receive_user - User ID receiving the assets
 * @param {number} data.receive_department - Department ID (optional)
 * @param {number} data.receive_location - Location ID (optional)
 * @param {string} data.receive_date - Receive date (YYYY-MM-DD)
 * @param {string} data.reason - Reason for receiving
 * @returns {Promise} Operation result
 */
export function batchReceiveAssets(data) {
  return request.post('/assets/list/batch_receive/', data)
}

/**
 * Batch return assets (return to idle status)
 * @param {Object} data - Return data
 * @param {Array<number>} data.asset_ids - Array of asset IDs
 * @param {string} data.return_date - Return date (YYYY-MM-DD)
 * @param {string} data.reason - Reason for returning
 * @returns {Promise} Operation result
 */
export function batchReturnAssets(data) {
  return request.post('/assets/list/batch_return/', data)
}

/**
 * Batch transfer assets (change department/user/location)
 * @param {Object} data - Transfer data
 * @param {Array<number>} data.asset_ids - Array of asset IDs
 * @param {number} data.to_department - Target department ID (optional)
 * @param {number} data.to_user - Target user ID (optional)
 * @param {number} data.to_location - Target location ID (optional)
 * @param {string} data.transfer_date - Transfer date (YYYY-MM-DD)
 * @param {string} data.reason - Reason for transfer
 * @returns {Promise} Operation result
 */
export function batchTransferAssets(data) {
  return request.post('/assets/list/batch_transfer/', data)
}

/**
 * Batch delete assets (soft delete)
 * @param {Array<number>} assetIds - Array of asset IDs
 * @returns {Promise} Operation result
 */
export function batchDeleteAssets(assetIds) {
  return request.post('/assets/list/batch_delete/', { asset_ids: assetIds })
}
