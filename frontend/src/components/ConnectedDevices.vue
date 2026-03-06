<template>
  <div
    class="backdrop-blur-lg bg-white/20 border border-white/20 rounded-2xl p-6 shadow-xl space-y-4"
  >
    <div class="flex items-center justify-between">
      <h1 class="text-xl font-bold text-black">Connected Devices</h1>
      <div class="text-xs text-gray-500">
        {{ lastUpdated ? lastUpdated.toLocaleTimeString() : '—' }}
      </div>
    </div>

    <div v-if="connected" class="overflow-x-auto rounded-lg shadow-inner">
      <table class="table-auto w-full text-sm border-separate border-spacing-0 bg-white/30">
        <thead>
          <tr class="bg-gradient-to-r from-purple-500 to-blue-400 text-white">
            <th class="px-2 py-1 text-left">Device</th>
            <th class="px-2 py-1 text-left">ID</th>
            <th class="px-2 py-1 text-left">Type</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="device in devices" :key="device.id">
            <td class="px-2 py-1 border-b border-dashed border-black/30">{{ device.name }}</td>
            <td class="px-2 py-1 border-b border-dashed border-black/30">{{ device.device_id }}</td>
            <td class="px-2 py-1 border-b border-dashed border-black/30">
              {{ device.device_type }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <div v-else class="p-4 bg-red-100 text-red-600 rounded-lg">Not connected</div>
  </div>
</template>

<script setup>
import { useDevicesStream } from '../composables/singletonStreams.js';

const { devices, lastUpdated, connected } = useDevicesStream();
</script>
