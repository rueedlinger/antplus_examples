<template>
  <div class="backdrop-blur-lg bg-white/80 rounded-2xl shadow-xl p-6 text-center space-y-6">
    <h1 class="text-2xl font-bold text-gray-800">Main</h1>

    <!-- ================= FULL WORKOUT TABLE ================= -->
    <div class="overflow-x-auto rounded-lg shadow-inner">
      <table class="table-auto w-full text-sm border-separate border-spacing-0 bg-white/30">
        <thead>
          <tr class="bg-gradient-to-r from-purple-500 to-blue-400 text-white">
            <th class="px-2 py-1 text-left border-b border-dashed border-black/30">
              Sensor Metrics Status
            </th>
            <th class="px-2 py-1 text-left border-b border-dashed border-black/30">
              Workout Status
            </th>
            <th class="px-2 py-1 text-left border-b border-dashed border-black/30">
              Current Interval
            </th>
            <th class="px-2 py-1 text-left border-b border-dashed border-black/30">
              Time Remaining Interval
            </th>
            <th class="px-2 py-1 text-left border-b border-dashed border-black/30">
              Time Spent Interval
            </th>
            <th class="px-2 py-1 text-left border-b border-dashed border-black/30">
              Total Time Spent
            </th>
            <th class="px-2 py-1 text-left border-b border-dashed border-black/30">Round</th>
          </tr>
        </thead>
        <tbody>
          <tr class="hover:bg-gray-50 transition">
            <td class="px-2 py-1 text-left border-b border-dashed border-black/30">
              <span :class="metrics.is_running ? 'text-blue-500 font-semibold' : 'text-pink-500 font-semibold'">
                {{ metrics.is_running ? 'Running' : 'Stopped' }}
              </span>
            </td>
            <td class="px-2 py-1 text-left border-b border-dashed border-black/30">
              <span :class="workout.is_running ? 'text-blue-500 font-semibold' : 'text-pink-500 font-semibold'">
                {{ workout.is_running ? 'Running' : 'Stopped' }}
              </span>
            </td>
            <td class="px-2 py-1 border-b border-dashed border-black/30 font-semibold">
              {{ workout.interval?.name ?? '-' }} ({{ workout.interval?.seconds ?? '-' }} s)
            </td>
            <td class="px-2 py-1 border-b border-dashed border-black/30">
              {{ formatTime(workout.time_remaining) }}
            </td>
            <td class="px-2 py-1 border-b border-dashed border-black/30">
              {{ formatTime(workout.time_spent) }}
            </td>
            <td class="px-2 py-1 border-b border-dashed border-black/30">
              {{ formatTime(workout.total_time_spent) }}
            </td>
            <td class="px-2 py-1 border-b border-dashed border-black/30">
              {{ workout.round_number ?? '-' }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- ================= BUTTONS ================= -->
    <div class="flex justify-center gap-4 flex-wrap">
      <!-- Metrics Toggle -->
      <button
        :disabled="loadingMetrics"
        @click="toggleMetrics"
        :class="[
          baseBtnClass,
          metrics.is_running
            ? 'bg-gradient-to-r from-red-500 to-pink-500'
            : 'bg-gradient-to-r from-purple-500 to-blue-400',
        ]"
      >
        <div v-if="loadingMetrics" class="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
        <span>{{ metrics.is_running ? 'Stop' : 'Start' }} Sensor Scanning...</span>
      </button>

      <!-- Workout Toggle -->
      <button
        :disabled="loadingWorkout"
        @click="toggleWorkout"
        :class="[
          baseBtnClass,
          workout.is_running
            ? 'bg-gradient-to-r from-red-500 to-pink-500'
            : 'bg-gradient-to-r from-purple-500 to-blue-400',
        ]"
      >
        <div v-if="loadingWorkout" class="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
        <span>{{ workout.is_running ? 'Stop' : 'Start' }} Workout</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue';
import axios from 'axios';
import { API } from '../config.js';
import { ToastType } from '../constants/toastType.js';
import { useMetricsStream, useWorkoutStream } from '../composables/singletonStreams.js';

const emit = defineEmits(['show-toast']);

/* ---------------- COMMON BUTTON STYLE ---------------- */
const baseBtnClass =
  'px-6 py-3 rounded-2xl font-semibold text-white shadow-lg hover:shadow-xl disabled:opacity-50 flex items-center justify-center space-x-2 transition-all duration-300';

/* ---------------- METRICS ---------------- */
const { metrics } = useMetricsStream();
const loadingMetrics = ref(false);

async function toggleMetrics() {
  if (loadingMetrics.value) return;
  loadingMetrics.value = true;

  try {
    const endpoint = metrics.is_running ? API.endpoints.stopMetrics : API.endpoints.startMetrics;
    const { data } = await axios.post(API.baseUrl + endpoint);

    // Immediately update singleton reactive state for all tabs
    metrics.is_running = !metrics.is_running;

    emit('show-toast', {
      message: data.message || (metrics.is_running ? 'Metrics started' : 'Metrics stopped'),
      title: metrics.is_running ? 'Started' : 'Stopped',
      type: ToastType.SUCCESS,
    });
  } catch (err) {
    emit('show-toast', {
      message: err.response?.data?.detail || err.message || 'Network error',
      title: 'Error',
      type: ToastType.ERROR,
    });
  } finally {
    loadingMetrics.value = false;
  }
}

/* ---------------- WORKOUT ---------------- */
const { workout } = useWorkoutStream();
const loadingWorkout = ref(false);

async function toggleWorkout() {
  if (loadingWorkout.value) return;
  loadingWorkout.value = true;

  try {
    const endpoint = workout.is_running ? API.endpoints.stopWorkout : API.endpoints.startWorkout;
    const { data } = await axios.post(API.baseUrl + endpoint);

    // Immediately update singleton reactive state for all tabs
    workout.is_running = !workout.is_running;

    emit('show-toast', {
      message: data.message || (workout.is_running ? 'Workout started' : 'Workout stopped'),
      title: workout.is_running ? 'Started' : 'Stopped',
      type: ToastType.SUCCESS,
    });
  } catch (err) {
    emit('show-toast', {
      message: err.response?.data?.detail || err.message || 'Network error',
      title: 'Error',
      type: ToastType.ERROR,
    });
  } finally {
    loadingWorkout.value = false;
  }
}

/* ---------------- FORMAT TIME ---------------- */
function formatTime(value) {
  if (value == null) return '-';
  const totalSeconds = Math.round(Number(value));
  const h = Math.floor(totalSeconds / 3600);
  const m = Math.floor((totalSeconds % 3600) / 60);
  const s = totalSeconds % 60;
  return `${String(h).padStart(2,'0')}:${String(m).padStart(2,'0')}:${String(s).padStart(2,'0')}`;
}
</script>