<template>
  <div class="max-w-3xl pb-10">
    <div class="mb-8 flex justify-between items-center">
      <div>
        <h2 class="text-3xl font-medium tracking-tighter text-brutal-ink">Create Assessment</h2>
        <p class="text-[9px] uppercase tracking-widest font-semibold text-gray-500 mt-1">Configure parameters and MCQs</p>
      </div>
      <button @click="$emit('change-tab', 'exams')" class="text-[10px] uppercase tracking-widest font-bold text-gray-500 hover:text-brutal-ink transition-colors">
        Cancel &larr;
      </button>
    </div>

    <form @submit.prevent="submitExam" class="bg-white border border-brutal-border p-8 flex flex-col gap-8">
      
      <div class="flex flex-col gap-6 border-b border-brutal-border/30 pb-8">
        <h3 class="text-[10px] uppercase tracking-super-wide font-bold text-brutal-red">1. Core Details</h3>
        
        <div class="flex flex-col gap-2">
          <label class="text-[9px] uppercase tracking-widest font-bold text-gray-500">Exam Title *</label>
          <input v-model="formData.title" type="text" required placeholder="e.g. Advanced Data Structures" class="w-full border-b border-brutal-border px-0 py-2 text-sm text-brutal-ink focus:outline-none focus:border-brutal-red bg-transparent" />
        </div>

        <div class="flex flex-col gap-2">
          <label class="text-[9px] uppercase tracking-widest font-bold text-gray-500">Description</label>
          <textarea v-model="formData.description" rows="2" placeholder="Brief instructions..." class="w-full border-b border-brutal-border px-0 py-2 text-sm text-brutal-ink focus:outline-none focus:border-brutal-red bg-transparent resize-none"></textarea>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div class="flex flex-col gap-2">
            <label class="text-[9px] uppercase tracking-widest font-bold text-gray-500">Duration (Mins) *</label>
            <input v-model.number="formData.duration" type="number" required min="1" class="w-full border-b border-brutal-border px-0 py-2 text-sm text-brutal-ink focus:outline-none focus:border-brutal-red bg-transparent" />
          </div>
          <div class="flex flex-col gap-2">
            <label class="text-[9px] uppercase tracking-widest font-bold text-gray-500">Start Date/Time</label>
            <input v-model="formData.start_time" type="datetime-local" class="w-full border-b border-brutal-border px-0 py-2 text-sm text-brutal-ink focus:outline-none focus:border-brutal-red bg-transparent" />
          </div>
          <div class="flex flex-col gap-2">
            <label class="text-[9px] uppercase tracking-widest font-bold text-gray-500">End Date/Time</label>
            <input v-model="formData.end_time" type="datetime-local" class="w-full border-b border-brutal-border px-0 py-2 text-sm text-brutal-ink focus:outline-none focus:border-brutal-red bg-transparent" />
          </div>
        </div>
      </div>

      <div class="flex flex-col gap-6 border-b border-brutal-border/30 pb-8">
        <div class="flex justify-between items-center">
          <h3 class="text-[10px] uppercase tracking-super-wide font-bold text-brutal-red">2. Questionnaire ({{ formData.questions.length }})</h3>
          <button type="button" @click="addQuestion" class="px-3 py-1 bg-brutal-ink text-white text-[9px] uppercase tracking-widest font-bold hover:bg-gray-800">
            + Add Question
          </button>
        </div>

        <div v-for="(q, index) in formData.questions" :key="index" class="bg-gray-50 p-6 border border-brutal-border relative">
          <button type="button" @click="removeQuestion(index)" class="absolute top-4 right-4 text-gray-400 hover:text-brutal-red font-bold text-sm">X</button>
          
          <div class="flex flex-col gap-4">
            <div class="flex flex-col gap-2">
              <label class="text-[9px] uppercase tracking-widest font-bold text-gray-500">Q{{ index + 1 }}. Question Text</label>
              <input v-model="q.text" type="text" required class="w-full border-b border-gray-300 px-0 py-2 text-sm focus:outline-none focus:border-brutal-ink bg-transparent" />
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div class="flex flex-col gap-1">
                <label class="text-[9px] uppercase font-bold text-gray-400">Option A</label>
                <input v-model="q.option_a" type="text" required class="border-b border-gray-300 py-1 text-sm bg-transparent focus:outline-none focus:border-brutal-ink" />
              </div>
              <div class="flex flex-col gap-1">
                <label class="text-[9px] uppercase font-bold text-gray-400">Option B</label>
                <input v-model="q.option_b" type="text" required class="border-b border-gray-300 py-1 text-sm bg-transparent focus:outline-none focus:border-brutal-ink" />
              </div>
              <div class="flex flex-col gap-1">
                <label class="text-[9px] uppercase font-bold text-gray-400">Option C</label>
                <input v-model="q.option_c" type="text" required class="border-b border-gray-300 py-1 text-sm bg-transparent focus:outline-none focus:border-brutal-ink" />
              </div>
              <div class="flex flex-col gap-1">
                <label class="text-[9px] uppercase font-bold text-gray-400">Option D</label>
                <input v-model="q.option_d" type="text" required class="border-b border-gray-300 py-1 text-sm bg-transparent focus:outline-none focus:border-brutal-ink" />
              </div>
            </div>

            <div class="flex flex-col gap-2 mt-2">
              <label class="text-[9px] uppercase tracking-widest font-bold text-brutal-ink">Correct Answer</label>
              <select v-model="q.correct_answer" required class="w-full p-2 border border-brutal-border text-sm bg-white focus:outline-none focus:border-brutal-red">
                <option disabled value="">Select the correct option...</option>
                <option :value="q.option_a">Option A</option>
                <option :value="q.option_b">Option B</option>
                <option :value="q.option_c">Option C</option>
                <option :value="q.option_d">Option D</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      <div v-if="errorMessage" class="text-[10px] uppercase font-bold text-brutal-red">{{ errorMessage }}</div>
      
      <button type="submit" :disabled="isSubmitting" class="w-full bg-brutal-ink text-white py-4 text-[10px] uppercase tracking-widest font-bold hover:bg-brutal-red transition-colors">
        {{ isSubmitting ? 'Deploying...' : 'Deploy Exam & Questions' }}
      </button>

    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const emit = defineEmits(['change-tab']);
