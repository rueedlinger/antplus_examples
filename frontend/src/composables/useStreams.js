// src/composables/useStreams.js
import { ref, reactive, onMounted, onUnmounted } from 'vue';
import { API } from '../config.js';

/* =========================================================
   Reusable SSE Helper
========================================================= */

function createSSEStream(url, onData, options = {}) {
  const { heartbeatMs = 5000, reconnectDelay = 2000 } = options;

  const connected = ref(false);
  const lastUpdated = ref(null);

  let source = null;
  let heartbeatTimeout = null;
  let reconnectTimeout = null;

  function clearTimers() {
    clearTimeout(heartbeatTimeout);
    clearTimeout(reconnectTimeout);
  }

  function resetHeartbeat() {
    clearTimeout(heartbeatTimeout);
    heartbeatTimeout = setTimeout(() => {
      connected.value = false;
      source?.close();
      scheduleReconnect();
    }, heartbeatMs);
  }

  function scheduleReconnect() {
    if (reconnectTimeout) return;
    reconnectTimeout = setTimeout(() => {
      reconnectTimeout = null;
      connect();
    }, reconnectDelay);
  }

  function connect() {
    clearTimers();
    if (source) source.close();

    source = new EventSource(url);

    source.onopen = () => {
      connected.value = true;
      resetHeartbeat();
    };

    source.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        onData(data);
        lastUpdated.value = new Date();
        connected.value = true;
        resetHeartbeat();
      } catch (err) {
        console.warn('SSE parse error:', err);
      }
    };

    source.onerror = () => {
      connected.value = false;
      source?.close();
      scheduleReconnect();
    };
  }

  onMounted(connect);

  onUnmounted(() => {
    clearTimers();
    source?.close();
  });

  return { connected, lastUpdated };
}

/* =========================================================
   METRICS STREAM
========================================================= */

export function useMetricsStream() {
  // Predefine all expected keys to ensure reactivity
  const metrics = reactive({
    power: null,
    ma_power: null,
    speed: null,
    ma_speed: null,
    cadence: null,
    ma_cadence: null,
    distance: null,
    ma_distance: null,
    heart_rate: null,
    ma_heart_rate: null,
    heart_rate_percent: null,
    ma_heart_rate_percent: null,
    zone_name: null,
    zone_description: null,
    ma_zone_name: null,
    ma_zone_description: null,
    is_running: null,
    last_sensor_update: null,
    last_sensor_name: null,
  });

  const { connected, lastUpdated } = createSSEStream(
    API.baseUrl + API.endpoints.metricsStream,
    (data) => Object.assign(metrics, data)
  );

  return { metrics, connected, lastUpdated };
}

/* =========================================================
   DEVICES STREAM
========================================================= */

export function useDevicesStream() {
  const devices = ref([]);

  const { connected, lastUpdated } = createSSEStream(
    API.baseUrl + API.endpoints.devicesStream,
    (data) => {
      devices.value = Array.isArray(data) ? data : [];
    }
  );

  return { devices, connected, lastUpdated };
}

/* =========================================================
   WORKOUT STREAM
========================================================= */

export function useWorkoutStream() {
  const workout = reactive({
    // Predefine all expected keys to ensure reactivity
    interval: { seconds: null, name: null },
    time_spent: null,
    time_remaining: null,
    total_time_spent: null,
    round_number: null,
    is_running: null,
  });

  const { connected, lastUpdated } = createSSEStream(
    API.baseUrl + API.endpoints.workoutStream,
    (data) => {
      // Merge interval object separately to ensure reactivity
      if (data.interval) {
        workout.interval.seconds = data.interval.seconds ?? null;
        workout.interval.name = data.interval.name ?? null;
      }
      Object.assign(workout, { ...data, interval: workout.interval });
    }
  );

  return { workout, connected, lastUpdated };
}