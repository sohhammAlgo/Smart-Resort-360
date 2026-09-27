import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "https://smart-resort-360-mbag.onrender.com";

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Interceptor to attach Authorization Bearer token from localStorage
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem("sr360_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Interceptor to handle 401 Unauthorized token expiry
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem("sr360_token");
      localStorage.removeItem("sr360_user");
      // Optional event or location redirect if unauthenticated
    }
    return Promise.reject(error);
  }
);