const API_BASE_URL = 'http://localhost:8000/api/admin';

const isSubmitting = ref(false);
const errorMessage = ref('');

const formData = ref({
  title: '',
  description: '',
  duration: 60,
  start_time: '',
  end_time: '',
  questions: [
    { text: '', option_a: '', option_b: '', option_c: '', option_d: '', correct_answer: '' }
  ]
});

const addQuestion = () => {
  formData.value.questions.push({ text: '', option_a: '', option_b: '', option_c: '', option_d: '', correct_answer: '' });
};

const removeQuestion = (index) => {
  formData.value.questions.splice(index, 1);
};

const getHeaders = () => ({
  'Authorization': `Bearer ${localStorage.getItem("access_token")}`,
  'Content-Type': 'application/json'
});

const submitExam = async () => {
  isSubmitting.value = true;
  errorMessage.value = '';

  try {
    const payload = { ...formData.value };
    if (payload.start_time) payload.start_time = new Date(payload.start_time).toISOString();
    if (payload.end_time) payload.end_time = new Date(payload.end_time).toISOString();

    const response = await fetch(`${API_BASE_URL}/exam/create/`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(payload)
    });

    if (response.ok) {
      emit('change-tab', 'exams');
    } else {
      const data = await response.json();
      errorMessage.value = data.error || 'Failed to create exam.';
    }
  } catch (error) {
    errorMessage.value = 'Network error occurred.';
  } finally {
    isSubmitting.value = false;
  }
};
</script>