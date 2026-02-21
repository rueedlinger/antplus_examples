<template>
  <tr :class="inactive ? 'bg-gray-100 text-gray-400' : ''">
    <td class="border border-gray-300 px-4 py-2 font-medium">
      {{ label }}
    </td>
    <td class="border border-gray-300 px-4 py-2">
      {{ value ?? "—" }}
    </td>
  </tr>
</template>

<script setup>
defineProps({
  label: String,
  value: [String, Number, Boolean],
  inactive: Boolean
})
</script>