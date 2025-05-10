<template>
    <div class="profile-container">
      <el-button class="back-dashboard-btn" type="primary" @click="$router.push('/home')">
        <i class="el-icon-arrow-left" style="margin-right:6px;"></i>Back to Dashboard
      </el-button>
      <el-card class="profile-card">
        <div class="profile-header">
          <el-avatar :size="64" icon="el-icon-user" class="profile-avatar" />
          <div>
            <h2>User Profile</h2>
            <p class="profile-email">{{ user.email }}</p>
          </div>
        </div>
        <el-form :model="form" :rules="rules" ref="profileForm" label-width="120px" class="profile-form">
          <el-form-item label="First Name" prop="first_name">
            <el-input v-model="form.first_name" placeholder="Enter your first name" />
          </el-form-item>
          <el-form-item label="Last Name" prop="last_name">
            <el-input v-model="form.last_name" placeholder="Enter your last name" />
          </el-form-item>
          <el-form-item label="Email">
            <el-input v-model="form.email" disabled />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" :loading="updating" @click="onUpdate">Update Profile</el-button>
            <el-button type="danger" :loading="deleting" @click="onDelete" plain>Delete Account</el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>
  </template>
  
  <script>
  import { ref, reactive, onMounted } from 'vue';
  import { ElMessage, ElMessageBox } from 'element-plus';
  import { authService } from '../services/api';
  import { useRouter } from 'vue-router';
  
  export default {
    name: 'ProfilePage',
    setup() {
      const router = useRouter();
      const user = reactive({ email: '' });
      const form = reactive({ first_name: '', last_name: '', email: '' });
      const updating = ref(false);
      const deleting = ref(false);
      const profileForm = ref(null);
  
      const rules = {
        first_name: [
          { required: true, message: 'First name is required', trigger: 'blur' },
          { min: 2, max: 30, message: '2-30 characters', trigger: 'blur' }
        ],
        last_name: [
          { required: true, message: 'Last name is required', trigger: 'blur' },
          { min: 2, max: 30, message: '2-30 characters', trigger: 'blur' }
        ]
      };
  
      const fetchUser = async () => {
        try {
          const data = await authService.getUserInfo();
          user.email = data.email;
          form.first_name = data.first_name;
          form.last_name = data.last_name;
          form.email = data.email;
        } catch (e) {
          ElMessage.error('Failed to load user info');
        }
      };
  
      const onUpdate = () => {
        profileForm.value.validate(async (valid) => {
          if (!valid) return;
          updating.value = true;
          try {
            await authService.updateUserInfo({
              first_name: form.first_name,
              last_name: form.last_name
            });
            ElMessage.success('Profile updated successfully');
            fetchUser();
          } catch (e) {
            ElMessage.error('Failed to update profile');
          } finally {
            updating.value = false;
          }
        });
      };
  
      const onDelete = () => {
        ElMessageBox.confirm(
          'Are you sure you want to delete your account? This action cannot be undone.',
          'Delete Account',
          {
            confirmButtonText: 'Delete',
            cancelButtonText: 'Cancel',
            type: 'warning',
          }
        ).then(async () => {
          deleting.value = true;
          try {
            await authService.deleteUser();
            ElMessage.success('Account deleted');
            authService.logout();
            router.push('/login');
          } catch (e) {
            ElMessage.error('Failed to delete account');
          } finally {
            deleting.value = false;
          }
        });
      };
  
      onMounted(fetchUser);
  
      return {
        user,
        form,
        rules,
        updating,
        deleting,
        profileForm,
        onUpdate,
        onDelete
      };
    }
  };
  </script>
  
  <style scoped>
  .profile-container {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #f5f7fa 60%, #e3eaff 100%);
    position: relative;
  }
  .profile-card {
    width: 100%;
    max-width: 420px;
    border-radius: 18px;
    box-shadow: 0 4px 24px rgba(64, 158, 255, 0.13);
    padding: 32px 28px 24px 28px;
    background: #fff;
  }
  .profile-header {
    display: flex;
    align-items: center;
    gap: 18px;
    margin-bottom: 24px;
  }
  .profile-avatar {
    background: linear-gradient(135deg, #36cfc9 0%, #409eff 100%);
    color: #fff;
  }
  .profile-header h2 {
    margin: 0 0 2px 0;
    font-size: 24px;
    font-weight: 700;
    color: #409eff;
  }
  .profile-email {
    color: #888;
    font-size: 14px;
    margin: 0;
  }
  .profile-form {
    margin-top: 10px;
  }
  .el-form-item {
    margin-bottom: 18px;
  }
  .el-input {
    border-radius: 12px;
  }
  .el-button[type='primary'] {
    border-radius: 16px;
    background: linear-gradient(90deg, #36cfc9 0%, #409eff 100%);
    border: none;
    font-weight: 500;
    padding: 8px 22px;
  }
  .el-button[type='danger'] {
    border-radius: 16px;
    font-weight: 500;
    padding: 8px 22px;
  }
  @media (max-width: 600px) {
    .profile-card {
      padding: 16px 6px 12px 6px;
      max-width: 98vw;
    }
    .profile-header h2 {
      font-size: 20px;
    }
  }
  .back-dashboard-btn {
    position: absolute;
    top: 32px;
    left: 50%;
    transform: translateX(-50%);
    z-index: 10;
    border-radius: 16px;
    background: linear-gradient(90deg, #36cfc9 0%, #409eff 100%);
    border: none;
    font-weight: 500;
    padding: 8px 22px;
    margin-bottom: 24px;
    box-shadow: 0 2px 8px #36cfc933;
    color: #fff;
    transition: background 0.2s, box-shadow 0.2s;
  }
  .back-dashboard-btn:hover {
    background: linear-gradient(90deg, #409eff 0%, #36cfc9 100%);
    box-shadow: 0 4px 16px #409eff33;
  }
  </style>
  