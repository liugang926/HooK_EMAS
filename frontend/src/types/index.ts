/**
 * 类型定义
 * 
 * 遵循 .cursorrules 规约:
 * - 禁止使用 any
 * - 所有 API 响应必须在 @/types 中定义 Interface
 */

// =====================================================
// 通用类型
// =====================================================

/** 分页响应 */
export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

/** 统一 API 响应格式 */
export interface ApiResponse<T = unknown> {
  code: number
  msg: string
  data: T
}

/** 树形节点 */
export interface TreeNode {
  id: number | string
  name: string
  children?: TreeNode[]
}

// =====================================================
// 用户和组织类型
// =====================================================

/** 用户 */
export interface User {
  id: number
  username: string
  nickname?: string
  display_name?: string
  email?: string
  phone?: string
  avatar?: string
  department?: number
  department_name?: string
  position?: string
  is_active: boolean
}

/** 部门 */
export interface Department extends TreeNode {
  id: number
  name: string
  code: string
  parent?: number
  manager?: number
  manager_name?: string
  children?: Department[]
}

/** 位置 */
export interface Location extends TreeNode {
  id: number
  name: string
  full_name?: string
  parent?: number
  children?: Location[]
}

/** 公司 */
export interface Company {
  id: number
  name: string
  code: string
  short_name?: string
  logo?: string
}

// =====================================================
// 资产类型
// =====================================================

/** 资产状态枚举 */
export type AssetStatus = 
  | 'idle'
  | 'in_use'
  | 'borrowed'
  | 'maintenance'
  | 'pending_maintenance'
  | 'disposed'
  | 'pending_disposal'
  | 'approving'

/** 资产分类 */
export interface AssetCategory extends TreeNode {
  id: number
  name: string
  code: string
  parent?: number
  depreciation_method?: string
  useful_life?: number
  salvage_rate?: number
  children?: AssetCategory[]
}

/** 资产 */
export interface Asset {
  id: number
  asset_code: string
  name: string
  category?: number
  category_name?: string
  status: AssetStatus
  brand?: string
  model?: string
  serial_number?: string
  unit: string
  quantity: number
  original_value: number
  current_value: number
  using_user?: number
  using_user_name?: string
  using_department?: number
  using_department_name?: string
  location?: number
  location_name?: string
  acquisition_date?: string
  created_at: string
  updated_at: string
}

/** 资产列表项（简化） */
export interface AssetListItem {
  id: number
  asset_code: string
  name: string
  category_name?: string
  status: AssetStatus
  original_value: number
  using_user_name?: string
  using_department_name?: string
}

// =====================================================
// 借用类型
// =====================================================

/** 借用状态 */
export type BorrowStatus = 
  | 'draft'
  | 'pending'
  | 'approved'
  | 'rejected'
  | 'borrowed'
  | 'completed'
  | 'returned'
  | 'cancelled'

/** 借用明细 */
export interface BorrowItem {
  id: number
  asset: number
  asset_name?: string
  asset_code?: string
  is_returned: boolean
  return_date?: string
  remark?: string
}

/** 借用单 */
export interface Borrow {
  id: number
  borrow_no: string
  borrower?: number
  borrower_name?: string
  borrow_department?: number
  borrow_department_name?: string
  borrow_date: string
  expected_return_date?: string
  actual_return_date?: string
  status: BorrowStatus
  reason?: string
  items: BorrowItem[]
  created_at: string
}

/** 借用统计 */
export interface BorrowStatistics {
  total_borrows: number
  borrowing_count: number
  overdue_count: number
  upcoming_count: number
  this_month_count: number
  this_month_returned: number
  borrower_stats: Array<{
    borrower__nickname?: string
    borrower_id: number
    count: number
  }>
}

/** 待归还项 */
export interface PendingReturn {
  id: number
  borrow_no: string
  borrower?: string
  borrower_id?: number
  borrow_department?: string
  borrow_date: string
  expected_return_date?: string
  days_remaining?: number
  is_overdue: boolean
  unreturned_count: number
  unreturned_items: Array<{
    id: number
    asset_id: number
    asset_name: string
    asset_code: string
  }>
  reason?: string
}

// =====================================================
// 领用类型
// =====================================================

/** 领用状态 */
export type ReceiveStatus = 'draft' | 'pending' | 'completed' | 'cancelled'

/** 领用明细 */
export interface ReceiveItem {
  id: number
  asset: number
  asset_name?: string
  asset_code?: string
  is_returned: boolean
  return_date?: string
}

/** 领用单 */
export interface Receive {
  id: number
  receive_no: string
  receive_user?: number
  receive_user_name?: string
  receive_department?: number
  receive_department_name?: string
  receive_date: string
  status: ReceiveStatus
  reason?: string
  items: ReceiveItem[]
  created_at: string
}

// =====================================================
// 调拨类型
// =====================================================

/** 调拨状态 */
export type TransferStatus = 'draft' | 'pending' | 'approved' | 'completed' | 'cancelled'

/** 调拨明细 */
export interface TransferItem {
  id: number
  asset: number
  asset_name?: string
  asset_code?: string
  original_using_user_name?: string
  original_using_department_name?: string
  original_location_name?: string
}

/** 调拨单 */
export interface Transfer {
  id: number
  transfer_no: string
  from_department?: number
  from_department_name?: string
  to_department?: number
  to_department_name?: string
  to_user?: number
  to_user_name?: string
  to_location?: number
  to_location_name?: string
  transfer_date: string
  status: TransferStatus
  reason?: string
  items: TransferItem[]
  created_at: string
}

// =====================================================
// 处置类型
// =====================================================

/** 处置方式 */
export type DisposalMethod = 'scrap' | 'sale' | 'donation' | 'transfer' | 'other'

/** 处置状态 */
export type DisposalStatus = 'draft' | 'pending' | 'approved' | 'completed' | 'cancelled'

/** 处置单 */
export interface Disposal {
  id: number
  disposal_no: string
  disposal_method: DisposalMethod
  disposal_date: string
  disposal_amount: number
  status: DisposalStatus
  reason?: string
  items: Array<{
    id: number
    asset: number
    asset_name?: string
    asset_code?: string
    original_value: number
    current_value: number
    disposal_value: number
  }>
  created_at: string
}

// =====================================================
// 维保类型
// =====================================================

/** 维保类型 */
export type MaintenanceType = 'repair' | 'maintain' | 'upgrade' | 'other'

/** 维保状态 */
export type MaintenanceStatus = 'pending' | 'in_progress' | 'completed' | 'cancelled'

/** 维保单 */
export interface Maintenance {
  id: number
  maintenance_no: string
  asset: number
  asset_name?: string
  asset_code?: string
  maintenance_type: MaintenanceType
  description?: string
  start_date: string
  end_date?: string
  actual_end_date?: string
  cost: number
  service_provider?: string
  status: MaintenanceStatus
  created_at: string
}
