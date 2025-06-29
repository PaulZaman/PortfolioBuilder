<template>
  <el-dialog
    v-model="visible"
    :title="`${ticker} - Stock Details`"
    width="70%"
    class="stock-detail-dialog fade-in"
    @close="handleClose"
  >
    <div v-loading="loading" class="stock-detail-content">
      <!-- Stock Info Section -->
      <div v-if="stockInfo" class="info-section">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-card class="info-card">
              <h3>Basic Information</h3>
              <div class="info-grid">
                <div class="info-item">
                  <span class="label">Company Name</span>
                  <span class="value">{{ stockInfo.name || stockInfo.shortName || stockInfo.longName || 'N/A' }}</span>
                </div>
                <div class="info-item">
                  <span class="label">Sector</span>
                  <span class="value">{{ stockInfo.sector || 'N/A' }}</span>
                </div>
                <div class="info-item">
                  <span class="label">Market Cap</span>
                  <span class="value">{{ formatMarketCap(stockInfo.marketCap) }}</span>
                </div>
                <div class="info-item">
                  <span class="label">Current Price</span>
                  <span class="value price-value">${{ stockInfo.previousClose?.toFixed(2) || 'N/A' }}</span>
                </div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="12">
            <el-card class="info-card">
              <h3>Financial Metrics</h3>
              <div class="info-grid">
                <div class="info-item">
                  <span class="label">P/E Ratio</span>
                  <span class="value">{{ stockInfo.forwardPE?.toFixed(2) || 'N/A' }}</span>
                </div>
                <div class="info-item">
                  <span class="label">52 Week High</span>
                  <span class="value">{{ stockInfo.fiftyTwoWeekHigh?.toFixed(2) || 'N/A' }}</span>
                </div>
                <div class="info-item">
                  <span class="label">52 Week Low</span>
                  <span class="value">{{ stockInfo.fiftyTwoWeekLow?.toFixed(2) || 'N/A' }}</span>
                </div>
                <div class="info-item">
                  <span class="label">Dividend Yield</span>
                  <span class="value">{{ (stockInfo.dividendYield * 100)?.toFixed(2) || 'N/A' }}%</span>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- Chart Section -->
      <div class="chart-section">
        <el-card class="chart-card">
          <h3>Price History (Last 30 Days)</h3>
          <div ref="chartContainer" class="chart-container"></div>
        </el-card>
      </div>

      <!-- Company Description -->
      <div v-if="stockInfo?.longBusinessSummary" class="description-section">
        <el-card class="description-card">
          <h3>Company Overview</h3>
          <p class="company-description">{{ stockInfo.longBusinessSummary }}</p>
        </el-card>
      </div>
    </div>

    <template #footer>
      <span class="dialog-footer">
        <el-button class="round-btn gradient-btn" @click="handleClose">Close</el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script>
import { ref, watch, nextTick, onUnmounted } from 'vue';
import { ElMessage } from 'element-plus';
import * as echarts from 'echarts';
import { marketService } from '../services/api';

