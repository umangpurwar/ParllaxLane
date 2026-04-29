<template>
  <div class="max-w-4xl mx-auto pb-10">
    <div class="mb-8">
      <h2 class="text-3xl font-medium tracking-tighter text-brutal-ink">Reports & Extracts</h2>
      <p class="text-[9px] uppercase tracking-widest font-semibold text-gray-500 mt-1">
        Download consolidated evaluation data
      </p>
    </div>

    <div class="space-y-6">
      <div v-for="exam in exams" :key="'rep-' + exam.id"
        class="bg-white border border-brutal-border p-6 md:p-8 flex flex-col gap-6">

        <!-- HEADER -->
        <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
          <div>
            <h3 class="text-xl font-medium tracking-tight text-brutal-ink">{{ exam.title }}</h3>
            <p class="text-[10px] uppercase tracking-widest font-semibold text-gray-500 mt-1">
              Date: {{ exam.date }}
            </p>
          </div>

          <div class="flex flex-col sm:flex-row gap-3 w-full md:w-auto">
            <button @click="toggleResults(exam.id)"
              class="px-5 py-3 bg-white border border-brutal-ink text-brutal-ink text-[9px] uppercase tracking-widest font-bold hover:bg-brutal-ink hover:text-white transition-colors flex-1 md:flex-auto text-center">
              Results
            </button>

            <button @click="toggleQA(exam.id)"
              class="px-5 py-3 bg-brutal-ink text-white text-[9px] uppercase tracking-widest font-bold hover:bg-brutal-red transition-colors flex-1 md:flex-auto text-center">
              Q & A
            </button>
          </div>
        </div>

        <!-- RESULTS TABLE -->
        <div v-if="selectedExam === exam.id && viewType === 'results'" class="border-t pt-4">
          <h4 class="text-sm font-bold text-brutal-ink mb-3">Results</h4>

          <table class="w-full text-sm text-left border">
            <thead class="bg-gray-100">
              <tr>
                <th class="p-2 border">User</th>
                <th class="p-2 border">Score</th>
                <th class="p-2 border">Attempts</th>
                <th class="p-2 border">Start</th>
                <th class="p-2 border">End</th>
                <th class="p-2 border">Duration</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in results" :key="user.username">
                <td class="p-2 border">{{ user.username }}</td>
                <td class="p-2 border">{{ user.score }}</td>
                <td class="p-2 border">{{ user.attempts }}</td>
                <td class="p-2 border">{{ formatTime(user.start_time) }}</td>
                <td class="p-2 border">{{ formatTime(user.end_time) }}</td>
                <td class="p-2 border">{{ getDuration(user.start_time, user.end_time) }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- QA VIEW -->
        <div v-if="selectedExam === exam.id && viewType === 'qa'" class="border-t pt-4">
          <h4 class="text-sm font-bold text-brutal-ink mb-3">Q & A</h4>

          <div v-for="q in qaData" :key="q.id" class="border-b py-3 text-sm text-brutal-ink">
            <p><strong>Q:</strong> {{ q.text }}</p>
            <p>A: {{ q.option_a }}</p>
            <p>B: {{ q.option_b }}</p>
            <p>C: {{ q.option_c }}</p>
            <p>D: {{ q.option_d }}</p>
            <p class="text-green-600 font-bold">
              Correct: {{ q.correct_answer?.toUpperCase() }}
            </p>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import api from '@/services/api';

defineProps({
  exams: Array
});

const selectedExam = ref(null);
const viewType = ref(""); // results | qa
const results = ref([]);
const qaData = ref([]);

// TOGGLE RESULTS
const toggleResults = async (examId) => {
  if (selectedExam.value === examId && viewType.value === 'results') {
    selectedExam.value = null;
    viewType.value = "";
    return;
  }

  selectedExam.value = examId;
  viewType.value = 'results';

  try {
    const res = await api.get(`admin/exam/${examId}/results/`);
    results.value = res.data;
  } catch (e) {
    console.error("Results fetch error:", e);
  }
};

//  TOGGLE QA
const toggleQA = async (examId) => {
  // toggle close
  if (selectedExam.value === examId && viewType.value === 'qa') {
    selectedExam.value = null;
    viewType.value = "";
    qaData.value = []; // reset
    return;
  }

  selectedExam.value = examId;
  viewType.value = 'qa';
  qaData.value = []; 

  try {
    const res = await api.get(`admin/exam/${examId}/qa/`);
    const data = res.data;

    console.log("QA DATA:", data); // debug

    // ensure it's array
    qaData.value = Array.isArray(data) ? data : [];

  } catch (e) {
    console.error("QA fetch error:", e);
  }
};

//  FORMAT TIME
const formatTime = (time) => {
  if (!time) return "Not submitted";
  return new Date(time).toLocaleString();
};

//  CALCULATE DURATION
const getDuration = (start, end) => {
  if (!start || !end) return "-";

  const diff = new Date(end) - new Date(start);
  const mins = Math.floor(diff / 60000);
  const secs = Math.floor((diff % 60000) / 1000);

  return `${mins}m ${secs}s`;
};
</script>