<template>
  <div class="bg-white rounded-xl shadow-md p-6">
    <h2 class="text-xl font-semibold mb-2 text-center">Connected Devices</h2>

    <div v-if="!devicesConnected" class="bg-yellow-200 text-yellow-800 p-2 rounded text-center mb-2">
      Devices connection lost. Reconnecting…
    </div>

    <div class="text-sm text-gray-500 mb-2 text-right">
      Last updated: {{ devicesLastUpdated ? devicesLastUpdated.toLocaleTimeString() : '—' }}
    </div>

    <ul class="divide-y divide-gray-200">
      <li v-for="device in devices" :key="device.device_id" class="py-2 flex justify-between text-sm">
        <span class="font-medium">{{ device.name }}</span>
        <span>ID: {{ device.device_id }} | Type: {{ device.device_type }}</span>
      </li>
    </ul>
  </div>
</template>

<script>
export default {
  name: "ConnectedDevices",
  props: {
    devices: { type: Array, required: true },
    devicesLastUpdated: { type: Date, required: false },
    devicesConnected: { type: Boolean, default: true },
  },
};
</script>