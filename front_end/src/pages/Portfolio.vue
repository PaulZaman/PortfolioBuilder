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
                <el-card 
                  v-for="portfolio in portfolios" 
                  :key="portfolio.id" 
                  class="portfolio-card enhanced-card fade-in cursor-pointer"
                  @click="showPortfolioDetails(portfolio)"
                >
                  <div class="portfolio-card-header">
                    <h3>{{ portfolio.name }}</h3>
                    <el-button 
                      class="remove-btn gradient-btn" 
                      type="danger" 
                      size="small" 
                      @click.stop="deletePortfolio(portfolio.id)"
                    >
                      Delete
                    </el-button>
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

    <!-- Portfolio Details Dialog -->
    <el-dialog
      v-model="showDetailsModal"
      :title="selectedPortfolio?.name"
      width="80%"
      class="portfolio-details-dialog"
    >
      <div v-if="selectedPortfolio" class="portfolio-details">
        <!-- Time Frame Selection -->
        <div class="time-frame-selection">
          <el-select v-model="selectedTimeFrame" class="time-frame-select" @change="handleTimeFrameChange">
            <el-option label="Daily" value="daily" />
            <el-option label="Weekly" value="weekly" />
            <el-option label="Monthly" value="monthly" />
            <el-option label="Quarterly" value="quarterly" />
          </el-select>
          
          <el-date-picker
            v-model="selectedStartDate"
            type="date"
            placeholder="Start Date"
            @change="handleDateChange"
          />
          
          <el-date-picker
            v-model="selectedEndDate"
            type="date"
            placeholder="End Date"
            @change="handleDateChange"
          />
          <el-button 
          class="gradient-btn" 
          type="primary" 
          @click="showOptimizeDialog(selectedPortfolio)"
        >
          Optimize Portfolio
        </el-button>
          <!-- Chart Type Toggle -->
          <el-radio-group v-model="chartType" @change="handleChartTypeChange" class="chart-type-toggle">
            <el-radio-button label="cumulative">Cumulative Return</el-radio-button>
            <el-radio-button label="daily">Daily Return</el-radio-button>
          </el-radio-group>
        </div>

        <div class="portfolio-summary">
          <div class="summary-item" v-if="selectedPortfolio.metrics">
            <div class="metric-header">
              <span class="label">Total Return</span>
              <el-tooltip
                :content="metricsDefinitions?.total_cum_return || 'Total cumulative return over the full period.'"
                placement="top"
                effect="light"
              >
                <el-icon class="info-icon"><InfoFilled /></el-icon>
              </el-tooltip>
            </div>
            <span :class="['value', getPerformanceClass(selectedPortfolio.performance_cum?.[selectedPortfolio.performance_cum.length - 1])]">
              {{ formatPerformance(selectedPortfolio.performance_cum?.[selectedPortfolio.performance_cum.length - 1]) }}
            </span>
          </div>
          <div class="summary-item" v-if="selectedPortfolio.metrics">
            <div class="metric-header">
              <span class="label">Sharpe Ratio</span>
              <el-tooltip
                :content="metricsDefinitions?.sharpe_ratio || 'Annualized risk-adjusted return based on daily data'"
                placement="top"
                effect="light"
              >
                <el-icon class="info-icon"><InfoFilled /></el-icon>
              </el-tooltip>
            </div>
            <span class="value">{{ formatMetricValue(selectedPortfolio.metrics.sharpe_ratio, 'sharpe_ratio') }}</span>
          </div>
          <div class="summary-item" v-if="selectedPortfolio.metrics">
            <div class="metric-header">
              <span class="label">Max Drawdown</span>
              <el-tooltip
                :content="metricsDefinitions?.max_drawdown || 'Maximum observed loss from peak to trough, calculated from daily data'"
                placement="top"
                effect="light"
              >
                <el-icon class="info-icon"><InfoFilled /></el-icon>
              </el-tooltip>
            </div>
            <span class="value text-red-500">{{ formatMetricValue(selectedPortfolio.metrics.max_drawdown, 'max_drawdown') }}</span>
          </div>
          <div class="summary-item" v-if="selectedPortfolio.metrics">
            <div class="metric-header">
              <span class="label">Volatility</span>
              <el-tooltip
                :content="metricsDefinitions?.volatility || 'Annualized standard deviation of returns, calculated from daily data'"
                placement="top"
                effect="light"
              >
                <el-icon class="info-icon"><InfoFilled /></el-icon>
              </el-tooltip>
            </div>
            <span class="value">{{ formatMetricValue(selectedPortfolio.metrics.volatility, 'volatility') }}</span>
          </div>
          <!-- More Metrics Toggle Box -->
          <div class="summary-item" @click="showMoreMetrics = !showMoreMetrics" style="cursor: pointer;">
            <div class="metric-header">
              <span class="label">More Metrics</span>
              <el-tooltip content="Click to view more metrics and their explanations." placement="top" effect="light">
                <el-icon class="info-icon"><InfoFilled /></el-icon>
              </el-tooltip>
            </div>
            <span class="value text-blue-500">
              <span v-if="!showMoreMetrics">↓ Show</span>
              <span v-else>↑ Hide</span>
            </span>
          </div>
        </div>

        <!-- More Metrics Section -->
        <div v-if="showMoreMetrics" class="more-metrics-container mt-4">
          <div class="metric-row" v-for="key in [
            'mean_yearly_return',
            'sortino_ratio',
            'calmar_ratio',
            'hit_ratio',
            'mean_daily_return',
            'best_daily_return',
            'worst_daily_return'
          ]" :key="key">
            <span class="metric-label">{{ key.replace(/_/g, ' ').toUpperCase() }}</span>
            <el-tooltip :content="metricsDefinitions[key]" placement="top" effect="light">
              <el-icon class="info-icon"><InfoFilled /></el-icon>
            </el-tooltip>
            <span class="metric-value">
              {{ formatMetricValue(selectedPortfolio.metrics[key], key) }}
            </span>
          </div>
        </div>

        <!-- Performance Chart -->
        <div class="performance-chart">
          <div ref="chartContainer" style="width: 100%; height: 400px;"></div>
        </div>

        <!-- Holdings Table -->
        <div class="holdings-table">
          <h3>Portfolio Holdings</h3>
          <el-table 
            :data="selectedPortfolio.weightsArray" 
            style="width: 100%"
            :cell-style="{ textAlign: 'center' }"
            :header-cell-style="{ textAlign: 'center' }"
          >
            <el-table-column prop="ticker" label="Ticker" min-width="200">
              <template #default="scope">
                <el-button 
                  type="text" 
                  @click="showStockInfo(scope.row.ticker)"
                  class="ticker-link"
                >
                  {{ scope.row.ticker }}
                </el-button>
              </template>
            </el-table-column>
            <el-table-column prop="weight" label="Weight" min-width="200">
              <template #default="scope">
                {{ (scope.row.weight * 100).toFixed(2) }}%
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </el-dialog>

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

    <!-- Stock Detail Modal -->
    <StockDetailModal
      v-model="showStockDetailModal"
      :ticker="selectedTicker"
    />

    <!-- Optimize Portfolio Modal -->
    <el-dialog
      v-model="showOptimizeModal"
      title="Optimize Portfolio"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form :model="optimizeForm" label-width="100px">
        <el-form-item label="Optimization Metric">
          <el-select v-model="optimizeForm.metric" style="width: 100%">
            <el-option v-for="item in optimizeMetricsOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="Start Date">
          <el-date-picker v-model="optimizeForm.start_date" type="date" placeholder="Select start date" style="width: 100%" />
        </el-form-item>
        <el-form-item label="End Date">
          <el-date-picker v-model="optimizeForm.end_date" type="date" placeholder="Select end date" style="width: 100%" />
        </el-form-item>
        <el-form-item label="Data Interval">
          <el-select v-model="optimizeForm.interval" style="width: 100%">
            <el-option label="Daily" value="1d" />
            <el-option label="Weekly" value="1wk" />
            <el-option label="Monthly" value="1mo" />
          </el-select>
        </el-form-item>
        <el-form-item label="Allow Short">
          <el-switch v-model="optimizeForm.allow_short" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showOptimizeModal = false">Cancel</el-button>
        <el-button type="primary" :loading="optimizing" @click="submitOptimize">Start Optimization</el-button>
      </template>
      <div v-if="optimizeResult" class="mt-4">
        <h4>Optimization Result</h4>
        <div v-if="optimizeResult.optimized_weights && optimizeResult.tickers">
          <el-table
            :data="optimizeResult.tickers.map(ticker => ({
              ticker,
              weight: optimizeResult.optimized_weights[ticker]
            }))"
            style="width: 100%"
          >
            <el-table-column prop="ticker" label="Ticker" />
            <el-table-column prop="weight" label="Weight">
              <template #default="scope">
                <span v-if="!isNaN(scope.row.weight)">
                  {{ (scope.row.weight * 100).toFixed(2) }}%
                </span>
                <span v-else>
                  No data
                </span>
              </template>
            </el-table-column>
          </el-table>
          <div class="mt-2">Optimization Metric: {{ optimizeResult.metric }}</div>
        </div>
        <div v-else>
          <span>No optimization result</span>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, onUnmounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { InfoFilled } from '@element-plus/icons-vue';
