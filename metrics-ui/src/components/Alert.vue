<template>
  <div role="alert" class="rounded-md shadow-lg overflow-hidden w-80">
    <div :class="headerClass" class="font-bold px-4 py-2 flex justify-between items-center">
      <span>{{ title }}</span>
      <button @click="$emit('close')" class="font-bold ml-4">&times;</button>
    </div>
    <div :class="bodyClass" class="px-4 py-3">
      <p>{{ message }}</p>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue"

const props = defineProps({
  type: String,
  title: String,
  message: String
})

defineEmits(["close"])

const headerClass = computed(() => {
  if (props.type === "success") return "bg-blue-600 text-white"
  if (props.type === "error") return "bg-red-600 text-white"
  if (props.type === "info") return "bg-yellow-600 text-white"
})

const bodyClass = computed(() => {
  if (props.type === "success") return "bg-blue-100 text-blue-800"
  if (props.type === "error") return "bg-red-100 text-red-800"
  if (props.type === "info") return "bg-yellow-100 text-yellow-800"
})
</script>