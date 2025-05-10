<template>
  <div class="portfolio-container fade-in">
    <el-container>
      <el-header class="portfolio-header enhanced-header">
        <div class="header-content">
          <div class="header-left">
            <img src="https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/svg/1f4b0.svg" alt="logo" class="logo" />
            <h2>My Portfolios</h2>
          </div>
          <div class="header-right">
            <el-button class="round-btn gradient-btn" type="primary" @click="showCreateModal = true">Create New Portfolio</el-button>
            <el-button class="round-btn gradient-btn" type="primary" @click="$router.push('/home')">Back to Dashboard</el-button>
          </div>
        </div>
      </el-header>

      <el-main class="portfolio-content">
        <!-- Portfolio List -->
        <el-row :gutter="20">
          <el-col :span="24">
            <el-card class="enhanced-card fade-in">
              <div v-if="loading" class="loading-state">
                <el-icon class="is-loading"><Loading /></el-icon>
                <span>Loading...</span>
              </div>
              <div v-else-if="portfolios.length === 0" class="empty-state">
                No portfolios yet. Click the button above to create a new portfolio.
              </div>
              <div v-else class="portfolio-grid">
                <el-card v-for="portfolio in portfolios" :key="portfolio.id" class="portfolio-card enhanced-card fade-in">
                  <div class="portfolio-card-header">
                    <h3>{{ portfolio.name }}</h3>
                    <el-button class="remove-btn gradient-btn" type="danger" size="small" @click="deletePortfolio(portfolio.id)">Delete</el-button>
                  </div>
                  <div class="portfolio-info">
                    <p>Created: {{ formatDate(portfolio.start_date) }}</p>
                    <div class="ticker-list">
                      <div v-for="item in portfolio.weightsArray" :key="item.ticker" class="ticker-item">
                        <span>{{ item.ticker }}</span>
                        <span>{{ (item.weight * 100).toFixed(2) }}%</span>
                      </div>
                    </div>
                  </div>
                </el-card>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </el-main>
    </el-container>

    <!-- Create Portfolio Modal -->
    <el-dialog
      v-model="showCreateModal"
      title="Create New Portfolio"
      width="50%"
      :close-on-click-modal="false"
      class="enhanced-dialog fade-in"
    >
      <el-form :model="newPortfolio" :rules="rules" ref="portfolioForm" label-width="120px">
        <el-form-item label="Portfolio Name" prop="name">
          <el-input v-model="newPortfolio.name" placeholder="Enter portfolio name" class="enhanced-input"></el-input>
        </el-form-item>
        <el-form-item label="Start Date" prop="start_date">
          <el-date-picker
            v-model="newPortfolio.start_date"
            type="date"
            placeholder="Select start date"
            style="width: 100%"
            class="enhanced-input"
          ></el-date-picker>
        </el-form-item>
        <el-form-item label="Stock Allocation">
          <div v-for="(item, index) in newPortfolio.items" :key="index" class="ticker-input">
            <el-select
              v-model="item.ticker"
              filterable
              placeholder="Select stock"
              style="width: 200px"
              class="enhanced-input"
            >
              <el-option
                v-for="stock in availableStocks"
                :key="stock.ticker"
                :label="`${stock.ticker} - ${stock.name}`"
                :value="stock.ticker"
                :disabled="isTickerSelected(stock.ticker, index)"
              >
                <span>{{ stock.ticker }}</span>
                <span style="float: right; color: #8492a6; font-size: 13px">
                  {{ stock.name }}
                </span>
              </el-option>
            </el-select>
            <el-input-number
              v-model="item.weight"
              :min="0"
              :max="1"
              :step="0.01"
              :precision="2"
              placeholder="Weight"
              style="width: 150px"
              class="enhanced-input"
            ></el-input-number>
            <el-button class="remove-btn gradient-btn" type="danger" @click="removeTicker(index)" :disabled="newPortfolio.items.length === 1">
              Remove
            </el-button>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button class="round-btn gradient-btn" type="primary" @click="addTicker">Add Stock</el-button>
          <el-button class="round-btn gradient-btn" @click="showCreateModal = false">Cancel</el-button>
          <el-button class="round-btn gradient-btn" type="primary" @click="submitPortfolio" :loading="submitting">
            Create
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { portfolioService, marketService } from '../services/api';

