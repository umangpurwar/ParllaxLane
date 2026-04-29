import axios from 'axios';
import router from '../router';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  }
});

// Refresh state
let isRefreshing = false;
let pendingRequests = [];

// Resolve queued requests
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

// Store auth data
export const setAuthData = (data) => {
  if (data?.access) {
    localStorage.setItem('access_token', data.access);
  }
  if (data?.refresh) {
    localStorage.setItem('refresh_token', data.refresh);
  }
  if (data?.org_role) {
    localStorage.setItem('org_role', data.org_role);
  }
  if (data?.org_slug) {
    localStorage.setItem('org_slug', data.org_slug);
  }
};

// Clear auth data
export const clearAuthData = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('org_role');
  localStorage.removeItem('org_slug');
};

// REQUEST INTERCEPTOR
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },
  (error) => Promise.reject(error)
);

// RESPONSE INTERCEPTOR
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // If no response or not 401 → reject
    if (!error.response || error.response.status !== 401) {
      return Promise.reject(error);
    }

    // Prevent infinite retry loop
    if (originalRequest._retry) {
      clearAuthData();
      router.replace('/login');
      return Promise.reject(error);
    }

    originalRequest._retry = true;

    const refreshToken = localStorage.getItem('refresh_token');

    if (!refreshToken) {
      clearAuthData();
      router.replace('/login');
      return Promise.reject(error);
    }

    // If refresh already running → queue request
    if (isRefreshing) {
      return new Promise((resolve, reject) => {
        pendingRequests.push({ resolve, reject });
      })
        .then((token) => {
          originalRequest.headers.Authorization = `Bearer ${token}`;
          return api(originalRequest);
        })
        .catch((err) => Promise.reject(err));
    }

    isRefreshing = true;

    try {
      const response = await axios.post(
        `${api.defaults.baseURL}token/refresh/`,
        { refresh: refreshToken }
      );

      const newAccessToken = response.data.access;

      // Save new token
      localStorage.setItem('access_token', newAccessToken);

      // Update default header
      api.defaults.headers.common.Authorization = `Bearer ${newAccessToken}`;

      // Process queued requests
      processQueue(null, newAccessToken);

      // Retry original request
      originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
      return api(originalRequest);

    } catch (refreshError) {
      processQueue(refreshError, null);

      clearAuthData();
      router.replace('/login');
      return Promise.reject(refreshError);

    } finally {
      isRefreshing = false;
    }
  }
);

export default api;