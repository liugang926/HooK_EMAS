import request from './request'

// ==================== Categories ====================
export function getSupplyCategories(params) {
  return request.get('/consumables/categories/', { params })
}

export function getSupplyCategoryTree(companyId) {
  return request.get('/consumables/categories/tree/', { params: { company: companyId } })
}

export function createSupplyCategory(data) {
  return request.post('/consumables/categories/', data)
}

export function updateSupplyCategory(id, data) {
  return request.put(`/consumables/categories/${id}/`, data)
}

export function deleteSupplyCategory(id) {
  return request.delete(`/consumables/categories/${id}/`)
}

// ==================== Supply List ====================
export function getSupplies(params) {
  return request.get('/consumables/list/', { params })
}

export function getSupply(id) {
  return request.get(`/consumables/list/${id}/`)
}

export function createSupply(data) {
  return request.post('/consumables/list/', data)
}

export function updateSupply(id, data) {
  return request.put(`/consumables/list/${id}/`, data)
}

export function deleteSupply(id) {
  return request.delete(`/consumables/list/${id}/`)
}

// ==================== Inbound ====================
export function getSupplyInbounds(params) {
  return request.get('/consumables/inbounds/', { params })
}

export function getSupplyInbound(id) {
  return request.get(`/consumables/inbounds/${id}/`)
}

export function createSupplyInbound(data) {
  return request.post('/consumables/inbounds/', data)
}

export function updateSupplyInbound(id, data) {
  return request.put(`/consumables/inbounds/${id}/`, data)
}

export function deleteSupplyInbound(id) {
  return request.delete(`/consumables/inbounds/${id}/`)
}

export function approveSupplyInbound(id) {
  return request.post(`/consumables/inbounds/${id}/approve/`)
}

// ==================== Outbound ====================
export function getSupplyOutbounds(params) {
  return request.get('/consumables/outbounds/', { params })
}

export function getSupplyOutbound(id) {
  return request.get(`/consumables/outbounds/${id}/`)
}

export function createSupplyOutbound(data) {
  return request.post('/consumables/outbounds/', data)
}

export function updateSupplyOutbound(id, data) {
  return request.put(`/consumables/outbounds/${id}/`, data)
}

export function deleteSupplyOutbound(id) {
  return request.delete(`/consumables/outbounds/${id}/`)
}

export function approveSupplyOutbound(id) {
  return request.post(`/consumables/outbounds/${id}/approve/`)
}

// ==================== Stock ====================
export function getSupplyStocks(params) {
  return request.get('/consumables/stocks/', { params })
}

// ==================== Common Options ====================
export function getWarehouses(params) {
  return request.get('/organizations/locations/', { params: { ...params, type: 'warehouse' } })
}

export function getDepartments(params) {
  return request.get('/organizations/departments/', { params })
}

export function getUsers(params) {
  return request.get('/auth/users/', { params })
}

export function getSuppliers(params) {
  return request.get('/procurement/suppliers/', { params })
}

// ==================== Code Generation ====================
export function generateSupplyCode(companyId) {
  return request.post('/system/code-rules/generate_code/', { 
    company: companyId, 
    code_type: 'supply_code' 
  })
}
