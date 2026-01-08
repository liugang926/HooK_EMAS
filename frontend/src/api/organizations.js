import request from './request'

// 公司
export function getCompanies(params) {
  return request.get('/organizations/companies/', { params })
}

export function getCompany(id) {
  return request.get(`/organizations/companies/${id}/`)
}

export function createCompany(data) {
  return request.post('/organizations/companies/', data)
}

export function updateCompany(id, data) {
  return request.put(`/organizations/companies/${id}/`, data)
}

export function deleteCompany(id) {
  return request.delete(`/organizations/companies/${id}/`)
}

// 部门
export function getDepartments(params) {
  return request.get('/organizations/departments/', { params })
}

export function getDepartmentTree(companyId) {
  return request.get('/organizations/departments/tree/', { params: { company: companyId } })
}

export function createDepartment(data) {
  return request.post('/organizations/departments/', data)
}

export function updateDepartment(id, data) {
  return request.put(`/organizations/departments/${id}/`, data)
}

export function deleteDepartment(id) {
  return request.delete(`/organizations/departments/${id}/`)
}

// 员工
export function getEmployees(params) {
  return request.get('/organizations/employees/', { params })
}

export function getEmployee(id) {
  return request.get(`/organizations/employees/${id}/`)
}

export function createEmployee(data) {
  return request.post('/organizations/employees/', data)
}

export function updateEmployee(id, data) {
  return request.put(`/organizations/employees/${id}/`, data)
}

export function deleteEmployee(id) {
  return request.delete(`/organizations/employees/${id}/`)
}

// 存放位置
export function getLocations(params) {
  return request.get('/organizations/locations/', { params })
}

export function getLocationTree(companyId) {
  return request.get('/organizations/locations/tree/', { params: { company: companyId } })
}

export function createLocation(data) {
  return request.post('/organizations/locations/', data)
}

export function updateLocation(id, data) {
  return request.put(`/organizations/locations/${id}/`, data)
}

export function deleteLocation(id) {
  return request.delete(`/organizations/locations/${id}/`)
}
