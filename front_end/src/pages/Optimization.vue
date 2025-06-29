<template>
  <div class="optimization-container fade-in">
    <el-container>
      <el-header class="optimization-header enhanced-header">
        <div class="header-content">
          <div class="header-left">
            <img src="https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/svg/1f4b0.svg" alt="logo" class="logo" />
            <h2>Portfolio Optimization</h2>
          </div>
          <div class="header-right">
            <el-button class="round-btn gradient-btn" type="primary" @click="$router.push('/home')">Back to Dashboard</el-button>
          </div>
        </div>
      </el-header>

      <el-main class="optimization-content">
        <!-- Portfolio Selection -->
        <el-row :gutter="20">
          <el-col :span="24">
            <el-card class="enhanced-card fade-in">
              <template #header>
                <div class="card-header">
                  <span>Select Portfolio to Optimize</span>
                </div>
              </template>
              <div v-if="loading" class="loading-state">
                <el-icon class="is-loading"><Loading /></el-icon>
                <span>Loading portfolios...</span>
              </div>
              <div v-else class="portfolio-selection">
                <el-button-group class="mode-selection">
                  <el-button
                    :type="optimizationMode === 'existing' ? 'primary' : 'default'"
                    class="round-btn gradient-btn"
                    @click="optimizationMode = 'existing'; handleModeChange();"
                  >
                    Optimize Existing Portfolio
                  </el-button>
                  <el-button
                    :type="optimizationMode === 'new' ? 'primary' : 'default'"
                    class="round-btn gradient-btn"
                    @click="optimizationMode = 'new'; handleModeChange();"
                  >
                    Create New Portfolio from Scratch
                  </el-button>
                </el-button-group>
                
                <div v-if="optimizationMode === 'existing'" class="portfolio-dropdown">
                  <el-select 
                    v-model="selectedPortfolioId" 
                    placeholder="Select a portfolio to optimize"
                    style="width: 100%"
                    @change="handlePortfolioChange"
                  >
                    <el-option
                      v-for="portfolio in portfolios"
                      :key="portfolio.id"
                      :label="portfolio.name"
                      :value="portfolio.id"
                    >
                      <div class="portfolio-option">
                        <span class="portfolio-name">{{ portfolio.name }}</span>
                        <span class="portfolio-date">Created: {{ formatDate(portfolio.start_date) }}</span>
                      </div>
                    </el-option>
                  </el-select>
                </div>
                
                <div v-if="optimizationMode === 'new'" class="new-portfolio-setup">
                  <el-form label-width="120px">
                    <el-form-item label="Stock Selection">
                      <div v-for="(item, index) in newPortfolio.items" :key="index" class="ticker-input">
                        <el-select
                          v-model="item.ticker"
                          filterable
                          placeholder="Select stock"
                          style="width: 300px"
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
                        <el-button class="remove-btn gradient-btn" type="danger" @click="removeTicker(index)" :disabled="newPortfolio.items.length === 1">
                          Remove
                        </el-button>
                      </div>
                    </el-form-item>
                  </el-form>
                  <div class="dialog-footer">
                    <el-button class="round-btn gradient-btn" type="primary" @click="addTicker">Add Stock</el-button>
                  </div>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>

        <!-- Optimization Form -->
        <el-row :gutter="20" class="mt-20" v-if="optimizationMode === 'existing' ? selectedPortfolioId : true">
          <el-col :span="24">
            <el-card class="enhanced-card fade-in">
              <template #header>
                <div class="card-header">
                  <span>Optimization Parameters</span>
                </div>
              </template>
              <el-form :model="optimizeForm" label-width="140px" class="optimization-form">
                <el-row :gutter="24">
                  <el-col :span="12">
                    <el-form-item label="Optimization Metric">
                      <el-select v-model="optimizeForm.metric" style="width: 100%">
                        <el-option 
                          v-for="item in optimizeMetricsOptions" 
                          :key="item.value" 
                          :label="item.label" 
                          :value="item.value" 
                        />
                      </el-select>
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item label="Data Interval">
                      <el-select v-model="optimizeForm.interval" style="width: 100%">
                        <el-option label="Daily" value="1d" />
                        <el-option label="Weekly" value="1wk" />
                        <el-option label="Monthly" value="1mo" />
                      </el-select>
                    </el-form-item>
                  </el-col>
                </el-row>
                <el-row :gutter="24">
                  <el-col :span="12">
                    <el-form-item label="Start Date">
                      <el-date-picker 
                        v-model="optimizeForm.start_date" 
                        type="date" 
                        placeholder="Select start date" 
                        style="width: 100%" 
                      />
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item label="End Date">
                      <el-date-picker 
                        v-model="optimizeForm.end_date" 
                        type="date" 
                        placeholder="Select end date" 
                        style="width: 100%" 
                      />
                    </el-form-item>
                  </el-col>
                </el-row>
                <el-row :gutter="24">
                  <el-col :span="12">
                    <el-form-item label="Allow Short Selling">
                      <el-switch v-model="optimizeForm.allow_short" />
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item>
                      <el-button 
                        type="primary" 
                        class="gradient-btn" 
                        :loading="optimizing" 
                        @click="submitOptimize"
                        style="width: 100%"
                      >
                        Start Optimization
                      </el-button>
                    </el-form-item>
                  </el-col>
                </el-row>
              </el-form>
            </el-card>
          </el-col>
        </el-row>

        <!-- Optimization Results -->
        <el-row :gutter="20" class="mt-20" v-if="optimizeResult">
          <el-col :span="24">
            <el-card class="enhanced-card fade-in">
              <template #header>
                <div class="card-header">
                  <span>Optimization Results</span>
                  <div class="header-actions">
                    <el-button 
                      v-if="optimizationMode === 'new' && optimizeResult?.optimized_weights"
                      type="success" 
                      size="large"
                      class="round-btn gradient-btn"
                      @click="showCreatePortfolioModal = true"
                    >
                      Create Portfolio with Optimized Weights
                    </el-button>
                    <el-button 
                      v-if="optimizationMode === 'existing' && optimizeResult?.optimized_weights"
                      type="success" 
                      size="small" 
                      @click="applyOptimization"
                    >
                      Apply to Portfolio
                    </el-button>
                  </div>
                </div>
              </template>
              <div class="optimization-results">
                <div class="result-summary">
                  <div class="summary-item">
                    <span class="label">Optimization Metric:</span>
                    <span class="value">{{ optimizeResult.metric }}</span>
                  </div>
                  <div class="summary-item" v-if="optimizeResult.original_metric">
                    <span class="label">Original Metric Value:</span>
                    <span class="value">{{ formatMetricValue(optimizeResult.original_metric, optimizeForm.metric) }}</span>
                  </div>
                  <div class="summary-item" v-if="optimizeResult.optimized_metric">
                    <span class="label">Optimized Metric Value:</span>
                    <span class="value text-green-500">{{ formatMetricValue(optimizeResult.optimized_metric, optimizeForm.metric) }}</span>
                  </div>
                </div>
                
                <div v-if="optimizeResult.optimized_weights && optimizeResult.tickers" class="weights-table">
                  <h4>Optimized Weights</h4>
                  <el-table
                    :data="optimizeResult.tickers.map(ticker => ({
                      ticker,
                      weight: optimizeResult.optimized_weights[ticker]
                    }))"
                    style="width: 100%"
                    :cell-style="{ textAlign: 'center' }"
                    :header-cell-style="{ textAlign: 'center' }"
                  >
                    <el-table-column prop="ticker" label="Stock Ticker" min-width="200">
                      <template #default="scope">
                        <div class="ticker-cell">
                          <span class="ticker-symbol">{{ scope.row.ticker }}</span>
                        </div>
                      </template>
                    </el-table-column>
                    <el-table-column prop="weight" label="Weight" min-width="200">
                      <template #default="scope">
                        <span v-if="!isNaN(scope.row.weight)" class="weight-value">
                          {{ (scope.row.weight * 100).toFixed(2) }}%
                        </span>
                        <span v-else class="weight-value no-data">
                          No data
                        </span>
                      </template>
                    </el-table-column>
                    <el-table-column label="Actions" min-width="150">
                      <template #default="scope">
                        <el-button 
                          type="text" 
                          @click="showStockInfo(scope.row.ticker)"
                          class="ticker-link"
                        >
                          <el-icon style="margin-right: 4px;"><View /></el-icon>
                          View Details
                        </el-button>
                      </template>
                    </el-table-column>
                  </el-table>
                </div>
                
                <div v-else class="no-result">
                  <el-empty description="No optimization result available" />
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </el-main>
    </el-container>

    <!-- Stock Detail Modal -->
    <StockDetailModal
      v-model="showStockDetailModal"
      :ticker="selectedTicker"
    />

    <!-- Create Portfolio Modal -->
    <el-dialog
      v-model="showCreatePortfolioModal"
      title="Create New Portfolio with Optimized Weights"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form :model="createPortfolioForm" :rules="createPortfolioRules" ref="createPortfolioFormRef" label-width="120px">
        <el-form-item label="Portfolio Name" prop="name">
          <el-input v-model="createPortfolioForm.name" placeholder="Enter portfolio name" />
        </el-form-item>
        <el-form-item label="Start Date">
          <span class="start-date-display">{{ formatDate(optimizeForm.start_date) }}</span>
        </el-form-item>
        <el-form-item label="Selected Stocks">
          <div class="selected-stocks">
            <div v-for="item in newPortfolio.items.filter(item => item.ticker)" :key="item.ticker" class="stock-item">
              <span class="stock-ticker">{{ item.ticker }}</span>
              <span class="stock-weight">{{ (optimizeResult.optimized_weights[item.ticker] * 100).toFixed(2) }}%</span>
            </div>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreatePortfolioModal = false">Cancel</el-button>
        <el-button type="primary" :loading="creatingPortfolio" @click="createPortfolioFromOptimization">
          Create Portfolio
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { 
  Loading, 
  ArrowLeft, 
  Collection, 
  Setting, 
  DataAnalysis, 
  TrendCharts, 
  Check, 
  Histogram, 
  View 
} from '@element-plus/icons-vue';
import { portfolioService, marketService } from '../services/api';
import StockDetailModal from '../components/StockDetailModal.vue';

