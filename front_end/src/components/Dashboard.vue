<template>
  <div class="home-container">
    <el-container>
      <el-header class="header">
        <div class="header-content">
          <h2>Welcome to Our Platform</h2>
          <div class="header-right">
            <el-dropdown @command="handleCommand">
              <span class="user-dropdown">
                <el-avatar :size="32" :src="userInfo?.avatar || ''" />
                <span class="username">{{ userInfo?.first_name }} {{ userInfo?.last_name }}</span>
                <el-icon><arrow-down /></el-icon>
              </span>
              <template #dropdown>
                <el-dropdown-menu class="profile-dropdown-menu">
                  <el-dropdown-item command="profile">
                    <el-icon style="margin-right:6px;"><User /></el-icon>Profile
                  </el-dropdown-item>
                  <el-dropdown-item command="settings">
                    <el-icon style="margin-right:6px;"><Setting /></el-icon>Settings
                  </el-dropdown-item>
                  <el-dropdown-item divided command="logout">
                    <el-icon style="margin-right:6px;"><SwitchButton /></el-icon>Logout
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
      </el-header>
      
      <el-main>
        <el-row :gutter="20">
          <el-col :span="24">
            <el-card class="welcome-card">
              <h3>Welcome, {{ userInfo?.first_name }}!</h3>
              <p>This is your personalized dashboard. Here you can manage your account and access various features.</p>
            </el-card>
          </el-col>
        </el-row>
        
        <el-row :gutter="20" class="mt-20">
          <el-col :span="8">
            <el-card class="feature-card">
              <template #header>
                <div class="card-header">
                  <span>Quick Actions</span>
                </div>
              </template>
              <div class="feature-content">
                <el-button type="primary" plain @click="router.push('/profile')">View Profile</el-button>
                <el-button type="success" plain>Edit Settings</el-button>
              </div>
            </el-card>
          </el-col>
          
          <el-col :span="8">
            <el-card class="feature-card cursor-pointer" @click="router.push('/market')">
              <template #header>
                <div class="card-header">
                  <span>Market Watch</span>
                </div>
              </template>
              <div class="feature-content">
                <div class="flex items-center justify-between">
                  <div>
                    <h4 class="text-lg font-medium mb-2">Stock Market</h4>
                    <p class="text-gray-500">Monitor your watchlist and track stock performance</p>
                  </div>
                  <el-icon class="text-2xl text-blue-500"><TrendCharts /></el-icon>
                </div>
              </div>
            </el-card>
          </el-col>
          
          <el-col :span="8">
            <el-card class="feature-card cursor-pointer" @click="router.push('/portfolio')">
              <template #header>
                <div class="card-header">
                  <span>Portfolio Management</span>
                </div>
              </template>
              <div class="feature-content">
                <div class="flex items-center justify-between">
                  <div>
                    <h4 class="text-lg font-medium mb-2">My Portfolios</h4>
                    <p class="text-gray-500">Manage your investment portfolios</p>
                  </div>
                  <el-icon class="text-2xl text-green-500"><Collection /></el-icon>
                </div>
              </div>
            </el-card>
          </el-col>
          
          <el-col :span="8">
            <el-card class="feature-card">
              <template #header>
                <div class="card-header">
                  <span>Account Status</span>
                </div>
              </template>
              <div class="feature-content">
                <p>Email: {{ userInfo?.email }}</p>
                <p>Member since: {{ new Date().toLocaleDateString() }}</p>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { ArrowDown, TrendCharts, Collection, User, Setting, SwitchButton } from '@element-plus/icons-vue';
import { authService } from '../services/api';

const router = useRouter();
const userInfo = ref(null);

onMounted(async () => {
  try {
    userInfo.value = await authService.getUserInfo();
  } catch (error) {
    ElMessage.error('Failed to get user information');
    router.push('/login');
  }
});

const handleCommand = (command) => {
  switch (command) {
    case 'profile':
      router.push('/profile');
      break;
    case 'settings':
      // Handle settings navigation
      break;
    case 'logout':
      authService.logout();
      ElMessage.success('Logged out successfully');
      router.push('/login');
      break;
  }
};
</script>

<style scoped>
.home-container {
  min-height: 100vh;
  width: 100vw;
  background-color: #f5f7fa;
  margin: 0;
  padding: 0;
  overflow-x: hidden;
  position: fixed;
  top: 0;
  left: 0;
}

.header {
  background-color: #fff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
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
  padding: 0 20px;
  box-sizing: border-box;
}

.header-content h2 {
  margin: 0;
  font-size: 24px;
  color: #2c3e50;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-dropdown {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 5px 10px;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.user-dropdown:hover {
  background-color: #f5f7fa;
}

.username {
  margin: 0 8px;
  font-weight: 500;
}

.el-main {
  margin-top: 60px;
  padding: 20px;
  width: 100%;
  max-width: none;
  box-sizing: border-box;
  min-height: calc(100vh - 60px);
}

.welcome-card {
  margin-bottom: 20px;
  background: linear-gradient(135deg, #409eff 0%, #36cfc9 100%);
  color: white;
  width: 100%;
  padding: 20px;
  box-sizing: border-box;
}

.welcome-card h3 {
  margin: 0;
  font-size: 24px;
}

.welcome-card p {
  margin: 10px 0 0;
  opacity: 0.9;
}

.feature-card {
  height: 100%;
  transition: transform 0.3s;
  margin-bottom: 20px;
}

.feature-card:hover {
  transform: translateY(-5px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.feature-content {
  padding: 10px 0;
}

.mt-20 {
  margin-top: 20px;
}

.el-button {
  margin: 5px;
}

/* 响应式布局 */
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
  
  .welcome-card h3 {
    font-size: 20px;
  }
}

.cursor-pointer {
  cursor: pointer;
}

.profile-dropdown-menu {
  min-width: 160px;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(64,158,255,0.13);
  font-size: 15px;
}
.profile-dropdown-menu .el-dropdown-menu__item {
  padding: 10px 18px;
  border-radius: 8px;
  transition: background 0.2s;
}
.profile-dropdown-menu .el-dropdown-menu__item:hover {
  background: #f0f7ff;
  color: #409eff;
}
</style> 