const portfolios = ref([]);
const loading = ref(false);
const showCreateModal = ref(false);
const submitting = ref(false);
const portfolioForm = ref(null);
const availableStocks = ref([]);

const newPortfolio = ref({
  name: '',
  start_date: '',
  items: [{ ticker: '', weight: 0 }]
});

const rules = {
  name: [
    { required: true, message: 'Please enter portfolio name', trigger: 'blur' },
    { min: 2, max: 50, message: 'Length should be 2 to 50 characters', trigger: 'blur' }
  ],
  start_date: [
    { required: true, message: 'Please select start date', trigger: 'change' }
  ]
};

const loadPortfolios = async () => {
  loading.value = true;
  try {
    const response = await portfolioService.getAllPortfolios();
    console.log('Portfolio response:', response.data);
    
    portfolios.value = (response.data.portfolios || []).map(portfolio => {
      console.log('Processing portfolio:', portfolio);
      
      const weightsArray = portfolio.tickers.map((ticker, index) => ({
        ticker,
        weight: parseFloat(portfolio.weights[index])
      }));

      return {
        ...portfolio,
        id: portfolio.ptfid,
        weightsArray,
        start_date: portfolio.start_date || portfolio.created_at || new Date().toISOString().split('T')[0]
      };
    });
    console.log('Processed portfolios:', portfolios.value);
  } catch (error) {
    console.error('Load portfolios error:', error);
    ElMessage.error('Failed to load portfolios: ' + (error.response?.data?.detail || error.message));
  } finally {
    loading.value = false;
  }
};

const loadAvailableStocks = async () => {
  try {
    const response = await marketService.getAllStocks();
    availableStocks.value = response.stocks || [];
  } catch (error) {
    console.error('Failed to load available stocks:', error);
    ElMessage.error('Failed to load available stocks');
  }
};

const isTickerSelected = (ticker, currentIndex) => {
  if (!ticker) return false;
  return newPortfolio.value.items.some((item, index) => 
    index !== currentIndex && item.ticker === ticker
  );
};

const submitPortfolio = async () => {
  if (!portfolioForm.value) return;
  
  await portfolioForm.value.validate(async (valid) => {
    if (!valid) return;
    
    submitting.value = true;
    try {
      const tickers = [];
      const weights = [];
      let totalWeight = 0;
      
      newPortfolio.value.items.forEach(item => {
        if (item.ticker && item.weight) {
          tickers.push(item.ticker);
          const weight = parseFloat(item.weight);
          weights.push(weight);
          totalWeight += weight;
        }
      });

      if (Math.abs(totalWeight - 1) > 0.0001) {
        ElMessage.error('Total weight must equal 1');
        return;
      }

      const formattedDate = newPortfolio.value.start_date instanceof Date 
        ? newPortfolio.value.start_date.toISOString().split('T')[0]
        : newPortfolio.value.start_date;

      const portfolioData = {
        name: newPortfolio.value.name,
        start_date: formattedDate,
        tickers: tickers,
        weights: weights
      };

      console.log('Sending portfolio data:', portfolioData);

      const response = await portfolioService.createPortfolio(portfolioData);
      console.log('Create portfolio response:', response.data);

      ElMessage.success('Portfolio created successfully');
      showCreateModal.value = false;
      await loadPortfolios();
      resetForm();
    } catch (error) {
      console.error('Create portfolio error:', error);
      console.error('Error response:', error.response?.data);
      ElMessage.error('Failed to create portfolio: ' + (error.response?.data?.detail || error.message));
    } finally {
      submitting.value = false;
    }
  });
};

const deletePortfolio = async (id) => {
  if (!id) {
    ElMessage.error('Invalid portfolio ID');
    return;
  }

  try {
    await ElMessageBox.confirm(
      'Are you sure you want to delete this portfolio? This action cannot be undone.',
      'Warning',
      {
        confirmButtonText: 'Confirm',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }
    );
    
    await portfolioService.deletePortfolio(id);
    ElMessage.success('Portfolio deleted successfully');
    await loadPortfolios();
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Delete portfolio error:', error);
      ElMessage.error('Failed to delete portfolio: ' + (error.response?.data?.detail || error.message));
    }
  }
};

const addTicker = () => {
  newPortfolio.value.items.push({ ticker: '', weight: 0 });
};

const removeTicker = (index) => {
  newPortfolio.value.items.splice(index, 1);
};

