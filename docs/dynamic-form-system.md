# Dynamic Form System Documentation

## Overview

The Dynamic Form System provides a flexible, centralized approach to managing form fields across all modules in the EAMS application. It enables:

- **Centralized Configuration**: All module definitions in one place (`module_registry.py`)
- **Dynamic Field Management**: Add/remove/modify fields without code changes
- **Custom Fields Support**: User-defined fields stored in `custom_fields` JSONField
- **Consistent UI/UX**: Uniform form rendering across all modules

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      MODULE_REGISTRY                             │
│  (Centralized configuration for all modules)                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Database Layer                                │
│  ┌─────────────┐  ┌─────────────────┐  ┌──────────────────┐     │
│  │ FieldGroup  │  │ FieldDefinition │  │ ModuleFormConfig │     │
│  └─────────────┘  └─────────────────┘  └──────────────────┘     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       API Layer                                  │
│  ┌──────────────────┐  ┌────────────────────┐                   │
│  │ ModuleRegistryAPI│  │ FormConfigViewSets │                   │
│  └──────────────────┘  └────────────────────┘                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Frontend Layer                               │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────────┐       │
│  │ DynamicForm │  │FieldRenderer │  │ useFormConfig     │       │
│  └─────────────┘  └──────────────┘  └───────────────────┘       │
└─────────────────────────────────────────────────────────────────┘
```

## Module Registry

### Location
`backend/apps/system/module_registry.py`

### Structure

```python
MODULE_REGISTRY = {
    'module_name': {
        'label': '模块中文名',
        'label_en': 'Module English Name',
        'api_base': '/api/module/',
        'icon': 'IconName',
        'code_rule': {
            'enabled': True,
            'code_type': 'module_code',
            'default_prefix': 'XX',
            'default_date_format': 'YYYYMMDD',
            'default_serial_length': 4,
        },
        'features': {
            'create': True,
            'edit': True,
            'delete': True,
            'import': True,
            'export': True,
            'batch_operations': True,
            'custom_fields': True,
        },
        'system_fields': [
            {
                'field_key': 'field_name',
                'field_name': '字段名称',
                'field_type': FieldType.TEXT,
                'is_required': True,
                'show_in_list': True,
                'width': 8,
                'sort_order': 1,
            },
            # ... more fields
        ],
    },
}
```

### Supported Field Types

| Type | Description | Config Options |
|------|-------------|----------------|
| `TEXT` | Single-line text | `placeholder` |
| `TEXTAREA` | Multi-line text | `rows` |
| `NUMBER` | Integer | `min`, `max` |
| `DECIMAL` | Decimal number | `min`, `max`, `precision` |
| `DATE` | Date picker | - |
| `DATETIME` | Date-time picker | - |
| `SELECT` | Single select dropdown | `options` |
| `MULTI_SELECT` | Multiple select | `options` |
| `RADIO` | Radio buttons | `options` |
| `CHECKBOX` | Checkboxes | `options` |
| `SWITCH` | Toggle switch | - |
| `REFERENCE` | Reference lookup | `reference_config` |
| `TREE_SELECT` | Tree selection | `reference_config` |
| `CASCADER` | Cascading select | `reference_config` |
| `IMAGE` | Image upload | - |
| `FILE` | File upload | - |
| `RICH_TEXT` | Rich text editor | - |
| `CODE` | Auto-generated code | `code_config` |

### Registered Modules

1. **Asset** (`asset`) - Fixed asset management
2. **Supply** (`supply`) - Office supplies management
3. **User** (`user`) - User management
4. **Department** (`department`) - Department management
5. **Purchase Order** (`purchase_order`) - Procurement orders
6. **Supplier** (`supplier`) - Supplier management
7. **Location** (`location`) - Asset location management

## API Endpoints

### Module Registry APIs

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/system/registry/` | GET | Get all modules or specific module |
| `/api/system/registry/<module>/fields/` | GET | Get system fields for module |
| `/api/system/registry/<module>/code-rule/` | GET | Get code generation rule |
| `/api/system/registry/features/` | GET | Get modules by feature |

### Form Config APIs

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/system/form/modules/` | GET/POST | Module form configurations |
| `/api/system/form/modules/form_config/` | GET | Get complete form config |
| `/api/system/form/groups/` | GET/POST | Field groups |
| `/api/system/form/fields/` | GET/POST | Field definitions |
| `/api/system/form/fields/by_module/` | GET | Get fields by module |
| `/api/system/form/fields/list_fields/` | GET | Get list display fields |

## Usage Examples

### Backend: Using Mixins

```python
from apps.system.mixins import DynamicFieldsMixin, CodeGenerationMixin