export default {
  name: 'StockDetailModal',
  props: {
    modelValue: {
      type: Boolean,
      default: false
    },
    ticker: {
      type: String,
      required: true
    }
  },
  emits: ['update:modelValue'],
  setup(props, { emit }) {
    const visible = ref(false);
    const loading = ref(false);
    const stockInfo = ref(null);
    const chartContainer = ref(null);
    let chart = null;

    // Watch for modelValue changes
    watch(() => props.modelValue, (newVal) => {
      visible.value = newVal;
      if (newVal && props.ticker) {
        loadStockData();
      }
    });

    // Watch for visible changes
    watch(visible, (newVal) => {
      emit('update:modelValue', newVal);
      if (!newVal) {
        cleanup();
      }
    });

    const loadStockData = async () => {
      loading.value = true;
      try {
        // Load stock info and history in parallel
        const [infoData, historyData] = await Promise.all([
          marketService.getTickerInfo(props.ticker),
          marketService.getTickerHistory(props.ticker)
        ]);

        stockInfo.value = infoData;
        
        // Initialize chart after data is loaded
        await nextTick();
        initChart(historyData);
      } catch (error) {
        console.error('Error loading stock data:', error);
        ElMessage.error('Failed to load stock data');
      } finally {
        loading.value = false;
      }
    };

    const initChart = (historyData) => {
      if (!chartContainer.value || !historyData.dates || !historyData.prices) {
        return;
      }

      // Destroy existing chart
      if (chart) {
        chart.dispose();
      }

      // Create new chart
      chart = echarts.init(chartContainer.value);

      const option = {
        tooltip: {
          trigger: 'axis',
          formatter: function(params) {
            const data = params[0];
            return `${data.name}<br/>Price: $${data.value.toFixed(2)}`;
          }
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: historyData.dates,
          axisLabel: {
            formatter: function(value) {
              return new Date(value).toLocaleDateString();
            }
          }
        },
        yAxis: {
          type: 'value',
          scale: true,
          axisLabel: {
            formatter: function(value) {
              return '$' + value.toFixed(2);
            }
          },
          min: function (value) {
            return value.min - (value.max - value.min) * 0.1;
          },
          max: function (value) {
            return value.max + (value.max - value.min) * 0.1;
          }
        },
        series: [
          {
            name: 'Price',
            type: 'line',
            data: historyData.prices,
            smooth: true,
            lineStyle: {
              color: '#409eff',
              width: 3
            },
            areaStyle: {
              color: {
                type: 'linear',
                x: 0,
                y: 0,
                x2: 0,
                y2: 1,
                colorStops: [
                  { offset: 0, color: 'rgba(64, 158, 255, 0.3)' },
                  { offset: 1, color: 'rgba(64, 158, 255, 0.05)' }
                ]
              }
            },
            itemStyle: {
              color: '#409eff'
            }
          }
        ]
      };

      chart.setOption(option);

      // Handle window resize
      window.addEventListener('resize', () => {
        if (chart) {
          chart.resize();
        }
      });
    };

    const formatMarketCap = (value) => {
      if (!value) return 'N/A';
      if (value >= 1e12) return `$${(value / 1e12).toFixed(2)}T`;
      if (value >= 1e9) return `$${(value / 1e9).toFixed(2)}B`;
      if (value >= 1e6) return `$${(value / 1e6).toFixed(2)}M`;
      return `$${value.toFixed(2)}`;
    };

    const handleClose = () => {
      visible.value = false;
    };

    const cleanup = () => {
      if (chart) {
        chart.dispose();
        chart = null;
      }
      stockInfo.value = null;
    };

    onUnmounted(() => {
      cleanup();
    });

    return {
      visible,
      loading,
      stockInfo,
      chartContainer,
      formatMarketCap,
      handleClose
    };
  }
};
</script>

<style scoped>
.stock-detail-dialog {
  border-radius: 18px;
}

.stock-detail-content {
  max-height: 70vh;
  overflow-y: auto;
}

.info-section {
  margin-bottom: 24px;
}

.info-card {
  border-radius: 14px;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.06);
  border: none;
}

.info-card h3 {
  margin: 0 0 16px 0;
  color: #409eff;
  font-size: 18px;
  font-weight: 600;
}

.info-grid {
  display: grid;
  gap: 12px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.info-item:last-child {
  border-bottom: none;
}

.label {
  font-weight: 500;
  color: #666;
  font-size: 14px;
}

.value {
  font-weight: 600;
  color: #333;
  font-size: 14px;
}

.price-value {
  color: #409eff;
  font-size: 16px;
}

.chart-section {
  margin-bottom: 24px;
}

.chart-card {
  border-radius: 14px;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.06);
  border: none;
}

.chart-card h3 {
  margin: 0 0 16px 0;
  color: #409eff;
  font-size: 18px;
  font-weight: 600;
}

.chart-container {
  height: 400px;
  width: 100%;
}

.description-section {
  margin-bottom: 24px;
}

.description-card {
  border-radius: 14px;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.06);
  border: none;
}

.description-card h3 {
  margin: 0 0 16px 0;
  color: #409eff;
  font-size: 18px;
  font-weight: 600;
}

.company-description {
  line-height: 1.6;
  color: #666;
  margin: 0;
  text-align: justify;
}

.round-btn {
  border-radius: 18px !important;
  font-weight: 500;
  padding: 8px 22px !important;
  font-size: 15px;
}

.gradient-btn {
  background: linear-gradient(90deg, #36cfc9 0%, #409eff 100%) !important;
  color: #fff !important;
  box-shadow: 0 2px 8px #36cfc933;
  border: none !important;
  transition: background 0.2s, box-shadow 0.2s;
}

.gradient-btn:hover {
  background: linear-gradient(90deg, #66b1ff 0%, #5cdbd3 100%) !important;
  box-shadow: 0 4px 16px #409eff33;
}

.fade-in {
  animation: fadeIn 0.3s;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Responsive design */
@media screen and (max-width: 768px) {
  .info-grid {
    gap: 8px;
  }
  
  .info-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }
  
  .chart-container {
    height: 300px;
  }
}
</style> 