<template>
  <div class="register-container">
    <div class="register-background">
      <div class="register-content">
        <el-card class="register-card">
          <template #header>
            <div class="card-header">
              <h2>Create Account</h2>
              <p class="subtitle">Join our community today</p>
            </div>
          </template>
          
          <el-form :model="registerForm" :rules="rules" ref="registerFormRef">
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item prop="first_name">
                  <el-input
                    v-model="registerForm.first_name"
                    placeholder="First Name"
                    :prefix-icon="User"
                    class="custom-input"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item prop="last_name">
                  <el-input
                    v-model="registerForm.last_name"
                    placeholder="Last Name"
                    :prefix-icon="User"
                    class="custom-input"
                  />
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-form-item prop="email">
              <el-input
                v-model="registerForm.email"
                placeholder="Email"
                :prefix-icon="Message"
                class="custom-input"
              />
            </el-form-item>
            
            <el-form-item prop="password">
              <el-input
                v-model="registerForm.password"
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
                @click="handleRegister" 
                :loading="loading" 
                class="register-button"
              >
                Create Account
              </el-button>
            </el-form-item>
            
            <div class="terms">
              <el-checkbox v-model="acceptTerms">
                I agree to the <a href="#" @click.prevent="showTerms">Terms of Service</a> and <a href="#" @click.prevent="showPrivacy">Privacy Policy</a>
              </el-checkbox>
            </div>
            
            <div class="login-link">
              Already have an account? <router-link to="/login">Sign in</router-link>
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
import { User, Lock, Message } from '@element-plus/icons-vue';
import { authService } from '../services/api';

const router = useRouter();
const registerFormRef = ref(null);
const loading = ref(false);
const acceptTerms = ref(false);

const registerForm = reactive({
  email: '',
  password: '',
  first_name: '',
  last_name: ''
});

const rules = {
  email: [
    { required: true, message: 'Please enter your email', trigger: 'blur' },
    { type: 'email', message: 'Please enter a valid email address', trigger: 'blur' }
  ],
  password: [
    { required: true, message: 'Please enter your password', trigger: 'blur' },
    { min: 6, message: 'Password must be at least 6 characters long', trigger: 'blur' }
  ],
  first_name: [
    { required: true, message: 'Please enter your first name', trigger: 'blur' }
  ],
  last_name: [
    { required: true, message: 'Please enter your last name', trigger: 'blur' }
  ]
};

const handleRegister = async () => {
  if (!registerFormRef.value) return;
  
  if (!acceptTerms.value) {
    ElMessage.warning('Please accept the terms and conditions');
    return;
  }
  
  await registerFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true;
      try {
        await authService.signup(registerForm);
        ElMessage.success('Registration successful');
        router.push('/home');
      } catch (error) {
        ElMessage.error(error.response?.data?.detail || 'Registration failed');
      } finally {
        loading.value = false;
      }
    }
  });
};

const showTerms = () => {
  ElMessage.info('Terms of Service coming soon');
};

const showPrivacy = () => {
  ElMessage.info('Privacy Policy coming soon');
};
</script>

<style scoped>
.register-container {
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

.register-background {
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

.register-content {
  width: 100%;
  padding: 20px;
  display: flex;
  justify-content: center;
  margin: 0;
  box-sizing: border-box;
}

.register-card {
  width: 100%;
  max-width: 600px;
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

.register-button {
  width: 100%;
  height: 45px;
  font-size: 16px;
  margin-top: 10px;
}

.terms {
  margin: 15px 0;
  text-align: center;
  color: #666;
}

.terms a {
  color: #409eff;
  text-decoration: none;
}

.terms a:hover {
  text-decoration: underline;
}

.login-link {
  text-align: center;
  margin-top: 20px;
  color: #666;
}

.login-link a {
  color: #409eff;
  text-decoration: none;
  font-weight: 500;
}

.login-link a:hover {
  text-decoration: underline;
}

/* 响应式布局 */
@media screen and (min-width: 768px) {
  .register-background {
    padding: 40px;
  }
  
  .register-card {
    padding: 30px;
    max-width: 700px;
  }
}

@media screen and (min-width: 1200px) {
  .register-background {
    padding: 60px;
  }
  
  .register-card {
    padding: 40px;
    max-width: 800px;
  }
}

@media screen and (min-width: 1600px) {
  .register-background {
    padding: 80px;
  }
  
  .register-card {
    padding: 50px;
    max-width: 900px;
  }
}

@media screen and (max-width: 480px) {
  .register-background {
    padding: 15px;
  }
  
  .register-card {
    padding: 15px;
  }
  
  .card-header h2 {
    font-size: 24px;
  }
  
  .subtitle {
    font-size: 14px;
  }
  
  .el-row {
    margin: 0 !important;
  }
  
  .el-col {
    padding: 0 !important;
  }
}
</style> 