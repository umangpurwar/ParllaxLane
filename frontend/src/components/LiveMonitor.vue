<template>
  <div class="h-full flex flex-col">
    <div class="flex justify-between items-end mb-6">
      <div>
        <h2 class="text-2xl font-medium tracking-tight text-brutal-ink">Live Invigilation</h2>
        <p class="text-[9px] uppercase tracking-widest font-semibold text-gray-500 mt-1 flex items-center gap-2">
          <span class="w-2 h-2 rounded-full bg-brutal-red animate-pulse"></span> System Monitoring Active
        </p>
      </div>
      
      <div class="flex gap-2 text-[10px] uppercase tracking-widest font-semibold">
        <button 
          @click="activeFilter = 'all'" 
          :class="activeFilter === 'all' ? 'bg-brutal-ink text-white' : 'bg-white text-brutal-ink hover:bg-gray-50'"
          class="border border-brutal-border px-3 py-1 transition-colors">
          All ({{ totalCandidates }})
        </button>
        <button 
          @click="activeFilter = 'risk'" 
          :class="activeFilter === 'risk' ? 'bg-brutal-red text-white' : 'bg-white text-brutal-red hover:bg-red-50'"
          class="border border-brutal-border px-3 py-1 transition-colors">
          High Risk ({{ highRiskCount }})
        </button>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4">
      
      <div v-for="user in displayedUsers" :key="user.id" 
           class="bg-white border border-brutal-border p-5 flex flex-col gap-4 transition-all hover:border-brutal-ink cursor-pointer"
           :class="{'border-l-4 border-l-brutal-red': user.riskScore >= 10 || user.totalViolations > 0}"
           @click="$emit('open-modal', user)">
        
        <div class="flex justify-between items-start">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 bg-brutal-ink text-brutal-paper flex items-center justify-center font-bold text-sm uppercase">
              {{ user.name.charAt(0) }}
            </div>
            <div>
              <h3 class="font-medium tracking-tight text-brutal-ink">{{ user.name }}</h3>
              <p class="text-[9px] uppercase tracking-widest font-semibold" 
                 :class="user.status === 'Active' ? 'text-green-600' : 'text-gray-400'">
                {{ user.status }}
              </p>
            </div>
          </div>
          <div class="text-right">
            <div class="text-2xl font-medium tracking-tighter" :class="(user.riskScore >= 10 || user.totalViolations > 0) ? 'text-brutal-red' : 'text-brutal-ink'">
              {{ user.riskScore }}<span class="text-[10px] font-normal text-gray-500 ml-1">Risk</span>
            </div>
          </div>
        </div>

        <div class="h-px w-full bg-brutal-border/50"></div>

        <div class="flex justify-between items-center text-[10px] uppercase tracking-widest font-bold">
          <div class="flex flex-col gap-1">
            <span class="text-gray-500">Camera</span>
            <span :class="user.health.camera ? 'text-brutal-ink' : 'text-brutal-red'">{{ user.health.camera ? '✅ ON' : '❌ OFF' }}</span>
          </div>
          <div class="flex flex-col gap-1">
            <span class="text-gray-500">Tab Focus</span>
            <span :class="user.health.tab ? 'text-brutal-ink' : 'text-brutal-red'">{{ user.health.tab ? '✅ ACTIVE' : '❌ AWAY' }}</span>
          </div>
          <div class="flex flex-col gap-1">
            <span class="text-gray-500">Fullscreen</span>
            <span :class="user.health.fullscreen ? 'text-brutal-ink' : 'text-brutal-red'">{{ user.health.fullscreen ? '✅ ON' : '❌ EXIT' }}</span>
          </div>
        </div>

      </div>

      <div v-if="displayedUsers.length === 0" class="col-span-full py-12 text-center text-sm font-medium text-gray-500 border border-dashed border-brutal-border">
        No candidates found matching this filter.
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue';

const emit = defineEmits(['open-modal']);

// State
const liveUsers = ref([]);
const activeFilter = ref('all'); 
let pollingInterval = null;
let isFetching = false; 

const CURRENT_EXAM_ID = () => localStorage.getItem("active_exam_id"); 
const API_BASE_URL = 'http://localhost:8000/api/admin';

// Headers
const getHeaders = () => ({
  'Authorization': `Bearer ${localStorage.getItem("access_token")}`,
  'Content-Type': 'application/json'
});


const handleUnauthorized = () => {
  localStorage.clear();
  window.location.href = "/login";
};


const fetchLiveMonitorData = async () => {

  if (isFetching || !localStorage.getItem("access_token")) return; 
  isFetching = true;

  const examId = localStorage.getItem("active_exam_id")
  try {
    if (!examId) return;
    const response = await fetch(
      `${API_BASE_URL}/exam/${examId}/live/`, 
      { headers: getHeaders() }
    );

    // expire token
    if (response.status === 401) {
      handleUnauthorized();
      return;
    }

    if (!response.ok) {
      console.error("API Error:", response.status);
      return;
    }

    const data = await response.json();

    liveUsers.value = data.map(item => ({
      id: item.attempt_id,
      username: item.username,
      name: item.username,
      status:
        item.status === 'active'
          ? 'Active'
          : item.status === 'terminated'
          ? 'Terminated'
          : 'Inactive',
      riskScore: item.risk_score || 0,
      totalViolations: item.violations_count || 0,
      health: {
        camera: item.system_health?.camera ?? true,
        tab: item.system_health?.tab_focus ?? true,
        fullscreen: item.system_health?.fullscreen ?? true
      }
    }));

  } catch (error) {
    console.error("Failed to fetch live monitoring data:", error);
  } finally {
    isFetching = false;
  }
};

// Lifecycle
onMounted(() => {
  if(pollingInterval){
    clearInterval(pollingInterval)
  }
  fetchLiveMonitorData();

  pollingInterval = setInterval(() => {
    fetchLiveMonitorData();
  }, 5000);
});

onUnmounted(() => {
  if (pollingInterval) clearInterval(pollingInterval);
});

// Computed
const totalCandidates = computed(() => liveUsers.value.length);

const highRiskUsersList = computed(() => {
  return liveUsers.value.filter(
    u => u.totalViolations > 0 || u.riskScore >= 10 || u.status === 'Terminated'
  );
});

const highRiskCount = computed(() => highRiskUsersList.value.length);

const displayedUsers = computed(() => {
  return activeFilter.value === 'risk' 
    ? highRiskUsersList.value 
    : liveUsers.value;
});
</script>