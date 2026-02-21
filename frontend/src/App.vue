<template>
  <div class="bg-gray-100 min-h-screen p-4 max-w-5xl mx-auto space-y-6">

    <!-- Floating Toasts -->
    <div class="fixed top-4 right-4 space-y-2 z-50">
      <Alert
        v-for="(toast, index) in toasts"
        :key="index"
        :type="toast.type"
        :title="toast.title"
        :message="toast.message"
        @close="removeToast(index)"
      />
    </div>
    <!-- Control Card -->
    <div class="bg-white rounded-xl shadow-md p-6 text-center space-y-4">
      <h2 class="text-xl font-semibold">Control Metrics</h2>
      <div class="flex justify-center space-x-4">
        <button
          @click="startMetrics"
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
          @click="stopMetrics"
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

    <!-- Settings Card -->
    <SettingsCard
      :settings="settings"
      :loading="loading.updateSettings"
      @update-settings="updateSettings"
    />

    <!-- Live Metrics Table -->
    <LiveMetrics
      :metrics="metrics"
      :metricsLastUpdated="metricsLastUpdated"
      :metricsConnected="metricsConnected"
    />

    <!-- Devices Table -->
    <ConnectedDevices
      :devices="devices"
      :devicesLastUpdated="devicesLastUpdated"
      :devicesConnected="devicesConnected"
    />

    <!-- Footer -->
<footer class="bg-gray-200 text-gray-700 text-center py-4 mt-6 rounded-xl shadow-inner">
  <p>
    Documentation: 
    <a 
      :href="API.baseUrl + '/docs'" 
      target="_blank" 
      class="text-blue-600 hover:underline"
    >
      Go to Docs
    </a>
  </p>
</footer>

  </div>
</template>

<script>
import Alert from "./components/Alert.vue";
import ConnectedDevices from "./components/ConnectedDevices.vue";
import LiveMetrics from "./components/LiveMetrics.vue";
import MetricRow from "./components/MetricRow.vue";
import SettingsCard from "./components/SettingsCard.vue";
import { API } from "./config.js";
import axios from "axios";
import { ToastType } from "./constants/toastType.js";


export default {
  name: "App",
  components: { Alert, MetricRow, LiveMetrics, ConnectedDevices, SettingsCard},

  data() {
    return {
      API,
      metrics: {
        power: null,
        speed: null,
        cadence: null,
        distance: null,
        heart_rate: null,
        heart_rate_percent: null,
        zone_name: null,        
        zone_description: null,        
        is_running: null
      },
      metricsLastUpdated: null,
      metricsConnected: true,
      devices: [],
      devicesLastUpdated: null,
      devicesConnected: true,
      settings: {
        speed_wheel_circumference_m: null,
        distance_wheel_circumference_m: null,
        age: null
      },
      lastValidSettings: {},
      metricsSource: null,
      devicesSource: null,
      toasts: [],
      loading: { start: false, stop: false, updateSettings: false }
    };
  },

  methods: {
    showToast(message, title, type = ToastType.SUCCESS) {      
      this.toasts.push({ message, title, type });
      setTimeout(() => this.toasts.shift(), 2000);
    },

    removeToast(index) {
      this.toasts.splice(index, 1);
    },

    // --- REST API ---
    async startMetrics() {
      if (this.loading.start) return;
      this.loading.start = true;
      try {
        const { data } = await axios.post(API.baseUrl + API.endpoints.startMetrics);
        this.showToast(data.message || "Metrics started", "Metrics Started", ToastType.SUCCESS);
      } catch (err) {
        this.showToast(err.response?.data?.message || err.message || "Network error", "Error Starting Metrics", ToastType.ERROR);
      } finally {
        this.loading.start = false;
      }
    },

    async stopMetrics() {
      if (this.loading.stop) return;
      this.loading.stop = true;
      //this.showToast("Stopping metrics...", "info", "Stop");
      try {
        const { data } = await axios.post(API.baseUrl + API.endpoints.stopMetrics);
        this.showToast(data.message || "Metrics stopped", "Metrics Stopped", ToastType.SUCCESS);
      } catch (err) {
        this.showToast(err.response?.data?.message || err.message || "Network error", "Error Stopping Metrics", ToastType.ERROR);
      } finally {
        this.loading.stop = false;
      }
    },

    async updateSettings(newSettings) {
      if (this.loading.updateSettings) return;
      this.loading.updateSettings = true;
      // this.showToast("Updating settings...", "info", "Update Settings");
      try {
        const { data } = await axios.post(
          API.baseUrl + API.endpoints.updateSettings,
          newSettings
        );
        // Replace parent settings reactively
        this.settings = { ...newSettings };
        this.lastValidSettings = { ...newSettings };
        this.showToast(data.message || "Settings updated", "Settings Updated", ToastType.SUCCESS);
      } catch (err) {
        // Revert to last valid settings
        this.settings = { ...this.lastValidSettings };
        this.showToast(err.response?.data?.message || err.message || "Network error", "Error Updating Settings", ToastType.ERROR);
      } finally {
        this.loading.updateSettings = false;
      }
    },

    async loadSettings() {
      try {
        const { data } = await axios.get(API.baseUrl + API.endpoints.getSettings);
        this.settings = data;
        
        this.lastValidSettings = { ...data };
      } catch (err) {
        console.warn("Failed to load settings:", err);
      }
    },

    // --- SSE ---
    connectMetricsStream() {
      if (this.metricsSource) {
        this.metricsSource.close();
        this.metricsSource = null;
      }

      const connect = () => {
        this.metricsSource = new EventSource(API.baseUrl + API.endpoints.metricsStream);

        this.metricsSource.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            Object.keys(this.metrics).forEach((key) => {
              this.metrics[key] = data[key];
            });
            this.metricsLastUpdated = new Date();
            this.metricsConnected = true;
          } catch (err) {
            console.warn("Metrics SSE parse error:", err);
          }
        };

        this.metricsSource.onerror = () => {
          this.metricsConnected = false;
          console.warn("Metrics SSE disconnected. Retrying in 2s...");
          if (this.metricsSource) {
            this.metricsSource.close();
            this.metricsSource = null;
          }
          setTimeout(connect, 2000);
        };
      };

      connect();
    },

    connectDevicesStream() {
      if (this.devicesSource) {
        this.devicesSource.close();
        this.devicesSource = null;
      }

      const connect = () => {
        this.devicesSource = new EventSource(API.baseUrl + API.endpoints.devicesStream);

        this.devicesSource.onmessage = (event) => {
          try {
            this.devices = JSON.parse(event.data);
            this.devicesLastUpdated = new Date();
            this.devicesConnected = true;
          } catch (err) {
            console.warn("Devices SSE parse error:", err);
          }
        };

        this.devicesSource.onerror = () => {
          this.devicesConnected = false;
          console.warn("Devices SSE disconnected. Retrying in 2s...");
          if (this.devicesSource) {
            this.devicesSource.close();
            this.devicesSource = null;
          }
          setTimeout(connect, 2000);
        };
      };

      connect();
    }
  },

  mounted() {
    this.loadSettings();
    this.connectMetricsStream();
    this.connectDevicesStream();
  }
};
</script>