<template>
  <tr :class="inactive ? 'bg-gray-100 text-gray-400' : ''">
    <td class="border border-gray-300 px-4 py-2 font-medium">
      {{ label }}
    </td>
    <td class="border border-gray-300 px-4 py-2 flex items-center space-x-2">
      <!-- Colored badge if value is a known zone -->
      <div
        v-if="zoneColor"
        class="w-4 h-4 rounded-full"
        :style="{ backgroundColor: zoneColor }"
      ></div>
      <span>{{ formattedValue }}</span>
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

// Map of zones to colors
const zoneColors = {
  RESTING: "#A0A0A0",  // gray
  ZONE_1: "#A0A0A0",   // gray
  ZONE_2: "#ADD8E6",   // light blue
  ZONE_3: "#2CA02C",   // green
  ZONE_4: "#FFD700",   // yellow
  ZONE_5: "#D62728"    // red
}
// Computed property for formatted value
const formattedValue = computed(() => {
  if (props.value === null || props.value === undefined) return "—"

  if (typeof props.value === 'boolean') return props.value ? 'Yes' : 'No'

  if (typeof props.value === 'number') return props.value.toLocaleString(undefined, { maximumFractionDigits: 2 })

  return props.value
})

// Compute color if value is a zone key
const zoneColor = computed(() => {
  if (!props.value) return null
  // Check if value matches a zone key exactly
  return zoneColors[props.value] || null
})
</script>