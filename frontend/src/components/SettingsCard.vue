<template>
  <div class="bg-white rounded-xl shadow-md p-6 space-y-4">
    <h2 class="text-xl font-semibold text-center">Settings</h2>
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div>
        <label class="text-sm font-medium">Speed Wheel Circumference (m)</label>
        <input
          type="number"
          step="0.001"
          min="0"
          v-model.number="localSettings.speed_wheel_circumference_m"
          class="border rounded px-2 py-1 w-full"
        />
      </div>
      <div>
        <label class="text-sm font-medium">Distance Wheel Circumference (m)</label>
        <input
          type="number"
          step="0.001"
          min="0"
          v-model.number="localSettings.distance_wheel_circumference_m"
          class="border rounded px-2 py-1 w-full"
        />
      </div>
      <div>
        <label class="text-sm font-medium">Age</label>
        <input
          type="number"
          min="1"
          v-model.number="localSettings.age"
          class="border rounded px-2 py-1 w-full"
        />
      </div>
    </div>

    <div class="text-center">
      <button
        @click="submitSettings"
        :disabled="loading"
        class="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 flex items-center justify-center space-x-2"
      >
        <!-- Tailwind spinner -->
        <div
          v-if="loading"
          class="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"
        ></div>
        <span>Update Settings</span>
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: "SettingsCard",
  props: {
    settings: { type: Object, required: true },
    loading: { type: Boolean, default: false }
  },
  data() {
    return {
      localSettings: { ...this.settings } // copy props for editing
    };
  },
  watch: {
    settings: {
      deep: true,
      handler(newSettings) {
        this.localSettings = { ...newSettings };
      }
    }
  },
  methods: {
    submitSettings() {
      this.$emit("update-settings", { ...this.localSettings });
    }
  }
};
</script>