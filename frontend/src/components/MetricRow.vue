<template>
  <tr :class="inactive ? 'bg-gray-100 text-gray-400' : ''">
    <td class="border border-gray-300 px-4 py-2 font-medium">
      {{ label }}
    </td>
    <td class="border border-gray-300 px-4 py-2">
      {{ formattedValue }}
    </td>
  </tr>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  label: String,
  value: [String, Number, Boolean],
  inactive: Boolean
})

// Computed property for formatted value
const formattedValue = computed(() => {
  if (props.value === null || props.value === undefined) return "—"

  if (typeof props.value === 'boolean') return props.value ? 'Yes' : 'No'

  if (typeof props.value === 'number') return props.value.toLocaleString(undefined, { maximumFractionDigits: 2 })

  return props.value
})
</script>