<template>
  <div class="bg-white rounded-xl shadow-md p-6">
    <h1 class="text-2xl font-bold mb-2 text-center">Live Metrics</h1>

    <div v-if="!metricsConnected" class="bg-yellow-200 text-yellow-800 p-2 rounded text-center mb-2">
      Metrics connection lost. Reconnecting…
    </div>

    <div class="text-sm text-gray-500 mb-2 text-right">
      Last updated: {{ metricsLastUpdated ? metricsLastUpdated.toLocaleTimeString() : '—' }}
    </div>

    <table class="table-auto w-full text-sm border-collapse border border-gray-300">
      <thead>
        <tr class="bg-gray-200">
          <th class="border border-gray-300 px-4 py-2">Metric</th>
          <th class="border border-gray-300 px-4 py-2">Value</th>
        </tr>
      </thead>
      <tbody>
        <MetricRow
          v-for="(value, key) in metrics"
          :key="key"
          :label="key"
          :value="value"
        />
      </tbody>
    </table>
  </div>
</template>

<script>
import MetricRow from "./MetricRow.vue";

export default {
  name: "LiveMetrics",
  components: { MetricRow },
  props: {
    metrics: { type: Object, required: true },
    metricsLastUpdated: { type: Date, required: false },
    metricsConnected: { type: Boolean, default: true },
  },
};
</script>