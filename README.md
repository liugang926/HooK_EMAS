# 钩子资产 - 企业固定资产管理系统

基于 Django + Vue3 的企业固定资产管理系统，支持企业微信、钉钉、飞书SSO单点登录。

## 功能特性

### 资产管理
- 资产录入、编辑、删除
- 资产分类管理
- 资产领用与退还
- 资产借用与归还
- 资产调拨
- 资产处置（报废、变卖等）
- 资产维保记录
- 资产标签打印

### 耗材管理
- 耗材档案管理
- 耗材入库/出库
- 实时库存查询
- 库存预警

### 采购管理
- 供应商管理
- 采购申请
- 采购订单
- 验收入库

### 盘点管理
- 盘点任务创建
- 移动端扫码盘点
- 盘点结果统计

### 报表中心
- 资产汇总报表
- 资产明细报表
- 部门资产统计
- 耗材出入库统计

### 财务管理
- 折旧方案设置
- 自动折旧计算
- 资产财务台账

### 系统设置
- 审批流配置
- 组织架构管理
- 权限管理
- 消息通知设置
- 操作日志

### SSO单点登录
- 企业微信登录
- 钉钉登录
- 飞书登录
- 组织架构同步

## 技术栈

### 后端
- Python 3.11+
- Django 5.0
- Django REST Framework
- PostgreSQL
- Redis
- Celery

### 前端
- Vue 3
- Vite
- Element Plus
- Pinia
- Vue Router
- ECharts
- Axios

### 部署
- Docker
- Docker Compose
- Nginx

## 快速开始

### 环境要求
- Docker 20.0+
- Docker Compose 2.0+

### 启动项目

1. 克隆项目
```bash
git clone <repository-url>
cd 企业固定资产管理
```

2. 复制环境变量配置
```bash
cp .env.example .env
# 编辑 .env 文件，配置数据库、Redis 等信息
```

3. 启动服务
```bash
docker-compose up -d
```

4. 初始化数据库
```bash
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser
```

5. 访问系统
- 前端: http://localhost:3000
- 后端API: http://localhost:8000/api/
- Django Admin: http://localhost:8000/admin/

## 开发指南

### 后端开发

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt

# 运行开发服务器
python manage.py runserver
```

### 前端开发

```bash
cd frontend

# 安装依赖
npm install

# 运行开发服务器
npm run dev

# 构建生产版本
npm run build
```

## API 文档

启动后端服务后，访问以下地址查看API文档：
- Swagger UI: http://localhost:8000/api/docs/
- ReDoc: http://localhost:8000/api/redoc/

## SSO 配置

### 企业微信

1. 登录企业微信管理后台
2. 创建自建应用
3. 获取 CorpID、AgentID、Secret
4. 在系统设置中配置 SSO

### 钉钉

1. 登录钉钉开放平台
2. 创建企业内部应用
3. 获取 AppKey、AppSecret
4. 配置回调地址

### 飞书

1. 登录飞书开放平台
2. 创建企业自建应用
3. 获取 App ID、App Secret
4. 配置重定向URL

## 目录结构

```
.
├── backend/                 # Django 后端
│   ├── apps/               # 应用模块
│   │   ├── accounts/       # 用户账户
│   │   ├── organizations/  # 组织架构
│   │   ├── assets/         # 资产管理
│   │   ├── consumables/    # 耗材管理
│   │   ├── procurement/    # 采购管理
│   │   ├── inventory/      # 盘点管理
│   │   ├── finance/        # 财务管理
│   │   ├── reports/        # 报表中心
│   │   ├── workflows/      # 审批流程
│   │   ├── sso/            # SSO单点登录
│   │   ├── notifications/  # 消息通知
│   │   └── system/         # 系统设置
│   ├── config/             # 项目配置
│   ├── Dockerfile
│   ├── manage.py
│   └── requirements.txt
├── frontend/               # Vue3 前端
│   ├── src/
│   │   ├── api/           # API 接口
│   │   ├── assets/        # 静态资源
│   │   ├── components/    # 公共组件
│   │   ├── layout/        # 布局组件
│   │   ├── router/        # 路由配置
│   │   ├── stores/        # 状态管理
│   │   ├── styles/        # 样式文件
│   │   └── views/         # 页面视图
│   ├── Dockerfile
│   ├── package.json
│   └── vite.config.js
├── docker-compose.yml
└── README.md
```

## 许可证

MIT License

## 联系方式

如有问题或建议，请提交 Issue。
