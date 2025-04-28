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
                <el-dropdown-menu>
                  <el-dropdown-item command="profile">Profile</el-dropdown-item>
                  <el-dropdown-item command="settings">Settings</el-dropdown-item>
                  <el-dropdown-item divided command="logout">Logout</el-dropdown-item>
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
                <el-button type="primary" plain>View Profile</el-button>
                <el-button type="success" plain>Edit Settings</el-button>
              </div>
            </el-card>
          </el-col>
          
          <el-col :span="8">
            <el-card class="feature-card">
              <template #header>
                <div class="card-header">
                  <span>Recent Activity</span>
                </div>
              </template>
              <div class="feature-content">
                <p>No recent activity</p>
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
import { ArrowDown } from '@element-plus/icons-vue';
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
      // Handle profile navigation
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
  width: 100%;
  background-color: #f5f7fa;
  margin: 0;
  padding: 0;
  overflow-x: hidden;
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
  padding: 20px;
  width: 100%;
  max-width: none;
  box-sizing: border-box;
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
</style> 