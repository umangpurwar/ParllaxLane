<template>
  <div class="max-w-4xl mx-auto pb-10">
    <div class="flex justify-between items-center mb-8">
      <div>
        <h2 class="text-3xl font-medium tracking-tighter text-brutal-ink">Exam Control</h2>
        <p class="text-[9px] uppercase tracking-widest font-semibold text-gray-500 mt-1">Manage, Postpone, or Disable Assessments</p>
      </div>
      <button @click="$emit('change-tab', 'create_exam')" class="bg-brutal-ink text-white px-4 py-2 text-[10px] uppercase tracking-widest font-bold hover:bg-brutal-red transition-colors">
        + New Exam
      </button>
    </div>

    <div class="space-y-6">
      <div v-for="exam in exams" :key="exam.id" class="bg-white border border-brutal-border p-6 flex flex-col gap-4">
        <div class="flex justify-between items-start md:items-center">
          <div>
            <h3 class="text-xl font-medium tracking-tight text-brutal-ink">{{ exam.title }}</h3>
            <p class="text-[10px] uppercase tracking-widest font-semibold text-gray-500 mt-1">Current Date: {{ exam.date }}</p>
          </div>
          <span class="px-3 py-1 text-[9px] uppercase tracking-widest font-bold text-white mt-2 md:mt-0" 
                :class="exam.status === 'Active' ? 'bg-brutal-red' : 'bg-gray-400'">
            {{ exam.status }}
          </span>
        </div>
        
        <div class="flex flex-col md:flex-row items-start md:items-center justify-between mt-4 border-t border-brutal-border/30 pt-6 gap-4">
          <div class="flex items-center gap-4">
            <label class="text-[9px] uppercase font-bold text-gray-500 tracking-widest">Postpone To:</label>
            <input 
              type="date" 
              v-model="exam.date" 
              @change="updateExamTime(exam)"
              class="border-b border-brutal-border text-sm focus:outline-none focus:border-brutal-red bg-transparent py-1 font-medium text-brutal-ink">
          </div>
          <button @click="toggleExamStatus(exam)" class="px-6 py-3 w-full md:w-auto border border-brutal-ink text-brutal-ink text-[10px] uppercase tracking-widest font-bold hover:bg-brutal-ink hover:text-white transition-colors">
            {{ exam.status === 'Active' ? 'Disable Exam' : 'Enable Exam' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const props = defineProps({
  exams: {
    type: Array,
    required: true
  }
});
defineEmits(['change-tab']);

const API_BASE_URL = 'http://localhost:8000/api/admin';

const getHeaders = () => ({
  'Authorization': `Bearer ${localStorage.getItem("access_token")}`,
  'Content-Type': 'application/json'
});

const toggleExamStatus = async (exam) => {
  try {
    // 1. Call DRF backend
    const response = await fetch(`${API_BASE_URL}/exam/${exam.id}/toggle/`, {
      method: 'POST',
      headers: getHeaders()
    });

    if (response.ok) {
      // 2. Update UI only if backend successfully toggled it
      exam.status = exam.status === 'Active' ? 'Disabled' : 'Active';
    } else {
      console.error("Failed to toggle exam status on server.");
    }
  } catch (error) {
    console.error("Network error:", error);
  }
};

const updateExamTime = async (exam) => {
  try {
    await fetch(`${API_BASE_URL}/exam/${exam.id}/update-time/`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({
        start_time: exam.date + "T00:00:00",
        end_time: exam.date + "T23:59:00"
      })
    });
  } catch (e) {
    console.error("Update time failed:", e);
  }
};

</script>