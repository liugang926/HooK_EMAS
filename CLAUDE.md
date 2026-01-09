# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

EAMS (Enterprise Asset Management System) is a Django REST Framework + Vue 3 based enterprise fixed asset management system supporting SSO integration (WeChat Work, DingTalk, Feishu).

**Tech Stack:**
- Backend: Django 5.0, DRF, PostgreSQL, Redis, Celery
- Frontend: Vue 3 (Composition API), Vite, Element Plus, Pinia
- Deployment: Docker Compose (development runs entirely in containers)

**Test Environment:**
- Frontend: http://localhost:3000/
- Backend API: http://localhost:8000/api/
- Admin credentials: admin / admin123

## Development Commands

### Backend (Django)
```bash
# Run development server
docker-compose exec backend python manage.py runserver

# Database migrations
docker-compose exec backend python manage.py makemigrations
docker-compose exec backend python manage.py migrate

# Create superuser
docker-compose exec backend python manage.py createsuperuser

# Shell access
docker-compose exec backend python manage.py shell
```

### Frontend (Vue 3)
```bash
# Install dependencies
npm install

# Development server
npm run dev

# Production build
npm run build

# Lint
npm run lint
```

### Docker Services
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f backend
docker-compose logs -f celery_worker

# Restart specific service
docker-compose restart backend
```

### Celery Tasks
```bash
# View Celery worker logs
docker-compose logs -f celery_worker

# Run Beat (scheduled tasks)
docker-compose up -d celery_beat
```

## Architecture

### Backend Structure

**App Modules** (`backend/apps/`):
- `common` - Base models, exception handling, shared utilities
- `accounts` - Custom user model (AUTH_USER_MODEL)
- `organizations` - Companies, departments, locations (tree structure using django-mptt)
- `assets` - Asset management, operations (receive, borrow, transfer, disposal)
- `consumables` - Supplies/consumables with inbound/outbound workflow
- `procurement` - Purchase orders, suppliers
- `inventory` - Stock counting tasks
- `finance` - Asset depreciation calculations
- `reports` - Report generation
- `workflows` - Approval workflow engine
- `sso` - WeChat Work, DingTalk, Feishu integration
- `notifications` - Message notifications
- `system` - Module registry, dynamic forms, operation logs

**Key Architectural Patterns:**

1. **Service Layer Pattern** - All business logic MUST be in `backend/services/`, never in Views. Each service inherits from `BaseService`:
   - `asset_service.py` - Asset CRUD and operations
   - `borrow_service.py`, `receive_service.py`, `transfer_service.py`, `disposal_service.py` - Asset operations
   - `maintenance_service.py` - Asset maintenance records
   - `batch_service.py` - Batch operations

2. **Adapter Pattern** - Third-party integrations in `backend/adapters/`:
   - All adapters inherit from `BasePlatformAdapter`
   - Must implement: `get_user_info()`, `send_notification()`, `_fetch_access_token()`
   - AccessTokens cached in Redis with automatic refresh
   - Implementations: `wework.py`, `dingtalk.py`, `feishu.py`

3. **BaseModel** (`apps/common/models.py`) - All models inherit from BaseModel providing:
   - Soft delete (`is_deleted`, `deleted_at`, `soft_delete()`)
   - Audit fields (`created_at`, `updated_at`, `created_by`)
   - Custom fields support via `custom_fields` JSONField
   - `SoftDeleteManager` - default manager excludes deleted records

4. **Unified Exception Handler** (`apps/common/exceptions.py`):
   - All API responses follow format: `{"code": int, "msg": str, "data": any}`
   - Use `BusinessException` for business logic errors
   - Helper functions: `success_response()`, `error_response()`

5. **Module Registry** (`apps/system/module_registry.py`):
   - Central configuration for all modules (asset, supply, user, department, purchase_order, supplier, etc.)
   - Defines system fields, code rules, API endpoints
   - Supports dynamic forms via `enable_custom_fields`
   - Used by `DynamicList` and `DynamicForm` frontend components

### Frontend Structure

**Key Directories:**
- `src/api/` - API request modules (assets.js, organizations.js, etc.) with axios interceptors for auth
- `src/composables/` - Vue composables for reusable logic (useAssetForm, useReceive, useBorrow, etc.)
- `src/stores/` - Pinia stores (user.js, app.js)
- `src/components/list/` - DynamicList component for generic table views
- `src/components/form/` - DynamicForm, FieldRenderer for form rendering
- `src/components/common/` - UserSelect, DepartmentSelect, LocationSelect, etc.

**Dynamic Module System:**
- `DynamicList` component uses `module_registry` to render list views
- `DynamicForm` component renders forms based on field definitions
- Field types: text, textarea, number, decimal, date, select, tree_select, reference, code, switch, image, file

**API Request Handler** (`src/api/request.js`):
- Auto-includes JWT token from localStorage
- Auto-adds `company` filter for multi-tenant data isolation
- Handles 401 token refresh automatically
- Error responses display as ElMessage toasts

## Coding Standards (from .cursorrules)

### Backend
- **Models**: Always inherit `BaseModel`. Money fields use `MoneyField()` helper (DecimalField 19,4). No physical deletes - use `soft_delete()`.
- **Views**: No business logic. Delegate to services. Use `@transaction.atomic` for multi-table operations.
- **Queries**: Optimize N+1 with `select_related()` (FK) and `prefetch_related()` (M2M).
- **Redis**: Cache AccessToken (7200s typical). Cache high-frequency data (categories, departments).
- **Comments**: Use English comments. Document complex formulas (e.g., depreciation calculations).

### Frontend
- **Script length**: Max 100 lines per component. Extract complex logic to composables.
- **Function length**: Max 80 lines. Split into smaller functions if needed.
- **No `any` types**: Define interfaces in `src/types/` for API responses.
- **State**: Global state in Pinia stores. Asset status flows use constants/enums, avoid magic strings.
- **File length**: Max 500 lines. Split by feature if exceeded.

### Third-Party Integration
- Inherit `BasePlatformAdapter` for new platforms
- Read secrets from `.env` only
- Return unified JSON error format

### Documentation
- Generate module docs in `docs/` after feature completion
- Generate fix docs in `docs/fix/` after bug fixes
- Docs must be reviewed before proceeding

## Testing

- Backend: Use pytest (configure tests in `backend/tests/`)
- Frontend: E2E with Playwright/Cypress (`.spec.ts` files)
- Test coverage required for core business paths (asset check-in, SSO sync, approval workflows)
- Browser headless mode checks: UI loading, API payloads, toast messages

## Environment Variables

Key variables in `.env`:
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection
- `WEWORK_CORP_ID`, `WEWORK_AGENT_ID`, `WEWORK_SECRET` - WeChat Work
- `DINGTALK_APP_KEY`, `DINGTALK_APP_SECRET` - DingTalk
- `FEISHU_APP_ID`, `FEISHU_APP_SECRET` - Feishu
- `JWT_SECRET` - JWT signing key
- `VITE_API_BASE_URL` - Frontend API base URL

## Multi-Company Architecture

The system supports multiple companies per tenant:
- `User.company` FK determines user's company
- Frontend auto-includes `company` param in API requests (excluded for auth, SSO, system config)
- Use `BaseService.get_user_company(user)` to get user's company

## Code Reuse Check

Before generating new code:
1. Check existing `services/` for reusable business logic
2. Check `composables/` for reusable frontend logic
3. Check `module_registry.py` for existing module configurations
4. Reference existing adapters (`adapters/`) for similar third-party integrations
