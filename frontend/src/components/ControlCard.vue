<template>
  <div class="bg-white rounded-xl shadow-md p-6 text-center space-y-4">
    <h2 class="text-xl font-semibold">Control Metrics</h2>
    <div class="flex justify-center space-x-4">
      <button
        @click="$emit('start')"
        :disabled="loading.start"
        class="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50 flex items-center justify-center space-x-2"
      >
        <svg v-if="loading.start" class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none"
             viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor"
                d="M4 12a8 8 0 018-8v4l3-3-3-3v4a8 8 0 00-8 8h4l-3 3 3 3H4z"></path>
        </svg>
        <span>Start</span>
      </button>

      <button
        @click="$emit('stop')"
        :disabled="loading.stop"
        class="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 disabled:opacity-50 flex items-center justify-center space-x-2"
      >
        <svg v-if="loading.stop" class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none"
             viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor"
                d="M4 12a8 8 0 018-8v4l3-3-3-3v4a8 8 0 00-8 8h4l-3 3 3 3H4z"></path>
        </svg>
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