class AssetViewSet(DynamicFieldsMixin, CodeGenerationMixin, viewsets.ModelViewSet):
    module_name = 'asset'
    queryset = Asset.objects.all()
    serializer_class = AssetSerializer
```

### Backend: Custom Fields in Model

```python
from apps.common.models import BaseModel

class Asset(BaseModel):
    name = models.CharField(max_length=200)
    # ... system fields
    
    # custom_fields inherited from BaseModel
    # Access: instance.get_custom_field('field_key')
    # Set: instance.set_custom_field('field_key', value)
```

### Frontend: DynamicForm Component

```vue
<template>
  <DynamicForm
    v-model="dialogVisible"
    module="asset"
    :mode="isEdit ? 'edit' : 'create'"
    :data="currentRecord"
    @success="handleSuccess"
  />
</template>

<script setup>
import DynamicForm from '@/components/form/DynamicForm.vue'
</script>
```

### Frontend: Using Form Config Composable

```javascript
import { useFormConfig } from '@/composables/useFormConfig'

const {
  formConfig,
  loading,
  loadFormConfig,
  initFormData,
  buildValidationRules,
  submitForm
} = useFormConfig('asset')

// Load configuration
await loadFormConfig('create')

// Initialize form data
const formData = initFormData(existingData)

// Submit form
await submitForm(formData, 'create')
```

## Management Commands

### Initialize Form Configurations

```bash
# Initialize all modules
python manage.py init_form_config

# Initialize specific module
python manage.py init_form_config --module asset

# Reset and reinitialize
python manage.py init_form_config --reset

# List available modules
python manage.py init_form_config --list
```

### Initialize Module Fields

```bash
# Initialize all modules
python manage.py init_module_fields

# Initialize specific module
python manage.py init_module_fields --module=asset

# Force overwrite existing
python manage.py init_module_fields --module=asset --force

# Dry run (preview)
python manage.py init_module_fields --dry-run
```

## Database Models

### FieldGroup

```python
class FieldGroup(models.Model):
    module = models.CharField(max_length=50)
    group_key = models.CharField(max_length=50)
    group_name = models.CharField(max_length=100)
    sort_order = models.IntegerField(default=0)
    is_collapsible = models.BooleanField(default=False)
    default_collapsed = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
```

### FieldDefinition

```python
class FieldDefinition(models.Model):
    module = models.CharField(max_length=50)
    field_key = models.CharField(max_length=100)
    field_name = models.CharField(max_length=100)
    field_type = models.CharField(max_length=20)
    group = models.ForeignKey(FieldGroup, null=True)
    
    # Permissions
    is_required = models.BooleanField(default=False)
    is_readonly = models.BooleanField(default=False)
    is_hidden = models.BooleanField(default=False)
    
    # Configuration
    options = models.JSONField(default=list)
    reference_config = models.JSONField(default=dict)
    number_config = models.JSONField(default=dict)
    default_value = models.JSONField(null=True)
    
    # List display
    show_in_list = models.BooleanField(default=False)
    list_sortable = models.BooleanField(default=False)
    list_searchable = models.BooleanField(default=False)
```

### ModuleFormConfig

```python
class ModuleFormConfig(models.Model):
    module = models.CharField(max_length=50, unique=True)
    module_label = models.CharField(max_length=100)
    api_base = models.CharField(max_length=200)
    
    # Permissions
    enable_create = models.BooleanField(default=True)
    enable_edit = models.BooleanField(default=True)
    enable_delete = models.BooleanField(default=True)
    enable_import = models.BooleanField(default=True)
    enable_export = models.BooleanField(default=True)
```

## Best Practices

1. **Always use MODULE_REGISTRY** as the source of truth for system fields
2. **Run init_form_config** after adding new modules to the registry
3. **Use mixins** in ViewSets for consistent behavior
4. **Store custom fields** in the `custom_fields` JSONField
5. **Keep field keys** consistent across frontend and backend
6. **Document new field types** when extending the system

## Related Documentation

- [Multi-Company Architecture](./architecture/multi-company-design.md)
- [API Documentation](./api/)
- [Frontend Components](./components/)
