import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000', // FastAPI后端地址
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true // 允许跨域请求携带凭证
});

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export const authService = {
  async signup(userData) {
    const response = await api.post('/api/signup', userData);
    if (response.data.token) {
      localStorage.setItem('token', response.data.token);
    }
    return response.data;
  },

  async login(credentials) {
    const response = await api.post('/api/login', credentials);
    if (response.data.token) {
      localStorage.setItem('token', response.data.token);
    }
    return response.data;
  },

  async getUserInfo() {
    const response = await api.get('/api/user-info');
    return response.data;
  },

  logout() {
    localStorage.removeItem('token');
  },

  isAuthenticated() {
    return !!localStorage.getItem('token');
  }
};

export const marketService = {
  async getWatchlist() {
    const response = await api.get('/api/user/watchlist');
    return response.data;
  },

  async getAllStocks() {
    const response = await api.get('/api/stocks');
    return response.data;
  },

  async addToWatchlist(ticker) {
    const response = await api.post(`/api/user/watchlist/add?ticker=${ticker}`);
    return response.data;
  },

  async removeFromWatchlist(ticker) {
    const response = await api.post(`/api/user/watchlist/remove?ticker=${ticker}`);
    return response.data;
  }
};

export default api; 