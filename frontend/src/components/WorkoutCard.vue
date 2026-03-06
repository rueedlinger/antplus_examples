<template>
  <div class="backdrop-blur-lg bg-white/80 rounded-2xl shadow-xl p-6 space-y-6">
    <h2 class="text-2xl font-semibold text-center text-black">Workout Intervals</h2>

    <div v-if="intervals.length === 0" class="text-gray-500 text-center">
      No intervals yet.
    </div>

    <table v-else class="table-auto w-full text-sm border-separate border-spacing-0 bg-white/30">
      <thead>
        <tr class="bg-gradient-to-r from-purple-500 to-blue-400 text-white">
          <th class="px-2 py-1 text-left border-b border-dashed border-black/30">Name</th>
          <th class="px-2 py-1 text-left border-b border-dashed border-black/30">HH</th>
          <th class="px-2 py-1 text-left border-b border-dashed border-black/30">MM</th>
          <th class="px-2 py-1 text-left border-b border-dashed border-black/30">SS</th>
          <th class="px-2 py-1 text-left border-b border-dashed border-black/30">Actions</th>
        </tr>
      </thead>

      <tbody>
        <tr v-for="(interval, index) in intervals" :key="index" class="hover:bg-gray-50 transition">

          <td class="px-2 py-1 border-b border-dashed border-black/30">
            <input
              v-model="interval.name"
              type="text"
              placeholder="Interval Name"
              class="w-full rounded px-2 py-1 bg-white/50 border border-black/100 text-black placeholder-black/50 focus:ring-2 focus:ring-purple-400 focus:border-transparent"
              :disabled="loading"
            />
          </td>

          <td class="px-2 py-1 border-b border-dashed border-black/30">
            <input
              v-model.number="interval.hours"
              type="number"
              min="0"
              class="w-16 text-center rounded px-1 py-1 bg-white/50 border border-black/100 text-black shadow-inner"
              :disabled="loading"
              @input="updateSeconds(interval)"
            />
          </td>

          <td class="px-2 py-1 border-b border-dashed border-black/30">
            <input
              v-model.number="interval.minutes"
              type="number"
              min="0"
              max="59"
              class="w-16 text-center rounded px-1 py-1 bg-white/50 border border-black/100 text-black shadow-inner"
              :disabled="loading"
              @input="updateSeconds(interval)"
            />
          </td>

          <td class="px-2 py-1 border-b border-dashed border-black/30">
            <input
              v-model.number="interval.secondsInput"
              type="number"
              min="0"
              max="59"
              class="w-16 text-center rounded px-1 py-1 bg-white/50 border border-black/100 text-black shadow-inner"
              :disabled="loading"
              @input="updateSeconds(interval)"
            />
          </td>

          <td class="px-2 py-1 border-b border-dashed border-black/30">
            <button
              :disabled="loading"
              class="bg-gradient-to-r from-purple-500 to-blue-400 text-white px-3 py-1 rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 disabled:opacity-50"
              @click="removeInterval(index)"
            >
              ✕
            </button>
          </td>

        </tr>
      </tbody>
    </table>

    <div class="flex gap-4 pt-4 flex-wrap justify-center">

      <button
        :disabled="loading"
        class="bg-gradient-to-r from-purple-500 to-blue-400 text-white px-4 py-2 rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 disabled:opacity-50"
        @click="addInterval"
      >
        Add Interval
      </button>

      <button
        :disabled="loading"
        class="bg-gradient-to-r from-purple-500 to-blue-400 text-white px-4 py-2 rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 flex items-center gap-2 disabled:opacity-50"
        @click="submitWorkout"
      >
        <div
          v-if="loading"
          class="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"
        ></div>

        <span>{{ loading ? 'Saving...' : 'Save Workout' }}</span>
      </button>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import axios from 'axios'
import { API } from '../config.js'
import { ToastType } from '../constants/toastType.js'

const emit = defineEmits(['update-workout','show-toast'])

const loading = ref(false)
const intervals = ref([])

const STORAGE_KEY = "workout_shared"

function initInterval(i){

  const h = Math.floor(i.seconds / 3600)
  const m = Math.floor((i.seconds % 3600) / 60)
  const s = i.seconds % 60

  return {
    ...i,
    hours:h,
    minutes:m,
    secondsInput:s
  }

}

function updateSeconds(interval){

  interval.seconds =
    interval.hours * 3600 +
    interval.minutes * 60 +
    interval.secondsInput

}

function addInterval(){

  intervals.value.push({
    name:'',
    hours:0,
    minutes:0,
    secondsInput:0,
    seconds:0
  })

}

function removeInterval(index){
  intervals.value.splice(index,1)
}

function isValid(){

  return intervals.value.every(
    i => i.name.trim().length > 0 && i.seconds > 0
  )

}

function updateLocal(data){

  intervals.value =
    (Array.isArray(data) ? data : [])
      .map(initInterval)

}

/* ================= LOAD ================= */

async function loadWorkout(){

  try{

    const res = await axios.get(
      API.baseUrl + API.endpoints.getWorkout
    )

    updateLocal(res.data)

    localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify(res.data)
    )

  }
  catch(err){

    emit('show-toast',{
      message:
        err.response?.data?.message ||
        err.message ||
        'Failed to load workout',
      title:'Error',
      type:ToastType.ERROR
    })

  }

}

/* ================= SUBMIT ================= */

async function submitWorkout(){

  if(!isValid()){

    emit('show-toast',{
      message:'Each interval must have a name and time > 0',
      title:'Invalid Input',
      type:ToastType.ERROR
    })

    return

  }

  loading.value = true

  try{

    const payload = intervals.value.map(i => ({
      name:i.name,
      seconds:i.seconds
    }))

    const res = await axios.post(
      API.baseUrl + API.endpoints.setWorkout,
      payload
    )

    updateLocal(res.data ?? payload)

    localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify(res.data ?? payload)
    )

    emit('update-workout',intervals.value)

    emit('show-toast',{
      message:'Workout saved successfully!',
      title:'Workout',
      type:ToastType.SUCCESS
    })

  }
  catch(err){

    emit('show-toast',{
      message:
        err.response?.data?.detail ||
        err.message ||
        'Failed to save workout',
      title:'Error',
      type:ToastType.ERROR
    })

  }
  finally{

    loading.value = false

  }

}

/* ================= TAB SYNC ================= */

function handleStorage(e){

  if(e.key === STORAGE_KEY && e.newValue){

    try{

      const data = JSON.parse(e.newValue)
      updateLocal(data)

    }
    catch(err){
      console.warn("storage parse error",err)
    }

  }

}

/* ================= INIT ================= */

onMounted(()=>{

  const cached = localStorage.getItem(STORAGE_KEY)

  if(cached){

    try{
      updateLocal(JSON.parse(cached))
    }
    catch{}

  }

  loadWorkout()

  window.addEventListener("storage",handleStorage)

})

onUnmounted(()=>{

  window.removeEventListener("storage",handleStorage)

})
</script>