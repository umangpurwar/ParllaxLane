<template>
  <div class="max-w-4xl mx-auto pb-10">
    <div class="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
      <div>
        <h2 class="text-3xl font-medium tracking-tighter text-brutal-ink">User Directory</h2>
        <p class="text-[9px] uppercase tracking-widest font-semibold text-gray-500 mt-1">Manage and search enrolled candidates</p>
      </div>
      <div class="relative w-full md:w-auto">
        <input type="text" v-model="searchQuery" placeholder="SEARCH USERS..." class="w-full md:w-64 bg-white border border-brutal-border px-4 py-3 text-[10px] text-brutal-ink uppercase tracking-widest focus:outline-none focus:border-brutal-red placeholder-gray-400" />
      </div>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div v-for="user in filteredUsers" :key="user.id" class="bg-white border border-brutal-border p-5 flex items-center justify-between">
        <div class="flex items-center gap-4">
          <div class="w-10 h-10 bg-brutal-ink text-brutal-paper flex items-center justify-center font-bold text-sm uppercase">
            {{ user.name.charAt(0) }}
          </div>
          <div>
            <h4 class="font-medium tracking-tight text-brutal-ink">{{ user.name }}</h4>
            <p class="text-[9px] uppercase tracking-widest text-gray-500">{{ user.id }}</p>
          </div>
        </div>
        <button @click="$emit('open-modal', user)" class="text-[9px] uppercase tracking-widest font-bold text-brutal-red hover:text-brutal-ink transition-colors">
          View
        </button>
      </div>
      
      <div v-if="filteredUsers.length === 0" class="col-span-full p-8 text-center text-sm font-medium text-gray-500">
        No users found matching "{{ searchQuery }}"
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';

// ADDED: Define emits so the 'View' button works
const emit = defineEmits(['open-modal']);

const searchQuery = ref('');
const allUsers = ref([]);

const API_BASE_URL = 'http://localhost:8000/api/admin';

const getHeaders = () => ({
  'Authorization': `Bearer ${localStorage.getItem("access_token")}`,
  'Content-Type': 'application/json'
});

// ADDED: The fetch pattern ready for your future Django endpoint
const fetchUsers = async () => {
  try {
    // Note: You will need to create this path in Django urls.py and views.py
    const response = await fetch(`${API_BASE_URL}/users/`, {
      headers: getHeaders()
    });

    if (response.ok) {
      const data = await response.json();
      allUsers.value = data.map(user => ({
        id: user.id || user.username, 
        username: user.username, // Needed to fetch their visual proofs later
        name: user.first_name ? `${user.first_name} ${user.last_name}` : user.username,
        status: user.status || 'Enrolled'
      }));
    } else {
      loadMockData(); // Fallback if endpoint returns 404
    }
  } catch (error) {
    console.warn("Backend /users/ endpoint not ready. Using mock data.");
    loadMockData(); // Fallback if network fails
  }
};

// Extracted mock data so the UI functions perfectly while you code the backend
const loadMockData = () => {
  allUsers.value = [
    { id: 'USR-802', username: 'johndoe', name: 'John Doe', status: 'Active' },
    { id: 'USR-441', username: 'sarahsmith', name: 'Sarah Smith', status: 'Active' },
    { id: 'USR-909', username: 'michaellee', name: 'Michael Lee', status: 'Terminated' },
    { id: 'USR-211', username: 'emmawatson', name: 'Emma Watson', status: 'Completed' },
    { id: 'USR-345', username: 'davidcarter', name: 'David Carter', status: 'Not Taken' },
  ];
};

onMounted(() => {
  fetchUsers();
});

const filteredUsers = computed(() => {
  if (!searchQuery.value) return allUsers.value;
  const q = searchQuery.value.toLowerCase();
  return allUsers.value.filter(u => 
    u.name.toLowerCase().includes(q) || 
    u.id.toLowerCase().includes(q) ||
    (u.username && u.username.toLowerCase().includes(q)) // Added username search support
  );
});
</script>