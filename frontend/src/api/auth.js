import request from './request'

// 用户名密码登录
export function login(data) {
  return request.post('/auth/login/', data)
}

// 刷新 Token
export function refreshToken(data) {
  return request.post('/auth/refresh/', data)
}

// 获取当前用户信息
export function getUserInfo() {
  return request.get('/auth/users/me/')
}

// 登出
export function logout() {
  return request.post('/auth/logout/')
}

// 修改密码
export function changePassword(data) {
  return request.post('/auth/users/change_password/', data)
}

// 获取企业微信登录URL
export function getWeWorkLoginUrl(redirectUri) {
  return request.get('/sso/wework/login/', { params: { redirect_uri: redirectUri } })
}

// 获取钉钉登录URL
export function getDingTalkLoginUrl(redirectUri) {
  return request.get('/sso/dingtalk/login/', { params: { redirect_uri: redirectUri } })
}

// 获取飞书登录URL
export function getFeishuLoginUrl(redirectUri) {
  return request.get('/sso/feishu/login/', { params: { redirect_uri: redirectUri } })
}

// ============================================
// User Company Membership APIs (Multi-Company)
// ============================================

// Get user company memberships list
export function getUserCompanyMemberships(params) {
  return request.get('/auth/user-company-memberships/', { params })
}

// Get current user's company memberships
export function getMyCompanies() {
  return request.get('/auth/user-company-memberships/my_companies/')
}

// Get memberships by user
export function getMembershipsByUser(userId) {
  return request.get('/auth/user-company-memberships/by_user/', {
    params: { user_id: userId }
  })
}

// Get memberships by company
export function getMembershipsByCompany(companyId) {
  return request.get('/auth/user-company-memberships/by_company/', {
    params: { company_id: companyId }
  })
}

// Create user company membership
export function createUserCompanyMembership(data) {
  return request.post('/auth/user-company-memberships/', data)
}

// Update user company membership
export function updateUserCompanyMembership(id, data) {
  return request.patch(`/auth/user-company-memberships/${id}/`, data)
}

// End user company membership
export function endUserCompanyMembership(id) {
  return request.post(`/auth/user-company-memberships/${id}/end_membership/`)
}

// Delete user company membership
export function deleteUserCompanyMembership(id) {
  return request.delete(`/auth/user-company-memberships/${id}/`)
}

// Batch assign users to company
export function batchAssignUsersToCompany(data) {
  return request.post('/auth/user-company-memberships/batch_assign/', data)
}

// Get membership statistics
export function getMembershipStatistics(companyId) {
  return request.get('/auth/user-company-memberships/statistics/', {
    params: companyId ? { company_id: companyId } : {}
  })
}

// Get users list
export function getUsers(params) {
  return request.get('/auth/users/', { params })
}

// Get roles list
export function getRoles(params) {
  return request.get('/auth/roles/', { params })
}