const portfolios = ref([]);
const loading = ref(false);
const selectedPortfolioId = ref(null);
const optimizing = ref(false);
const optimizeResult = ref(null);
const showStockDetailModal = ref(false);
const selectedTicker = ref(null);
const optimizationMode = ref('existing');
const showCreatePortfolioModal = ref(false);
const creatingPortfolio = ref(false);
const createPortfolioFormRef = ref(null);
const showCreateModal = ref(false);
const submitting = ref(false);
const portfolioForm = ref(null);
const availableStocks = ref([]);

const optimizeForm = ref({
  metric: 'sharpe',
  start_date: '',
  end_date: '',
  interval: '1d',
  allow_short: false
});

const newPortfolio = ref({
  name: '',
  start_date: '',
  items: [{ ticker: '' }]
});

const createPortfolioForm = ref({
  name: ''
});

const createPortfolioRules = {
  name: [
    { required: true, message: 'Please enter portfolio name', trigger: 'blur' }
  ]
};

const rules = {
  name: [
    { required: true, message: 'Please enter portfolio name', trigger: 'blur' },
    { min: 2, max: 50, message: 'Length should be 2 to 50 characters', trigger: 'blur' }
  ],
  start_date: [
    { required: true, message: 'Please select start date', trigger: 'change' }
  ]
};

