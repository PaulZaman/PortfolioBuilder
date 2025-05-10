<template>
  <div class="market-container fade-in">
    <el-container>
      <el-header class="market-header enhanced-header">
        <div class="header-content">
          <div class="header-left">
            <img src="https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/svg/1f4c8.svg" alt="logo" class="logo" />
            <h2>Market Watch</h2>
          </div>
          <div class="header-right">
            <el-button class="round-btn gradient-btn" type="primary" @click="$router.push('/home')">Back to Dashboard</el-button>
          </div>
        </div>
      </el-header>

      <el-main class="market-content">
        <!-- Search and Add Stock Section -->
        <el-row :gutter="20" class="mb-4">
          <el-col :span="24">
            <el-card class="enhanced-card fade-in">
              <div class="flex gap-4 align-center">
                <el-input
                  v-model="searchQuery"
                  placeholder="Search stocks..."
                  class="flex-1 enhanced-input"
                  clearable
                >
                  <template #prefix>
                    <el-icon><Search /></el-icon>
                  </template>
                </el-input>
                <el-button class="round-btn gradient-btn" type="primary" @click="showAddStockModal = true">
                  Add Stock
                </el-button>
              </div>
            </el-card>
          </el-col>
        </el-row>

        <!-- Watchlist Table -->
        <el-row :gutter="20">
          <el-col :span="24">
            <el-card class="enhanced-card fade-in">
              <el-table :data="filteredWatchlist" style="width: 100%" v-loading="loading" class="enhanced-table" @row-click="rowClick">
                <el-table-column prop="ticker" label="Ticker" min-width="100" />
                <el-table-column prop="name" label="Company Name" min-width="200" show-overflow-tooltip />
                <el-table-column prop="price" label="Current Price" min-width="120">
                  <template #default="scope">
                    <span
                      v-if="scope.row.price"
                      :class="['price-cell', priceFlashMap[scope.row.ticker]?.flash]"
                    >
                      <span v-if="priceArrow(scope.row, 'up')" class="arrow-up">▲</span>
                      <span v-if="priceArrow(scope.row, 'down')" class="arrow-down">▼</span>
                      ${{ scope.row.price.toLocaleString() }}
                    </span>
                    <span v-else class="text-gray-400">N/A</span>
                  </template>
                </el-table-column>
                <el-table-column prop="daily_performance" label="Daily Change" min-width="120">
                  <template #default="scope">
                    <span :class="['performance-cell', getPerformanceClass(scope.row.daily_performance)]">
                      <span v-if="scope.row.daily_performance > 0" class="arrow-up">▲</span>
                      <span v-else-if="scope.row.daily_performance < 0" class="arrow-down">▼</span>
                      {{ formatPerformance(scope.row.daily_performance) }}
                    </span>
                  </template>
                </el-table-column>
                <el-table-column label="Actions" min-width="100" fixed="right">
                  <template #default="scope">
                    <el-button
                      class="remove-btn gradient-btn"
                      type="danger"
                      size="small"
                      @click.stop="removeFromWatchlist(scope.row.ticker)"
                    >
                      Remove
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
            </el-card>
          </el-col>
        </el-row>
      </el-main>
    </el-container>

    <!-- Add Stock Modal -->
    <el-dialog
      v-model="showAddStockModal"
      title="Add Stock to Watchlist"
      width="50%"
      class="enhanced-dialog fade-in"
    >
      <el-input
        v-model="stockSearchQuery"
        placeholder="Search stocks..."
        class="mb-4 enhanced-input"
        clearable
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>

      <el-scrollbar height="400px">
        <div class="stock-list">
          <el-card
            v-for="stock in filteredAvailableStocks"
            :key="stock.ticker"
            class="mb-2 cursor-pointer hover:bg-gray-50 enhanced-card stock-card fade-in"
            @click="addToWatchlist(stock.ticker)"
          >
            <div class="flex justify-between items-center">
              <div>
                <div class="font-medium">{{ stock.ticker }}</div>
                <div class="text-sm text-gray-500">{{ stock.name }}</div>
              </div>
              <el-button class="round-btn gradient-btn" type="primary" size="small">Add</el-button>
            </div>
          </el-card>
        </div>
      </el-scrollbar>

      <template #footer>
        <span class="dialog-footer">
          <el-button class="round-btn gradient-btn" @click="showAddStockModal = false">Cancel</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch, nextTick } from 'vue';
import { marketService } from '../services/api';
import { Search } from '@element-plus/icons-vue';
import { ElMessage } from 'element-plus';

