// src/config.js
export const API = {
  baseUrl: "http://127.0.0.1:8000", // e.g., "http://localhost:5000" or leave empty for same-origin

  endpoints: {
    startMetrics: "/metrics/start",
    stopMetrics: "/metrics/stop",
    getSettings: "/metrics/settings",
    updateSettings: "/metrics/settings",
    metricsStream: "/metrics/stream",
    devicesStream: "/metrics/devices/stream"
  }
};