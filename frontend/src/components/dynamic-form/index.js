/**
 * Dynamic Form Components
 * 
 * Export all dynamic form related components for easy import.
 */

import DynamicField from './DynamicField.vue'
import DynamicForm from './DynamicForm.vue'
import FormDesigner from './FormDesigner.vue'
import LayoutRow from './LayoutRow.vue'
import DynamicModuleDialog from './DynamicModuleDialog.vue'

export {
    DynamicField,
    DynamicForm,
    FormDesigner,
    LayoutRow,
    DynamicModuleDialog
}

export default {
    install(app) {
        app.component('DynamicField', DynamicField)
        app.component('DynamicForm', DynamicForm)
        app.component('FormDesigner', FormDesigner)
        app.component('LayoutRow', LayoutRow)
        app.component('DynamicModuleDialog', DynamicModuleDialog)
    }
}