export default {
  name: 'MarketPage',
  components: {
    Search
  },
  setup() {
    const watchlist = ref([]);
    const availableStocks = ref([]);
    const searchQuery = ref('');
    const stockSearchQuery = ref('');
    const showAddStockModal = ref(false);
    const loading = ref(false);
    const selectedRow = ref(null);

    // 新增：记录每只股票的上一次价格和闪烁状态
    const priceFlashMap = ref({});

    // 监听 watchlist 变化，判断价格变动
    watch(watchlist, (newList, oldList) => {
      if (!oldList || oldList.length === 0) {
        // 初始化时记录价格
        newList.forEach(stock => {
          priceFlashMap.value[stock.ticker] = { last: stock.price, flash: '' };
        });
        return;
      }
      newList.forEach(stock => {
        const oldStock = oldList.find(s => s.ticker === stock.ticker);
        if (oldStock && stock.price !== oldStock.price) {
          // 价格变动，设置闪烁class
          const flashClass = stock.price > oldStock.price ? 'flash-green' : 'flash-red';
          priceFlashMap.value[stock.ticker] = { last: stock.price, flash: flashClass };
          // 动画结束后移除class
          nextTick(() => {
            setTimeout(() => {
              if (priceFlashMap.value[stock.ticker]) {
                priceFlashMap.value[stock.ticker].flash = '';
              }
            }, 700);
          });
        } else if (!oldStock) {
          // 新增股票
          priceFlashMap.value[stock.ticker] = { last: stock.price, flash: '' };
        }
      });
    }, { deep: true });

    // Fetch watchlist
    const fetchWatchlist = async () => {
      loading.value = true;
      try {
        const response = await marketService.getWatchlist();
        watchlist.value = response.watchlist;
      } catch (error) {
        console.error('Error fetching watchlist:', error);
        ElMessage.error('Failed to fetch watchlist');
      } finally {
        loading.value = false;
      }
    };

    // Fetch available stocks
    const fetchAvailableStocks = async () => {
      try {
        const response = await marketService.getAllStocks();
        availableStocks.value = response.stocks;
      } catch (error) {
        console.error('Error fetching available stocks:', error);
        ElMessage.error('Failed to fetch available stocks');
      }
    };

    // Add stock to watchlist
    const addToWatchlist = async (ticker) => {
      try {
        await marketService.addToWatchlist(ticker);
        await fetchWatchlist();
        showAddStockModal.value = false;
        ElMessage.success(`${ticker} added to watchlist`);
      } catch (error) {
        console.error('Error adding stock to watchlist:', error);
        ElMessage.error('Failed to add stock to watchlist');
      }
    };

    // Remove stock from watchlist
    const removeFromWatchlist = async (ticker) => {
      try {
        await marketService.removeFromWatchlist(ticker);
        await fetchWatchlist();
        ElMessage.success(`${ticker} removed from watchlist`);
      } catch (error) {
        console.error('Error removing stock from watchlist:', error);
        ElMessage.error('Failed to remove stock from watchlist');
      }
    };

    // Format performance display
    const formatPerformance = (performance) => {
      if (performance === null || performance === undefined) return 'N/A';
      return `${performance > 0 ? '+' : ''}${performance.toFixed(2)}%`;
    };

    // Set performance color
    const getPerformanceClass = (performance) => {
      if (performance === null || performance === undefined) return 'text-gray-500';
      return performance > 0 ? 'text-green-500' : 'text-red-500';
    };

    // Filter watchlist
    const filteredWatchlist = computed(() => {
      return watchlist.value.filter(stock =>
        stock.ticker.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
        stock.name.toLowerCase().includes(searchQuery.value.toLowerCase())
      );
    });

    // Filter available stocks
    const filteredAvailableStocks = computed(() => {
      return availableStocks.value.filter(stock =>
        stock.ticker.toLowerCase().includes(stockSearchQuery.value.toLowerCase()) ||
        stock.name.toLowerCase().includes(stockSearchQuery.value.toLowerCase())
      );
    });

    // Fetch data on component mount
    onMounted(() => {
      fetchWatchlist();
      fetchAvailableStocks();
    });

    // 行点击高亮
    const rowClick = (row) => {
      selectedRow.value = row.ticker;
    };

    // 价格箭头
    const priceArrow = (row, type) => {
      const flash = priceFlashMap.value[row.ticker]?.flash;
      if (type === 'up') return flash === 'flash-green';
      if (type === 'down') return flash === 'flash-red';
      return false;
    };

    return {
      watchlist,
      availableStocks,
      searchQuery,
      stockSearchQuery,
      showAddStockModal,
      loading,
      filteredWatchlist,
      filteredAvailableStocks,
      addToWatchlist,
      removeFromWatchlist,
      formatPerformance,
      getPerformanceClass,
      priceFlashMap,
      rowClick,
      selectedRow,
      priceArrow
    };
  }
};
</script>

