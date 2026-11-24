import axios from 'axios';

const TOKEN_KEY = 'fs_access_token';
const USER_KEY = 'fs_user';

const rawUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
export const API_URL = rawUrl.replace(/\/+$/, '');

export function getToken() {
  try {
    return window.localStorage.getItem(TOKEN_KEY);
  } catch {
    return null;
  }
}

export function setToken(token) {
  try {
    window.localStorage.setItem(TOKEN_KEY, token);
  } catch {
    /* Storage can be unavailable in private browsing; the in-memory session still works. */
  }
}

export function getStoredUser() {
  try {
    const raw = window.localStorage.getItem(USER_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

export function setStoredUser(user) {
  try {
    if (user) window.localStorage.setItem(USER_KEY, JSON.stringify(user));
    else window.localStorage.removeItem(USER_KEY);
  } catch {
    /* Ignore storage failures. */
  }
}

export function clearSession() {
  try {
    window.localStorage.removeItem(TOKEN_KEY);
    window.localStorage.removeItem(USER_KEY);
  } catch {
    /* Ignore storage failures. */
  }
  if (typeof window !== 'undefined') {
    window.dispatchEvent(new CustomEvent('fs:session-cleared'));
  }
}

export const apiClient = axios.create({
  baseURL: API_URL,
  timeout: 30000,
  headers: { Accept: 'application/json' },
});

apiClient.interceptors.request.use(
  (config) => {
    const token = getToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error),
);

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error?.response?.status === 401) {
      clearSession();
      const path = window.location.pathname;
      if (!path.startsWith('/login') && !path.startsWith('/register')) {
        window.location.replace('/login');
      }
    }
    return Promise.reject(error);
  },
);
