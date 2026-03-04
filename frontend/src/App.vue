<template>
  <div class="min-h-screen w-full bg-gray-100 flex flex-col items-center p-4 md:p-6">
    <div class="w-full max-w-7xl space-y-6">
      <!-- Floating Toasts -->
      <div class="fixed top-6 right-6 space-y-3 z-50">
        <AlertCard
          v-for="(toast, index) in toasts"
          :key="index"
          :type="toast.type"
          :title="toast.title"
          :message="toast.message"
          class="backdrop-blur-lg bg-white/90 shadow-xl rounded-2xl border border-white/20 p-4 text-sm md:text-base"
          @close="removeToast(index)"
        />
      </div>

      <!-- Tabs -->
      <div class="border-b border-gray-300">
        <nav class="-mb-px flex flex-wrap justify-start gap-2 md:gap-4">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            @click="activeTab = tab.id"
            :class="[
              'whitespace-nowrap py-2 px-3 md:py-3 md:px-4 border-b-4 font-semibold text-sm md:text-base rounded-t-lg transition-all',
              activeTab === tab.id
                ? 'border-gradient-to-r from-purple-500 to-blue-400 text-purple-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300',
            ]"
          >
            {{ tab.label }}
          </button>
        </nav>
      </div>

      <!-- Tab Content -->
      <div>
        <transition name="fade" mode="out-in">
          <!-- Main Tab -->
          <div v-if="activeTab === 'main'" key="main" class="space-y-6">
            <ControlCard
              class="w-full bg-white/90 border border-white/20 rounded-2xl p-4 md:p-6 shadow-xl shadow-inner"
              @show-toast="showToast($event.message, $event.title, $event.type)"
            />

            <LiveMetrics
              class="w-full bg-white/90 border border-white/20 rounded-2xl p-4 md:p-6 shadow-xl shadow-inner overflow-x-auto"
            />

            <ConnectedDevices
              class="w-full bg-white/90 border border-white/20 rounded-2xl p-4 md:p-6 shadow-xl shadow-inner overflow-x-auto"
            />
          </div>

          <!-- Settings Tab -->
          <SettingsCard
            v-else-if="activeTab === 'settings'"
            key="settings"
            class="w-full bg-white/90 border border-white/20 rounded-2xl p-4 md:p-6 shadow-xl shadow-inner"
            @show-toast="showToast($event.message, $event.title, $event.type)"
          />

          <!-- Workout Tab -->
          <WorkoutCard
            v-else-if="activeTab === 'workout'"
            key="workout"
            class="w-full bg-white/90 border border-white/20 rounded-2xl p-4 md:p-6 shadow-xl shadow-inner"
            @show-toast="showToast($event.message, $event.title, $event.type)"
          />
        </transition>
      </div>

      <!-- Footer -->

      <footer class="text-gray-600 text-center text-xs md:text-sm py-3 md:py-4 mt-6 md:mt-8">
        <p>
          Doc:
          <a
            :href="API.baseUrl + '/docs'"
            target="_blank"
            class="underline font-semibold hover:text-gray-800"
          >
            OpenAPI</a
          >

          GitHub:
          <a
            href="https://github.com/rueedlinger/amwa"
            target="_blank"
            class="underline font-semibold hover:text-gray-800"
          >
            amwa
          </a>
        </p>
      </footer>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import AlertCard from './components/AlertCard.vue';
import ConnectedDevices from './components/ConnectedDevices.vue';
import LiveMetrics from './components/LiveMetrics.vue';
import SettingsCard from './components/SettingsCard.vue';
import ControlCard from './components/ControlCard.vue';
import WorkoutCard from './components/WorkoutCard.vue';
import { API } from './config.js';
import { ToastType } from './constants/toastType.js';

const activeTab = ref('main');

const tabs = [
  { id: 'main', label: 'Main' },
  { id: 'settings', label: 'Settings' },
  { id: 'workout', label: 'Workout' },
];

const toasts = ref([]);

function showToast(message, title, type = ToastType.SUCCESS) {
  toasts.value.push({ message, title, type });
  setTimeout(() => toasts.value.shift(), 3000);
}

function removeToast(index) {
  toasts.value.splice(index, 1);
}
</script>