<style scoped>
.market-container {
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

.market-header.enhanced-header {
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
  font-size: 26px;
  color: #fff;
  letter-spacing: 1px;
  font-weight: 700;
}

.market-content {
  margin-top: 60px;
  padding: 32px 0 0 0;
  width: 100%;
  max-width: none;
  box-sizing: border-box;
  min-height: calc(100vh - 60px);
}

.enhanced-card {
  border-radius: 18px;
  box-shadow: 0 2px 12px rgba(64, 158, 255, 0.07);
  border: none;
  padding: 18px 24px;
  background: #fff;
}

.enhanced-table ::v-deep .el-table__header th {
  background: #f0f7ff;
  font-weight: 700;
  color: #409eff;
  font-size: 16px;
}

.enhanced-table ::v-deep .el-table__row {
  transition: background 0.2s, transform 0.2s;
  cursor: pointer;
}
.enhanced-table ::v-deep .el-table__row:hover {
  background: #e6f7ff !important;
  transform: scale(1.01);
}
.enhanced-table ::v-deep .el-table__row.selected-row {
  background: #d0eaff !important;
  box-shadow: 0 2px 8px #b3e5fc33;
}

.price-cell {
  font-weight: bold;
  font-size: 16px;
  color: #222;
  letter-spacing: 0.5px;
}
.performance-cell {
  font-weight: bold;
  font-size: 15px;
}
.text-green-500 {
  color: #1abc9c !important;
}
.text-red-500 {
  color: #e74c3c !important;
}

.remove-btn {
  border-radius: 16px !important;
  font-weight: 500;
  background: #ffeaea;
  color: #e74c3c;
  border: none;
  transition: background 0.2s, color 0.2s;
}
.remove-btn:hover {
  background: #ffbdbd !important;
  color: #fff !important;
}

.round-btn {
  border-radius: 18px !important;
  font-weight: 500;
  padding: 8px 22px !important;
  font-size: 15px;
}

.enhanced-input .el-input__inner {
  border-radius: 14px !important;
  font-size: 15px;
  padding: 8px 14px;
}

.stock-list {
  padding: 10px;
}
.stock-card {
  border-radius: 14px;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.06);
  border: none;
  transition: box-shadow 0.2s, background 0.2s;
}
.stock-card:hover {
  box-shadow: 0 4px 16px rgba(64, 158, 255, 0.13);
  background: #f0f7ff !important;
}

.enhanced-dialog .el-dialog {
  border-radius: 18px;
}

.cursor-pointer {
  cursor: pointer;
}

.align-center {
  align-items: center;
}

/* Responsive layout */
@media screen and (min-width: 1200px) {
  .el-main {
    padding: 30px 60px;
  }
  .header-content {
    padding: 0 60px;
  }
}

@media screen and (min-width: 1600px) {
  .el-main {
    padding: 40px 80px;
  }
  .header-content {
    padding: 0 80px;
  }
}

@media screen and (max-width: 768px) {
  .el-main {
    padding: 10px;
  }
  .header-content {
    padding: 0 10px;
  }
  .market-content {
    padding: 10px 0 0 0;
  }
  .enhanced-card {
    padding: 10px 6px;
  }
  .price-cell, .performance-cell {
    font-size: 14px;
  }
}

.flash-green {
  animation: flash-green-bg 0.7s;
}
.flash-red {
  animation: flash-red-bg 0.7s;
}
@keyframes flash-green-bg {
  0% { background-color: #e6ffed; }
  50% { background-color: #b7f5c9; }
  100% { background-color: transparent; }
}
@keyframes flash-red-bg {
  0% { background-color: #ffeaea; }
  50% { background-color: #ffbdbd; }
  100% { background-color: transparent; }
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

body, .market-container {
  font-family: 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', Arial, sans-serif;
  font-weight: 400;
  letter-spacing: 0.1px;
}

.fade-in {
  animation: fadeIn 0.7s;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.arrow-up {
  color: #1abc9c;
  font-size: 13px;
  margin-right: 2px;
  font-weight: bold;
}
.arrow-down {
  color: #e74c3c;
  font-size: 13px;
  margin-right: 2px;
  font-weight: bold;
}

.gradient-btn {
  background: linear-gradient(90deg, #36cfc9 0%, #409eff 100%) !important;
  color: #fff !important;
  box-shadow: 0 2px 8px #36cfc933;
  border: none !important;
  transition: background 0.2s, box-shadow 0.2s;
}
.gradient-btn:hover {
  background: linear-gradient(90deg, #409eff 0%, #36cfc9 100%) !important;
  box-shadow: 0 4px 16px #409eff33;
}
</style> 