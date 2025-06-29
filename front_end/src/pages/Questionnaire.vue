<template>
  <div class="questionnaire-container fade-in">
    <el-container>
      <el-header class="questionnaire-header enhanced-header">
        <div class="header-content">
          <div class="header-left">
            <img src="https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/svg/1f4dd.svg" alt="logo" class="logo" />
            <h2>Questionnaire</h2>
          </div>
          <div class="header-right">
            <el-button class="round-btn gradient-btn" type="primary" @click="$router.push('/home')">Back to Dashboard</el-button>
          </div>
        </div>
      </el-header>
      
      <el-main class="questionnaire-content">
        <Questionnaire />
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { authService } from '../services/api';
import Questionnaire from '../components/Questionnaire.vue';

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
</script>

<style scoped>
.questionnaire-container {
  min-height: 100vh;
  width: 100vw;
  background: linear-gradient(135deg, #f5f7fa 60%, #e3eaff 100%);
  margin: 0;
  padding: 0;
  overflow-x: hidden;
  top: 0;
  left: 0;
}

.questionnaire-header.enhanced-header {
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

.questionnaire-content {
  margin-top: 60px;
  padding: 32px 0 0 0;
  width: 100%;
  max-width: none;
  box-sizing: border-box;
  min-height: calc(100vh - 60px);
  display: flex;
  justify-content: center;
  align-items: flex-start;
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
  animation: fadeIn 0.7s;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Responsive layout */
@media screen and (min-width: 1200px) {
  .questionnaire-content {
    padding: 30px 60px 0 60px;
  }
  
  .header-content {
    padding: 0 60px;
  }
}

@media screen and (min-width: 1600px) {
  .questionnaire-content {
    padding: 40px 80px 0 80px;
  }
  
  .header-content {
    padding: 0 80px;
  }
}

@media screen and (max-width: 768px) {
  .questionnaire-content {
    padding: 15px 0 0 0;
  }
  
  .header-content {
    padding: 0 15px;
  }
  
  .header-content h2 {
    font-size: 20px;
  }
  
  .logo {
    width: 28px;
    height: 28px;
    margin-right: 10px;
  }
}

body, .questionnaire-container {
  font-family: 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', Arial, sans-serif;
  font-weight: 400;
  letter-spacing: 0.1px;
}
</style> 