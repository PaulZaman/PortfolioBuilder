<template>
  <div class="market-page">
    <el-container>
      <el-header class="header">
        <div class="header-content">
          <h2>Market Watch</h2>
          <div class="header-right">
            <el-button type="primary" @click="$router.push('/home')">Back to Dashboard</el-button>
          </div>
        </div>
      </el-header>

      <el-main>
        <!-- Search and Add Stock Section -->
        <el-row :gutter="20" class="mb-4">
          <el-col :span="24">
            <el-card>
              <div class="flex gap-4">
                <el-input
                  v-model="searchQuery"
                  placeholder="Search stocks..."
                  class="flex-1"
                >
                  <template #prefix>
                    <el-icon><Search /></el-icon>
                  </template>
                </el-input>
                <el-button type="primary" @click="showAddStockModal = true">
                  Add Stock
                </el-button>
              </div>
            </el-card>
          </el-col>
        </el-row>

        <!-- Watchlist Table -->
        <el-row :gutter="20">
          <el-col :span="24">
            <el-card>
              <el-table :data="filteredWatchlist" style="width: 100%" v-loading="loading">
                <el-table-column prop="ticker" label="Ticker" min-width="100" />
                <el-table-column prop="name" label="Company Name" min-width="200" show-overflow-tooltip />
                <el-table-column prop="price" label="Current Price" min-width="120">
                  <template #default="scope">
                    <span v-if="scope.row.price">${{ scope.row.price.toLocaleString() }}</span>
                    <span v-else class="text-gray-400">N/A</span>
                  </template>
                </el-table-column>
                <el-table-column prop="daily_performance" label="Daily Change" min-width="120">
                  <template #default="scope">
                    <span :class="getPerformanceClass(scope.row.daily_performance)">
                      {{ formatPerformance(scope.row.daily_performance) }}
                    </span>
                  </template>
                </el-table-column>
                <el-table-column label="Actions" min-width="100" fixed="right">
                  <template #default="scope">
                    <el-button
                      type="danger"
                      size="small"
                      @click="removeFromWatchlist(scope.row.ticker)"
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
    >
      <el-input
        v-model="stockSearchQuery"
        placeholder="Search stocks..."
        class="mb-4"
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
            class="mb-2 cursor-pointer hover:bg-gray-50"
            @click="addToWatchlist(stock.ticker)"
          >
            <div class="flex justify-between items-center">
              <div>
                <div class="font-medium">{{ stock.ticker }}</div>
                <div class="text-sm text-gray-500">{{ stock.name }}</div>
              </div>
              <el-button type="primary" size="small">Add</el-button>
            </div>
          </el-card>
        </div>
      </el-scrollbar>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showAddStockModal = false">Cancel</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
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
      getPerformanceClass
    };
  }
};
</script>

<style scoped>
.market-page {
  min-height: 100vh;
  background-color: #f5f7fa;
}

.header {
  background-color: #fff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  width: 100%;
  padding: 0;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
  width: 100%;
  margin: 0;
  padding: 0 20px;
  box-sizing: border-box;
}

.el-main {
  padding: 20px;
  width: 100%;
  max-width: none;
  box-sizing: border-box;
}

.stock-list {
  padding: 10px;
}

.cursor-pointer {
  cursor: pointer;
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
    padding: 15px;
  }
  
  .header-content {
    padding: 0 15px;
  }
}
</style> 