const optimizeMetricsOptions = [
  { label: 'Sharpe Ratio', value: 'sharpe' },
  { label: 'Sortino Ratio', value: 'sortino' },
  { label: 'Total Return', value: 'total return' },
  { label: 'Weekly Return', value: 'weekly return' },
  { label: 'Daily Return', value: 'daily return' }
];

const loadPortfolios = async () => {
  loading.value = true;
  try {
    const response = await portfolioService.getAllPortfolios();
    portfolios.value = (response.data.portfolios || []).map(portfolio => {
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

const handlePortfolioChange = () => {
  if (selectedPortfolioId.value) {
    const portfolio = portfolios.value.find(p => p.id === selectedPortfolioId.value);
    if (portfolio) {
      optimizeForm.value.start_date = portfolio.start_date ? new Date(portfolio.start_date) : '';
      optimizeForm.value.end_date = new Date();
    }
  }
  optimizeResult.value = null;
};

const handleModeChange = () => {
  if (optimizationMode.value === 'new') {
    optimizeForm.value.start_date = '';
    optimizeForm.value.end_date = '';
    optimizeForm.value.allow_short = false;
    newPortfolio.value.items = [{ ticker: '' }];
  }
  optimizeResult.value = null;
};

const submitOptimize = async () => {
  if (optimizationMode.value === 'existing' && !selectedPortfolioId.value) {
    ElMessage.warning('Please select a portfolio first');
    return;
  }
  
  if (optimizationMode.value === 'new') {
    const validItems = newPortfolio.value.items.filter(item => item.ticker);
    
    if (validItems.length < 2) {
      ElMessage.warning('Please add at least 2 stocks');
      return;
    }
    
    // Check for duplicates
    const tickers = validItems.map(item => item.ticker);
    const uniqueTickers = [...new Set(tickers)];
    if (uniqueTickers.length !== tickers.length) {
      ElMessage.warning('Please remove duplicate stocks');
      return;
    }
  }

  optimizing.value = true;
  try {
    const startDate = optimizeForm.value.start_date instanceof Date
      ? optimizeForm.value.start_date.toISOString().split('T')[0]
      : optimizeForm.value.start_date;
    const endDate = optimizeForm.value.end_date instanceof Date
      ? optimizeForm.value.end_date.toISOString().split('T')[0]
      : optimizeForm.value.end_date;

    let params;
    
    if (optimizationMode.value === 'existing') {
      params = {
        metric: optimizeForm.value.metric,
        start_date: startDate,
        end_date: endDate,
        interval: optimizeForm.value.interval,
        allow_short: optimizeForm.value.allow_short
      };
      const response = await portfolioService.optimizePortfolio(selectedPortfolioId.value, params);
      optimizeResult.value = response.data;
    } else {
      // New portfolio optimization
      const validItems = newPortfolio.value.items.filter(item => item.ticker);
      const tickers = validItems.map(item => item.ticker);
      
      params = {
        tickers: tickers,
        metric: optimizeForm.value.metric,
        start_date: startDate,
        end_date: endDate,
        interval: optimizeForm.value.interval,
        allow_short: optimizeForm.value.allow_short
      };
      const response = await portfolioService.optimizeNewPortfolio(params);
      optimizeResult.value = response.data;
    }
    
    ElMessage.success('Optimization completed successfully');
  } catch (error) {
    console.error('Optimization error:', error);
    ElMessage.error('Optimization failed: ' + (error.response?.data?.detail || error.message));
  } finally {
    optimizing.value = false;
  }
};

const applyOptimization = async () => {
  if (!optimizeResult.value?.optimized_weights) {
    ElMessage.warning('No optimization result to apply');
    return;
  }

  try {
    await ElMessageBox.confirm(
      'Are you sure you want to apply the optimized weights to your portfolio? This will update the current portfolio weights.',
      'Confirm Application',
      {
        confirmButtonText: 'Apply',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }
    );

    const tickers = Object.keys(optimizeResult.value.optimized_weights);
    const weights = tickers.map(ticker => optimizeResult.value.optimized_weights[ticker]);

    const updateData = {
      tickers: tickers,
      weights: weights
    };

    await portfolioService.updatePortfolio(selectedPortfolioId.value, updateData);
    ElMessage.success('Portfolio updated successfully with optimized weights');
    
    // Refresh portfolios list
    await loadPortfolios();
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Apply optimization error:', error);
      ElMessage.error('Failed to apply optimization: ' + (error.response?.data?.detail || error.message));
    }
  }
};

const showStockInfo = async (ticker) => {
  try {
    selectedTicker.value = ticker;
    showStockDetailModal.value = true;
  } catch (error) {
    console.error('Error opening stock detail:', error);
    ElMessage.error('Failed to open stock detail');
  }
};

const formatDate = (date) => {
  if (!date) return 'Not set';
  try {
    const dateObj = typeof date === 'string' ? new Date(date) : date;
    if (isNaN(dateObj.getTime())) return 'Invalid date';
    return dateObj.toLocaleDateString('en-US', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit'
    }).replace(/\//g, '-');
  } catch (error) {
    return 'Invalid date';
  }
};

const formatMetricValue = (value, key) => {
  if (value === null || value === undefined || isNaN(value)) return 'N/A';
  
  const numValue = parseFloat(value);
  if (isNaN(numValue)) return 'N/A';
  
  if (key.includes('return')) {
    return (numValue * 100).toFixed(2) + '%';
  } else if (key === 'max_drawdown' || key === 'volatility') {
    return (numValue * 100).toFixed(2) + '%';
  } else {
    return numValue.toFixed(2);
  }
};

const addTicker = () => {
  newPortfolio.value.items.push({ ticker: '' });
};

const removeTicker = (index) => {
  newPortfolio.value.items.splice(index, 1);
};

const createPortfolioFromOptimization = async () => {
  const formRef = createPortfolioFormRef.value;
  if (!formRef) return;
  
  try {
    await formRef.validate();
  } catch (error) {
    return;
  }
  
  creatingPortfolio.value = true;
  try {
    const validItems = newPortfolio.value.items.filter(item => item.ticker);
    const tickers = validItems.map(item => item.ticker);
    
    // Convert optimized_weights from object to array format
    const weights = tickers.map(ticker => optimizeResult.value.optimized_weights[ticker]);
    
    const portfolioData = {
      name: createPortfolioForm.value.name,
      start_date: optimizeForm.value.start_date.toISOString().split('T')[0],
      tickers: tickers,
      weights: weights
    };
    
    await portfolioService.createPortfolio(portfolioData);
    
    ElMessage.success('Portfolio created successfully with optimized weights');
    showCreatePortfolioModal.value = false;
    
    // Reset form
    createPortfolioForm.value = {
      name: ''
    };
    
    // Refresh portfolios list
    await loadPortfolios();
    
  } catch (error) {
    console.error('Create portfolio error:', error);
    ElMessage.error('Failed to create portfolio: ' + (error.response?.data?.detail || error.message));
  } finally {
    creatingPortfolio.value = false;
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

      const response = await portfolioService.createPortfolio(portfolioData);

      ElMessage.success('Portfolio created successfully');
      showCreateModal.value = false;
      await loadPortfolios();
      resetForm();
    } catch (error) {
      console.error('Create portfolio error:', error);
      ElMessage.error('Failed to create portfolio: ' + (error.response?.data?.detail || error.message));
    } finally {
      submitting.value = false;
    }
  });
};

const resetForm = () => {
  if (portfolioForm.value) {
    portfolioForm.value.resetFields();
  }
  newPortfolio.value = {
    name: '',
    start_date: '',
    items: [{ ticker: '' }]
  };
};

onMounted(() => {
  loadPortfolios();
  loadAvailableStocks();
});
</script>

<style scoped>
.optimization-container {
  min-height: 100vh;
  width: 100vw;
  background: linear-gradient(135deg, #f5f7fa 60%, #e3eaff 100%);
  margin: 0;
  padding: 0;
  overflow-x: hidden;
  top: 0;
  left: 0;
}

.optimization-header.enhanced-header {
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

.header-left {
  display: flex;
  align-items: center;
}

.logo {
  width: 36px;
  height: 36px;
  margin-right: 14px;
  vertical-align: middle;
}

.optimization-content {
  margin-top: 60px;
  padding: 20px;
  width: 100%;
  max-width: none;
  box-sizing: border-box;
  min-height: calc(100vh - 60px);
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

.card-header {
  display: flex;
  justify-content: space-between;
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

.portfolio-selection {
  padding: 1rem 0;
}

.portfolio-option {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.portfolio-name {
  font-weight: 500;
}

.portfolio-date {
  color: #909399;
  font-size: 12px;
}

.optimization-form {
  padding: 1rem 0;
}

.optimization-form :deep(.el-form-item__label) {
  font-weight: 500;
  color: #2c3e50;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.optimization-form :deep(.el-form-item) {
  margin-bottom: 20px;
}

.mt-20 {
  margin-top: 20px;
}

.round-btn {
  border-radius: 20px;
  padding: 8px 20px;
  font-weight: 500;
  font-size: 15px;
  color: #fff !important;
  background: linear-gradient(90deg, #409eff 0%, #36cfc9 100%) !important;
  border: none !important;
  box-shadow: none;
  transition: background 0.3s;
}

.round-btn:hover, .round-btn:focus {
  background: linear-gradient(90deg, #66b1ff 0%, #5cdbd3 100%) !important;
  color: #fff !important;
}

.gradient-btn {
  background: linear-gradient(90deg, #409eff 0%, #36cfc9 100%) !important;
  border: none !important;
  color: #fff !important;
  box-shadow: none;
}

.gradient-btn:hover, .gradient-btn:focus {
  background: linear-gradient(90deg, #66b1ff 0%, #5cdbd3 100%) !important;
  color: #fff !important;
}

.el-button-group .el-button {
  margin-right: 0 !important;
}

.mode-selection {
  margin-bottom: 20px;
  width: 100%;
  display: flex;
  gap: 10px;
  justify-content: flex-start;
}

.optimization-results {
  padding: 1rem 0;
}

.result-summary {
  display: flex;
  gap: 40px;
  margin-bottom: 30px;
  flex-wrap: wrap;
}

.summary-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
  min-width: 200px;
}

.summary-item .label {
  font-size: 14px;
  color: #666;
}

.summary-item .value {
  font-size: 18px;
  font-weight: 600;
}

.weights-table {
  margin-top: 20px;
}

.weights-table h4 {
  margin-bottom: 16px;
  color: #2c3e50;
  font-size: 16px;
  font-weight: 600;
}

.no-result {
  text-align: center;
  padding: 2rem;
}

.ticker-cell {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.ticker-link {
  color: #409EFF;
  text-decoration: none;
  cursor: pointer;
}

.ticker-link:hover {
  color: #66b1ff;
  text-decoration: underline;
}

.text-green-500 {
  color: #67c23a;
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
  .optimization-content {
    padding: 30px 60px;
  }
  .header-content {
    padding: 0 60px;
  }
}

@media screen and (min-width: 1600px) {
  .optimization-content {
    padding: 40px 80px;
  }
  .header-content {
    padding: 0 80px;
  }
}

@media screen and (max-width: 768px) {
  .optimization-content {
    padding: 15px;
  }
  .header-content {
    padding: 0 15px;
  }
  .result-summary {
    flex-direction: column;
  }
}

/* Element Plus table customization */
:deep(.el-table) {
  --el-table-border-color: #ebeef5;
  --el-table-header-bg-color: #f5f7fa;
  border-radius: 12px;
}

:deep(.el-table th) {
  font-weight: 600;
  color: #2c3e50;
  background: #f5f7fa;
  text-align: center !important;
}

:deep(.el-table td) {
  color: #606266;
  text-align: center !important;
}

:deep(.el-table--border) {
  border: 1px solid #e9ecef;
}

:deep(.el-table__cell) {
  text-align: center !important;
}

/* Form customization */
:deep(.el-input__wrapper) {
  border-radius: 8px;
}

:deep(.el-select .el-input__wrapper) {
  border-radius: 8px;
}

:deep(.el-date-editor) {
  border-radius: 8px;
}

.portfolio-dropdown {
  margin-top: 15px;
}

.new-portfolio-setup {
  margin-top: 15px;
}

.ticker-input {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
  align-items: center;
}

.add-ticker-btn {
  margin-top: 10px;
}

.header-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.enhanced-input {
  border-radius: 8px;
}

.remove-btn {
  background: linear-gradient(90deg, #f56c6c 0%, #ff9c9c 100%) !important;
  border: none !important;
  color: #fff !important;
  box-shadow: none;
  font-weight: 500;
  font-size: 15px;
  border-radius: 20px;
  padding: 8px 20px;
  transition: background 0.3s;
}

.remove-btn:hover, .remove-btn:focus {
  background: linear-gradient(90deg, #f78989 0%, #ffb3b3 100%) !important;
  color: #fff !important;
}

.dialog-footer {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

.selected-stocks {
  max-height: 200px;
  overflow-y: auto;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 10px;
  background: #f8f9fa;
}

.stock-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  margin-bottom: 8px;
  background: white;
  border-radius: 6px;
  border: 1px solid #e4e7ed;
}

.stock-item:last-child {
  margin-bottom: 0;
}

.stock-ticker {
  font-weight: 600;
  color: #2c3e50;
}

.stock-weight {
  color: #409eff;
  font-weight: 500;
}

.start-date-display {
  color: #606266;
  font-weight: 500;
  padding: 8px 12px;
  background: #f8f9fa;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  display: inline-block;
}
</style> 