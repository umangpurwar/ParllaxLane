import axios from 'axios';
import router from '../router';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  }
});

//  Refresh state
let isRefreshing = false;
let pendingRequests = [];

//  Resolve queued requests
const processQueue = (error, token = null) => {
  pendingRequests.forEach(p => {
    if (error) {
      p.reject(error);
    } else {
      p.resolve(token);
    }
  });
  pendingRequests = [];
};

//  Request interceptor
api.interceptors.request.use(
  (config) => {
    const token =
      localStorage.getItem('access_token') ||
      localStorage.getItem('token');

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

//  Response interceptor
api.interceptors.response.use(
  res => res,
  async error => {
    const originalRequest = error.config;

    //  Not 401 → just reject
    if (!error.response || error.response.status !== 401) {
      return Promise.reject(error);
    }

    //  Already retried → logout
    if (originalRequest._retry) {
      localStorage.clear();
      router.replace('/login');
      return Promise.reject(error);
    }

    originalRequest._retry = true;

    const refresh = localStorage.getItem("refresh_token");

    if (!refresh) {
      localStorage.clear();
      router.replace("/login");
      return Promise.reject(error);
    }

    // 🔁 If refresh already in progress → queue request
    if (isRefreshing) {
      return new Promise((resolve, reject) => {
        pendingRequests.push({ resolve, reject });
      })
      .then(token => {
        originalRequest.headers["Authorization"] = `Bearer ${token}`;
        return api(originalRequest);
      })
      .catch(err => Promise.reject(err));
    }

    isRefreshing = true;

    try {
      const res = await axios.post(
        `${api.defaults.baseURL}token/refresh/`,
        { refresh }
      );

      const newAccess = res.data.access;

      // Save new token
      localStorage.setItem("access_token", newAccess);

      // Update defaults
      api.defaults.headers.common["Authorization"] = `Bearer ${newAccess}`;

      // Resolve queued requests
      processQueue(null, newAccess);

      // Retry original request
      originalRequest.headers["Authorization"] = `Bearer ${newAccess}`;
      return api(originalRequest);

    } catch (err) {
      processQueue(err, null);

      localStorage.clear();
      router.replace("/login");
      return Promise.reject(err);

    } finally {
      isRefreshing = false;
    }
  }
);

export default api;