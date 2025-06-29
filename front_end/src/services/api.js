import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000', // FastAPI backend address
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true // allow cross-domain requests to carry credentials
});

// request interceptor
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
    const token = localStorage.getItem('token');
    if (!token) return false;
    
    // check if token is expired
    try {
      const tokenData = JSON.parse(atob(token.split('.')[1]));
      const expirationTime = tokenData.exp * 1000; // convert to milliseconds
      if (Date.now() >= expirationTime) {
        this.logout(); // if token is expired, clear it
        return false;
      }
      return true;
    } catch (e) {
      this.logout(); // if token is invalid, clear it
      return false;
    }
  },

  async updateUserInfo(userData) {
    const response = await api.put('/api/user-update', userData);
    return response.data;
  },

  async deleteUser() {
    const response = await api.delete('/api/user/delete');
    return response.data;
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
  },

  async getTickerInfo(ticker) {
    const response = await api.get(`/api/tickers/info/${ticker}`);
    return response.data;
  },

  async getTickerHistory(ticker) {
    const response = await api.get(`/api/tickers/hist/${ticker}`);
    return response.data;
  }
};

export const portfolioService = {
  async getAllPortfolios() {
    return await api.get('/api/portfolios/get');
  },

  async getPortfolioById(id, params = {}) {
    return await api.get(`/api/portfolios/get/${id}`, { params });
  },

  async createPortfolio(portfolioData) {
    return await api.post('/api/portfolios/create', portfolioData);
  },

  async updatePortfolio(id, portfolioData) {
    return await api.put(`/api/portfolios/update/${id}`, portfolioData);
  },

  async deletePortfolio(id) {
    return await api.delete(`/api/portfolios/delete/${id}`);
  },

  async getMetrics() {
    return await api.get('/api/portfolios/metrics');
  },

  async optimizePortfolio(ptfid, params) {
    return await api.post(`/api/portfolios/optimize/${ptfid}`, params);
  },

  async optimizeNewPortfolio(params) {
    return await api.post('/api/portfolios/optimize', params);
  }
};

export const questionnaireService = {
  async getQuestionnaires() {
    const response = await api.get('/api/questionnaires/');
    return response.data;
  },

  async submitQuestionnaire(answers) {
    const answersArray = Object.keys(answers).map(questionId => {
      const answer = answers[questionId];
      return [answer];
    });
    
    const response = await api.post('/api/questionnaires/', { answers: answersArray });
    return response.data;
  },

  async getUserResponse() {
    const response = await api.get('/api/questionnaires/response');
    return response.data;
  },

  async getStockSuggestions() {
    const response = await api.get('/api/questionnaires/stocks-suggestions');
    return response.data;
  },

  async getMetricSuggestions() {
    const response = await api.get('/api/questionnaires/metric-suggestions');
    return response.data;
  }
};

export default api; 