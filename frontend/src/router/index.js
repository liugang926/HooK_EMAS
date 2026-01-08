import { createRouter, createWebHistory } from 'vue-router'
import NProgress from 'nprogress'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/login/index.vue'),
    meta: { title: '登录', requiresAuth: false }
  },
  // Redirect route for forcing page refresh (used when switching company)
  {
    path: '/redirect/:path(.*)',
    name: 'Redirect',
    component: () => import('@/views/redirect/index.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/',
    component: () => import('@/layout/index.vue'),
    redirect: '/index',
    children: [
      {
        path: 'index',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/index.vue'),
        meta: { title: '首页', icon: 'HomeFilled' }
      },
      // 待办
      {
        path: 'todo',
        name: 'Todo',
        component: () => import('@/views/todo/index.vue'),
        meta: { title: '待办', icon: 'Bell' }
      },
      // 资产管理
      {
        path: 'assets',
        name: 'Assets',
        redirect: '/assets/list',
        meta: { title: '资产', icon: 'Box' },
        children: [
          {
            path: 'list',
            name: 'AssetList',
            component: () => import('@/views/assets/list/index.vue'),
            meta: { title: '资产库' }
          },
          {
            path: 'create',
            name: 'AssetCreate',
            component: () => import('@/views/assets/create/index.vue'),
            meta: { title: '资产录入' }
          },
          {
            path: 'receive',
            name: 'AssetReceive',
            component: () => import('@/views/assets/receive/index.vue'),
            meta: { title: '资产领用&退还' }
          },
          {
            path: 'borrow',
            name: 'AssetBorrow',
            component: () => import('@/views/assets/borrow/index.vue'),
            meta: { title: '资产借用&归还' }
          },
          {
            path: 'transfer',
            name: 'AssetTransfer',
            component: () => import('@/views/assets/transfer/index.vue'),
            meta: { title: '资产调拨' }
          },
          {
            path: 'disposal',
            name: 'AssetDisposal',
            component: () => import('@/views/assets/disposal/index.vue'),
            meta: { title: '资产处置' }
          },
          {
            path: 'maintenance',
            name: 'AssetMaintenance',
            component: () => import('@/views/assets/maintenance/index.vue'),
            meta: { title: '资产维保' }
          },
          {
            path: 'settings',
            name: 'AssetSettings',
            component: () => import('@/views/assets/settings/index.vue'),
            meta: { title: '资产设置' }
          }
        ]
      },
      // 办公用品管理 (原耗材模块)
      {
        path: 'supplies',
        name: 'OfficeSupplies',
        redirect: '/supplies/list',
        meta: { title: '办公用品', icon: 'Goods' },
        children: [
          {
            path: 'list',
            name: 'SuppliesList',
            component: () => import('@/views/supplies/list/index.vue'),
            meta: { title: '用品档案' }
          },
          {
            path: 'inbound',
            name: 'SuppliesInbound',
            component: () => import('@/views/supplies/inbound/index.vue'),
            meta: { title: '入库管理' }
          },
          {
            path: 'outbound',
            name: 'SuppliesOutbound',
            component: () => import('@/views/supplies/outbound/index.vue'),
            meta: { title: '领用管理' }
          },
          {
            path: 'stock',
            name: 'SuppliesStock',
            component: () => import('@/views/supplies/stock/index.vue'),
            meta: { title: '实时库存' }
          },
          {
            path: 'settings',
            name: 'SuppliesSettings',
            component: () => import('@/views/supplies/settings/index.vue'),
            meta: { title: '用品设置' }
          }
        ]
      },
      // 采购管理
      {
        path: 'procurement',
        name: 'Procurement',
        redirect: '/procurement/suppliers',
        meta: { title: '采购', icon: 'ShoppingCart' },
        children: [
          {
            path: 'suppliers',
            name: 'Suppliers',
            component: () => import('@/views/procurement/suppliers/index.vue'),
            meta: { title: '供应商管理' }
          },
          {
            path: 'requests',
            name: 'PurchaseRequests',
            component: () => import('@/views/procurement/requests/index.vue'),
            meta: { title: '采购申请' }
          },
          {
            path: 'orders',
            name: 'PurchaseOrders',
            component: () => import('@/views/procurement/orders/index.vue'),
            meta: { title: '采购订单' }
          }
        ]
      },
      // 盘点
      {
        path: 'inventory',
        name: 'Inventory',
        redirect: '/inventory/tasks',
        meta: { title: '盘点', icon: 'Document' },
        children: [
          {
            path: 'tasks',
            name: 'InventoryTasks',
            component: () => import('@/views/inventory/tasks/index.vue'),
            meta: { title: '资产盘点任务' }
          }
        ]
      },
      // 报表
      {
        path: 'reports',
        name: 'Reports',
        redirect: '/reports/assets',
        meta: { title: '报表', icon: 'DataAnalysis' },
        children: [
          {
            path: 'assets',
            name: 'AssetReports',
            component: () => import('@/views/reports/assets/index.vue'),
            meta: { title: '资产报表' }
          },
          {
            path: 'supplies',
            name: 'SuppliesReports',
            component: () => import('@/views/reports/supplies/index.vue'),
            meta: { title: '办公用品报表' }
          }
        ]
      },
      // 财务
      {
        path: 'finance',
        name: 'Finance',
        redirect: '/finance/depreciation',
        meta: { title: '财务', icon: 'Money' },
        children: [
          {
            path: 'depreciation',
            name: 'Depreciation',
            component: () => import('@/views/finance/depreciation/index.vue'),
            meta: { title: '折旧方案' }
          },
          {
            path: 'ledger',
            name: 'Ledger',
            component: () => import('@/views/finance/ledger/index.vue'),
            meta: { title: '资产财务台账' }
          }
        ]
      },
      // 设置
      {
        path: 'settings',
        name: 'Settings',
        redirect: '/settings/companies',
        meta: { title: '设置', icon: 'Setting' },
        children: [
          {
            path: 'companies',
            name: 'Companies',
            component: () => import('@/views/settings/companies/index.vue'),
            meta: { title: '公司管理' }
          },
          {
            path: 'sso',
            name: 'SSO',
            component: () => import('@/views/settings/sso/index.vue'),
            meta: { title: 'SSO单点登录' }
          },
          {
            path: 'workflow',
            name: 'Workflow',
            component: () => import('@/views/settings/workflow/index.vue'),
            meta: { title: '审批流' }
          },
          {
            path: 'organization',
            name: 'Organization',
            component: () => import('@/views/settings/organization/index.vue'),
            meta: { title: '组织员工' }
          },
          {
            path: 'permissions',
            name: 'Permissions',
            component: () => import('@/views/settings/permissions/index.vue'),
            meta: { title: '账号权限' }
          },
          {
            path: 'memberships',
            name: 'UserMemberships',
            component: () => import('@/views/settings/memberships/index.vue'),
            meta: { title: '用户公司关系' }
          },
          {
            path: 'cross-transfer',
            name: 'CrossCompanyTransfer',
            component: () => import('@/views/settings/cross-transfer/index.vue'),
            meta: { title: '跨公司调拨' }
          },
          {
            path: 'messages',
            name: 'Messages',
            component: () => import('@/views/settings/messages/index.vue'),
            meta: { title: '消息设置' }
          },
          {
            path: 'logs',
            name: 'Logs',
            component: () => import('@/views/settings/logs/index.vue'),
            meta: { title: '系统日志' }
          },
          {
            path: 'system',
            name: 'SystemConfig',
            component: () => import('@/views/settings/system/index.vue'),
            meta: { title: '系统配置' }
          }
        ]
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/error/404.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  NProgress.start()
  
  const token = localStorage.getItem('access_token')
  const requiresAuth = to.meta.requiresAuth !== false
  
  if (requiresAuth && !token) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
  } else if (to.name === 'Login' && token) {
    next({ name: 'Dashboard' })
  } else {
    // 设置页面标题
    document.title = to.meta.title ? `${to.meta.title} - 钩子资产` : '钩子资产'
    next()
  }
})

router.afterEach(() => {
  NProgress.done()
})

export default router
