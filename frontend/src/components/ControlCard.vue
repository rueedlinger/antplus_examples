<template>
  <div class="bg-white rounded-xl shadow-md p-6 text-center space-y-4">
    <h2 class="text-xl font-semibold">Control Metrics</h2>
    <div class="flex justify-center space-x-4">
      <!-- Start Button -->
      <button
        @click="$emit('start')"
        :disabled="loading.start"
        class="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50 flex items-center justify-center space-x-2"
      >
        <!-- Tailwind Spinner -->
        <div v-if="loading.start" class="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
        <span>Start</span>
      </button>

      <!-- Stop Button -->
      <button
        @click="$emit('stop')"
        :disabled="loading.stop"
        class="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 disabled:opacity-50 flex items-center justify-center space-x-2"
      >
        <!-- Tailwind Spinner -->
        <div v-if="loading.stop" class="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
        <span>Stop</span>
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: "ControlCard",
  props: {
    loading: {
      type: Object,
      required: true
    }
  }
};
</script>