<template>
  <div class="flex flex-col gap-8 max-w-5xl">
    <div>
      <p class="text-[9px] uppercase tracking-wide-ish font-semibold text-gray-600 mb-3">Quick Actions</p>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <button @click="$emit('change-tab', 'create_exam')" class="flex flex-col items-center justify-center bg-white border border-brutal-border p-8 hover:border-brutal-red hover:text-brutal-red transition-colors group">
          <svg class="w-8 h-8 mb-3 text-brutal-ink group-hover:text-brutal-red" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="square" stroke-linejoin="miter" stroke-width="2" d="M12 4v16m8-8H4"></path></svg>
          <span class="text-[10px] uppercase tracking-widest font-semibold">Create Exam</span>
        </button>
        </div>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div class="bg-white border border-brutal-border p-8 flex flex-col justify-between">
        <span class="text-[10px] uppercase tracking-widest font-semibold text-gray-500">Active Exams</span>
        <span class="text-5xl font-medium tracking-tighter mt-6">{{ activeExamsCount }}</span>
      </div>
      <div class="bg-white border border-brutal-border p-8 flex flex-col justify-between">
        <span class="text-[10px] uppercase tracking-widest font-semibold text-gray-500">Live Candidates</span>
        <span class="text-5xl font-medium tracking-tighter mt-6 text-brutal-red">{{ liveCandidatesCount }}</span>
      </div>
      <div class="bg-white border border-brutal-border p-8 flex flex-col justify-between">
        <span class="text-[10px] uppercase tracking-widest font-semibold text-gray-500">High Risk Users</span>
        <span class="text-5xl font-medium tracking-tighter mt-6">{{ highRiskCount }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
// Define the props coming from AdminDashboard.vue
defineProps({
  activeExamsCount: {
    type: Number,
    default: 0
  },
  liveCandidatesCount: {
    type: Number,
    default: 0
  },
  highRiskCount: {
    type: Number,
    default: 0
  }
});

// Define the event that tells the parent to switch tabs
defineEmits(['change-tab']);
</script>