import axios from 'axios';
import router from '../router'; // Adjust path to your Vue router

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  }
});

// Request Interceptor: Attach JWT Token
api.interceptors.request.use(
  (config) => {
    const token =
      localStorage.getItem('access_token') ||
      localStorage.getItem('token'); // legacy fallback
    if (token) {
      if (!localStorage.getItem('access_token')) {
        localStorage.setItem('access_token', token);
      }
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response Interceptor: Handle 401 and global errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      if (error.response.status === 401) {
        // Token expired or invalid
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('token');
        localStorage.removeItem('is_admin');
        router.push('/login');
      } else if (error.response.status === 500) {
        console.error("Critical Backend Error. Check server logs.");
        // Optionally trigger a global toast/notification here
      }
    }
    return Promise.reject(error);
  }
);

export default api;
