<template>
  <div class="backdrop-blur-lg bg-white/80 rounded-2xl shadow-xl p-6 text-center space-y-6">
    <h2 class="text-2xl font-semibold text-center text-black mb-4">Settings</h2>

    <table class="table-auto w-full text-sm border-separate border-spacing-0 bg-white/30">
      <thead>
        <tr class="bg-gradient-to-r from-purple-500 to-blue-400 text-white">
          <th class="px-2 py-1 text-left border-b border-dashed border-black/30">Setting</th>
          <th class="px-2 py-1 text-left border-b border-dashed border-black/30">Value</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(value, key) in localSettings" :key="key" class="hover:bg-gray-50 transition">
          <td class="px-2 py-1 border-b border-dashed border-black/30 text-left">{{ formatLabel(key) }}</td>
          <td class="px-2 py-1 border-b border-dashed border-black/30">
            <input
              v-if="key !== 'device_ids'"
              v-model.number="localSettings[key]"
              type="number"
              step="0.001"
              min="0"
              :disabled="loading"
              class="border rounded px-2 py-1 w-full bg-white/50"
            />
            <input
              v-else
              v-model="deviceIdsInput"
              type="text"
              :disabled="loading"
              class="border rounded px-2 py-1 w-full bg-white/50"
              placeholder="e.g. 1,2,3"
            />
          </td>
        </tr>
      </tbody>
    </table>

    <div class="flex justify-center mt-4">
      <button
        :disabled="loading"
        class="px-6 py-2 rounded-2xl font-semibold bg-gradient-to-r from-purple-500 to-blue-400 text-white shadow disabled:opacity-50"
        @click="submitSettings"
      >
        <span v-if="!loading">Update Settings</span>
        <span v-else>Updating...</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, computed, onMounted, onUnmounted } from 'vue';
import axios from 'axios';
import { API } from '../config.js';
import { ToastType } from '../constants/toastType.js';

const emit = defineEmits(['show-toast']);
const loading = ref(false);

// -----------------------------
// Reactive settings
// -----------------------------
const localSettings = reactive({
  speed_wheel_circumference_m: null,
  distance_wheel_circumference_m: null,
  age: null,
  device_ids: null,
});

// -----------------------------
// Device IDs computed mapper
// -----------------------------
const deviceIdsInput = computed({
  get() {
    return Array.isArray(localSettings.device_ids)
      ? localSettings.device_ids.join(',')
      : '';
  },
  set(value) {
    const cleaned = value
      .split(',')
      .map(v => v.trim())
      .filter(v => v !== '')   // remove empty values first
      .map(v => Number(v))
      .filter(v => !isNaN(v));

    localSettings.device_ids = cleaned.length ? cleaned : null;
  },
});

// -----------------------------
// Helper to format label
// -----------------------------
function formatLabel(key) {
  return key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
}

// -----------------------------
// Update localSettings safely
// -----------------------------
function updateLocalSettings(data) {
  if (!data) return;
  for (const key in localSettings) {
    if (data[key] !== undefined) {
      if (Array.isArray(data[key])) {
        localSettings[key] = [...data[key]];
      } else {
        localSettings[key] = data[key];
      }
    }
  }
}

// -----------------------------
// Load settings from API
// -----------------------------
async function loadSettings() {
  try {
    const { data } = await axios.get(API.baseUrl + API.endpoints.getSettings);
    updateLocalSettings(data);

    // Save to localStorage for cross-tab sync
    localStorage.setItem('settings_shared', JSON.stringify(data));
  } catch (err) {
    emit('show-toast', {
      message: err.response?.data?.message || err.message || 'Failed to load settings',
      title: 'Error',
      type: ToastType.ERROR,
    });
  }
}

// -----------------------------
// Submit settings
// -----------------------------
async function submitSettings() {
  if (loading.value) return;
  loading.value = true;

  try {
    const payload = {
      ...localSettings,
      device_ids: Array.isArray(localSettings.device_ids) ? [...localSettings.device_ids] : null,
    };

    await axios.post(API.baseUrl + API.endpoints.updateSettings, payload);

    // Update local state and localStorage so other tabs see it
    updateLocalSettings(payload);
    localStorage.setItem('settings_shared', JSON.stringify(payload));

    emit('show-toast', {
      message: 'Settings updated successfully!',
      title: 'Settings',
      type: ToastType.SUCCESS,
    });
  } catch (err) {
    emit('show-toast', {
      message: err.response?.data?.detail || err.response?.data?.message || err.message || 'Failed to update settings',
      title: 'Error',
      type: ToastType.ERROR,
    });
  } finally {
    loading.value = false;
  }
}

// -----------------------------
// Sync across tabs
// -----------------------------
function handleStorageChange(event) {
  if (event.key === 'settings_shared' && event.newValue) {
    try {
      const data = JSON.parse(event.newValue);
      updateLocalSettings(data);
    } catch {}
  }
}

// -----------------------------
// Initial load
// -----------------------------
onMounted(() => {
  // Load cached settings instantly
  const cached = localStorage.getItem('settings_shared');
  if (cached) {
    try {
      const data = JSON.parse(cached);
      updateLocalSettings(data);
    } catch {}
  }

  // Fetch fresh settings from API
  loadSettings();

  window.addEventListener('storage', handleStorageChange);
});

onUnmounted(() => {
  window.removeEventListener('storage', handleStorageChange);
});
</script>