<template>
  <div class="max-w-4xl mx-auto pb-10">
    <div class="mb-8">
      <h2 class="text-3xl font-medium tracking-tighter text-brutal-ink">Reports & Extracts</h2>
      <p class="text-[9px] uppercase tracking-widest font-semibold text-gray-500 mt-1">Download consolidated evaluation data</p>
    </div>

    <div class="space-y-6">
      <div v-for="exam in exams" :key="'rep-' + exam.id" class="bg-white border border-brutal-border p-6 md:p-8 flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
        <div>
          <h3 class="text-xl font-medium tracking-tight text-brutal-ink">{{ exam.title }}</h3>
          <p class="text-[10px] uppercase tracking-widest font-semibold text-gray-500 mt-1">Date: {{ exam.date }}</p>
        </div>
        
        <div class="flex flex-col sm:flex-row gap-3 w-full md:w-auto">
          <button @click="downloadCandidateReport(exam.id)" class="px-5 py-3 bg-white border border-brutal-ink text-brutal-ink text-[9px] uppercase tracking-widest font-bold hover:bg-brutal-ink hover:text-white transition-colors flex-1 md:flex-auto whitespace-nowrap text-center">
            Candidate Data
          </button>
          <button @click="downloadQAReport(exam.id)" class="px-5 py-3 bg-brutal-ink text-white text-[9px] uppercase tracking-widest font-bold hover:bg-brutal-red transition-colors flex-1 md:flex-auto whitespace-nowrap text-center">
            Exam Q&A
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  exams: {
    type: Array,
    required: true
  }
});

const API_BASE_URL = 'http://localhost:8000/api/admin';

const getHeaders = () => ({
  'Authorization': `Bearer ${localStorage.getItem("access_token")}`,
});

// Helper function to handle secure file downloads
const downloadFile = async (url, filename) => {
  try {
    const response = await fetch(url, { headers: getHeaders() });
    if (!response.ok) throw new Error("Download failed");
    
    const blob = await response.blob();
    const downloadUrl = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(downloadUrl);
  } catch (error) {
    console.error("Error downloading report:", error);
  }
};

const downloadCandidateReport = (examId) => {
  downloadFile(`${API_BASE_URL}/export_excel/${examId}/`, `Exam_${examId}_Candidates.xlsx`);
};

const downloadQAReport = (examId) => {
  downloadFile(`${API_BASE_URL}/export_pdf/${examId}/`, `Exam_${examId}_QA_Report.pdf`);
};
</script>