const resetForm = () => {
  if (portfolioForm.value) {
    portfolioForm.value.resetFields();
  }
  newPortfolio.value = {
    name: '',
    start_date: '',
    items: [{ ticker: '', weight: 0 }]
  };
};

const formatDate = (date) => {
  if (!date) {
    console.log('No date provided');
    return 'Not set';
  }
  try {
    console.log('Formatting date:', date, 'Type:', typeof date);
    const dateObj = typeof date === 'string' ? new Date(date) : date;
    if (isNaN(dateObj.getTime())) {
      console.error('Invalid date:', date);
      return 'Invalid date';
    }
    return dateObj.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  } catch (error) {
    console.error('Date formatting error:', error, 'Date value:', date);
    return 'Invalid date';
  }
};

onMounted(() => {
  loadPortfolios();
  loadAvailableStocks();
});
</script>

<style scoped>
.portfolio-container {
  min-height: 100vh;
  width: 100vw;
  background: linear-gradient(135deg, #f5f7fa 60%, #e3eaff 100%);
  margin: 0;
  padding: 0;
  overflow-x: hidden;
  position: fixed;
  top: 0;
  left: 0;
}

.portfolio-header.enhanced-header {
  background: linear-gradient(90deg, #409eff 0%, #36cfc9 100%);
  box-shadow: 0 4px 16px rgba(64, 158, 255, 0.08);
  width: 100%;
  padding: 0;
  position: fixed;
  top: 0;
  left: 0;
  z-index: 1000;
  height: 60px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
  width: 100%;
  margin: 0;
  padding: 0 32px;
  box-sizing: border-box;
}

.header-content h2 {
  margin: 0;
  font-size: 24px;
  color: #fff;
}

.portfolio-content {
  margin-top: 60px;
  padding: 20px;
  width: 100%;
  max-width: none;
  box-sizing: border-box;
  min-height: calc(100vh - 60px);
}

.portfolio-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
  padding: 1rem;
}

.portfolio-card {
  transition: all 0.3s ease;
}

.portfolio-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.portfolio-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.portfolio-card-header h3 {
  margin: 0;
  font-size: 18px;
  color: #2c3e50;
}

.portfolio-info {
  color: #606266;
}

.ticker-list {
  margin-top: 1rem;
}

.ticker-item {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem 0;
  border-bottom: 1px solid #eee;
}

.ticker-item:last-child {
  border-bottom: none;
}

.ticker-input {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
  align-items: center;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  color: #666;
}

.empty-state {
  text-align: center;
  padding: 2rem;
  color: #666;
  background: #f5f7fa;
  border-radius: 8px;
}

.enhanced-card {
  border-radius: 12px;
  border: none;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.enhanced-card:hover {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
}

.enhanced-input {
  border-radius: 8px;
}

.round-btn {
  border-radius: 20px;
  padding: 8px 20px;
}

.gradient-btn {
  background: linear-gradient(90deg, #409eff 0%, #36cfc9 100%);
  border: none;
  color: white;
}

.gradient-btn:hover {
  background: linear-gradient(90deg, #66b1ff 0%, #5cdbd3 100%);
  color: white;
}

.remove-btn {
  background: linear-gradient(90deg, #f56c6c 0%, #ff9c9c 100%);
  border: none;
  color: white;
}

.remove-btn:hover {
  background: linear-gradient(90deg, #f78989 0%, #ffb3b3 100%);
  color: white;
}

.logo {
  width: 36px;
  height: 36px;
  margin-right: 14px;
  vertical-align: middle;
}

.header-left {
  display: flex;
  align-items: center;
}

.fade-in {
  animation: fadeIn 0.7s;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Responsive layout */
@media screen and (min-width: 1200px) {
  .portfolio-content {
    padding: 30px 60px;
  }
  .header-content {
    padding: 0 60px;
  }
}

@media screen and (min-width: 1600px) {
  .portfolio-content {
    padding: 40px 80px;
  }
  .header-content {
    padding: 0 80px;
  }
}

@media screen and (max-width: 768px) {
  .portfolio-content {
    padding: 15px;
  }
  .header-content {
    padding: 0 15px;
  }
  .portfolio-grid {
    grid-template-columns: 1fr;
  }
}

body, .portfolio-container {
  font-family: 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', Arial, sans-serif;
  font-weight: 400;
  letter-spacing: 0.1px;
}
</style>