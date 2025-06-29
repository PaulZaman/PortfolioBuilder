import { createRouter, createWebHistory } from 'vue-router';
import { authService } from '../services/api';

const routes = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../components/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../components/Register.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/home',
    name: 'Home',
    component: () => import('../components/Dashboard.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/market',
    name: 'Market',
    component: () => import('../pages/Market.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/portfolio',
    name: 'Portfolio',
    component: () => import('../pages/Portfolio.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/optimization',
    name: 'Optimization',
    component: () => import('../pages/Optimization.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('../pages/Profile.vue'),
    meta: { requiresAuth: true }
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

router.beforeEach(async (to, from, next) => {
  const isAuthenticated = authService.isAuthenticated();
  
  // if requiresAuth
  if (to.meta.requiresAuth) {
    if (!isAuthenticated) {
      // redirect to login page
      next({ path: '/login', query: { redirect: to.fullPath } });
      return;
    }
    
    // if authenticated, verify token is valid
    try {
      await authService.getUserInfo();
      next();
    } catch (error) {
      // token is invalid, clear and redirect to login page
      authService.logout();
      next({ path: '/login', query: { redirect: to.fullPath } });
    }
    return;
  }
  
  // if authenticated and visiting login/register page
  if ((to.path === '/login' || to.path === '/register') && isAuthenticated) {
    next('/home');
    return;
  }
  
  // if visiting root path
  if (to.path === '/') {
    next(isAuthenticated ? '/home' : '/login');
    return;
  }
  
  next();
});

export default router; 