import { portfolioService, marketService } from '../services/api';
import * as echarts from 'echarts';
import StockDetailModal from '../components/StockDetailModal.vue';

const portfolios = ref([]);
const loading = ref(false);
const showCreateModal = ref(false);
const submitting = ref(false);
const portfolioForm = ref(null);
const availableStocks = ref([]);
const showDetailsModal = ref(false);
const selectedPortfolio = ref(null);
const chartContainer = ref(null);
let chart = null;

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

const loadMetricsDefinitions = async () => {
  try {
    const response = await portfolioService.getMetrics();
    metricsDefinitions.value = response.data;
  } catch (error) {
    console.error('Failed to load metrics definitions:', error);
    // don't show error message, because it's optional
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

const handleTimeFrameChange = () => {
  if (selectedPortfolio.value) {
    showPortfolioDetails(selectedPortfolio.value);
  }
};

const handleDateChange = () => {
  if (selectedPortfolio.value) {
    showPortfolioDetails(selectedPortfolio.value);
  }
};

const handleChartTypeChange = () => {
  if (selectedPortfolio.value) {
    initChart();
  }
};

const showPortfolioDetails = async (portfolio) => {
  try {
    console.log('Showing portfolio details for:', portfolio);
    if (!portfolio || !portfolio.ptfid) {
      throw new Error('Invalid portfolio data');
    }

    const params = {
      time_frame: selectedTimeFrame.value,
      start_date: selectedStartDate.value ? selectedStartDate.value.toISOString().split('T')[0] : null,
      end_date: selectedEndDate.value ? selectedEndDate.value.toISOString().split('T')[0] : null
    };
    console.log('Request params:', params);
    
    const response = await portfolioService.getPortfolioById(portfolio.ptfid, params);
    console.log('Portfolio details response:', response);
    
    if (!response.data) {
      throw new Error('No data received from server');
    }

    // update selected portfolio data
    const updatedPortfolio = {
      ...response.data,
      weightsArray: response.data.tickers.map((ticker, index) => ({
        ticker,
        weight: parseFloat(response.data.weights[index])
      }))
    };

    // handle metrics data
    if (response.data.metrics) {
      console.log('Raw metrics data from API:', response.data.metrics);
      updatedPortfolio.metrics = {
        sharpe_ratio: parseFloat(response.data.metrics.sharpe_ratio) || null,
        max_drawdown: parseFloat(response.data.metrics.max_drawdown) || null,
        volatility: parseFloat(response.data.metrics.volatility) || null,
        mean_yearly_return: parseFloat(response.data.metrics.mean_yearly_return) || null,
        sortino_ratio: parseFloat(response.data.metrics.sortino_ratio) || null,
        calmar_ratio: parseFloat(response.data.metrics.calmar_ratio) || null,
        hit_ratio: parseFloat(response.data.metrics.hit_ratio) || null,
        mean_daily_return: parseFloat(response.data.metrics.mean_daily_return) || null,
        best_daily_return: parseFloat(response.data.metrics.best_daily_return) || null,
        worst_daily_return: parseFloat(response.data.metrics.worst_daily_return) || null
      };
      console.log('Processed metrics data:', updatedPortfolio.metrics);
    } else {
      console.log('No metrics data in response');
      updatedPortfolio.metrics = {
        sharpe_ratio: null,
        max_drawdown: null,
        volatility: null,
        mean_yearly_return: null,
        sortino_ratio: null,
        calmar_ratio: null,
        hit_ratio: null,
        mean_daily_return: null,
        best_daily_return: null,
        worst_daily_return: null
      };
    }

    // handle performance_cum data
    if (response.data.performance_cum) {
      updatedPortfolio.performance_cum = response.data.performance_cum;
    }

    selectedPortfolio.value = updatedPortfolio;
    showDetailsModal.value = true;
    
    // auto fill date field - set default value
    if (response.data.dates && response.data.dates.length > 0) {
      const dates = response.data.dates.map(date => new Date(date));
      const minDate = new Date(Math.min(...dates));
      const maxDate = new Date(Math.max(...dates));
      
      // set default start time to creation time, end time to current time
      selectedStartDate.value = new Date(portfolio.start_date);
      selectedEndDate.value = new Date();
    }
    
    await nextTick();
    initChart();
  } catch (error) {
    console.error('Error loading portfolio details:', error);
    ElMessage.error('Failed to load portfolio details: ' + (error.response?.data?.detail || error.message));
  }
};

const initChart = () => {
  if (!chartContainer.value || !selectedPortfolio.value) {
    console.error('Chart initialization failed: missing container or portfolio data');
    return;
  }

  console.log('Initializing chart with data:', selectedPortfolio.value);
  console.log('Chart type:', chartType.value);
  console.log('Performance data:', selectedPortfolio.value.performance);
  console.log('Performance cum data:', selectedPortfolio.value.performance_cum);
  console.log('Dates data:', selectedPortfolio.value.dates);

  // destroy old chart
  if (chart) {
    chart.dispose();
  }

  try {
    // create new chart
    chart = echarts.init(chartContainer.value);
    
    // check necessary data
    if (!selectedPortfolio.value.performance || !Array.isArray(selectedPortfolio.value.performance)) {
      throw new Error('Missing or invalid performance data');
    }

    // generate date array (if no date data, use index as x-axis)
    const dates = selectedPortfolio.value.dates || 
                 Array.from({length: selectedPortfolio.value.performance.length}, (_, i) => 
                   new Date(Date.now() - (selectedPortfolio.value.performance.length - i) * 24 * 60 * 60 * 1000)
                     .toLocaleDateString('en-US', {
                       year: 'numeric',
                       month: '2-digit',
                       day: '2-digit'
                     }).replace(/\//g, '-')
                 );

    console.log('Processed dates:', dates);

    // according to chart type, select data
    let chartData, chartTitle, yAxisFormatter;
    if (chartType.value === 'cumulative' && selectedPortfolio.value.performance_cum && Array.isArray(selectedPortfolio.value.performance_cum)) {
      // Convert decimal to percentage for chart display
      chartData = selectedPortfolio.value.performance_cum.map(value => value * 100);
      chartTitle = 'Cumulative Portfolio Performance';
      yAxisFormatter = '{value}%';
      console.log('Using cumulative data, length:', chartData.length);
    } else {
      // Convert decimal to percentage for chart display
      chartData = selectedPortfolio.value.performance.map(value => value * 100);
      chartTitle = 'Daily Portfolio Performance';
      yAxisFormatter = '{value}%';
      console.log('Using daily data, length:', chartData.length);
      if (chartType.value === 'cumulative') {
        console.log('Cumulative data not available or invalid');
      }
    }

    // ensure data length matches
    if (chartData.length !== dates.length) {
      console.warn('Data length mismatch, using performance data length');
      const minLength = Math.min(chartData.length, dates.length);
      chartData = chartData.slice(0, minLength);
      dates = dates.slice(0, minLength);
    }

    // optimize date format
    const formattedDates = dates.map(date => {
      try {
        let dateObj;
        
        // handle quarterly format (Q1-2024, Q2-2024, etc.)
        if (typeof date === 'string' && date.match(/^Q[1-4]-\d{4}$/)) {
          const [quarter, year] = date.split('-');
          const quarterNum = parseInt(quarter.substring(1));
          const yearNum = parseInt(year);
          const month = (quarterNum - 1) * 3; // Q1=0, Q2=3, Q3=6, Q4=9
          dateObj = new Date(yearNum, month, 1);
        } else {
          dateObj = new Date(date);
        }
        
        if (isNaN(dateObj.getTime())) {
          console.warn('Invalid date:', date);
          return 'Invalid Date';
        }
        
        if (selectedTimeFrame.value === 'daily') {
          return dateObj.toLocaleDateString('en-US', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit'
          }).replace(/\//g, '-');
        } else if (selectedTimeFrame.value === 'quarterly') {
          // for quarterly, display as Q1-2024 format
          const quarter = Math.floor(dateObj.getMonth() / 3) + 1;
          const year = dateObj.getFullYear();
          return `Q${quarter}-${year}`;
        } else {
          return dateObj.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: '2-digit'
          });
        }
      } catch (error) {
        console.error('Error formatting date:', date, error);
        return 'Invalid Date';
      }
    });

    console.log('Formatted dates:', formattedDates);

    const option = {
      title: {
        text: chartTitle,
        left: 'center'
      },
      tooltip: {
        trigger: 'axis',
        formatter: function(params) {
          const date = params[0].axisValue;
          const value = params[0].data;
          return `${date}<br/>${chartType.value === 'cumulative' ? 'Cumulative Return' : 'Daily Return'}: ${value.toFixed(2)}%`;
        }
      },
      xAxis: {
        type: 'category',
        data: formattedDates,
        axisLabel: {
          rotate: 45,
          formatter: function(value) {
            return value;
          }
        }
      },
      yAxis: {
        type: 'value',
        axisLabel: {
          formatter: yAxisFormatter
        }
      },
      series: [{
        name: chartType.value === 'cumulative' ? 'Cumulative Return' : 'Daily Return',
        type: 'line',
        data: chartData,
        smooth: true,
        lineStyle: {
          width: 3
        },
        areaStyle: {
          opacity: 0.1
        }
      }],
      grid: {
        left: '3%',
        right: '4%',
        bottom: '15%',
        containLabel: true
      }
    };

    chart.setOption(option);
    console.log('Chart initialized successfully');
  } catch (error) {
    console.error('Error initializing chart:', error);
    ElMessage.error('Failed to initialize chart: ' + error.message);
  }
};

const formatPerformance = (value) => {
  if (value === null || value === undefined) return 'N/A';
  const percentage = value * 100;  // Convert decimal to percentage
  return `${percentage > 0 ? '+' : ''}${percentage.toFixed(2)}%`;
};

const getPerformanceClass = (value) => {
  if (value === null || value === undefined) return '';
  return value > 0 ? 'text-green-500' : 'text-red-500';
};

// listen to window size change and adjust chart size
window.addEventListener('resize', () => {
  if (chart) {
    chart.resize();
  }
});

// clean up when component unmounts
onUnmounted(() => {
  if (chart) {
    chart.dispose();
  }
  window.removeEventListener('resize', () => {
    if (chart) {
      chart.resize();
    }
  });
});

// Add new refs for time frame and date selection
const selectedTimeFrame = ref('daily');
const selectedStartDate = ref(null);
const selectedEndDate = ref(null);
const chartType = ref('cumulative');
const metricsDefinitions = ref(null);

// Add new reactive variables
const showStockDetailModal = ref(false);
const selectedTicker = ref(null);
const showMoreMetrics = ref(false);

// Add new methods
const showStockInfo = async (ticker) => {
  try {
    selectedTicker.value = ticker;
    showStockDetailModal.value = true;
  } catch (error) {
    console.error('Error opening stock detail:', error);
    ElMessage.error('Failed to open stock detail');
  }
};

const formatMetricValue = (value, key) => {
  if (value === null || value === undefined || isNaN(value)) return 'N/A';
  
  const numValue = parseFloat(value);
  if (isNaN(numValue)) return 'N/A';
  
  if (key.includes('return')) {
    // convert return metrics to percentage
    return (numValue * 100).toFixed(2) + '%';
  } else if (key === 'max_drawdown' || key === 'volatility') {
    // convert max drawdown and volatility to percentage
    return (numValue * 100).toFixed(2) + '%';
  } else {
    // ratio metrics keep original value
    return numValue.toFixed(2);
  }
};

// optimize related
const showOptimizeModal = ref(false);
const optimizing = ref(false);
const optimizeForm = ref({
  metric: 'sharpe',
  start_date: '',
  end_date: '',
  interval: '1d',
  allow_short: false
});
const optimizeResult = ref(null);
const optimizeTargetPortfolio = ref(null);

const optimizeMetricsOptions = [
  { label: 'Sharpe Ratio', value: 'sharpe' },
  { label: 'Sortino Ratio', value: 'sortino' },
  { label: 'Total Return', value: 'total return' },
  { label: 'Weekly Return', value: 'weekly return' },
  { label: 'Daily Return', value: 'daily return' }
];

const showOptimizeDialog = (portfolio) => {
  optimizeTargetPortfolio.value = portfolio;
  optimizeForm.value = {
    metric: 'sharpe',
    start_date: portfolio.start_date || '',
    end_date: '',
    interval: '1d',
    allow_short: false
  };
  optimizeResult.value = null;
  showOptimizeModal.value = true;
};

const submitOptimize = async () => {
  if (!optimizeTargetPortfolio.value) return;
  optimizing.value = true;
  try {
    const startDate = optimizeForm.value.start_date instanceof Date
      ? optimizeForm.value.start_date.toISOString().split('T')[0]
      : optimizeForm.value.start_date;
    const endDate = optimizeForm.value.end_date instanceof Date
      ? optimizeForm.value.end_date.toISOString().split('T')[0]
      : optimizeForm.value.end_date;

    const params = {
      metric: optimizeForm.value.metric,
      start_date: startDate,
      end_date: endDate,
      interval: optimizeForm.value.interval,
      allow_short: optimizeForm.value.allow_short
    };
    console.log('submit params', params);
    const response = await portfolioService.optimizePortfolio(optimizeTargetPortfolio.value.ptfid, params);
    console.log('Optimization result:', response.data);
    optimizeResult.value = response.data;
  } catch (error) {
    ElMessage.error('Optimization failed: ' + (error.response?.data?.detail || error.message));
  } finally {
    optimizing.value = false;
  }
};

onMounted(() => {
  loadPortfolios();
  loadAvailableStocks();
  loadMetricsDefinitions();
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

.portfolio-details {
  padding: 20px;
}

.portfolio-summary {
  display: flex;
  gap: 40px;
  margin-bottom: 30px;
}

.summary-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.summary-item .label {
  font-size: 14px;
  color: #666;
}

.summary-item .value {
  font-size: 24px;
  font-weight: 600;
}

.performance-chart {
  margin: 30px 0;
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.holdings-table {
  margin-top: 30px;
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.holdings-table h3 {
  margin-bottom: 20px;
  color: #2c3e50;
  font-size: 18px;
  font-weight: 600;
}

.cursor-pointer {
  cursor: pointer;
}

.text-green-500 {
  color: #67c23a;
}

.text-red-500 {
  color: #f56c6c;
}

.time-frame-selection {
  display: flex;
  gap: 16px;
  align-items: center;
  margin-bottom: 24px;
  flex-wrap: wrap;
}

.time-frame-select {
  min-width: 120px;
}

.chart-type-toggle {
  margin-left: auto;
}

.chart-type-toggle .el-radio-button__inner {
  border-radius: 8px;
  padding: 8px 16px;
  font-size: 14px;
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
  font-size: 24px;
  font-weight: 600;
}

:deep(.el-table) {
  --el-table-border-color: #ebeef5;
  --el-table-header-bg-color: #f5f7fa;
  width: 100% !important;
}

:deep(.el-table__header) {
  width: 100% !important;
}

:deep(.el-table__body) {
  width: 100% !important;
}

:deep(.el-table__cell) {
  text-align: center !important;
}

:deep(.el-table th) {
  font-weight: 600;
  color: #2c3e50;
  text-align: center !important;
}

:deep(.el-table td) {
  color: #606266;
  text-align: center !important;
}

.metric-note {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
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

.stock-info {
  padding: 20px;
}

.info-section {
  margin-bottom: 24px;
}

.info-section h4 {
  margin-bottom: 16px;
  color: #2c3e50;
  font-size: 16px;
  font-weight: 600;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
}

.info-item .label {
  font-size: 12px;
  color: #666;
}

.info-item .value {
  font-size: 16px;
  font-weight: 500;
  color: #2c3e50;
}

.metric-header {
  display: flex;
  align-items: center;
  gap: 4px;
}

.info-icon {
  color: #909399;
  font-size: 14px;
  cursor: help;
}

.company-description {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 16px;
  margin-top: 8px;
  line-height: 1.6;
  color: #2c3e50;
  font-size: 14px;
  max-height: 300px;
  overflow-y: auto;
}

.company-description p {
  margin: 0;
  white-space: pre-wrap;
}

.portfolio-metrics {
  margin-top: 20px;
  padding: 16px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.metric-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.metric-label {
  font-size: 14px;
  color: #666;
}

.metric-value {
  font-size: 16px;
  font-weight: 600;
}
</style>