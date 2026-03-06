// src/composables/singletonStreams.js
import { ref, reactive } from 'vue';
import { API } from '../config.js';

const tabId = Math.random().toString(36).slice(2);

/* ------------------------
   Metrics Singleton
------------------------ */
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
const metricsConnected = ref(false);
const metricsLastUpdated = ref(null);
let metricsSource = null;
let metricsChannel = null;

function initMetricsStream() {
  if (metricsSource) return; // already initialized

  metricsChannel = new BroadcastChannel('sse-metrics');
  metricsChannel.onmessage = (ev) => {
    if (ev.data.tabId !== tabId) Object.assign(metrics, ev.data.metrics);
    metricsLastUpdated.value = new Date();
    metricsConnected.value = true;
  };

  metricsSource = new EventSource(API.baseUrl + API.endpoints.metricsStream);
  metricsSource.onopen = () => (metricsConnected.value = true);

  metricsSource.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      Object.assign(metrics, data);
      metricsLastUpdated.value = new Date();
      metricsConnected.value = true;

      metricsChannel.postMessage({ tabId, metrics: data });
    } catch (err) {
      console.warn('Metrics SSE parse error', err);
    }
  };

  metricsSource.onerror = () => {
    metricsConnected.value = false;
    metricsSource.close();
    metricsSource = null;
    setTimeout(initMetricsStream, 2000);
  };
}

/* ------------------------
   Devices Singleton
------------------------ */
const devices = ref([]);
const devicesConnected = ref(false);
const devicesLastUpdated = ref(null);
let devicesSource = null;
let devicesChannel = null;

function initDevicesStream() {
  if (devicesSource) return;

  devicesChannel = new BroadcastChannel('sse-devices');
  devicesChannel.onmessage = (ev) => {
    if (ev.data.tabId !== tabId && Array.isArray(ev.data.devices)) {
      devices.value = ev.data.devices;
      devicesLastUpdated.value = new Date(ev.data.lastUpdated);
      devicesConnected.value = ev.data.connected;
    }
  };

  devicesSource = new EventSource(API.baseUrl + API.endpoints.devicesStream);
  devicesSource.onopen = () => (devicesConnected.value = true);

  devicesSource.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      if (!Array.isArray(data)) return;
      devices.value = data;
      devicesLastUpdated.value = new Date();
      devicesConnected.value = true;

      devicesChannel.postMessage({
        tabId,
        devices: data,
        lastUpdated: devicesLastUpdated.value,
        connected: devicesConnected.value,
      });
    } catch (err) {
      console.warn('Devices SSE parse error', err);
    }
  };

  devicesSource.onerror = () => {
    devicesConnected.value = false;
    devicesSource.close();
    devicesSource = null;
    setTimeout(initDevicesStream, 2000);
  };
}

/* ------------------------
   Workout Singleton
------------------------ */
const workout = reactive({
  interval: { seconds: null, name: null },
  time_spent: null,
  time_remaining: null,
  total_time_spent: null,
  round_number: null,
  is_running: null,
});
const workoutConnected = ref(false);
const workoutLastUpdated = ref(null);
let workoutSource = null;
let workoutChannel = null;

function initWorkoutStream() {
  if (workoutSource) return;

  workoutChannel = new BroadcastChannel('sse-workout');
  workoutChannel.onmessage = (ev) => {
    if (ev.data.tabId !== tabId && ev.data.workout) {
      Object.assign(workout, ev.data.workout);
      workoutLastUpdated.value = new Date();
      workoutConnected.value = true;
    }
  };

  workoutSource = new EventSource(API.baseUrl + API.endpoints.workoutStream);
  workoutSource.onopen = () => (workoutConnected.value = true);

  workoutSource.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);

      // Ensure interval object always exists
      workout.interval = {
        seconds: data.interval?.seconds ?? null,
        name: data.interval?.name ?? null,
      };

      // Merge the rest of the workout data
      Object.assign(workout, { ...data, interval: workout.interval });

      workoutLastUpdated.value = new Date();
      workoutConnected.value = true;

      // Broadcast to other tabs
      workoutChannel.postMessage({ tabId, workout: data });
    } catch (err) {
      console.warn('Workout SSE parse error', err);
    }
  };

  workoutSource.onerror = () => {
    workoutConnected.value = false;
    workoutSource.close();
    workoutSource = null;
    setTimeout(initWorkoutStream, 2000);
  };
}

/* ------------------------
   Export composables
------------------------ */
export function useMetricsStream() {
  initMetricsStream();
  return { metrics, connected: metricsConnected, lastUpdated: metricsLastUpdated };
}

export function useDevicesStream() {
  initDevicesStream();
  return { devices, connected: devicesConnected, lastUpdated: devicesLastUpdated };
}

export function useWorkoutStream() {
  initWorkoutStream();
  return { workout, connected: workoutConnected, lastUpdated: workoutLastUpdated };
}