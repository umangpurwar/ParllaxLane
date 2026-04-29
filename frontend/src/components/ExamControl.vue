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
               <!-- BUTTON GROUP -->
                <div class="flex gap-2 w-full md:w-auto">
    
             <!-- EDIT BUTTON -->
            <button 
            @click="editExam(exam)"
              class="px-6 py-3 w-full md:w-auto border border-brutal-ink text-brutal-ink text-[10px] uppercase tracking-widest font-bold hover:bg-brutal-ink hover:text-white transition-colors">
              Edit
              </button>

            <!-- DELETE BUTTON -->
            <button 
              @click="deleteExam(exam)"
              class="px-6 py-3 w-full md:w-auto border border-brutal-ink text-brutal-ink text-[10px] uppercase tracking-widest font-bold hover:bg-brutal-red hover:text-white transition-colors">
                Delete
              </button>

            <!-- TOGGLE BUTTON -->
            <button 
             @click="toggleExamStatus(exam)" 
            class="px-6 py-3 w-full md:w-auto border border-brutal-ink text-brutal-ink text-[10px] uppercase tracking-widest font-bold hover:bg-brutal-ink hover:text-white transition-colors">
            {{ exam.status === 'Active' ? 'Disable Exam' : 'Enable Exam' }}
          </button>

          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import api from '@/services/api';

const props = defineProps({
  exams: {
    type: Array,
    required: true
  }
});
const emit = defineEmits(['change-tab']);

const editExam = (exam) => {
  // store exam to edit
  localStorage.setItem("edit_exam", JSON.stringify(exam));

  // open form
  emit('change-tab', 'create_exam');
};

const deleteExam = async (exam) => {
  const confirmDelete = confirm(`Delete exam "${exam.title}"?`);
  if (!confirmDelete) return;

  try {
    // Axios throws an error for non-2xx responses, so resolving means success
    await api.delete(`admin/exam/${exam.id}/delete/`);
    emit('change-tab', 'exams');
  } catch (e) {
    console.error("Delete error:", e);
  }
};

const toggleExamStatus = async (exam) => {
  try {
    await api.post(`admin/exam/${exam.id}/toggle/`);
    //  ONLY update from backend truth
    exam.is_active = !exam.is_active;
    exam.status = exam.is_active ? 'Active' : 'Disabled';
  } catch (error) {
    console.error("Network error:", error);
  }
};

const updateExamTime = async (exam) => {
  try {
    await api.patch(`admin/exam/${exam.id}/update/`, {
      start_time: new Date(exam.date + "T00:00").toISOString(),
      end_time: new Date(exam.date + "T23:59").toISOString()
    });
  } catch (e) {
    console.error("Update time failed:", e);
  }
};

</script>