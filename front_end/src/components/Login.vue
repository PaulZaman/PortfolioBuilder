<template>
  <div class="login-container">
    <div class="login-background">
      <div class="login-content">
        <el-card class="login-card">
          <template #header>
            <div class="card-header">
              <h2>Welcome Back</h2>
              <p class="subtitle">Sign in to continue</p>
            </div>
          </template>
          
          <el-form :model="loginForm" :rules="rules" ref="loginFormRef">
            <el-form-item prop="email">
              <el-input
                v-model="loginForm.email"
                placeholder="Email"
                :prefix-icon="User"
                class="custom-input"
              />
            </el-form-item>
            
            <el-form-item prop="password">
              <el-input
                v-model="loginForm.password"
                type="password"
                placeholder="Password"
                :prefix-icon="Lock"
                show-password
                class="custom-input"
              />
            </el-form-item>
            
            <el-form-item>
              <el-button 
                type="primary" 
                @click="handleLogin" 
                :loading="loading" 
                class="login-button"
              >
                Sign In
              </el-button>
            </el-form-item>
            
            <div class="form-footer">
              <div class="remember-me">
                <el-checkbox v-model="rememberMe">Remember me</el-checkbox>
              </div>
              <div class="forgot-password">
                <a href="#" @click.prevent="handleForgotPassword">Forgot password?</a>
              </div>
            </div>
            
            <div class="register-link">
              Don't have an account? <router-link to="/register">Create one</router-link>
            </div>
          </el-form>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { User, Lock } from '@element-plus/icons-vue';
import { authService } from '../services/api';

const router = useRouter();
const loginFormRef = ref(null);
const loading = ref(false);
const rememberMe = ref(false);

const loginForm = reactive({
  email: '',
  password: ''
});

const rules = {
  email: [
    { required: true, message: 'Please enter your email', trigger: 'blur' },
    { type: 'email', message: 'Please enter a valid email address', trigger: 'blur' }
  ],
  password: [
    { required: true, message: 'Please enter your password', trigger: 'blur' },
    { min: 6, message: 'Password must be at least 6 characters long', trigger: 'blur' }
  ]
};

const handleLogin = async () => {
  if (!loginFormRef.value) return;
  
  await loginFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true;
      try {
        await authService.login(loginForm);
        ElMessage.success('Login successful');
        router.push('/home');
      } catch (error) {
        ElMessage.error(error.response?.data?.detail || 'Login failed');
      } finally {
        loading.value = false;
      }
    }
  });
};

const handleForgotPassword = () => {
  // Implement forgot password functionality
  ElMessage.info('Forgot password feature coming soon');
};
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  width: 100vw;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f5f7fa;
  margin: 0;
  padding: 0;
  overflow-x: hidden;
  position: fixed;
  top: 0;
  left: 0;
}

.login-background {
  position: relative;
  width: 100%;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  justify-content: center;
  align-items: center;
  margin: 0;
  padding: 20px;
  box-sizing: border-box;
}

.login-content {
  width: 100%;
  padding: 20px;
  display: flex;
  justify-content: center;
  margin: 0;
  box-sizing: border-box;
}

.login-card {
  width: 100%;
  max-width: 500px;
  border-radius: 8px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  background-color: rgba(255, 255, 255, 0.95);
  margin: 0;
  padding: 20px;
  box-sizing: border-box;
}

.card-header {
  text-align: center;
  padding: 20px 0;
}

.card-header h2 {
  margin: 0;
  color: #2c3e50;
  font-size: 28px;
}

.subtitle {
  margin: 10px 0 0;
  color: #666;
  font-size: 16px;
}

.custom-input {
  margin-bottom: 15px;
}

.login-button {
  width: 100%;
  height: 45px;
  font-size: 16px;
  margin-top: 10px;
}

.form-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 15px 0;
}

.remember-me {
  color: #666;
}

.forgot-password a {
  color: #409eff;
  text-decoration: none;
}

.forgot-password a:hover {
  text-decoration: underline;
}

.register-link {
  text-align: center;
  margin-top: 20px;
  color: #666;
}

.register-link a {
  color: #409eff;
  text-decoration: none;
  font-weight: 500;
}

.register-link a:hover {
  text-decoration: underline;
}

/* 响应式布局 */
@media screen and (min-width: 768px) {
  .login-background {
    padding: 40px;
  }
  
  .login-card {
    padding: 30px;
    max-width: 600px;
  }
}

@media screen and (min-width: 1200px) {
  .login-background {
    padding: 60px;
  }
  
  .login-card {
    padding: 40px;
    max-width: 700px;
  }
}

@media screen and (min-width: 1600px) {
  .login-background {
    padding: 80px;
  }
  
  .login-card {
    padding: 50px;
    max-width: 800px;
  }
}

@media screen and (max-width: 480px) {
  .login-background {
    padding: 15px;
  }
  
  .login-card {
    padding: 15px;
  }
  
  .card-header h2 {
    font-size: 24px;
  }
  
  .subtitle {
    font-size: 14px;
  }
}
</style> 