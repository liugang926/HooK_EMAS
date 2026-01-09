/**
 * API 响应处理工具函数
 * 
 * 提供统一的方法来处理后端 API 响应，特别是分页响应
 * 确保所有页面使用一致的方式处理 API 返回数据
 */

/**
 * 从 API 响应中提取列表数据
 * 
 * 后端可能返回以下格式之一：
 * 1. 分页响应: { count: 100, next: null, previous: null, results: [...] }
 * 2. 直接数组: [...]
 * 3. 嵌套结构: { data: { results: [...] } }
 * 
 * @param {Object|Array} response - API 响应数据
 * @returns {Array} 提取的列表数据
 */
export function extractListData(response) {
    if (!response) return []

    // 如果已经是数组，直接返回
    if (Array.isArray(response)) return response

    // 尝试从不同的响应结构中提取数组
    // 优先级: results > data.results > data > response
    if (Array.isArray(response.results)) return response.results
    if (response.data && Array.isArray(response.data.results)) return response.data.results
    if (response.data && Array.isArray(response.data)) return response.data

    return []
}

/**
 * 从 API 响应中提取分页信息
 * 
 * @param {Object} response - API 响应数据
 * @returns {Object} 分页信息 { total, pageSize, currentPage, hasNext, hasPrevious }
 */
export function extractPaginationInfo(response) {
    if (!response || Array.isArray(response)) {
        return { total: 0, pageSize: 20, currentPage: 1, hasNext: false, hasPrevious: false }
    }

    return {
        total: response.count || 0,
        pageSize: response.page_size || 20,
        currentPage: response.page || 1,
        hasNext: !!response.next,
        hasPrevious: !!response.previous
    }
}

/**
 * 获取请求所有数据的参数（禁用分页）
 * 
 * @param {Object} params - 原始请求参数
 * @param {number} maxItems - 最大返回数量，默认 1000
 * @returns {Object} 带有分页参数的请求参数
 */
export function withAllItems(params = {}, maxItems = 1000) {
    return {
        ...params,
        page_size: maxItems
    }
}

/**
 * 构建标准分页请求参数
 * 
 * @param {Object} options - 分页选项
 * @param {number} options.page - 当前页码，默认 1
 * @param {number} options.pageSize - 每页数量，默认 20
 * @param {string} options.ordering - 排序字段
 * @param {string} options.search - 搜索关键词
 * @returns {Object} 标准化的分页参数
 */
export function buildPaginationParams({ page = 1, pageSize = 20, ordering = '', search = '' } = {}) {
    const params = {
        page,
        page_size: pageSize
    }

    if (ordering) params.ordering = ordering
    if (search) params.search = search

    return params
}

/**
 * 提取错误信息（用于显示友好的错误提示）
 * 
 * 后端可能返回以下错误格式：
 * 1. { detail: "错误信息" }
 * 2. { non_field_errors: ["错误1", "错误2"] }
 * 3. { field_name: ["字段错误1"] }
 * 4. 字符串
 * 
 * @param {Object} errorResponse - error.response.data
 * @returns {string} 格式化的错误信息
 */
export function extractErrorMessage(errorResponse) {
    if (!errorResponse) return '请求失败'
    if (typeof errorResponse === 'string') return errorResponse

    // 检查常见的错误字段
    if (errorResponse.detail) return errorResponse.detail
    if (errorResponse.message) return errorResponse.message
    if (errorResponse.error) return errorResponse.error

    // 处理 non_field_errors
    if (errorResponse.non_field_errors) {
        return Array.isArray(errorResponse.non_field_errors)
            ? errorResponse.non_field_errors.join('，')
            : errorResponse.non_field_errors
    }

    // 处理字段级别错误
    const fieldErrors = []
    for (const [key, value] of Object.entries(errorResponse)) {
        if (Array.isArray(value)) {
            fieldErrors.push(`${key}: ${value.join(', ')}`)
        } else if (typeof value === 'string') {
            fieldErrors.push(`${key}: ${value}`)
        }
    }

    if (fieldErrors.length > 0) {
        return fieldErrors.join('；')
    }

    return JSON.stringify(errorResponse)
}

/**
 * 组合使用示例:
 * 
 * // 获取分页列表
 * const res = await request.get('/api/items/', { params: buildPaginationParams({ page: 1, pageSize: 20 }) })
 * const items = extractListData(res)
 * const pagination = extractPaginationInfo(res)
 * 
 * // 获取全部数据（用于下拉选择等）
 * const res = await request.get('/api/options/', { params: withAllItems() })
 * const options = extractListData(res)
 * 
 * // 处理错误
 * try {
 *   await request.post('/api/items/', data)
 * } catch (error) {
 *   const msg = extractErrorMessage(error.response?.data)
 *   ElMessage.error(msg)
 * }
 */
