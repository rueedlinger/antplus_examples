export const API = {
  baseUrl: import.meta.env.VITE_API_BASE_URL || "",

  endpoints: {
    startMetrics: "/metrics/start",
    stopMetrics: "/metrics/stop",
    getSettings: "/metrics/settings",
    updateSettings: "/metrics/settings",
    metricsStream: "/metrics/stream",
    devicesStream: "/metrics/devices/stream"
  }
};