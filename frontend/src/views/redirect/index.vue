<script setup>
/**
 * Redirect component for forcing page refresh
 * 
 * Used when switching company to reload data with new company filter.
 * Immediately redirects back to the target path.
 */
import { onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

onMounted(() => {
  const { params, query } = route
  const path = '/' + params.path
  router.replace({ path, query })
})
</script>

<template>
  <div></div>
</template>
