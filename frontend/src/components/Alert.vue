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
import { ToastType } from "../constants/toastType.js"

const props = defineProps({
  type: {
    type: String,
    default: ToastType.SUCCESS
  },
  title: String,
  message: String
})

defineEmits(["close"])

const headerClass = computed(() => {
  switch (props.type) {
    case ToastType.SUCCESS:
      return "bg-blue-600 text-white"
    case ToastType.ERROR:
      return "bg-red-600 text-white"
    case ToastType.INFO:
      return "bg-yellow-600 text-white"
    default:
      return "bg-gray-600 text-white"
  }
})

const bodyClass = computed(() => {
  switch (props.type) {
    case ToastType.SUCCESS:
      return "bg-blue-100 text-blue-800"
    case ToastType.ERROR:
      return "bg-red-100 text-red-800"
    case ToastType.INFO:
      return "bg-yellow-100 text-yellow-800"
    default:
      return "bg-gray-100 text-gray-800"
  }
})
</script>